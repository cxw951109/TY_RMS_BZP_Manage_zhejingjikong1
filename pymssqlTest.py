import pymssql
 #引入pymssql模块


def conn():
    connect = pymssql.connect('192.168.10.19', 'sa', 'zfdz.com', 'UFDATA_001_2020') #服务器名,账户,密码,数据库名
    if connect:
        print("连接成功!")
    return connect


if __name__ == '__main__':
    conn = conn()