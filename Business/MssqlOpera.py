
import pymysql
pymysql.install_as_MySQLdb()
import pymysql
 #引入pymssql模块

class MssqlOpera(object):
    
    def __init__(self):
        pass

    def connect(self):
        connect = pymssql.connect('127.0.0.1', 'sa', '123456', 'UFDATA_001_2020') #服务器名,账户,密码,数据库名
        if connect:
            print("连接成功!")
        return connect

    def execute(self,sql):
        conn=self.connect()
        cursor = conn.cursor()
        cursor.execute(sql)
        list=cursor.fetchall()
        conn.close()
        return list

    def executeOne(self,sql):
        conn=self.connect()
        cursor = conn.cursor()
        cursor.execute(sql)
        entity=cursor.fetchone()
        conn.close()
        return entity

if __name__ == '__main__':
    conn = conn()