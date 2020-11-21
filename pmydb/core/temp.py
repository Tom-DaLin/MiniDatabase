# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 21:32:25 2020

@author: Team317
"""

from pmydb.core.database import Database
from pmydb.core import SerializedInterface
from pmydb.parser import *
import prettytable
import base64
import os
from pmydb.core.field import Field
from pmydb.core import FieldKey,FieldType,TYPE_MAP


'''
(1)json.dumps()函数是将一个Python数据类型列表进行json格式的编码（可以这么理解，json.dumps()函数是将字典转化为字符串）
(2)json.loads()函数是将json格式数据转换为字典（可以这么理解，json.loads()函数是将字符串转化为字典）
'''

# 解码数据
def _decode_db(content):
    content = base64.decodebytes(content)
    return content.decode()[::-1]


# 编码数据 str-->bytes-->base64 逆序
def _encode_db(content):
    content = content[::-1].encode()
    return base64.encodebytes(content)


# 数据库引擎
class Engine:
    def __init__(self, db_name=None, format_type ='dict', path=r'D:\ProgramCoding\GitProject\MiniDatabase\db.data'):
        ...
        self.__current_db = None  # 标示当前使用的数据库
        print('文件是否存在：', os.path.exists(path))

        
        # 如果初始化时数据库名字参数不为空，调用 select_db 方法选中数据库
        if db_name is not None:
            self.select_db(db_name)
        self.__database_objs = {}       # 数据库映射表
        self.__database_names = []      # 数据库名字集合
        self.path = path
        self.__load_databases()        # 将以前的数据库，数据表load起来
        self.__format_type = format_type  # 数据默认返回格式

        # 数据库映射表，衔接parser模块
        self.operator = {
            'create': self.__create,
            'show': self.__show,
            'use': self.__use,
            'insert': self.__insert,
            'update': self.__update,
            'delete': self.__delete,
            'exit': self.__exit,
            'quit':self.__quit,
            
            'select': self.__search,
            'drop': self.__drop,

        }
    
    ## 传入一条语句，执行相关操作
    def handle(self, message):

        # 如果前四个字符为exit或quit则关闭窗口，退出程序
        if message[0:4] in ['exit', 'quit']:
            print('exit', 'temp--退出，关闭窗口')
            return 'exit'
        
        # 其他指令需分别进行解析
        Info = message.split('\n\n')  # 用两个行分隔符作为两条不同语句的分隔条件
        print("Info:", Info)
        for info in Info:
            info = info.split(' ')
            print(info)
            message = self.operator[info[0]](info)
        print("for循环后得到的message：", message)
        
        # 更新数据库信息
        if info[0] in ['insert', 'update', 'delete', 'create', 'drop', 'use']:
            print("需更新数据库")
            self.commit()  # 提交数据库改动
            return [info[0], "Successful execution!"]
        
        # 查询语句
        if info[0] in ['select', 'show']:
            return [info[0], message]
        
        
        
        

        
    ## use 选中数据库
    def __use(self, info):
        print(info)
        return self.select_db(info[1].split('\n')[0])
    
    # 选择数据库
    def select_db(self, db_name):
        # 如果不存在该数据库索引，抛出数据库不存在异常
        if db_name not in self.__database_objs:
            raise Exception('has not this database')

        # 将对应名字的 Database 对象赋值给 __current_db
        self.__current_db = self.__database_objs[db_name]

    
    ## create 创建数据库、数据表
    def __create(self, info):
        command = 'create_' + ' '.join(x for x in info[1:])
        print(command)
        eval('self.' + command)

    # 创建数据表
    def create_table(self, name, **options):
        self.__check_is_choose()
        self.__current_db.create_table(name, **options)
        print("将要创建数据表")
        print("")
    
    # 创建数据库
    def create_database(self, database_name):
        # 判断数据库名字是否存在，如果存在，抛出数据库已存在异常
        if database_name in self.__database_objs:
            raise Exception('Database exist')

        # 追加数据库名字
        self.__database_names.append(database_name)

        # 关联数据库对象和数据库名
        self.__database_objs[database_name] = Database(database_name)

    ## show 展示数据库
    def __show(self, info):
        if info[1].split('\n')[0] == 'databases':
            print('come in')
            data =  self.get_database(format_type='dict')
        elif info[1].split('\n')[0] == 'tables':
            data = self.get_table(format_type='dict')
        pt = prettytable.PrettyTable(data[0].keys())
        pt.align = 'l'
        for line in data:
            pt.align = 'r'
            pt.add_row(line.values())
        print(pt)
        return data
        
    ## insert 向数据表插入数据
    def __insert(self, info):
        # insert ('t_test', 123, 'test2', 18)
        message = ' '.join(x for x in info)
        arg = message.split('(')[1].split(')')[0].split(',')  # 获得所有参数
        Arg = arg[0] + ', data={' + ','.join(x for x in arg[1:]) + '}' # 将参数转为字符串
        command = 'self.' + 'insert(' + Arg + ')'  # 得到字符串形式的命令
        eval(command) # 执行命令
        
    def insert(self,table_name,**data):
        ## __get_table()返回table对象，用.insert()向table中插入数据
        return self.__get_table(table_name).insert(**data)

    ## update 更新指定数据表数据
    def __update(self, action):
        table = action['table']
        data = action['data']
        conditions = action['conditions']
        
        return self.update(table, data, conditions=conditions)
    
    def update(self, table_name, data, **conditions):
        self.__get_table(table_name).update(data, **conditions)
        

    ## drop 删除数据库
    def __drop(self, info):
        if action['kind'] == 'database':
            return self.drop_database(action['name'])
        return self.drop_table(action['name'])

    def drop_database(self,database_name):
        # 判断数据库名字是否存在，如果存在，抛出数据库已存在异常
        if database_name not in self.__database_objs:
            raise Exception('Database not exist')

        self.__database_names.remove(database_name)

        self.__database_objs.pop(database_name, True)  #删除成功返回True
    
    
    ## delete 删除指定数据表
    def __delete(self, info):
        table_name = info[1]
        self.delete(table_name, conditions=conditions)
    def delete(self, table_name, **conditions):
        return self.__get_table(table_name).delete(**conditions)
    

    ## select 查询语句 当前仅支持单表简单查询
    def __search(self, info):
        # print('engine __search:', action)
        table = info[3].split('\n')[0]
        fields = info[1]
        conditions = []
        print("come here")
        print("table : ", table)
        

        return self.search(table, fields=fields, conditions=conditions)

    # 查询指定数据表数据
    def search(self, table_name, fields='*', sort='ASC', **conditions):
        # 通过数据表名字获取指定的 Table 对象，再调用它的 search 方法获取查询结果
        # print('into search')
        # print(table_name, fields, sort, conditions)
        return self.__get_table(table_name).search(fields=fields, sort=sort, format_type=self.__format_type,
                                                   **conditions)

    
    ## quit、exit 退出
    def __quit(self, _):
        return 'quit'
    
    def __exit(self, _):
        return 'exit'
    
    
    

    def serialized(self):
        return SerializedInterface.json.dumps([
             database.serialized() for database in self.__database_objs.values()
        ])

        

    #保存数据库
    def __dump_databases(self):
        with open(self.path, 'wb') as f:
            # 编码json字符串
            a = self.serialized()
            content = _encode_db(a)
            f.write(content)

    def deserialized(self, content):
        data_obj = SerializedInterface.json.loads(content)

        for database in data_obj:
            database = Database.deserialized(database)
            # 获取数据库名字
            db_name = database.get_name()

            # 追加数据库名字和绑定数据库对象
            self.__database_names.append(db_name)
            self.__database_objs[db_name] = database

    # 加载数据库
    def __load_databases(self):
        if not os.path.exists(self.path):
            return
        with open(self.path, 'rb') as f:
            content = f.read()

        if content:
            # 解码数据，并把数据传给反序列化函数
            self.deserialized(_decode_db(content))

    # 提交数据库改动
    def commit(self):
        self.__dump_databases()

    # 回滚数据库改动，目前的实现有问题，不会判断以前的数据库表是否存在
    def rollback(self):
        self.__load_databases()


    # 获取数据表
    def __get_table(self, table_name):

        # 判断当前是否有选中的数据库
        self.__check_is_choose()

        # 获取对应的 Table 对象
        table = self.__current_db.get_table_obj(table_name)

        # 如果 Table 对象为空，抛出异常
        if table is None:
            raise Exception('not table %s' % table_name)

        # 返回 Table 对象
        return table

    # 检查是否选择数据库
    def __check_is_choose(self):
        # 如果当前没有选中的数据库，抛出为选择数据库异常
        if not self.__current_db or not isinstance(self.__current_db, Database):
            raise Exception('No database choose')





    # 实现外部接口
    # 创建数据表


    # 获取数据库名
    def get_database(self, format_type='list'):
        databases = self.__database_names

        if format_type == 'dict':
            tmp = []
            for database in databases:
                tmp.append({'name': database})

            databases = tmp

        return databases

    # 获取数据表
    def get_table(self, format_type='list'):
        self.__check_is_choose()

        tables = self.__current_db.get_table()

        if format_type == 'dict':
            tmp = []
            for table in tables:
                tmp.append({'name': table})

            tables = tmp

        return tables

    # 添加执行函数,statement为SQL字符串
    def execute(self, statement):
        action = SQLParser().parse(statement)
        # print('execute action:', action)

        ret = 0
        if action['type'] in self.__action_map:
            ## 字典与函数相结合
            ret = self.__action_map[action['type']](action)

            if action['type'] in ['insert', 'update', 'delete', 'create', 'drop']:
                self.commit()
        # print('execute ret:', ret)
        return ret







    




    # 执行，命令行入口接口，在此输入sql
    def run(self):
        while True:
            # 获得SQL输入
            statement = input('\033[00;37mpmydb> ')
            # print(statement)
            try:
                
                # print(type(statement),statement)
                ret = self.execute(statement)
                # print('ret:', ret)
                if ret in ['exit', 'quit']:
                    print('Goodbye!')
                    return
                if ret:
                    pt = prettytable.PrettyTable(ret[0].keys())
                    pt.align = 'l'
                    for line in ret:
                        pt.align = 'r'
                        pt.add_row(line.values())
                    print(pt)
            except Exception as exc:
                print('\033[00;31m' + str(exc))

    # testcase 执行，命令行入口接口，在此输入sql
    def run_test(self):
        # statements = ['use test_db', "insert into t_test (f_name,f_age) values ('test',30)"]
        statements = ['create database xyxdb','use xyxdb']
        for i in range(2):
            # 获得SQL输入
            statement = statements[i]
            # print(statement)
            try:
                print(type(statement), statement)
                ret = self.execute(statement)
                print('ret:', ret)
                if ret in ['exit', 'quit']:
                    print('Goodbye!')
                    return
                if ret:
                    pt = prettytable.PrettyTable(ret[0].keys())
                    pt.align = 'l'
                    for line in ret:
                        pt.align = 'r'
                        pt.add_row(line.values())
                    print(pt)
            except Exception as exc:
                print('\033[00;31m' + str(exc))

        







