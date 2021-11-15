import threading
import json
from dateutil.relativedelta import relativedelta
import datetime
import time
import random

from Business.BllPurchaseOrder import BllPurchaseOrder
from DataEntity.EntityPurchaseOrder import EntityPurchaseOrder
from Lib.Utils import *
from Business.BllMedicament import BllMedicament
from Business.BllWarning import BllWarning
from Business.BllMedicament import BllMedicamentVariety
from DataEntity.EntityWarning import EntityWarning
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.elements import BinaryExpression, BooleanClauseList
from sqlalchemy.sql import func
import traceback


class SupervisionWarning:

    def __init__(self):
        # 删除视频事件
        self.deleteVideoDatetime = None

    def supervision_start(self):
        p = threading.Thread(target=self.supervision_start_thread)
        p.start()

    def supervision_start_thread(self):
        while True:
            try:
                print("222222222222222222222222")
                BllWarning().executeNoParam("delete from RMS_Warning where  ObjectType not in('7') ")
                # 查询预警数量和某一类型当前在库数量
                SQL = """
               SELECT  b.VarietyId as VarietyId, b.CustomerId, b.Name, b.EnglishName, b.CASNumber, b.Purity, b.Speci,  b.SpeciUnit, sum(case when a.Status = 1 then 1 else 0 end) as normal_count, b.InventoryWarningValue 
               from RMS_MedicamentVariety  as b LEFT JOIN RMS_Medicament as a on b.VarietyId = a.VarietyId  GROUP by b.VarietyId
                """
                data_obj_list = BllMedicamentVariety().execute(SQL).fetchall()
                PurchaseSumCount = 0
                PurchaseOrderDrugInfo = ""
                PurchaseOrderContent = []
                is_data = True
                for data_obj in data_obj_list:
                    if data_obj.InventoryWarningValue is not None:
                        if data_obj.InventoryWarningValue > data_obj.normal_count:
                            if PurchaseOrderDrugInfo != '':
                                PurchaseOrderDrugInfo += '，'
                            count = data_obj.InventoryWarningValue - data_obj.normal_count
                            PurchaseSumCount += count
                            PurchaseOrderDrugInfo += data_obj.Name + "(" + str(data_obj.Speci) + str(
                                data_obj.SpeciUnit) + "):" + str(count) + "个"
                            PurchaseOrderContent.append(
                                {"PurchaseOrderDetailedId": "", "DrugName": data_obj.Name,
                                 "EnglishName": data_obj.EnglishName,
                                 "CASNumber": data_obj.CASNumber,
                                 "Purity": data_obj.Purity,
                                 "Speci": data_obj.Speci, "SpeciUnit": data_obj.SpeciUnit, "Count": count,
                                 "uuid": str(Utils.UUID())})

                            warning_obj = EntityWarning(WarningId=str(Utils.UUID()), CustomerId=data_obj.CustomerId,
                                                        ObjectType=3, ObjectId=data_obj.VarietyId,
                                                        ObjectName=data_obj.Name,
                                                        WarningContent='药剂种类余量预警：药剂种类 ' + data_obj.Name + ', ' +
                                                                       ' 当前种类药剂余量' + str(
                                                            data_obj.normal_count) + '瓶，' + '小于设定余量' +
                                                                       str(data_obj.InventoryWarningValue) + '瓶；',
                                                        WarningDate=datetime.datetime.now(),
                                                        WarningUserName='系统', IsSolve=0, IsAdd=1)
                            bool_ = BllWarning().insert(warning_obj)
                            if bool_:
                                print('插入成功！')
                if PurchaseSumCount:
                    PurchaseOrder = BllPurchaseOrder().findList(and_(EntityPurchaseOrder.CreateDate.isnot(None),
                                                                     EntityPurchaseOrder.CreateUserId == "1111111111")).order_by(
                        EntityPurchaseOrder.CreateDate).first()
                    if PurchaseOrder:
                        print(22222222222222)
                        CreateDate = datetime.datetime.strptime(PurchaseOrder.CreateDate, '%Y-%m-%d %H:%M:%S')
                        print((datetime.datetime.now() - CreateDate).days < 5)
                        print(PurchaseOrder.PurchaseOrderDrugInfo == PurchaseOrderDrugInfo)
                        print(PurchaseOrder.PurchaseOrderDrugInfo)
                        print(PurchaseOrderDrugInfo)

                        if (
                                datetime.datetime.now() - CreateDate).days < 5 and PurchaseOrder.PurchaseOrderDrugInfo == PurchaseOrderDrugInfo:
                            is_data = False

                    if is_data:
                        entityPurchaseOrder = EntityPurchaseOrder(PurchaseOrderId=str(Utils.UUID()),
                                                                  PurchaseOrderCode='10' + str(Utils.createOrderCode()),
                                                                  ApproveInfoId='', IsCompletePurchase=0,
                                                                  PurchaseOrderContent=Utils.resultAlchemyData(
                                                                      PurchaseOrderContent),
                                                                  Description="当前药剂种类数量低于预警量，系统自动生成采购单",
                                                                  PurchaseOrderStatus=1,
                                                                  CreateDate=datetime.datetime.now().strftime(
                                                                      '%Y-%m-%d %H:%M:%S'),
                                                                  CreateUserId="1111111111",
                                                                  CreateUserName='系统',
                                                                  PurchaseOrderTotalCount=PurchaseSumCount,
                                                                  PurchaseOrderDrugInfo=PurchaseOrderDrugInfo)
                        bool_ = BllPurchaseOrder().insert(entityPurchaseOrder)
                        if bool_:
                            print('生成采购单成功')
                time.sleep(1)

                # SQL查询过期预警数量
                SQL = """
                select  * from rms_medicament a where a.ExpirationDate < now();
                """
                expire_obj_list = BllWarning().execute(SQL).fetchall()
                if expire_obj_list is not None:
                    for expire_obj in expire_obj_list:
                        if expire_obj.Status != 3:
                            warning_obj = EntityWarning(WarningId=str(Utils.UUID()), CustomerId=expire_obj.CustomerId,
                                                        ObjectType=2, ObjectId=expire_obj.MedicamentId,
                                                        ObjectName=expire_obj.Name,
                                                        WarningContent='药剂过期预警：过期药剂 ' + expire_obj.Name + '(' + expire_obj.BarCode + '), ' +
                                                                       ' 当前时间:' + str(
                                                            datetime.datetime.now().strftime(
                                                                '%Y-%m-%d %H:%M:%S')) + '；超出设定过期时间' +
                                                                       (expire_obj.ExpirationDate or '') + '；位置:' + str(
                                                            expire_obj.ClientCode or '') + '号柜' + str(
                                                            expire_obj.Place or ''),
                                                        WarningDate=datetime.datetime.now(),
                                                        WarningUserName='系统', IsSolve=0, IsAdd=1)
                            bool_ = BllWarning().insert(warning_obj)
                            if bool_:
                                print('插入成功！')
                time.sleep(1)

                # SQL查询保质期预警数量
                SQL = """
                select  * from rms_medicament a where a.ExpirationDate < DATE_ADD(now(), INTERVAL a.ShelfLifeWarningValue DAY);
                """
                expireIdList = [x.MedicamentId for x in expire_obj_list]
                shelflife_obj_list = BllWarning().execute(SQL).fetchall()
                if shelflife_obj_list is not None:
                    for expire_obj in shelflife_obj_list:
                        if (expire_obj.Status != 3 and expire_obj.MedicamentId not in expireIdList):
                            warning_obj = EntityWarning(WarningId=str(Utils.UUID()), CustomerId=expire_obj.CustomerId,
                                                        ObjectType=1, ObjectId=expire_obj.MedicamentId,
                                                        ObjectName=expire_obj.Name,
                                                        WarningContent='药剂保质期预警：药剂 ' + expire_obj.Name + '(' + expire_obj.BarCode + ')' + '超过保质期预警线, ' +
                                                                       ' 当前时间:' + str(
                                                            datetime.datetime.now().strftime(
                                                                '%Y-%m-%d %H:%M:%S')) + '；设定警戒线：' +
                                                                       str(expire_obj.ShelfLifeWarningValue) + '天；位置:' + expire_obj.ClientCode + '号柜' + (
                                                                           expire_obj.Place if expire_obj.Place else ''),
                                                        WarningDate=datetime.datetime.now(),
                                                        WarningUserName='系统', IsSolve=0, IsAdd=1)
                            bool_ = BllWarning().insert(warning_obj)
                            if bool_:
                                print('插入成功！')
                time.sleep(1)

                # SQL查询领用超期预警数量
                todayDate = datetime.datetime.now().strftime("%Y-%m-%d")
                SQL = """
                SELECT DATEDIFF('""" + todayDate + """',STR_TO_DATE(a.ByUserDate,'%Y-%m-%d')) as userDays,b.UseDaysWarningValue,a.ByUserName,a.`Name`,a.BarCode,a.MedicamentId,a.CustomerId  FROM rms_medicament a LEFT JOIN rms_medicamentvariety b ON a.VarietyId=b.VarietyId   WHERE DATEDIFF('""" + todayDate + """',STR_TO_DATE(a.ByUserDate,'%Y-%m-%d'))>b.UseDaysWarningValue AND a.`Status`=2;
                """
                shelflife_obj_list = BllWarning().execute(SQL).fetchall()

                if shelflife_obj_list is not None:
                    for expire_obj in shelflife_obj_list:
                        warning_obj = EntityWarning(WarningId=str(Utils.UUID()), CustomerId=expire_obj.CustomerId,
                                                    ObjectType=6, ObjectId=expire_obj.MedicamentId,
                                                    ObjectName=expire_obj.Name,
                                                    WarningContent='出库超期预警：用户 ' + expire_obj.ByUserName + ' 已领用 ' + expire_obj.Name + '(' + expire_obj.BarCode + ')' + str(
                                                        expire_obj.userDays) + '天，超过预警线, ' + str(
                                                        expire_obj.UseDaysWarningValue) + '天',
                                                    WarningDate=datetime.datetime.now(),
                                                    WarningUserName='系统', IsSolve=0, IsAdd=1)
                        bool_ = BllWarning().insert(warning_obj)
                        if bool_:
                            print('插入成功！')
                time.sleep(1)

                # SQL查询药柜滤芯保质期预警
                SQL = """
                SELECT * FROM `rms_client`;
        
                """
                filter_obj_list = BllWarning().execute(SQL).fetchall()
                if filter_obj_list is not None:
                    for filter_obj in filter_obj_list:
                        # if filter_obj.FilterProductionDate is not None:
                        if filter_obj.FilterProductionDate and filter_obj.FilterShelfLife:
                            # 滤芯过期提前预警时间   生产日期 + 保质期 - 提前预警天数
                            filter_expire_date = filter_obj.FilterProductionDate + datetime.timedelta(days=(
                                    filter_obj.FilterShelfLife - filter_obj.FilterShelfLifeWarningValue))
                            if filter_expire_date <= datetime.datetime.now():
                                BllWarning_obj = BllWarning().findList(
                                    EntityWarning.ObjectId == filter_obj.ClientId).all()
                                if not BllWarning_obj:

                                    warning_obj = EntityWarning(WarningId=str(Utils.UUID()),
                                                                CustomerId=filter_obj.CustomerId,
                                                                ObjectType=5, ObjectId=filter_obj.ClientId,
                                                                ObjectName=filter_obj.ClientName,
                                                                WarningContent=filter_obj.ClientName + '药柜滤芯保质期预警：药柜滤芯提前预警时间' + str(
                                                                    filter_obj.FilterShelfLifeWarningValue) + '天，生产日期' +
                                                                               filter_obj.FilterProductionDate.strftime(
                                                                                   '%Y-%m-%d %H:%M:%S') + '，当前时间:' +
                                                                               str(datetime.datetime.now().strftime(
                                                                                   '%Y-%m-%d %H:%M:%S')) + ',保质期:' + str(
                                                                    filter_obj.FilterShelfLife) + '天；已达到提前预警时间；',
                                                                WarningDate=datetime.datetime.now(),
                                                                WarningUserName='系统', IsSolve=0, IsAdd=1)
                                    bool_ = BllWarning().insert(warning_obj)
                                    if bool_:
                                        print('插入成功！')

                time.sleep(1)

            except Exception as e:
                print(str(e))
                # logUtil().debug('预警监测：'+traceback.format_exc())
                logger.debug('预警监测：' + traceback.format_exc())
            time.sleep(3600)
