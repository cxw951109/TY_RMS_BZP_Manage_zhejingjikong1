from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import json
import base64
import copy
import pdfkit
from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import urlquote
from TY_RMS_Multiple_Manage.settings import *

from Business.BllApproveInfo import *
from Business.BllApproveInfoProcess import *
from Business.BllPurchaseOrder import *
from Business.BllPurchaseOrderDetailed import *
from Business.BllAcceptanceOrder import *
from Business.BllAcceptanceOrderDetailed import *
from Business.BllMedicamentTemplate import *
from Business.BllMedicament import *
from Business.BllPeriodCheck import *
from Business.BllPeriodCheckDetailed import *
from Business.BllClient import *
from Business.BllKey import *
from Business.BllKeyRecord import *
from DataEntity.EntityPurchaseOrder import *
from DataEntity.EntityPurchaseOrderDetailed import *
from DataEntity.EntityAcceptanceOrder import *
from DataEntity.EntityAcceptanceOrderDetailed import *
from DataEntity.EntityMedicamentTemplate import *
from DataEntity.EntityPeriodCheck import *
from DataEntity.EntityPeriodCheckDetailed import *
from DataEntity.EntityMedicament import *
from DataEntity.EntityKey import *
from DataEntity.EntityKeyRecord import *
from Lib.searchDrug import GetDrugTypeData
from Lib.Utils import *
from Lib.create_barcode import CreateBarcode
from Lib.reportExcel import *
from Lib.Model import *


@require_http_methods(['GET'])
def PutInTemplate(request):
    if request.method == 'GET':
        return render(request, 'Hazardous/PutInTemplate.html', locals())


@require_http_methods(['GET'])
def UseView(request):
    if request.method == 'GET':
        return render(request, 'Hazardous/HazardousUse.html', locals())


@require_http_methods(['GET'])
def ReturnView(request):
    if request.method == 'GET':
        return render(request, 'Hazardous/HazardousReturn.html', locals())


@require_http_methods(['GET'])
def PutInTemplate(request):
    if request.method == 'GET':
        return render(request, 'Hazardous/PutInTemplate.html', locals())


# 获取U盘模板列表
@require_http_methods(['GET'])
def getUpanTemplateFile(request):
    fileList = []
    file_path = Utils.getUDiskPath()
    if (file_path != ''):
        for i in [os.sep.join([file_path, v]) for v in os.listdir(file_path)]:
            # if (os.path.basename(i).startswith('tem_') and (os.path.isfile(i)) and (
            #         os.path.basename(i).endswith('.xlsx'))):
            if os.path.basename(i) == 'reagentTemplate.xlsx':
                fileList.append(os.path.basename(i))
    print(fileList)
    return JsonResponse({'data': fileList})


# 获得危化品入库模板的JSON数据
@require_http_methods(['GET'])
def getHazardousTemplateListJson(request):
    if request.method == 'GET':
        TemplateName = request.GET.get('TemplateName', '')
        CreateUserName = request.GET.get('CreateUserName', '')
        TemplateContent = request.GET.get('TemplateContent', '')
        ClientId = request.GET.get('ClientId', '')
        curPage = int(request.GET.get('page', '1'))
        pageSize = int(request.GET.get('limit', '10'))
        pageParam = PageParam(curPage, pageSize)
        try:
            data = BllMedicamentTemplate().getAllHazardousTemplateList(pageParam, TemplateName, CreateUserName,
                                                                       TemplateContent,
                                                                       ClientId)
            return JsonResponse({'data': json.loads(Utils.resultAlchemyData(data)), 'code': 0, 'msg': '',
                                 'count': pageParam.totalRecords})
        except Exception as e:
            print(e)
            return JsonResponse({'data': [], 'code': 0, 'msg': '', 'count': 1})


# 新增试剂模板视图处理函数
@require_http_methods(['GET'])
def HazardousTemplateForm(request):
    if request.method == 'GET':
        NewDrugTemplateOrderCode = '40' + Utils.createOrderCode()
        return render(request, 'Hazardous/TemplateForm.html', locals())


