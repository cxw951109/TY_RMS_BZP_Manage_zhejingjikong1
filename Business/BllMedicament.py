from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.elements import BinaryExpression
from Business.Repository import *
from Business.BllMedicamentRecord import *
from Business.BllUserMedicament import *
from Business.BllWarning import *
from Business.BllMedicamentVariety import *
from Business.BllMedicamentTemplate import *
from DataEntity.EntityMedicamentTemplate import *
from DataEntity.EntityMedicament import *
from DataEntity.EntityMedicamentVariety import *
from DataEntity.EntityMedicamentRecord import *
from DataEntity.EntityClient import *
from DataEntity.EntityWarning import *
from DataEntity.EntityUser import *
from Lib.Utils import *
import datetime
from Lib.Model import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.elements import BinaryExpression, BooleanClauseList
from sqlalchemy.sql import func, text
import threading

#试剂流程业务逻辑类


class BllMedicament(Repository):
    # _instance_lock = threading.Lock()
    # #实现单例模式
    #
    # def __new__(cls, *args, **kwargs):
    #     if not hasattr(BllMedicament, "_instance"):
    #         with BllMedicament._instance_lock:
    #             if not hasattr(BllMedicament, "_instance"):
    #                 BllMedicament._instance = object.__new__(cls)
    #     return BllMedicament._instance

    def __init__(self, entityType=EntityMedicament):
        return super().__init__(entityType)

    #获取试剂列表
    def getDrugList(self, customerId, keyWord, pageParam):
        keyWord = '%'+keyWord+'%'
        orm_query = self.findList().filter(EntityMedicament.CustomerId == customerId
                                           ).filter(or_(EntityMedicament.RFID.like(keyWord), EntityMedicament.Name.like(keyWord))).order_by(desc(EntityMedicament.PutInStorageDate))
        return self.queryPage(orm_query, pageParam)

    # 试剂入库
    def drugPutIn(self, entityDrug=EntityMedicament(),entityClient=EntityClient(),entityUser=EntityUser()):
        entityDrugRecord = EntityMedicamentRecord()
        entityDrugRecord.RecordId = Utils.UUID()
        entityDrugRecord.CustomerId = entityClient.CustomerId
        entityDrugRecord.ClientId = entityClient.ClientId
        entityDrugRecord.ClientCode = entityClient.ClientCode
        entityDrugRecord.VarietyId = entityDrug.VarietyId
        entityDrugRecord.MedicamentId = entityDrug.MedicamentId
        entityDrugRecord.RecordRemain=entityDrug.Remain
        entityDrugRecord.Price = entityDrug.Price
        entityDrugRecord.RecordType = 1
        entityDrugRecord.IsEmpty = 0
        entityDrugRecord.CreateDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entityDrugRecord.CreateUserId = entityUser.UserId
        entityDrugRecord.CreateUserName = entityUser.RealName
        # 创建事务
        self.beginTrans()
        self.session.add(entityDrug)
        if(entityDrug.Status==1):
            self.session.add(entityDrugRecord)
        boolean_ = self.commitTrans()
        print(boolean_, 66666666666)
        return boolean_


    # 试剂领用
    def drugUse(self, entityDrug=EntityMedicament(), entityClient=EntityClient(), entityUser=EntityUser()):
        #创建事务
        self.beginTrans()
        self.session.merge(entityDrug)
        if(BllUserMedicament().isJInZhiUser(entityUser.UserId,entityDrug.MedicamentId)):
            warning_obj = EntityWarning(WarningId=str(Utils.UUID()), CustomerId=entityDrug.CustomerId,
                                        ObjectType=7, ObjectId=entityDrug.MedicamentId, ObjectName=entityDrug.Name,
                                        WarningContent= entityUser.RealName+'违规领用了试剂“'+entityDrug.Name+'”（'+entityDrug.BarCode+'）',WarningDate=datetime.datetime.now(),
                                        WarningUserName=entityUser.RealName, IsSolve=0, IsAdd=1)
            BllWarning().insert(warning_obj)
        entityDrugRecord=EntityMedicamentRecord()
        entityDrugRecord.RecordId=Utils.UUID()
        entityDrugRecord.CustomerId=entityClient.CustomerId
        entityDrugRecord.ClientId=entityClient.ClientId
        entityDrugRecord.ClientCode=entityClient.ClientCode
        entityDrugRecord.VarietyId=entityDrug.VarietyId
        entityDrugRecord.MedicamentId=entityDrug.MedicamentId
        entityDrugRecord.Price=entityDrug.Price
        entityDrugRecord.RecordType=DrugRecordType.Use
        entityDrugRecord.RecordRemain=entityDrug.Remain
        entityDrugRecord.IsEmpty=0
        entityDrugRecord.CreateDate=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entityDrugRecord.CreateUserId=entityUser.UserId
        entityDrugRecord.CreateUserName=entityUser.RealName
        self.session.add(entityDrugRecord)
        entityVariety = BllMedicamentVariety().findEntity(entityDrug.VarietyId)
        entityVariety.NormalCount-=1
        entityVariety.UseCount+=1
        self.session.merge(entityVariety)
        self.commitTrans()

    # 试剂归还
    def drugReturn(self, entityDrug=EntityMedicament(), entityClient=EntityClient(), entityUser=EntityUser()):
        #创建事务
        self.beginTrans()
        self.session.merge(entityDrug)
        entityDrugRecord=EntityMedicamentRecord()
        entityDrugRecord.RecordId=Utils.UUID()
        if(entityDrug.Status!=3):
            entityDrugRecord.CustomerId=entityClient.CustomerId
            entityDrugRecord.ClientId=entityClient.ClientId
            entityDrugRecord.ClientCode=entityClient.ClientCode
            lastRemain=BllMedicamentRecord().getLastRecordRemain(entityDrug.MedicamentId)
            entityDrugRecord.UseQuantity=float(lastRemain)-float(entityDrug.Remain if entityDrug.Remain else 0)
            entityDrugRecord.RecordRemain=entityDrug.Remain
        else:
             entityDrugRecord.CustomerId=entityUser.CustomerId
             entityDrugRecord.ClientId='0'
             entityDrugRecord.ClientCode=0
             entityDrugRecord.UseQuantity=entityDrug.Remain
             entityDrugRecord.RecordRemain=0
             entityDrug.Remain=0
             self.session.merge(entityDrug)
        entityDrugRecord.VarietyId=entityDrug.VarietyId
        entityDrugRecord.MedicamentId=entityDrug.MedicamentId
        entityDrugRecord.Price=entityDrug.Price
        entityDrugRecord.RecordType=DrugRecordType.Return
        entityDrugRecord.IsEmpty=1 if(entityDrug.Status==DrugStatus.Empty) else 0
        entityDrugRecord.CreateDate=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entityDrugRecord.CreateUserId=entityUser.UserId
        entityDrugRecord.CreateUserName=entityUser.RealName
        self.session.add(entityDrugRecord)
        entityVariety = BllMedicamentVariety().findEntity(entityDrug.VarietyId)
        if(entityDrug.Remain!=0):
            entityVariety.NormalCount+=1
        else:
            entityVariety.EmptyCount += 1
        entityVariety.UseCount-=1
        self.session.merge(entityVariety)

        self.commitTrans()

    #获取离保质期最近的同类试剂
    def getDrugNearExpired(self, varietyId, customerId):
        drugList = self.findList().order_by(
            desc(EntityMedicament.ExpirationDate)).limit(1)
        return drugList.first()

    #获取待归还试剂列表
    def getWaitReturnDrugList(self, customerId):
        drugList = self.findList(and_(EntityMedicament.CustomerId ==
                                      customerId, EntityMedicament.Status == DrugStatus.Out)).all()
        return drugList

    #获取待入库试剂模板
    def getWaitPutInDrugTemplateList(self, customerId, clientId):
        templateList = BllMedicamentTemplate().findList(and_(EntityMedicamentTemplate.CustomerId == customerId,
                                                             EntityMedicamentTemplate.ClientId == clientId, EntityMedicamentTemplate.IsWaitExport == 1)).all()
        return templateList

    #获取所有试剂列表
    def getAllDrugList(self, _searchWord, pageParam,clientId=''):
        queryStr=''
        queryParams={}
        if(clientId==''):
            queryStr = 'select * from RMS_Medicament where  (IsHazardous is null or IsHazardous<>1) and (Name like :searchWord or BarCode like :searchWord or EnglishName like :searchWord or Remark1 like :searchWord or Remark2 like :searchWord or Remark3 like :searchWord or Remark4 like :searchWord) order by PutInDate desc'
            queryParams = {"searchWord": '%'+_searchWord+'%'}
        else:
            queryStr = 'select * from RMS_Medicament where (IsHazardous is null or IsHazardous<>1) and ClientId=:clientId and ( Name like :searchWord or BarCode like :searchWord or EnglishName like :searchWord or Remark1 like :searchWord or Remark2 like :searchWord or Remark3 like :searchWord or Remark4 like :searchWord) order by PutInDate desc'
            queryParams = {"searchWord": '%'+_searchWord+'%','clientId':clientId}
        print('获取试剂列表',queryStr + (' limit ' + str((pageParam.curPage-1)*pageParam.pageRows)+','+str(pageParam.pageRows) if pageParam.pageRows != 0 else ''))
        templateList = self.execute(queryStr + (' limit ' + str((pageParam.curPage-1)*pageParam.pageRows)+','+str(pageParam.pageRows) if pageParam.pageRows != 0 else ''), queryParams).fetchall()
        pageParam.totalRecords = self.execute(queryStr.replace('*', 'count(*)'), queryParams).fetchone()[0]
        print(pageParam.totalRecords)
        jsonData = Utils.mysqlTable2Model(templateList)
        return jsonData

    #获取所有试剂列表(包括危化品)
    def getAllList(self, _searchWord, pageParam,clientId=''):
        queryStr=''
        queryParams={}
        if(clientId==''):
            queryStr = 'select * from RMS_Medicament where  Name like :searchWord or BarCode like :searchWord or EnglishName like :searchWord or Remark1 like :searchWord or Remark2 like :searchWord or Remark3 like :searchWord or Remark4 like :searchWord order by PutInDate desc'
            queryParams = {"searchWord": '%'+_searchWord+'%'}
        else:
            queryStr = 'select * from RMS_Medicament where ClientId=:clientId and ( Name like :searchWord or BarCode like :searchWord or EnglishName like :searchWord or Remark1 like :searchWord or Remark2 like :searchWord or Remark3 like :searchWord or Remark4 like :searchWord) order by PutInDate desc'
            queryParams = {"searchWord": '%'+_searchWord+'%','clientId':clientId}
        print('获取试剂列表',queryStr + (' limit ' + str((pageParam.curPage-1)*pageParam.pageRows)+','+str(pageParam.pageRows) if pageParam.pageRows != 0 else ''))
        templateList = self.execute(queryStr + (' limit ' + str((pageParam.curPage-1)*pageParam.pageRows)+','+str(pageParam.pageRows) if pageParam.pageRows != 0 else ''), queryParams).fetchall()
        pageParam.totalRecords = self.execute(queryStr.replace('*', 'count(*)'), queryParams).fetchone()[0]
        jsonData = Utils.mysqlTable2Model(templateList)
        return jsonData

    #获取所有危化品列表
    def getAllHazardousList(self, _searchWord, pageParam,clientId=''):
        queryStr=''
        queryParams={}
        if(clientId==''):
            queryStr = 'select * from RMS_Medicament where IsHazardous=1 and (Name like :searchWord or BarCode like :searchWord or EnglishName like :searchWord or Remark1 like :searchWord or Remark2 like :searchWord or Remark3 like :searchWord or Remark4 like :searchWord) order by PutInDate desc'
            queryParams = {"searchWord": '%'+_searchWord+'%'}
        else:
            queryStr = 'select * from RMS_Medicament where ClientId=:clientId and IsHazardous=1 and ( Name like :searchWord or BarCode like :searchWord or EnglishName like :searchWord or Remark1 like :searchWord or Remark2 like :searchWord or Remark3 like :searchWord or Remark4 like :searchWord) order by PutInDate desc'
            queryParams = {"searchWord": '%'+_searchWord+'%','clientId':clientId}
        print('获取试剂列表',queryStr + (' limit ' + str((pageParam.curPage-1)*pageParam.pageRows)+','+str(pageParam.pageRows) if pageParam.pageRows != 0 else ''))
        templateList = self.execute(queryStr + (' limit ' + str((pageParam.curPage-1)*pageParam.pageRows)+','+str(pageParam.pageRows) if pageParam.pageRows != 0 else ''), queryParams).fetchall()
        pageParam.totalRecords = self.execute(queryStr.replace('*', 'count(*)'), queryParams).fetchone()[0]
        jsonData = Utils.mysqlTable2Model(templateList)
        return jsonData


    # 删除试剂
    def delete_drug(self, MedicamentId, medicament_obj):
        # 开启事物
        self.beginTrans()
        medicament_variety_obj = BllMedicamentVariety().findEntity(
            EntityMedicamentVariety.VarietyId == medicament_obj.VarietyId)
        medicament_variety_obj.TotalCount -= 1
        medicament_variety_obj.NormalCount -= 1
        self.session.delete(medicament_obj)
        self.session.merge(medicament_variety_obj)
        self.commitTrans()


    # 库存余量查询,柱状图
    def select_total(self):
        querySte = "SELECT  a.Name, sum(a.Status)  FROM rms_medicament a GROUP BY a.Name"
        templateList = self.execute(querySte).fetchall()
        jsonData = Utils.mysqlTable2Model(templateList)
        # jsonData = dict(jsonData)
        nameDatas = []
        totalDatas = []
        total_names = {}
        for i in jsonData:
            total_names[i["Name"]] = int(i["sum(a.Status)"])
        total_names = sorted(total_names.items(),
                             key=lambda item: item[1], reverse=True)
        for total_name in total_names:
            if len(totalDatas) > 9:
                nameDatas[9] = "其他"
                totalDatas[9] += int(list(total_name)[1])
            else:
                nameDatas.append(list(total_name)[0])
                totalDatas.append(list(total_name)[1])
        return nameDatas, totalDatas

    # 使用次数查询,圆饼图

    def select_usage(self):
        querySte = "SELECT COUNT(a.RecordType),b.Name FROM rms_medicamentrecord a LEFT JOIN rms_medicament b ON a.MedicamentId=b.MedicamentId WHERE(a.RecordType = 2) GROUP BY b.Name"
        templateList = self.execute(querySte).fetchall()
        jsonData = Utils.mysqlTable2Model(templateList)
        total_names = []
        sortData = []
        for i in jsonData:
            total_names.append(
                {"value": int(i["COUNT(a.RecordType)"]), "name": str(i["Name"])})
        total_names = sorted(total_names, key=lambda r: r['value'])
        for i in total_names:
            if (len(sortData) > 9):
                sortData[9]["name"] = "其他"
                sortData[9]["value"] += int(i["value"])
            else:
                sortData.append(
                    {"value": int(i["value"]), "name": str(i["name"])})

        return sortData

    # 危险品信息模糊查询
    def select_danger(self, name):
        querySte = "SELECT a.ename, a.cname, a.chucunfangfa, a.yongtu, a.weight, a.xingzhiyuwendingxing, a.dangerpic,a.cas,a.formula,a.wuxing,a.dulixue, a.shengtaixue, a.othername, a.safestr FROM rms_msds a WHERE a.cname LIKE '%{}%' ORDER BY (CASE WHEN a.cname='{}' THEN 1 WHEN a.cname like '{}%' THEN 2 WHEN a.cname like '%{}%' THEN 3 WHEN a.cname like '%{}' THEN 4 ELSE 5 END) limit 0,19".format(
            name, name, name, name, name)
        templateList = self.execute(querySte).fetchall()
        jsonData = Utils.mysqlTable2Model(templateList)
        dangerData = []
        for i in jsonData:
            dangerData.append({"ename": i["ename"], "cname": i["cname"],"cas":i["cas"],"formula":i["formula"],"wuxing":i["wuxing"],"dulixue":i["dulixue"],"chucunfangfa": i["chucunfangfa"], "yongtu": i["yongtu"], "weight": i["weight"],
                              "xingzhiyuwendingxing": i["xingzhiyuwendingxing"], "dangerpic": i["dangerpic"], "shengtaixue": i["shengtaixue"], "othername": i["othername"], "safestr": i["safestr"]})
        return dangerData

    def select_template(self, search_word):
        from Lib.searchDrug import GetDrugTypeData
        import json
        querySte = """SELECT a.TemplateContent FROM rms_medicamenttemplate a WHERE a.TemplateName not LIKE '%模板%' AND a.TemplateContent LIKE '%"Name":"%{}%"%'""".format(search_word)
        templateList = self.execute(querySte).fetchall()
        jsonDatas = Utils.mysqlTable2Model(templateList)
        if jsonDatas:
            data_list = []
            for jsonData in jsonDatas:
                listDatas = json.loads(jsonData["TemplateContent"])
                for listData in listDatas:
                    print(listData)
                    if search_word in listData["Name"]:
                        dictData = {
                        "id": str(listData["CASNumber"]),
                        "value": str(listData["Name"]),
                        "EnglishName": str(listData["EnglishName"]),
                        "subvalue": str(listData["VarietyId"]),
                        "Purity": str(listData["Purity"]),             
                        "Manufacturer": str(listData["Manufacturer"]),             
                        "Distributor": str(listData["Distributor"]),             
                        "ProductionDate": str(listData["ProductionDate"]),             
                        "ShelfLife": str(listData["ShelfLife"]),             
                        "Price": str(listData["Price"]),             
                        "ExportCount": str(listData["ExportCount"]),             
                        "Speci": str(listData["Speci"]),             
                        "Unit": str(listData["Unit"]),             
                        "SpeciUnit": str(listData["SpeciUnit"]),             
                        "Remain": str(listData["Remain"]),             
                        }
                        data_list.append(dictData)
            data_list = [dict(t) for t in set([tuple(d.items()) for d in data_list])]
            print(data_list)
            print(type(data_list))
            return data_list
        else:
            data_list = GetDrugTypeData.search_data(search_word)
            print(data_list)
            return data_list
            
        # for jsonData in jsonDatas:
        #     print(jsonData)
        #     print(type(jsonData))
        #     for i in jsonData:
        #         print(i)
        #         # print(type(i))

    def get_usecode(self,clientId):
        ClientUseCode =self.session.query(EntityClient.ClientUseCode).filter(EntityClient.ClientId == clientId).first()
        return ClientUseCode

    #获取层灯
    def get_lig(self,null_place,ClientUseCode):
        re_list =[]
        temp_list =[int(i) for i in null_place]
        if ClientUseCode == "HC9":
            re =any([0 < i < 13 for i in temp_list])
            if re:
                re_list.append("49")
            re1 =any([12 < i < 25 for i in temp_list])
            if re1:
                re_list.append("50")
            re2 =any([24 < i < 37 for i in temp_list])
            if re2:
                re_list.append("51")
            re3 =any([36 < i < 49 for i in temp_list])
            if re3:
                re_list.append("52")
        else:
            re =any([0 < i < 31 for i in temp_list])
            if re:
                re_list.append("181")
            re1 =any([30 < i < 61 for i in temp_list])
            if re1:
                re_list.append("182")
            re2 =any([60 < i < 91 for i in temp_list])
            if re2:
                re_list.append("183")
            re3 =any([90 < i < 121 for i in temp_list])
            if re3:
                re_list.append("184")
            re4 =any([120 < i < 151 for i in temp_list])
            if re4:
                re_list.append("185")   
        return re_list        


    # 获取推荐货道
    def get_boxlist(self, clientId, type, num=0):
        session = Repository.DBSession()
        wait_num = 0
        if type == 'up':
            wait_num = self.findCount(EntityMedicament.ClientId == clientId,
                                      EntityMedicament.Status == DrugStatus.Normal, EntityMedicament.Place == '')
            num = num + wait_num
        query = session.query(EntityMedicament.Place).filter(EntityMedicament.ClientId == clientId,
                                                             EntityMedicament.Place != '').all()
        print(query)
        query = [int(i[0]) for i in query]
        print("已用货道",query)
        ClientUseCode =session.query(EntityClient.ClientUseCode).filter(EntityClient.ClientId == clientId).first()
        if ClientUseCode == 'HC9':
            last = 49
        else:
            last =151
        #根据型号计算位置
        null_place = ['%s' % i for i in range(1, last) if i not in query]
        if num <= len(null_place):
            re_list = self.get_lig(null_place[wait_num:num],ClientUseCode)
            return null_place[wait_num:num],re_list
        else:
            return False