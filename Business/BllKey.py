from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.elements import BinaryExpression
from Business.Repository import *
from DataEntity.EntityKeyRecord import EntityKeyRecord
from DataEntity.EntityMedicamentVariety import *
from DataEntity.EntityUser import *
from DataEntity.EntityModule import *
from DataEntity.EntityKey import *
from Lib.Utils import *

import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.elements import BinaryExpression, BooleanClauseList
from sqlalchemy.sql import func
import threading


# 功能模块
class BllKey(Repository):
    # _instance_lock = threading.Lock()
    # #实现单例模式
    #
    # def __new__(cls, *args, **kwargs):
    #     if not hasattr(BllLog, "_instance"):
    #         with BllLog._instance_lock:
    #             if not hasattr(BllLog, "_instance"):
    #                 BllLog._instance = object.__new__(cls)
    #     return BllLog._instance

    def __init__(self, entityType=EntityKey):
        return super().__init__(entityType)

    # 获取所有钥匙列表(包括危化品)
    def getAllList(self, _searchWord, pageParam, clientId=''):
        queryStr = ''
        queryParams = {}
        if (clientId == ''):
            queryStr = 'select * from RMS_Key where  Name like :searchWord or BarCode like :searchWord or ClientCode like :searchWord or CorrespondingClientCode like :searchWord order by CreateDate desc'
            queryParams = {"searchWord": '%' + _searchWord + '%'}
        else:
            queryStr = 'select * from RMS_Medicament where ClientId=:clientId and ( Name like :searchWord or BarCode like :searchWord or ClientCode like :searchWord or CorrespondingClientCode like :searchWord) order by CreateDate desc'
            queryParams = {"searchWord": '%' + _searchWord + '%', 'clientId': clientId}
        print('获取钥匙列表', queryStr + (' limit ' + str((pageParam.curPage - 1) * pageParam.pageRows) + ',' + str(
            pageParam.pageRows) if pageParam.pageRows != 0 else ''))
        try:
            templateList = self.execute(queryStr + (
                ' limit ' + str((pageParam.curPage - 1) * pageParam.pageRows) + ',' + str(
                    pageParam.pageRows) if pageParam.pageRows != 0 else ''), queryParams).fetchall()
            pageParam.totalRecords = self.execute(queryStr.replace('*', 'count(*)'), queryParams).fetchone()[0]
            jsonData = Utils.mysqlTable2Model(templateList)
        except:
            return []
        return jsonData

    # 钥匙新增
    def KeyUpdate(self, entityKey=EntityKey(), entityClient=EntityClient(), entityUser=EntityUser(), str_sm=""):
        entityKeyRecord = EntityKeyRecord()
        entityKeyRecord.RecordId = Utils.UUID()
        entityKeyRecord.CustomerId = entityClient.CustomerId
        entityKeyRecord.ClientId = entityClient.ClientId
        entityKeyRecord.ClientCode = entityClient.ClientCode
        entityKeyRecord.KeyId = entityKey.Id
        entityKeyRecord.Name = entityKey.Name
        entityKeyRecord.BarCode = entityKey.BarCode
        entityKeyRecord.RecordType = str_sm
        entityKeyRecord.Place = entityKey.Place
        entityKeyRecord.CreateDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entityKeyRecord.CreateUserId = entityUser.UserId
        entityKeyRecord.CreateUserName = entityUser.RealName
        # 创建事务
        self.beginTrans()
        self.session.add(entityKey)
        self.session.add(entityKeyRecord)
        boolean_ = self.commitTrans()
        print(boolean_, 66666666666)
        return boolean_