# 获取试剂展示处理视图函数, 返回JSON数据
@require_http_methods(['GET'])
def HazardousListJson(request):
    if request.method == 'GET':
        name = request.GET.get("searchValue", '')
        FlowNo_type = int(request.GET.get("FlowNo", 1))
        clientId = request.GET.get("clientId", '')
        status = request.GET.get("status", '')
        isMyUse = request.GET.get("isMyUse", '')
        user = request.session['login_user']
        allSearch = request.GET.get("allSearch", '1')
        drug_list = BllMedicament().getAllHazardousList(name, PageParam(1, 0), clientId)
        if (status != ''):
            drug_list = [x for x in drug_list if x.get("Status") == int(status)]
        if (isMyUse == '1'):
            drug_list = [x for x in drug_list if x.get("ByUserId") == user["UserId"]]
        return JsonResponse({'data': drug_list, 'code': 0, 'msg': '', 'count': len(drug_list)})


# 试剂扫一维条码入库处理视图
@csrf_exempt
def PutInView(request):
    if request.method == 'POST':
        template_index = request.POST.get('template_index')
        userInfo = request.session['login_user']
        customerId = request.POST.get('CustomerId')
        barCode = request.POST.get("barCode")
        clientId = request.POST.get("client_id")
        place = request.POST.get("place")
        clientEntity = BllClient().findEntity(EntityClient.ClientId == clientId)
        # 获取存储的session  template_list 根据前段传来的值判断取第几个模板
        if (int(template_index) >= len(request.session['template_list'])):
            print('sssssssssssssssssssssssssssssssssssssss')
            retrunData = Utils.resultData(1, '该模板已被全部绑定！')
            return JsonResponse(retrunData)
        drugInfo = request.session['template_list'][int(template_index)]
        # try:
        drugEntity = BllMedicament().findEntity(EntityMedicament.BarCode == barCode)
        if (drugEntity is not None):
            retrunData = Utils.resultData(1, '此条码已被绑定！')
        else:
            if drugInfo['Speci'] == '':
                drugInfo['Speci'] = 0
            drugVariety = BllMedicamentVariety().createDrugVariety(customerId, drugInfo.get('Name'),
                                                                   drugInfo.get('EnglishName')
                                                                   , drugInfo.get('CASNumber'), drugInfo.get('Purity'),
                                                                   drugInfo.get('Unit'), drugInfo.get('SpeciUnit'),
                                                                   drugInfo.get('Speci'),
                                                                   BllUser().findEntity(userInfo.get('UserId')))
            drugEntity = EntityMedicament()
            drugId = Utils.UUID()
            drugEntity.MedicamentId = drugId
            drugEntity.VarietyId = drugVariety.VarietyId
            drugEntity.BarCode = barCode
            drugEntity.CustomerId = customerId
            drugEntity.ClientId = clientEntity.ClientId
            drugEntity.ClientCode = clientEntity.ClientCode
            drugEntity.CASNumber = drugInfo.get('CASNumber', '')
            drugEntity.Name = drugInfo.get('Name', '')
            drugEntity.EnglishName = drugInfo.get('EnglishName', '')
            drugEntity.Purity = drugInfo.get('Purity', '')
            drugEntity.Manufacturer = drugInfo.get('Manufacturer', '')
            drugEntity.Distributor = drugInfo.get('Distributor', '')
            productionDate = drugInfo.get('ProductionDate') or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            drugEntity.ProductionDate = productionDate[:10]
            drugEntity.ShelfLife = int(drugInfo.get('ShelfLife') or '6000')
            drugEntity.ExpirationDate = (
                    datetime.datetime.strptime(productionDate[:10], "%Y-%m-%d") + datetime.timedelta(
                days=drugEntity.ShelfLife)).strftime("%Y-%m-%d %H:%M:%S")
            drugEntity.InventoryWarningValue = 10
            drugEntity.ShelfLifeWarningValue = 10
            drugEntity.UseDaysWarningValue = 10
            drugEntity.Unit = drugInfo.get('Unit', '')
            drugEntity.SpeciUnit = drugInfo.get('SpeciUnit', '')
            drugEntity.Speci = float(drugInfo.get('Speci') or '0')
            drugEntity.Price = float(drugInfo.get('Price') or '0')
            drugEntity.Place = place
            drugEntity.Remain = float(drugInfo.get('Remain') or '0')  ###不知道模板中是否有--待确认
            drugEntity.PutInDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            drugEntity.PutInUserId = userInfo.get('UserId', '')
            drugEntity.PutInUserName = userInfo.get('RealName', '')
            drugEntity.Remark1 = drugInfo.get('Remark1', '')
            drugEntity.Remark2 = drugInfo.get('Remark2', '')
            drugEntity.Remark3 = drugInfo.get('Remark3', '')
            drugEntity.Remark4 = drugInfo.get('Remark4', '')
            drugEntity.Remark5 = drugInfo.get('Remark5', '')
            drugEntity.Remark6 = drugInfo.get('Remark6', '')
            drugEntity.Remark7 = drugInfo.get('Remark7', '')
            drugEntity.Remark8 = drugInfo.get('Remark8', '')
            drugEntity.Remark9 = drugInfo.get('Remark9', '')
            drugEntity.Remark10 = drugInfo.get('Remark10', '')
            drugEntity.IsHazardous = 1
            drugEntity.Status = DrugStatus.Normal
            BllMedicament().drugPutIn(drugEntity, clientEntity, BllUser().findEntity(userInfo.get('UserId')))
            # retrunData = Utils.resultData(0,'试剂入库成功！',drugEntity)
            retrunData = Utils.resultData(0, '试剂入库成功！', data=drugId)
        # except Exception as e:
        #     print(e)
        #     retrunData = Utils.resultData(1,str(e))
        return JsonResponse(retrunData)


