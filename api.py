# ！/usr/bin/env python
# _*_ coding:utf-8 _*_

'''

@author: yerik

@contact: xiangzz159@qq.com

@time: 2018/4/18 11:17

@desc: 数据库查询

'''

import re
import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
import sqlalchemy
import six
import models
import mutations


class CountableConnection(relay.Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()

    @staticmethod
    def resolve_total_count(root, info):
        return root.length


class CustomSQLAlchemyObjectType(SQLAlchemyObjectType):
    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, model=None, registry=None,
                                    skip_registry=False, only_fields=(),
                                    exclude_fields=(), connection=None,
                                    use_connection=None, interfaces=(),
                                    id=None, **options):
        # Force it to use the countable connection
        countable_conn = connection or CountableConnection.create_type(
            "{}CountableConnection".format(model.__name__),
            node=cls)

        super(CustomSQLAlchemyObjectType, cls).__init_subclass_with_meta__(
            model,
            registry,
            skip_registry,
            only_fields,
            exclude_fields,
            countable_conn,
            use_connection,
            interfaces,
            id,
            **options)


class Admin(CustomSQLAlchemyObjectType):
    class Meta:
        model = models.Admin
        interfaces = (relay.Node,)

        # 限制字段查询
        exclude_fields = ['password']


class Book(CustomSQLAlchemyObjectType):
    class Meta:
        model = models.Book
        interfaces = (relay.Node,)


class FilteringConnectionField(SQLAlchemyConnectionField):
    RELAY_ARGS = ['first', 'last', 'before', 'after']
    SPECIAL_ARGS = ['distinct', 'op', 'jsonkey', 'order']

    @classmethod
    def get_query(cls, model, info, **args):
        from sqlalchemy import or_
        from sqlalchemy.orm import load_only
        query = super(FilteringConnectionField, cls).get_query(model, info)
        from sqlalchemy.orm import joinedload
        distinct_filter = False  # default value for distinct
        op = 'eq'
        jsonkey_input = None
        ALLOWED_OPS = ['gt', 'lt', 'le', 'ge', 'eq', 'ne',
                       '=', '>', '<', '>=', '<=', '!=']

        cont_fields = ['edges', 'node']
        skip_fields = ['totalCount', 'pageInfo']
        fields = info.field_asts  # [0].selection_set.selections
        load_fields = {}
        field_names = []

        def convert(name):
            import re
            s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
            return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

        while isinstance(fields, list):
            for field in fields:
                name = field.name.value
                if name in cont_fields:
                    fields = field.selection_set.selections
                elif name in skip_fields or name[0].isupper():
                    continue
                else:
                    if field.selection_set is not None:
                        keyname = name
                        field_names.append(name)
                        load_fields.update({keyname: []})
                        fields = field.selection_set.selections
                    else:
                        load_fields[keyname].append(convert(name))
                        fields = None

        query = query.options(load_only(*load_fields[field_names[0]]))

        if len(field_names) > 1:
            column = getattr(model, convert(field_names[1]), None)
            query = query.options(joinedload(column, innerjoin=True).load_only(*load_fields[field_names[1]]))

        for field, value in args.items():
            if field == 'distinct':
                distinct_filter = value
            elif field == 'op':
                if value in ALLOWED_OPS:
                    op = value
            elif field == 'jsonkey':
                jsonkey_input = value
            elif field == 'order':
                ascending = not value.startswith('-')
                column_name = value if not value.startswith('-') else value[1:]
                column = getattr(model, convert(column_name), None)

                if ascending:
                    query = query.order_by(column)
                else:
                    query = query.order_by(column.desc())

        for field, value in args.items():
            if field not in (cls.RELAY_ARGS + cls.SPECIAL_ARGS):
                from sqlalchemy.sql.expression import func, cast
                jsonb = False
                jsonkey = None
                if '__' in field:
                    field, jsonkey = field.split('__')
                if jsonkey is None:
                    jsonkey = jsonkey_input

                column = getattr(model, field, None)

                if str(column.type) == "TSVECTOR":
                    query = query.filter(column.match("'{}'".format(value)))

                elif str(column.type) == "JSONB":
                    jsonb = True
                    if jsonkey is not None:
                        query = query.filter(column.has_key(jsonkey))
                        column = column[jsonkey].astext
                    values = value.split('+')

                    for value in values:
                        value = value.strip()
                        if value.startswith("~"):
                            column = cast(column, sqlalchemy.String)
                            # if field == 'reactants' or field == 'products':
                            #    column = func.replace(func.replace(column, 'gas', ''), 'star', '')

                            search_string = '%' + value[1:] + '%'

                            if not value == "~":
                                query = query.filter(
                                    column.ilike(search_string))
                            # else:
                            #    query = query.group_by(column)

                        else:
                            if field == 'reactants' or field == 'products':
                                if not 'star' in value and not 'gas' in value:
                                    or_statement = or_(column.has_key(value),
                                                       column.has_key(value +
                                                                      'gas'),
                                                       column.has_key(value +
                                                                      'star'))

                                    query = query.filter(or_statement)
                                else:
                                    query = query.filter(column.has_key(value))
                            else:
                                if jsonkey is not None:
                                    query = query.filter(column == value)
                                else:
                                    query = query.filter(column.has_key(value))

                    # if distinct_filter:
                    # TO DO: SELECT DISTINCT jsonb_object_keys(reactants) FROM reaction

                elif isinstance(value, six.string_types):
                    if value.startswith("~"):
                        search_string = '%' + value[1:] + '%'
                        if not query == "~":
                            query = query.filter(column.ilike(search_string))
                    else:
                        query = query.filter(column == value)

                    # if distinct_filter:
                    #     query = query.distinct(column)#.group_by(column)

                else:
                    if op in ['ge', '>=']:
                        query = query.filter(column >= value)
                    elif op in ['gt', '>']:
                        query = query.filter(column > value)
                    elif op in ['lt', '<']:
                        query = query.filter(column < value)
                    elif op in ['le', '<=']:
                        query = query.filter(column <= value)
                    elif op in ['ne', '!=']:
                        query = query.filter(column != value)
                    else:
                        query = query.filter(column == value)

                if distinct_filter:
                    query = query.distinct(column)  # .group_by(getattr(model, field))

        query = query.limit(200)
        return query


