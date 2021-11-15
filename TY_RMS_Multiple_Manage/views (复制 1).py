# 导入系统第三方模块
import datetime
import json

# 导入django自带的功能
from django.views.decorators.http import require_http_methods
from django.shortcuts import HttpResponse, render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, date, timedelta
# 导入自定义的功能
from Lib.Utils import *
from Lib.Model import *
from Business.BllUser import *
from Business.BllMedicament import *
from Business.BllMedicamentTemplate import *
from Business.BllWarning import *
from Business.BllClient import *
from Business.BllHumitureRecord import *
from Business.BllLog import *
from DataEntity.EntityMedicament import *
from DataEntity.EntityClient import *


def get_user_ip(request):
    """
    获取访问用户ip
    :param request:
    :return:
    """
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        return request.META['HTTP_X_FORWARDED_FOR']
    else:
        return request.META['REMOTE_ADDR']


@Utils.log_exception
@require_http_methods(['GET'])
def home(request):
    if request.method == 'GET':
        # 获取预警数量
        visitType = ''
        try:
            user_ = request.session['login_user']
            user_id=user_["UserId"]
            user = BllUser().findEntity(user_id)
            role_id = user.RoleId
            SQL = """
            
            SELECT c.ModuleId, c.ModuleCode, c.SortIndex, c.ModuleName from(SELECT a.ModuleId, b.ModuleCode, 
            b.SortIndex, b.ModuleName FROM `RMS_ModuleRelation` as a LEFT JOIN RMS_Module as b on a.ModuleId = 
            b.ModuleId WHERE ObjectId = :user_id and ObjectType = 2 and a.ModuleType=2 UNION
            SELECT a.ModuleId, b.ModuleCode, b.SortIndex, b.ModuleName FROM `RMS_ModuleRelation` as a
                LEFT JOIN RMS_Module as b on a.ModuleId = b.ModuleId  WHERE ObjectId = :role_id and ObjectType = 1 and a.ModuleType=2) 
                as c ORDER BY c.SortIndex asc;
            """
            module_relation_obj_list = BllUser().execute(SQL, {'user_id': user_id, 'role_id': role_id}).fetchall()
            module_relation_obj_list = Utils.mysqlTable2Model(module_relation_obj_list)

            # 用列表推导式生成一个ModuleCode列表
            object_id_list = [x['ModuleCode'] for x in module_relation_obj_list]

            print(object_id_list)
            #SQL = 'SELECT count(*) as number_ FROM `RMS_Warning` WHERE IsSolve = 0 and now() > WarningDate;'
            SQL = 'SELECT count(*) as number_ FROM `RMS_Warning` WHERE IsSolve = 0'
            warning_obj = BllWarning().execute(SQL).fetchone()
            warning_nb = warning_obj.number_
            try:
                user = request.session['login_user']
                roleName = user['RoleName']
                visitType = request.GET.get('visitType')
                request.session['visitType'] = visitType
                # if(((visitType=='1') or (visitType=='2'))):
                #     request.session['visitType']='1'
                # else:
                #     request.session['visitType']=''
                request.session.set_expiry(0)
            except Exception as e:
                print(e)
                roleName = ''
            return render(request, 'home.html', locals())
        except Exception as e:
            BllWarning().session.rollback()
            logger.debug('数据为空', e)
            return render(request, 'home.html', locals())
        finally:
            BllWarning().session.close()