# 绑定模板入库
@csrf_exempt
def RFID_bind(request):
    try:
        time.sleep(0.5)
        template_index = request.POST.get('template_index')
        CustomerId = request.POST.get('CustomerId')
        if CustomerId == 'None':
            CustomerId = ''
        ClientId = request.POST.get('client_id')
        RFID = request.POST.get('RFID')
        if RFID == "" or RFID is None:
            return JsonResponse({'data': Utils.resultData(1, 'RFID不能为空！')})
        # 获取存储的session  template_list 根据前段传来的值判断取第几个模板
        if (int(template_index) >= len(request.session['template_list'])):
            return JsonResponse({'data': Utils.resultData(1, '该模板已被全部绑定！')})
        drugInfo = request.session['template_list'][int(template_index)]
        # 获取存储的user
        user = request.session['login_user']
        drugEntity = BllMedicament().findEntity(EntityMedicament.BarCode == RFID)
        if (drugEntity is not None):
            return JsonResponse({'data': Utils.resultData(1, '该试剂已被绑定！')})
        else:
            if drugInfo['Speci'] == '':
                drugInfo['Speci'] = 0
            drugVariety = BllMedicamentVariety().createDrugVariety(CustomerId, drugInfo.get('Name')
                                                                   , drugInfo.get('CASNumber'),
                                                                   drugInfo.get('EnglishName'), drugInfo.get('Purity'),
                                                                   drugInfo.get('Unit'), drugInfo.get('SpeciUnit'),
                                                                   drugInfo.get('Speci'),
                                                                   BllUser().findEntity(user.get('UserId')))
            drugEntity = EntityMedicament()
            drugEntity.MedicamentId = str(Utils.UUID())
            drugEntity.VarietyId = drugVariety.VarietyId
            drugEntity.BarCode = RFID
            drugEntity.CustomerId = CustomerId
            drugEntity.ClientId = ClientId
            drugEntity.CASNumber = drugInfo.get('CASNumber')
            drugEntity.Name = drugInfo.get('Name')
            drugEntity.EnglishName = drugInfo.get('EnglishName')
            drugEntity.Purity = drugInfo.get('Purity')
            drugEntity.Manufacturer = drugInfo.get('Manufacturer')
            drugEntity.Distributor = drugInfo.get('Distributor')
            drugEntity.ProductionDate = drugInfo.get('ProductionDate')
            drugEntity.ShelfLife = int(drugInfo.get('ShelfLife'))
            drugEntity.ExpirationDate = (
                    datetime.datetime.strptime(drugInfo.get('ProductionDate'), "%Y-%m-%d") + datetime.timedelta(
                days=drugEntity.ShelfLife)).strftime("%Y-%m-%d %H:%M:%S")
            drugEntity.InventoryWarningValue = 10
            drugEntity.ShelfLifeWarningValue = 10
            drugEntity.UseDaysWarningValue = 10
            drugEntity.Unit = drugInfo.get('Unit')
            drugEntity.SpeciUnit = drugInfo.get('SpeciUnit')
            drugEntity.Speci = drugInfo.get('Speci')
            drugEntity.Price = drugInfo.get('Price')
            drugEntity.Place = drugInfo.get('Place')
            drugEntity.IsSupervise = 0  # 默认非重点监管
            drugEntity.Remain = drugInfo.get('Speci')
            drugEntity.PutInDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            drugEntity.PutInUserId = user.get('UserId')
            drugEntity.PutInUserName = user.get('RealName')
            drugEntity.Status = 5
            drugEntity.IsHazardous = 1

            boolean_ = BllMedicament().drugPutIn(drugEntity, BllClient().findEntity(ClientId),
                                                 BllUser().findEntity(user.get('UserId')))
            # retrunData = Utils.resultData(0,'试剂入库成功！',drugEntity)
            if boolean_:
                return JsonResponse({'data': Utils.resultData(0, '试剂入库成功！')})
            else:
                return JsonResponse({'data': Utils.resultData(1, '数据异常，入库失败！')})

    except Exception as e:
        print(e, 888888888888)
        return JsonResponse({'data': Utils.resultData(1, '数据异常, 入库失败！')})


