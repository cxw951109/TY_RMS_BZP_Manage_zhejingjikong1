from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.elements import BinaryExpression
import types

Base = declarative_base()  # 生成orm基类


# 用户角色实体类
class EntityKey(Base):
    __tablename__ = "RMS_Key"

    Id = Column(String(50), primary_key=True)  # ID
    BarCode = Column(String(50))  # 条码
    ClientId = Column(String(50))  # 终端ID
    ClientCode = Column(String(50))  # 终端编号
    Name = Column(String(50))  # 钥匙名称
    Place = Column(String(50))  # 钥匙在终端的位置序号
    Status = Column(Integer)  # 钥匙状态  1在库  2出库  5待绑定
    CorrespondingClientId = Column(String(50))  # 钥匙对应柜子的id
    CorrespondingClientCode = Column(String(50))  # 钥匙对应柜子的编号
    CreateDate = Column(String(50))  # 创建日期





# engine = create_engine('mysql+pymysql://root:123456@127.0.0.1/ty_standard_talons_yanshi?charset=utf8',
#                        pool_recycle=10600, pool_size=100, max_overflow=20)
# # 连接mysql数据库，echo为是否打印结果
# Base.metadata.create_all(engine) #创建表结构
