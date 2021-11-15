from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from Business.BllAcceptanceOrder import BllAcceptanceOrder
from Business.BllClient import *
from Business.BllClientUser import *
from Business.BllPurchaseOrder import BllPurchaseOrder
from Business.BllUser import *
from Business.BllMedicament import *
from Business.BllMedicamentRecord import *
from DataEntity.EntityAcceptanceOrder import EntityAcceptanceOrder

from DataEntity.EntityMedicamentRecord import *
from DataEntity.EntityPurchaseOrder import EntityPurchaseOrder
from Lib.Utils import *
from Lib.Model import *
from django.shortcuts import HttpResponse
import json
# 获取药剂使用次数
@require_http_methods(["GET"])
def usage_record(request):
    jsonData = BllMedicament().select_usage()
    return HttpResponse(json.dumps(jsonData))

# 获取库存余量
@require_http_methods(['GET'])
def form_total(request):
    jsonData = BllMedicament().select_total()
    return HttpResponse(json.dumps(jsonData))

# 获取试剂列表Json数据
@require_http_methods(['GET'])
@csrf_exempt
def getDrugList(request):
    if request.method == 'GET':
        name = request.GET.get("searchValue", '')
        curPage = int(request.GET.get("curPage", 1))
        pageSize = int(request.GET.get("pageSize", 10))
        drug_list = BllMedicament().getAllDrugList(name, PageParam(curPage, pageSize))
        return JsonResponse({'data': json.loads(Utils.resultAlchemyData(drug_list)), 'message': '成功', 'status': 0})


# 获取用户列表Json数据
@require_http_methods(['GET'])
@csrf_exempt
def getUserList(request):
    if request.method == 'GET':
        searchValue = request.GET.get('searchValue', '')
        curPage = int(request.GET.get("curPage", 1))
        pageSize = int(request.GET.get("pageSize", 10))
        queryOrm = BllUser().findList()
        data = BllUser().queryPage(queryOrm, PageParam(curPage, pageSize))
        return JsonResponse({'data': json.loads(Utils.resultAlchemyData(data)), 'message': '成功', 'status': 0})


# 获取用户流转记录Json数据
@require_http_methods(['GET'])
@csrf_exempt
def getDrugRecordList(request):
    if request.method == 'GET':
        searchValue = request.GET.get('userRealName', '')
        curPage = int(request.GET.get("curPage", 1))
        pageSize = int(request.GET.get("pageSize", 10))
        print(searchValue)
        queryOrm = None
        if not searchValue:
            queryOrm = BllMedicamentRecord().findList()
        else:
            queryOrm = BllMedicamentRecord().findList(EntityMedicamentRecord.CreateUserName == searchValue)
        data = BllMedicamentRecord().queryPage(queryOrm, PageParam(curPage, pageSize))
        return JsonResponse({'data': json.loads(Utils.resultAlchemyData(data)), 'message': '成功', 'status': 0})


