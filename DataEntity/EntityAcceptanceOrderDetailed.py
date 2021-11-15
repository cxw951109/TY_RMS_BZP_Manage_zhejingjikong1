from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.elements import BinaryExpression
import types


class EntityAcceptanceOrderDetailed(declarative_base()):
    __tablename__ = "RMS_AcceptanceOrderDetailed"  # 没用到

    AcceptanceOrderDetailedId = Column(String(50), primary_key=True)
    AcceptanceOrderId = Column(String(50))  # 验收单id
    DrugName = Column(String(50))  # 药剂名称
    DrugCode = Column(String(50))
    CASNumber = Column(String(50))  # 标准号
    Speci = Column(Float)  # 规格
    SpeciUnit = Column(String(50))  # 规格单位
    Purity = Column(String(50))  # 纯度
    Batch = Column(String(50))  #
    PackageStatus = Column(String(50))  # 包状态
    MarkStatus = Column(String(50))  # 标记状态
    CertificateStatus = Column(String(50))  # 证书状态
    CertCharaValue = Column(String(50))  # 证书内容
    CertUncertainty = Column(String(50))  # 证书不确定性
    DetectionMethod = Column(String(50))  # 检测方法
    DetectionCharaValue = Column(String(50))  # 检测特征值
    DetectionUncertainty = Column(String(50))  # 检测
    BasicComponent = Column(String(50))  # 基本成分
    StorageConditions = Column(String(50))  # 存储条件
    Security = Column(String(50))  # 安全
    SpecialRequirements = Column(String(50))  # 特殊要求
    Manufacturer = Column(String(50))  # 生产商
    Distributor = Column(String(50))  # 销售商
    ProductionDate = Column(String(50))  # 生产日期
    ExpirationDate = Column(String(50))  # 过期日期
    ShelfLife = Column(Integer)  # 保质期
    BuyDate = Column(String(50))  # 购买日期
    Count = Column(Integer)  # 购买数量
    SortIndex = Column(Integer)
    CreateDate = Column(String(50))  # 验收单日期
    AcceptanceDate = Column(String(50))  # 验收日期
    AcceptanceUserId = Column(String(50))  # 验收人id
    AcceptanceUserName = Column(String(50))  # 验收人名称
    AcceptanceComment = Column(String(50))  # 验收结论