# 获取主页今日入库、今日领用、今日归还 库存预警、过期药剂、保质期预警
@Utils.log_exception
@require_http_methods(['GET'])
def main(request):

    if request.method == 'GET':
        try:
            # 今日入库数量
            SQL = """
                   SELECT sum(CASE WHEN RecordType=1 then 1 else 0 end) as 'putIn',  
                    sum(CASE WHEN RecordType=2 then 1 else 0 end) as 'useCount',
                    sum(CASE WHEN RecordType=3 then 1 else 0 end) as 'returnCount'
                    FROM `RMS_MedicamentRecord` as a RIGHT JOIN RMS_Medicament as b on a.MedicamentId = b.MedicamentId
                    WHERE DATE_FORMAT(CreateDate,'%Y-%m-%d')= DATE_FORMAT(NOW(),'%Y-%m-%d');
                               """
            HumitureRecord_obj = BllHumitureRecord().execute(SQL).fetchone()

            # 今日入库
            putInCount = HumitureRecord_obj['putIn']
            # 今日领用
            useCount = HumitureRecord_obj['useCount']
            # 今日归还
            returnCount = HumitureRecord_obj['returnCount']

            SQL = """
                SELECT SUM(CASE when ObjectType=3 then 1 else 0 end) as DurgSurplusEarlyWarning, 
                SUM(CASE when ObjectType=2 then 1 else 0 end) as expireWarning, 
                SUM(CASE when ObjectType=1 then 1 else 0 end) as shelflifeWarning FROM `RMS_Warning` where IsSolve = 0
          
            """
            # 获取全部预警
            warning_obj = BllWarning().execute(SQL).fetchone()

            # 保质期预警数量
            shelflifeWarning = warning_obj['shelflifeWarning']
            # 库存预警数量
            DurgSurplusEarlyWarning = warning_obj['DurgSurplusEarlyWarning']
            # 过期预警数量
            expireWarning = warning_obj['expireWarning']

            return render(request, 'main.html', locals())
        except Exception as e:
            logger.debug('数据异常, ' + str(e))
        return render(request, 'main.html')


# 条码登录
def account_barcode(request):
    barcode = request.GET.get('barCode')
    user_obj = BllUser().findEntity(EntityUser.BarCode == barcode)
    if user_obj:
        if user_obj.IsEnabled == 1:
            request.session['login_user'] = json.loads(
                Utils.resultAlchemyData(user_obj))
            return JsonResponse(Utils.resultData(1, '登录成功'))
        else:
            logger.info(user_obj.RoleName + '正在尝试登陆后台管理')
            return JsonResponse(Utils.resultData(0, '该账户已被禁用, 暂时无法登陆, 请联系管理员'))
    else:
        return JsonResponse(Utils.resultData(0, '该条码用户不存在！'))

# post请求csrf失效


@require_http_methods(['GET', 'POST'])
@csrf_exempt
def account_login(request):
    print("111111111")
    if request.method == 'GET':
        try:
            del request.session['login_user']
        except Exception as e:
            pass
        return render(request, 'account/login.html', locals())
    elif request.method == 'POST':
        # try:
            userAccount = request.POST['userAccount']
            userPassword = Utils.MD5(request.POST['userPassword'])
            print(userAccount, '-'+userPassword)
            user = BllUser().login(userAccount, userPassword)
            print(user, "0000000000000000000000000000000000")

            if user:
                if user.IsEnabled == 1:
                    request.session['login_user'] = json.loads(
                        Utils.resultAlchemyData(user))
                    visitType = request.GET.get('visitType')
                    # print('fffffffffffff',visitType)
                    request.session['visitType'] = visitType
                    # if(((visitType=='1') or (visitType=='2'))):
                    #     request.session['visitType']='1'
                    # else:
                    #     request.session['visitType']=''
                    request.session.set_expiry(0)
                    logger.info('登录成功')
                    user.LastVisitDate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    BllUser().update(user)
                    ip_ = get_user_ip(request)
                   
                    if ip_ is None:
                        ip_ = ''
                    log_obj = EntityLog(LogId=str(Utils.UUID()), CustomerId=user.CustomerId, LogType=1,
                                        OperateUserId=user.UserId, OperateAccount=user.Account, OperateUserName=user.RealName,
                                        OperateTypeCode='登录后台成功', OperateType='登录成功', IPAddress=ip_,
                                        ExecuteResult='用户登录后台成功', OperateDate=datetime.datetime.now(),
                                        IsAdd=1)
                    BllLog().insert(log_obj)
                    return JsonResponse(Utils.resultData(1, '登录成功'))
                else:
                    logger.info(user.RoleName + '正在尝试登陆后台管理')
                    return JsonResponse(Utils.resultData(0, '您不是管理员或该账户已被禁用, 暂时无法登陆, 请联系管理员'))

            else:
                logger.info('账号或密码不正确, 登录失败')
                return JsonResponse(Utils.resultData(0, '账号或密码不正确, 登录失败'))
        # except Exception as e:
        #     return JsonResponse(Utils.resultData(0, '数据异常, 登录失败'))

