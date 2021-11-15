from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.elements import BinaryExpression
import types

Base = declarative_base()  # 生成orm基类


# 钥匙流转记录实体类
class EntityKeyRecord(Base):
    __tablename__ = "RMS_KeyRecord"

    RecordId = Column(String(50), primary_key=True)  # 流转记录ID
    ClientId = Column(String(50))  # 终端ID
    ClientCode = Column(String(50))  # 终端编号
    CustomerId = Column(String(50))  # 客户ID
    KeyId = Column(String(50))  # 钥匙ID
    Name = Column(String(50))  # 钥匙名称
    BarCode = Column(String(50))  # 钥匙条码
    RecordType = Column(String(50))  # 记录类型（1：入库 2：领用 3：归还）
    Place = Column(String(50))  # 记录钥匙当前位置
    CreateDate = Column(String(50))  # 创建日期
    CreateUserId = Column(String(50))  # 创建人ID
    CreateUserName = Column(String(50))  # 创建人名称
    IsAdd = Column(Integer)

# engine = create_engine('mysql+pymysql://root:123456@127.0.0.1/ty_standard_talons_yanshi?charset=utf8',
#                        pool_recycle=10600, pool_size=100, max_overflow=20)
# # 连接mysql数据库，echo为是否打印结果
# Base.metadata.create_all(engine) #创建表结构