@require_http_methods(['GET'])
def shelfReturn(request):
    if request.method == 'GET':
        return render(request, 'Hazardous/shelfReturn.html', locals())


# 试剂归还处理视图
@csrf_exempt
def HazardousReturnView(request):
    if request.method == 'GET':
        return render(request, 'Hazardous/shelfReturn.html', locals())
    elif request.method == 'POST':
        data_list = json.loads(request.POST.get("data_list"))
        print("data:", data_list)
        print("data:", type(data_list))
        data = data_list[0]
        Place = request.POST.get("Place")
        retrunData = ''
        userInfo = request.session['login_user']

        print('id:' + data["MedicamentId"])
        try:
            drugEntity = BllMedicament().findEntity(EntityMedicament.MedicamentId == data["MedicamentId"])
            if (drugEntity is None):
                retrunData = Utils.resultData(1, '药剂条码无效！')
            elif (drugEntity.Status != DrugStatus.Out):
                retrunData = Utils.resultData(1, '此药剂未被领用！')
            else:
                customerId = drugEntity.CustomerId
                clientId = drugEntity.ClientId
                if data["IsEmpty"] == 1:
                    drugEntity.Status = DrugStatus.Empty
                else:
                    drugEntity.Status = DrugStatus.Normal
                drugEntity.Remain = data["Remain"]
                if Place:
                    drugEntity.Place = Place
                BllMedicament().drugReturn(drugEntity, BllClient().findEntity(clientId),
                                           BllUser().findEntity(userInfo.get('UserId')))
                retrunData = Utils.resultData(0, '药剂归还成功！', data=Utils.resultAlchemyData(drugEntity))

        except Exception as e:
            retrunData = Utils.resultData(1, str(e))
        return JsonResponse(retrunData)


@require_http_methods(['GET'])
def shelfUse(request):
    if request.method == 'GET':
        return render(request, 'Hazardous/shelfUse.html', locals())