@require_http_methods(['GET'])
def video_index(request):
    if request.method == 'GET':
        # 获取当前日期
        today = (date.today() + relativedelta.relativedelta(days=0)).strftime('%Y-%m-%d')
        # 获取昨天的日期
        # yesterday = (date.today() + timedelta(days=-1)).strftime('%Y-%m-%d')
        last_year = (datetime.datetime.now() + relativedelta.relativedelta(days=-1)).strftime('%Y-%m-%d')
        return render(request, 'video/index.html', locals())

@require_http_methods(['GET'])
def account_logout(request):
    if request.method == 'GET':
        path = request.META.get('HTTP_REFERER', '/')
        del request.session['login_user']
        visitType = request.session.get('visitType')
        # if(((visitType=='1') or (visitType=='2'))):
        #     return redirect('/account/login?visitType=1')
        # else:
        #     return redirect('/account/login')
        if(visitType):
            return redirect('/account/login?visitType='+visitType)
        else:
            return redirect('/account/login')


@require_http_methods(['GET'])
def drug_scanBarCode(request):
    if request.method == 'GET':
        return render(request, 'drug/scanBarCode.html', locals())


# 获取药剂展示页面
@require_http_methods(['GET'])
def drug_index(request):
    if request.method == 'GET':
        try:
            user = request.session['login_user']
            roleName = user['RoleName']
        except Exception as e:
            print(e)
            roleName = ''
        try:
            searchValue = request.GET['searchValue']
            return render(request, 'drug/index.html', locals())
        except:
            return render(request, 'drug/index.html', locals())


# 获取药剂展示处理视图函数, 返回JSON数据
@require_http_methods(['GET'])
def drug_GetDrugListJson(request):
    if request.method == 'GET':
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        name = request.GET.get("searchValue", '')
        clientId = request.GET.get("clientId", '')
        pageParam = PageParam(page, limit)
        
        drug_list = BllMedicament().getAllDrugList(name, pageParam, clientId)
        return JsonResponse({'data': drug_list, "code": 0, "count":pageParam.totalRecords})


# 根据药剂ID  get方式查询返回药剂信息，post修改药剂信息
@require_http_methods(['GET', 'POST'])
@csrf_exempt
def drug_form(request, drug_id):
    if request.method == 'GET':
        drug_obj = BllMedicament().findEntity(drug_id)
        return render(request, 'drug/form.html', locals())
    elif request.method == 'POST':
        CASNumber = request.POST['CASNumber']
        EnglishName = request.POST['EnglishName']
        ProductionDate = request.POST['ProductionDate']
        ExpirationDate = request.POST['ExpirationDate']
        ShelfLife = request.POST['ShelfLife']
        Manufacturer = request.POST['Manufacturer']
        Distributor = request.POST['Distributor']
        IsSupervise = 0
        Price = request.POST['Price']
        Remark1 = request.POST['Remark1']
        Remark2 = request.POST['Remark2']
        Remark3 = request.POST['Remark3']
        drug_obj = BllMedicament().findEntity(drug_id)
        drug_obj.CASNumber = CASNumber
        drug_obj.EnglishName = EnglishName
        drug_obj.ProductionDate = ProductionDate
        drug_obj.ExpirationDate = ExpirationDate
        drug_obj.ShelfLife = ShelfLife
        drug_obj.IsSupervise = IsSupervise
        drug_obj.Manufacturer = Manufacturer
        drug_obj.Distributor = Distributor
        drug_obj.Price = Price
        drug_obj.Remark1 = Remark1
        drug_obj.Remark2 = Remark2
        drug_obj.Remark3 = Remark3
        BllMedicament().update(drug_obj)
        return JsonResponse(Utils.resultData('1', '修改成功', 'drug_obj'))