def get_filter_fields(model):
    """Generate filter fields (= comparison)
    from graphene_sqlalcheme model
    """
    # publication_keys = ['publisher', 'doi', 'title', 'journal', 'authors', 'year']
    filter_fields = {}
    for column_name in dir(model):
        # print('FF {model} => {column_name}'.format(**locals()))
        if not column_name.startswith('_') \
                and not column_name in ['metadata', 'query', 'cifdata']:
            column = getattr(model, column_name)
            column_expression = column.expression

            if '=' in str(column_expression):  # filter out foreign keys
                continue
            elif column_expression is None:  # filter out hybrid properties
                continue
            elif not ('<' in repr(column_expression) and '>' in repr(column_expression)):
                continue

            # column_type = repr(column_expression).split(',')[1].strip(' ()')
            column_type = re.split('\W+', repr(column_expression))

            column_type = column_type[2]
            if column_type == 'Integer':
                filter_fields[column_name] = getattr(graphene, 'Int')()
            elif column_type == 'TSVECTOR':
                filter_fields[column_name] = getattr(graphene, 'String')()
            elif column_type == 'JSONB':
                filter_fields[column_name] = getattr(graphene, 'String')()
            elif column_type == 'BigInteger':
                filter_fields[column_name] = getattr(graphene, 'Float')()
            else:
                filter_fields[column_name] = getattr(graphene, column_type)()
    # always add a distinct filter
    filter_fields['distinct'] = graphene.Boolean()
    filter_fields['op'] = graphene.String()
    filter_fields['search'] = graphene.String()
    filter_fields['jsonkey'] = graphene.String()
    filter_fields['order'] = graphene.String()

    return filter_fields


class Query(graphene.ObjectType):
    node = relay.Node.Field()
    books = FilteringConnectionField(
        Book, **get_filter_fields(models.Book)
    )

schema = graphene.Schema(
    query=Query,
    mutation=mutations.MyMutations,
    types=[
        Book,
    ])
