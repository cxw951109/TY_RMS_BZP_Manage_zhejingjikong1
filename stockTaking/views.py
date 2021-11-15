import json

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse

from Business.BllMedicamentVariety import BllMedicamentVariety
from Lib.Utils import Utils


@require_http_methods(['GET'])
def index(request):
    if request.method == 'GET':
        # 查询数据库中不同品种的类名
        SQL = """
         SELECT * FROM `RMS_MedicamentVariety`;
        """
        variety_obj_list = BllMedicamentVariety().execute(SQL).fetchall()
        return render(request, 'stockTaking/index.html', locals())


@require_http_methods(['GET'])
def index_json(request):
    if request.method == 'GET':
        try:
            clientId = request.GET.get("clientId", '')
            SQL = """
            select  a.* from rms_medicamentvariety as a right join (select Name,VarietyId from rms_medicament
            """

            if clientId:
                SQL += " where ClientId='" + clientId + "'"
            SQL += " group by VarietyId) as b on a.VarietyId = b.VarietyId where a.VarietyId is not null"
            # print(SQL)
            variety_obj_list = BllMedicamentVariety().execute(SQL).fetchall()
            d, a = {}, []
            for rowproxy in variety_obj_list:
                for column, value in rowproxy.items():
                    d = {**d, **{column: value}}
                a.append(json.loads(Utils.resultAlchemyData(d)))
            return JsonResponse(Utils.resultData(1, "获取成功", a))
        except Exception as e:
            print(e)
            print(e.__traceback__.tb_lineno)
            return JsonResponse(Utils.resultData(0, "数据异常"))


# 校验库存视图处理函数
@require_http_methods(['POST'])
@csrf_exempt
def checkStock(request):
    if request.method == 'POST':
        # 获取前段传来的Json数据
        clientId = request.POST.get('clientId')
        input_values_list = request.POST.get('input_values_list')
        # 读取数据库的种类数据
        SQL = """
        select  a.VarietyId, sum(case when b.`Status` = 1 then 1 else 0 end) as TotalCount, b.Name, b.Purity 
        from rms_medicamentvariety as a LEFT JOIN rms_medicament as b on a.VarietyId = b.VarietyId 
        """
        if (clientId != ''):
            SQL += "  WHERE b.ClientId='" + clientId + "'"
        SQL += '  GROUP BY a.VarietyId'
        Variety_obj_list = BllMedicamentVariety().execute(SQL).fetchall()

        # 把前端获取到的值与后端比较 值不一样的数据放入列表
        different_list = []
        print(Variety_obj_list)
        for Variety_obj in Variety_obj_list:
            for input_value in eval(input_values_list):
                if Variety_obj.VarietyId == input_value['varietyId']:
                    # 如果没有添加库存值, 则库存为0
                    if Variety_obj.TotalCount == None:
                        Variety_obj.TotalCount = 0
                    try:
                        if int(Variety_obj.TotalCount) != int(input_value['value']):
                            difference = int(input_value['value']) - Variety_obj.TotalCount
                            Purity = Variety_obj.Purity
                            if not Purity:
                                Purity = ""
                            different_list.append({'VarietyId': Variety_obj.VarietyId, 'value': Variety_obj.TotalCount,
                                                   'name': Variety_obj.Name, 'Purity': Purity,
                                                   'error_number': int(input_value['value']), 'difference': difference})

                    except Exception as e:
                        print(e)
                        return JsonResponse(Utils.resultData('0', '库存数量请输入整数'))

        return JsonResponse(Utils.resultData('1', '获取成功', data=different_list))
        # return render(request, 'stockTaking/checkStock.html', {'data': different_list})


# 获取库存结果页面
@require_http_methods(['GET'])
def resultPage(request):
    if request.method == 'GET':
        return render(request, 'stockTaking/resultPage.html', locals())


# 获取结果数据
@require_http_methods(['POST'])
@csrf_exempt
def getResultListJson(request):
    if request.method == 'POST':
        stockData = request.POST.get('stockData')
        stockData = eval(stockData)
        return JsonResponse({'data': stockData})


# 查看指定类别的流转记录
@require_http_methods(['GET'])
def stockingRecord(request):
    if request.method == 'GET':
        VarietyId = request.GET.get('VarietyId', '')
        return render(request, 'stockTaking/medTypeRecord.html', locals())