# 申购提醒
@require_http_methods(['GET'])
@csrf_exempt
def getWantPurchaseList(request):
    if request.method == 'GET':
        # dtj = BllPurchaseOrder().findList(EntityPurchaseOrder.PurchaseOrderStatus == 1).all()
        # name_list = []
        # data_list = []
        # if dtj:
        #     for i in dtj:
        #         content = json.loads(i.PurchaseOrderContent)
        #         for data in content:
        #             name_list.append(
        #                 {'name': data['DrugName'], 'Speci': data['Speci'], 'SpeciUnit': data['SpeciUnit']})
        # for i in name_list:
        #     print(i)
        #     data_obj = BllMedicamentVariety().findList(
        #         and_(EntityMedicamentVariety.Name == i['name'], EntityMedicamentVariety.Speci == float(i['Speci']),
        #              EntityMedicamentVariety.SpeciUnit == i['SpeciUnit'])).first()
        #     count = 0
        #     WarningValue = 0
        #     if data_obj:
        #         WarningValue = data_obj.InventoryWarningValue
        #         drug_list = BllMedicament().findList(and_(EntityMedicament.VarietyId == data_obj.VarietyId,
        #                                                   EntityMedicament.Name == data_obj.Name)).all()
        #         for drug in drug_list:
        #             if drug.Status == 1:
        #                 count += 1
        #     try:
        #         Speci = '%.2f' % float(i['Speci'])
        #     except:
        #         Speci = ""
        #     name = i['name'] + '(' + str(Speci) + i['SpeciUnit'] + ')'
        #     data = {'name': name, 'warningValue': WarningValue, 'stockCount': count, 'status': 0}
        #     if data not in data_list:
        #         data_list.append(data)
        dtj = BllPurchaseOrder().findList(
            or_(EntityPurchaseOrder.PurchaseOrderStatus == 1, EntityPurchaseOrder.PurchaseOrderStatus == 2)).all()
        name_list = []
        data_list = []
        if dtj:
            for i in dtj:
                content = json.loads(i.PurchaseOrderContent)
                for data in content:
                    name_list.append(
                        {'name': data['DrugName'], 'Speci': data['Speci'], 'SpeciUnit': data['SpeciUnit'],
                         'status': i.PurchaseOrderStatus})
        for i in name_list:
            print(i)
            data_obj = BllMedicamentVariety().findList(
                and_(EntityMedicamentVariety.Name == i['name'], EntityMedicamentVariety.Speci == float(i['Speci']),
                     EntityMedicamentVariety.SpeciUnit == i['SpeciUnit'])).first()
            count = 0
            WarningValue = 0
            if data_obj:
                WarningValue = data_obj.InventoryWarningValue
                drug_list = BllMedicament().findList(and_(EntityMedicament.VarietyId == data_obj.VarietyId,
                                                          EntityMedicament.Name == data_obj.Name)).all()
                for drug in drug_list:
                    if drug.Status == 1:
                        count += 1
            try:
                Speci = '%.2f' % float(i['Speci'])
                name = i['name'] + '(' + str(Speci) + i['SpeciUnit'] + ')'
            except:
                Speci = ""
                name = i['name']
            if i['status'] == 1:  # 未提交申请
                status = 0  # 未处理
            else:
                status = 1  # 已申购
            data = {'name': name, 'warningValue': WarningValue, 'stockCount': count, 'status': status}
            if data not in data_list:
                data_list.append(data)

        return JsonResponse({'data': data_list, 'message': '成功', 'status': 0})


# 待入库提醒  已验收的采购单
@require_http_methods(['GET'])
@csrf_exempt
def getAcceptance(request):
    if request.method == 'GET':
        data = BllAcceptanceOrder().findList(EntityAcceptanceOrder.AcceptanceOrderStatus == 2).order_by(
            desc(EntityAcceptanceOrder.CreateDate)).all()
        return JsonResponse(
            {'data': json.loads(Utils.resultAlchemyData(data)), 'code': 0, 'msg': '', })


# 统计数据  今日入库  今日领用  今日归还  采购到货
@require_http_methods(['GET'])
@csrf_exempt
def getStatisticalData(request):
    if request.method == 'GET':
        # 今日入库数量
        SQL = """
               SELECT sum(CASE WHEN RecordType=1 then 1 else 0 end) as 'putIn',  
                sum(CASE WHEN RecordType=2 then 1 else 0 end) as 'useCount',
                sum(CASE WHEN RecordType=3 then 1 else 0 end) as 'returnCount'
                FROM `RMS_MedicamentRecord` as a RIGHT JOIN RMS_Medicament as b on a.MedicamentId = b.MedicamentId
                WHERE DATE_FORMAT(CreateDate,'%Y-%m-%d')= DATE_FORMAT(NOW(),'%Y-%m-%d');
                           """
        obj = BllMedicament().execute(SQL).fetchone()
        # 今日入库
        putInCount = obj['putIn']
        if not putInCount:
            putInCount = 0
        # 今日领用
        useCount = obj['useCount']
        if not useCount:
            useCount = 0
        # 今日归还
        returnCount = obj['returnCount']
        if not returnCount:
            returnCount = 0

        # 采购到货
        sql_purchase = """
               SELECT sum(AcceptanceOrderTotalCount) as 'purchaseCount'
                FROM RMS_AcceptanceOrder WHERE AcceptanceOrderStatus=2;
                           """
        purchase = BllAcceptanceOrder().execute(sql_purchase).fetchone()
        purchaseCount = purchase['purchaseCount']
        if not purchaseCount:
            purchaseCount = 0
        return JsonResponse({"putInCount": putInCount, "useCount": useCount, "returnCount": returnCount,
                             "purchaseCount": purchaseCount})