# 获取药剂类型的JSON数据
@require_http_methods(['GET'])
def drug_GetDrugTypeListJson(request):
    if request.method == 'GET':
        return render(request, 'drug/drugTypeIndex.html', locals())


# 访问入库模板视图处理函数
@require_http_methods(['GET'])
def drugTemplate_index(request):
    if request.method == 'GET':
        try:
            searchValue = request.GET['searchValue']
            return render(request, 'drugTemplate/index.html', locals())
        except:
            pass
        return render(request, 'drugTemplate/index.html', locals())


# 新增单次模块视图处理函数
@require_http_methods(['GET'])
def drugTemplate_itemForm(request):
    if request.method == 'GET':
        template_obj = BllMedicamentTemplate().findEntity(request.GET.get('template_id'))
        index = int(request.GET.get('id', '0'))
        if(template_obj):
            jsonList = json.loads(template_obj.TemplateContent)
            itemContent = jsonList[index]
            print(itemContent)
        return render(request, 'drugTemplate/itemForm.html', locals())


# 新增单次模块视图处理函数
@require_http_methods(['GET'])
def drugTemplate_update_form(request, template_id):
    if request.method == 'GET':
        template_obj = BllMedicamentTemplate().findEntity(template_id)
        # 将template_obj中的字符串类型转化为列表取第一个值为字典类型
        templateId = template_id
        template_content = eval(template_obj.TemplateContent)[0]
        return render(request, 'drugTemplate/form.html', locals())


# 新增药剂模板视图处理函数
@require_http_methods(['GET'])
def drugTemplate_form(request):
    if request.method == 'GET':
        return render(request, 'drugTemplate/form.html', locals())


# 删除选中药品模板视图处理函数
@require_http_methods(['POST'])
@csrf_exempt
def drugTemplate_deleteTemplate(request):
    if request.method == 'POST':
        templateId = request.POST['templateId']
        entity_tem_obj = BllMedicamentTemplate().findEntity(templateId)
        entity_tem_obj.IsWaitExport = 0
        BllMedicamentTemplate().update(entity_tem_obj)
        return JsonResponse(Utils.resultData('1', '删除成功', ''))


# 返回获取ClientListJson数据
@require_http_methods(['GET'])
def drugTemplate_clientListJson(request):
    if request.method == 'GET':
        template_cls_list = BllClient().findList().all()
        # 将获取到的对象转化成字符串
        template_cls_list = Utils.resultAlchemyData(template_cls_list)
        return JsonResponse({'data': json.loads(template_cls_list)})


