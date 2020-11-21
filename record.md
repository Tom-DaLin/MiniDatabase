## 创建数据库、数据表的操作方法：

创建数据库：

create database ('table_test')

或

create database (database_name='table_test')

创建数据表：

create table (
    name='t_test',
    f_id=Field(data_type=FieldType.INT, keys=[FieldKey.PRIMARY, FieldKey.INCREMENT]),
    f_name=Field(data_type=FieldType.VARCHAR, keys=FieldKey.NOT_NULL),
    f_age=Field(data_type=FieldType.INT, keys=FieldKey.NOT_NULL)
)

## 选中数据库
use test_db

## 插入数据信息
insert ('t_test', 'f_id':123, 'f_name':'test2', 'f_age':18)

## 展示数据库、数据表
show databases
show tables


## 其他命令
**删： DELETE FROM 表名称 WHERE 列名称 = 值**  
**更新：UPDATE 表名称 SET 列名称 = 新值 WHERE 列名称 = 某值**    



### 查询指令

**查：SELECT 列名称 FROM 表名称 WHERE 列名称 = 值**    

格式为：

select 列名称 from 表名称

where 列名称 = 值

[{'f_id': 100, 'f_name': 'shiyanlou_001', 'f_age': 20}, {'f_id': 200, 'f_name': 'shiyanlou_002', 'f_age': 10}, {'f_id': 3, 'f_name': 'test', 'f_age': 30}, 

{'f_id': 4, 'f_name': 'test', 'f_age': 30},

 {'f_id': 5, 'f_name': 'test', 'f_age': 30}, 

{'f_id': 6, 'f_name': 'test', 'f_age': 30}]