# 总库存量
@require_http_methods(['GET'])
@csrf_exempt
def getAllStockCount(request):
    if request.method == 'GET':
        SQL = """
               SELECT sum(CASE WHEN IsHazardous=1 then 1 else 0 end) as 'hazardousCount', 
               count(*) as 'allCount'
                FROM RMS_Medicament WHERE Status=1;
                           """
        obj = BllMedicament().execute(SQL).fetchone()
        # 总库存量
        all_stock_count = obj['allCount']
        # 危化品库存量
        hazardous_count = obj['hazardousCount']
        if not hazardous_count:
            hazardous_count = 0
        if all_stock_count:
            # 危化品占比
            hazardous_proportion = hazardous_count / all_stock_count
        else:
            all_stock_count = 0
            hazardous_proportion = 0
        return JsonResponse(
            {"allCount": all_stock_count, "hazardousCount": hazardous_count,
             "hazardousProportion": hazardous_proportion})


# 常用试剂
@require_http_methods(['GET'])
@csrf_exempt
def getOftenUse(request):
    if request.method == 'GET':
        querySte = "SELECT count(a.RecordType) as 'count',b.Name FROM rms_medicamentrecord a LEFT JOIN rms_medicament b ON a.MedicamentId=b.MedicamentId WHERE(a.RecordType = 2) GROUP BY b.Name"
        templateList = BllMedicament().execute(querySte).fetchall()
        jsonData = Utils.mysqlTable2Model(templateList)
        total_names = []
        sortData = []
        for i in jsonData:
            total_names.append(
                {"value": int(i["count"]), "name": str(i["Name"])})
        total_names = sorted(total_names, key=lambda r: r['value'])
        for i in total_names:
            if (len(sortData) > 10):
                sortData[10]["name"] = "其他"
                sortData[10]["value"] += int(i["value"])
            else:
                sortData.append(
                    {"value": int(i["value"]), "name": str(i["name"])})
        print(sortData)
        return JsonResponse({'data': sortData})
        # return HttpResponse(json.dumps(sortData))


# api主页
@require_http_methods(['GET'])
@csrf_exempt
def index(request):
    if request.method == 'GET':
        return render(request, 'index/index.html', locals())


# 获取预警Json数据
@require_http_methods(['GET'])
@csrf_exempt
def getWarningListJson(request):
    if request.method == 'GET':
        warning_list = BllWarning().findList().order_by(desc(EntityWarning.IsSolve), desc(EntityWarning.WarningDate),
                                                        desc(EntityWarning.SolveDate)).all()
        return JsonResponse({'data': json.loads(Utils.resultAlchemyData(warning_list))})