# 返回获取ClientListJson数据
@require_http_methods(['POST'])
@csrf_exempt
def drugTemplate_saveTemplateData(request):
    if request.method == 'POST':
        TemplateId = request.POST['TemplateId']
        TemplateName = request.POST['TemplateName']
        ClientId = request.POST['ClientId']
        TemplateContent = request.POST['TemplateContent']
        itemTemplateCount = request.POST['itemTemplateCount']
        # 获取client对象  用来保存ClientName的值
        client_obj = BllClient().findEntity(ClientId)
        # if not TemplateId:
        # 随机生成uuid字符串作为主键
        str_uuid = str(Utils.UUID())
        # 获取当前系统时间
        CreateDate = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        # 获取创建用户姓名
        CreateUserName = request.session['login_user']['RealName']
        CreateUserId = request.session['login_user']['UserId']
        SQL = """
        SELECT  BarCodeCount, StartBarCode FROM `RMS_MedicamentTemplate` where StartBarCode =  (SELECT MAX(StartBarCode) from RMS_MedicamentTemplate)
        """
        tem_obj = BllMedicament().execute(SQL).fetchone()
        if tem_obj is None:
            max_barcode = 100001
        else:
            max_barcode = tem_obj.StartBarCode
            BarCodeCount = tem_obj.BarCodeCount
            # 获取最大的开始barcode + 数量
            max_barcode = int(max_barcode) + int(BarCodeCount)
        StartBarCode = max_barcode
        # 新增药剂模板记录
        account = EntityMedicamentTemplate(TemplateId=str_uuid, TemplateName=TemplateName, ClientId=ClientId,
                                           ClientName=client_obj.ClientName, TemplateContent=TemplateContent,
                                           CreateDate=CreateDate,  CreateUserId=CreateUserId, CustomerId=client_obj.CustomerId,
                                           CreateUserName=CreateUserName, IsWaitExport=1, BarCodeCount=int(itemTemplateCount),
                                           StartBarCode=str(StartBarCode))
        BllMedicamentTemplate().insert(account)
        return JsonResponse(Utils.resultData('1', '添加成功', ''))
        # else:
        # # 修改模板内容
        # template_obj = BllMedicamentTemplate().findEntity(TemplateId)
        # template_obj.TemplateName = TemplateName
        # template_obj.CustomerId = client_obj.CustomerId
        # template_obj.ClientId = ClientId
        # template_obj.ClientName = client_obj.ClientName
        # template_obj.TemplateContent = TemplateContent
        # BllMedicamentTemplate().update(template_obj)
        # return JsonResponse(Utils.resultData('1', '修改成功', ''))


# 获得药品入库模板的JSON数据
@require_http_methods(['GET'])
def drugTemplate_getTemplateListJson(request):
    if request.method == 'GET':
        try:
            
            searchValue = request.GET.get('searchValue', '')
            page = int(request.GET.get("page", 1))
            limit = int(request.GET.get("limit", 10))
            pageParam = PageParam(page, limit)
            if searchValue:
                # data = BllMedicamentTemplate().getAllTemplateList(searchValue)
                queryOrm = BllMedicamentTemplate().findList(EntityMedicamentTemplate.TemplateName.like('%'+searchValue+'%'),EntityMedicamentTemplate.IsWaitExport==1).order_by(desc(EntityMedicamentTemplate.CreateDate))
                data = BllMedicamentTemplate().queryPage(queryOrm, pageParam)
                data = json.loads(Utils.resultAlchemyData(data))
                for i in data:
                    data[i]["TemplateContent"] = json.loads(data[i]["TemplateContent"])[0:10]
                    
                return JsonResponse({'data': data, "code": 0, "count":pageParam.totalRecords})
            else:

                # data = BllMedicamentTemplate().getAllTemplateList('')
                queryOrm = BllMedicamentTemplate().findList(EntityMedicamentTemplate.IsWaitExport==1).order_by(desc(EntityMedicamentTemplate.CreateDate))
                data = BllMedicamentTemplate().queryPage(queryOrm, pageParam)
                data = json.loads(Utils.resultAlchemyData(data))
                for i in range(len(data)):
                    data[i]["TemplateContent"] = json.loads(data[i]["TemplateContent"])[0:10]
                return JsonResponse({'data': data, "code": 0, "count":pageParam.totalRecords})
        except Exception as e:
            print(e)
            return JsonResponse({'data': []})


@require_http_methods(['GET'])
def home_homeDrugRecord(request, drug_id):
    if request.method == 'GET':
        return render(request, 'home/homeDrugRecord.html', locals())


@require_http_methods(['GET'])
def log_index(request):
    if request.method == 'GET':
        return render(request, 'log/index.html', locals())


@require_http_methods(['GET'])
def drug_drugTypeForm(request):
    if request.method == 'GET':
        return render(request, 'drug/drugTypeForm.html', locals())


# 404页面处理方案
def page_not_found(request, exception):
    logger.debug('页面没有找到')
    return HttpResponse('地址错误')

#
# # 500服务器错误处理方案
# def server_error(request):
#     logger.debug('服务器错误')
#     return redirect('home')