# 试剂领用处理视图
@csrf_exempt
def HazardousUseView(request):
    if request.method == 'GET':
        return render(request, 'Hazardous/shelfUse.html', locals())
    elif request.method == 'POST':
        drugIdList = request.POST.get("drugId", "").split(',')
        retrunData = ''
        userInfo = request.session['login_user']
        try:
            for drugId in drugIdList:
                print('drugId:', drugId)
                drugEntity = BllMedicament().findEntity(EntityMedicament.MedicamentId == drugId)
                print('drugEntity:', drugEntity)
                if (drugEntity.Status != DrugStatus.Normal and drugEntity.Status != DrugStatus.Empty):
                    continue
                elif (drugEntity.Status == DrugStatus.Empty):
                    continue
                else:
                    print('drugEntity1:', drugEntity)
                    customerId = drugEntity.CustomerId
                    clientId = drugEntity.ClientId
                    goodDrug = BllMedicament().getDrugNearExpired(drugEntity.VarietyId, customerId)
                    drugEntity.ByUserDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    drugEntity.ByUserId = userInfo.get('UserId')
                    drugEntity.ByUserName = userInfo.get('RealName')
                    drugEntity.Status = DrugStatus.Out
                    BllMedicament().drugUse(drugEntity, BllClient().findEntity(clientId),
                                            BllUser().findEntity(userInfo.get('UserId')))
            retrunData = Utils.resultData(0, '试剂领用成功！')

        except Exception as e:
            print(e)
            retrunData = Utils.resultData(1, str(e))
        return JsonResponse(retrunData)


# 获取试剂展示页面
@require_http_methods(['GET'])
def KeyManagement(request):
    if request.method == 'GET':
        try:
            user = request.session['login_user']
            roleName = user['RoleName']
        except Exception as e:
            print(e)
            roleName = ''
        try:
            searchValue = request.GET['searchValue']
            return render(request, 'Hazardous/KeyManagement.html', locals())
        except:
            return render(request, 'Hazardous/KeyManagement.html', locals())


# 获取试剂展示处理视图函数, 返回JSON数据
@require_http_methods(['GET'])
def GetKeyListJson(request):
    if request.method == 'GET':
        name = request.GET.get("searchValue", '')
        clientId = request.GET.get("clientId", '')
        status = request.GET.get("status", '')
        # user = request.session['login_user']
        key_list = BllKey().getAllList(name, PageParam(1, 0), clientId)
        if status:
            key_list = [x for x in key_list if x.get("Status") == int(status)]
        return JsonResponse({'data': key_list, 'code': 0, 'msg': '', 'count': len(key_list)})


# 根据试剂ID  get方式查询返回钥匙信息，post修改钥匙信息
@require_http_methods(['GET', 'POST'])
@csrf_exempt
def key_form(request):
    if request.method == 'GET':
        key_id = request.GET.get("key_id", "")
        if key_id:
            key_obj = BllKey().findEntity(key_id)
        return render(request, 'Hazardous/key_form.html', locals())
    elif request.method == 'POST':
        print(request.POST)
        userInfo = request.session['login_user']
        id = request.POST.get("Id", "")
        BarCode = request.POST.get("BarCode", "")
        Name = request.POST.get("Name", "")
        Place = request.POST.get("Place", "")
        Status = int(request.POST["Status"])
        clientId = request.POST.get("clientId", "")
        CorrespondingClientId = request.POST.get("CorrespondingClientId", "")
        CorrespondingClientCode = ""
        ClientCode = ""
        if BarCode == "":
            return JsonResponse(Utils.resultData('0', '条码编号不能为空'))
        if clientId == "":
            return JsonResponse(Utils.resultData('0', '钥匙存放的终端不能为空'))
        clientId_obj = BllClient().findEntity(clientId)
        if not clientId_obj:
            return JsonResponse(Utils.resultData('0', '数据异常'))
        ClientCode = clientId_obj.ClientCode
        if CorrespondingClientId:
            CorrespondingClientId_obj = BllClient().findEntity(CorrespondingClientId)
            if not CorrespondingClientId_obj:
                return JsonResponse(Utils.resultData('0', '数据异常'))
            CorrespondingClientCode = CorrespondingClientId_obj.ClientCode

        if id:
            key_obj = BllKey().findEntity(id)
            obj = BllKey().findEntity(and_(EntityKey.BarCode == BarCode, EntityKey.Id != id))
            if obj:
                return JsonResponse(Utils.resultData('0', '条码编号已存在'))
            str_sm = ""
            if key_obj.BarCode != BarCode:
                str_sm += "更改钥匙编号;"
            if key_obj.Name != Name:
                str_sm += "更改钥匙名称;"
            if key_obj.Status != Status:
                str_sm += "更改钥匙状态;"
            if key_obj.Place != Place or key_obj.ClientId != clientId:
                str_sm += "更改钥匙存放位置;"
            if key_obj.CorrespondingClientId != CorrespondingClientId:
                str_sm += "更改钥匙管理终端;"
            key_obj.Name = Name
            key_obj.BarCode = BarCode
            key_obj.Place = Place
            key_obj.ClientId = clientId
            key_obj.ClientCode = ClientCode
            key_obj.CorrespondingClientId = CorrespondingClientId
            key_obj.CorrespondingClientCode = CorrespondingClientCode
            key_obj.Status = Status
            if str_sm == "":
                BllKey().update(key_obj)
            else:
                BllKey().KeyUpdate(key_obj, clientId_obj, BllUser().findEntity(userInfo.get('UserId')), str_sm)
            return JsonResponse(Utils.resultData('1', '修改成功', ''))
        else:
            CreateDate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            key_obj = BllKey().findEntity(EntityKey.BarCode == BarCode)
            if key_obj is None:
                Id = str(Utils.UUID())
                key = EntityKey(
                    Id=Id, BarCode=BarCode, ClientId=clientId, ClientCode=ClientCode, Name=Name, Place=Place,
                    CorrespondingClientId=CorrespondingClientId, CorrespondingClientCode=CorrespondingClientCode,
                    Status=Status, CreateDate=CreateDate)
                # BllKey().insert(key)
                BllKey().KeyUpdate(key, clientId_obj, BllUser().findEntity(userInfo.get('UserId')), '新增钥匙')
                return JsonResponse(Utils.resultData('1', '保存成功', ''))
            else:
                return JsonResponse(Utils.resultData('0', '该条码编号已存在', ''))