# 获取温度静态展示数据
@require_http_methods(['GET'])
def getTemperatureEchartsJson(request):
    if request.method == 'GET':
        # 前段echarts展示series 字段的所有数据
        series_list = []

        # 获取最近24小时的值
        data_hour_list = []
        curtime_hour = datetime.datetime.now().strftime('%H')
        y = int(curtime_hour)
        for x in range(24):
            data_hour_list.append(str(y) + ':00')
            if y == 0:
                y = 23
                continue
            y -= 1
        data_hour_list = list(reversed(data_hour_list))
        # 获取所有客户端
        client_list = BllClient().getAllClientList()
        # 客户端名字列表
        client_name_list = []

        for client_obj in client_list:
            client_name_list.append(client_obj.ClientName)
            # 定义两个字典, 键相同, 一个字典保存次数, 一个字典保存温度总数
            temperature_dict = {}
            temperature_dict_count = {}
            # 获取当前时间
            curtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # 当前时间减去24小时
            start_time = (parser.parse(datetime.datetime.now().strftime('%Y-%m-%d %H')) + relativedelta.relativedelta(
                hours=-23)).strftime('%Y-%m-%d %H:%M:%S')

            # 获取温湿度的所有对象
            humiture_obj_list = BllHumitureRecord().findList(and_(EntityHumitureRecord.ClientId == client_obj.ClientId,
                                                                  EntityHumitureRecord.RecordDate.between(start_time,
                                                                                                          curtime))).all()

            # 遍历求出每一个对象
            for humiture_obj in humiture_obj_list:

                # 获取每一个对象的RecordDate的时间值
                hum_hour = humiture_obj.RecordDate.strftime('%H')
                # 判断当前hum_hour是否在定义的字典中, 如果没有,hum_hour作为键
                # 1作为当前时间共有几个数值, humiture_obj.Temperature的温度作为值
                if hum_hour not in temperature_dict:
                    temperature_dict_count[hum_hour] = 1
                    temperature_dict[hum_hour] = humiture_obj.Temperature
                # 如果存在, 数值+1, 温度值叠加
                else:
                    temperature_dict[hum_hour] += humiture_obj.Temperature
                    temperature_dict_count[hum_hour] += 1

            # 求温度的平均值
            for each_count in temperature_dict_count.keys():
                if each_count in temperature_dict:
                    temperature_dict[each_count] = round(temperature_dict[each_count]
                                                         / temperature_dict_count[each_count], 2)
            # 求出当前时间近24小时的温度值和小时值
            data_temperate = []
            for data_hour in data_hour_list:
                if len(data_hour) == 4:
                    data_hour = '0' + str(data_hour)

                if str(data_hour[:-3]) in temperature_dict:
                    data_temperate.append(temperature_dict[data_hour[:-3]])
                else:
                    data_temperate.append('0.0')

            series_list.append({"name": client_obj.ClientName, "type": "line",
                                "data": data_temperate,
                                "markPoint":
                                    {"data": [{"type": "max", "name": "最大值"}, {"type": "min", "name": "最小值"}]},
                                "markLine": {"data": [{"type": "average", "name": "平均值"}]}})

        data = {"title": {"text": "",
                          "textStyle": {
                              "fontWeight": 'normal',
                              "color": '#b9babe'
                          }},
                "tooltip": {"trigger": "axis"},
                # 下载为图片
                'toolbox': {
                    'show': 'true',
                    'feature': {
                        'saveAsImage': {
                            'show': 'true',
                            'type': 'jpeg',
                            'name': '温度监控折线图',
                            'excludeComponents': "['toolbox']",
                            'pixelRatio': '2',
                            'icon': 'image:///static/img/download.png',
                        },
                        'magicType': {'show': 'true', 'type': ['line', 'bar']},
                        'restore': {
                            'show': 'true',
                        }
                    }

                },
                "legend": {"data": client_name_list},
                "grid": {"x": 55, "x2": 55, "y2": 24},
                "calculable": True,
                "xAxis": [{"type": "category",
                           "boundaryGap": False,
                           "data": data_hour_list,
                           "axisLine": {
                               "lineStyle": {
                                   "color": '#b9babe',
                               }
                           },
                           "axisLabel": {
                               "textStyle": {
                                   "color": '#b9babe',
                                   "fontSize": '16'
                               },
                           }}
                          ],
                "yAxis": [{"type": "value", "axisLine": {
                    "lineStyle": {
                        "color": '#b9babe',
                    }
                }, "axisLabel": {"formatter": "{value} °C",
                                 "textStyle": {
                                     "color": '#b9babe',
                                     "fontSize": '16'
                                 },
                                 }}],
                "series": series_list}

        return JsonResponse(Utils.resultData('1', '数据获取成功', data=data))
