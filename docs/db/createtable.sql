DROP TABLE IF EXISTS `admin`;
CREATE TABLE `admin` (
  `id` VARCHAR(64) NOT NULL COMMENT 'ID',
  `email` varchar(255) DEFAULT NULL COMMENT '登入邮箱',
  `name` varchar(255) DEFAULT NULL COMMENT '名称',
  `password` varchar(255) DEFAULT NULL COMMENT '密码',
  `role_id` INT(8) DEFAULT NULL COMMENT '角色id',
  `role_name` varchar(255) DEFAULT NULL COMMENT '角色名称',
  `created_by` varchar(64) DEFAULT NULL COMMENT '创建人id',
  `last_modified_by` varchar(64) DEFAULT NULL COMMENT '更新人id',
  `del_flag` INT(1) NOT NULL DEFAULT '1' COMMENT '状态：0：废弃，1：正常',
  `create_time` BIGINT(20) NULL COMMENT '创建时间',
  `update_time` BIGINT(20) NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8 COMMENT='管理账户表';

DROP TABLE IF EXISTS `book`;
CREATE TABLE `book`(
  `id` VARCHAR(64) NOT NULL COMMENT 'ID',
  `name` VARCHAR(64) NULL COMMENT '书名',
  `author`	VARCHAR(64) NOT NULL COMMENT '作者',
  `title` VARCHAR(255) NOT NULL COMMENT '标题',
  `price` INT(10) NULL COMMENT '价格',
  `del_flag` INT(1) NOT NULL DEFAULT '1' COMMENT '状态：0：废弃，1：正常',
  `create_time` BIGINT(20) NULL COMMENT '创建时间',
  `update_time` BIGINT(20) NULL COMMENT '更新时间',
  PRIMARY KEY(`id`)
)ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='书';