@require_http_methods(['GET'])
def getSelectStatusListJson(request):
    if request.method == 'GET':
        status_list = [{'name': '全部', 'value': ''}, {'name': '在库', 'value': '1'}, {'name': '出库', 'value': '2'},
                       {'name': '未绑定', 'value': '5'}]
        return JsonResponse(status_list, safe=False)


@require_http_methods(['GET', 'POST'])
@csrf_exempt
def key_barCode(request):
    if request.method == 'GET':
        return render(request, 'Hazardous/key_barCode.html', locals())


@require_http_methods(['GET', 'POST'])
@csrf_exempt
def deleteKey(request):
    try:
        if request.method == 'POST':
            deleteIds = request.POST.get("deleteIds", '')
            deleteIds = deleteIds.split(',')
            for KeyId in deleteIds:
                BllKey().delete(EntityKey.Id == KeyId)
                BllKeyRecord().delete(EntityKeyRecord.KeyId == KeyId)
            return JsonResponse(Utils.resultData('1', '删除成功', ''))
    except Exception as e:
        return JsonResponse(Utils.resultData('0', str(e), ''))


# 获取试剂流转记录
@require_http_methods(['GET'])
def KeyRecord(request):
    if request.method == 'GET':
        key_id = request.GET.get('key_id', '')
        return render(request, 'Hazardous/KeyRecord.html', locals())


# 获取试剂记录今日入库 领用 归还Json数据
@require_http_methods(['GET'])
def getKeyRecordListJson(request):
    if request.method == 'GET':
        try:
            key_id = request.GET.get('key_id', '')
            if key_id:
                KeyRecord_obj_list = BllKeyRecord().findList(EntityKeyRecord.KeyId == key_id).order_by(
                    EntityKeyRecord.CreateDate.desc()).all()
                key_list = json.loads(Utils.resultAlchemyData(KeyRecord_obj_list))
            else:
                key_list = []
            # print(key_list)
            return JsonResponse({'data': key_list, 'code': 0, 'msg': '', 'count': len(key_list)})

        except Exception as e:
            logger.info('数据异常' + str(e))
            print(e)
            print(e.__traceback__.tb_lineno)
            return JsonResponse({'data': ''})
