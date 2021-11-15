import json
import datetime

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from Business.BllUser import *
from Business.BllWarning import *
from Business.BllMedicamentRecord import *


# 用户访问个人信息页面
@require_http_methods(['GET'])
def myInfo(request):
    if request.method == 'GET':
        user = request.session['login_user']
        return render(request, 'home/myInfo.html', locals())


# 保存用户信息视图处理函数
@require_http_methods(['POST'])
@csrf_exempt
def saveMyBaseInfo(request):
    if request.method == 'POST':
        UserId = request.POST['UserId']
        RealName = request.POST['RealName']
        Email = request.POST['Email']
        Birthday = request.POST['Birthday']
        QQ = request.POST['QQ']
        Mobile = request.POST['Mobile']

        user = BllUser().findEntity(UserId)
        user.RealName = RealName
        user.Email = Email
        if not Birthday:
            pass
        else:
            user.Birthday = datetime.datetime.strptime(Birthday, '%Y-%m-%d')
        user.QQ = QQ
        user.Mobile = Mobile
        request.session['login_user'] = json.loads(Utils.resultAlchemyData(user))
        BllUser().update(user)
        return JsonResponse(Utils.resultData('1', '保存成功', ''))


# 用户访问个人信息页面
@csrf_exempt
@require_http_methods(['POST'])
@require_POST
def saveMyPwd(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        NewPwd = request.POST['NewPwd']
        NewPwd1 = request.POST['NewPwd1']
        OldPwd = request.POST.get('OldPwd', '')
        if NewPwd != NewPwd1:
            return JsonResponse(Utils.resultData('0', '新密码与确认密码不一致, 保存失败'))
        # 判断是修改自己 还是其他用户
        if user_id is None:
            user = request.session['login_user']
            user = BllUser().findEntity(user['UserId'])
            if user.Password != Utils.MD5(OldPwd).upper():
                return JsonResponse(Utils.resultData('0', '原密码输入错误, 保存失败'))
            user.Password = Utils.MD5(NewPwd).upper()
            BllUser().update(user)
            return JsonResponse(Utils.resultData('1', '保存成功', data=user.UserId))
        else:
            user = BllUser().findEntity(user_id)
            user.Password = Utils.MD5(NewPwd).upper()
            BllUser().update(user)

            return JsonResponse(Utils.resultData('1', '保存成功', data=user_id))


@require_http_methods(['GET'])
def saveUser(request, user_id):
    if request.method == 'GET':
        return render(request, 'home/saveUser.html', {'user_id': user_id})


# 获取近期预警列表前5条
@require_http_methods(['GET'])
def getWarningList(request):
    if request.method == 'GET':
        try:
            SQL = """
            SELECT WarningId, WarningDate, WarningContent, ObjectName FROM `RMS_Warning` where IsSolve = 0  ORDER BY WarningDate desc;
            """
            warning_list = BllWarning().execute(SQL).fetchall()[:3]
            warning_list = Utils.mysqlTable2Model(warning_list)
            return JsonResponse({'data': Utils.resultAlchemyData(warning_list)})
        except Exception as e:
            logger.debug('数据为空')
            return JsonResponse({'data': []})


# 获取药剂流转记录
@require_http_methods(['GET'])
def homeDrugRecord(request):
    if request.method == 'GET':
        days = request.GET.get('days')
        recordType = request.GET.get('recordType')
        BarCode = request.GET.get('BarCode', '')
        varietyId = request.GET.get('VarietyId', '')
        if not varietyId:
            varietyId = ''
        return render(request, 'home/homeDrugRecord.html', locals())


# 获取药剂记录今日入库 领用 归还Json数据
@require_http_methods(['GET'])
def getRecordTypeDrugRecordListJson(request):
    if request.method == 'GET':
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        BarCode = request.GET.get('BarCode', '')
        varietyId = request.GET.get('varietyId', '')
        # 如果没传入varietyId则代表不是进入药剂类别流转记录页面
        if not varietyId:
            try:
                # 如果  BarCode 没有值则代表获取首页入库数据
                if not BarCode:
                    recordType = request.GET.get('recordType')

                    # 获取今日入库 领用 归还数据库
                    sql1 = """
                         select a.BarCode, a.CASNumber, a.ClientCode, a.`Name`, a.Purity, b.CreateDate, b.RecordType, b.CreateUserName, 
                         a.Place from RMS_Medicament as a LEFT JOIN RMS_MedicamentRecord as b on a.MedicamentId = 
                         b.MedicamentId where b.RecordType=:recordType and DATE_FORMAT(b.CreateDate, '%Y-%m-%d')
                          = DATE_FORMAT(now(),'%Y-%m-%d')
                         """
                    # 获取今日入库 领用 归还所有数据
                    SQL = sql1 + " LIMIT {},{};".format((page-1)*limit, limit)
                    SQL_Len = "SELECT COUNT(*) FROM (" + sql1 + ") s"
                    MedicamentRecord_obj_list = BllMedicamentRecord().execute(SQL, {'recordType': recordType}).fetchall()
                    drug_obj_list_len = BllMedicamentRecord().execute(SQL_Len, {'recordType': recordType}).fetchall()
                    drug_obj_list_len = int(Utils.mysqlTable2Model(drug_obj_list_len)[0]["COUNT(*)"])
                    return JsonResponse({'data': json.loads(Utils.resultAlchemyData(Utils.mysqlTable2Model(MedicamentRecord_obj_list))), "code": 0, "count": drug_obj_list_len})
                # 如果  BarCode 有值则代表查看药剂流转记录
                else:

                    # 书写查看药剂流转记录SQL语句 条件BarCode

                    sql1 = """
                    select a.BarCode, a.CASNumber, a.ClientCode, a.`Name`, a.Purity, b.CreateDate, b.RecordType, b.CreateUserName, 
                         a.Place from RMS_Medicament as a right JOIN RMS_MedicamentRecord as b on a.MedicamentId = 
                         b.MedicamentId WHERE a.BarCode = :BarCode
                    """
                    SQL = sql1 + " LIMIT {},{};".format((page-1)*limit, limit)
                    SQL_Len = "SELECT COUNT(*) FROM (" + sql1 + ") s"
                    MedicamentRecord_obj_list = BllMedicamentRecord().execute(SQL, {'BarCode': BarCode}).fetchall()
                    drug_obj_list_len = BllMedicamentRecord().execute(SQL_Len, {'BarCode': BarCode}).fetchall()
                    drug_obj_list_len = int(Utils.mysqlTable2Model(drug_obj_list_len)[0]["COUNT(*)"])
                    aaa = json.loads(Utils.resultAlchemyData(Utils.mysqlTable2Model(MedicamentRecord_obj_list)))
                    print(aaa)
                    return JsonResponse({'data': json.loads(Utils.resultAlchemyData(Utils.mysqlTable2Model(MedicamentRecord_obj_list))), "code": 0, "count": drug_obj_list_len})
            except Exception as e:
                logger.info('数据异常')
                return JsonResponse({'data': ''})
        else:
            try:
                SQL = """
                select a.BarCode, a.ClientCode, a.CASNumber, a.`Name`, a.Purity, b.CreateDate, b.RecordType, b.CreateUserName, 
                         a.Place from RMS_Medicament as a RIGHT JOIN RMS_MedicamentRecord as b on a.MedicamentId = 
                         b.MedicamentId where a.VarietyId = :VarietyId
                         """
                SQL = sql1 + " LIMIT {},{};".format((page-1)*limit, limit)
                SQL_Len = "SELECT COUNT(*) FROM (" + sql1 + ") s"
                typeRecord_obj_list = BllMedicamentRecord().execute(SQL, {'VarietyId': varietyId}).fetchall()
                drug_obj_list_len = BllMedicamentRecord().execute(SQL_Len, {'VarietyId': varietyId}).fetchall()
                drug_obj_list_len = int(Utils.mysqlTable2Model(drug_obj_list_len)[0]["COUNT(*)"])
                return JsonResponse({'data': json.loads(Utils.resultAlchemyData(Utils.mysqlTable2Model(MedicamentRecord_obj_list))), "code": 0, "count": drug_obj_list_len})
            except Exception as e:
                logger.info('数据异常')
                return JsonResponse({'data': ''})


# 主页库存预警 过期药剂 保质期预警返回页面处理函数
@require_http_methods(['GET'])
def homeWarningRecord(request):
    if request.method == 'GET':
        warningType = request.GET.get('warningType', '')
        if warningType:
            return render(request, 'home/homeWarningRecord.html', locals())
        else:
            logger.debug('没有传入预警类型')
            return render(request, 'main.html', locals())


# 主页库存预警 过期药剂 保质期预警返回Json数据页面
@require_http_methods(['GET'])
def homeWarningListJson(request):
    if request.method == 'GET':
        warningType = request.GET.get('warningType', '')
        if warningType:
            try:
                # 编写库存预警 过期药剂 保质期预警不同类型的SQL语句
                SQL = """
                 SELECT  * FROM RMS_Warning WHERE RMS_Warning.ObjectType = :warningType and IsSolve = 0 ORDER BY WarningDate desc;
                        """
                warning_obj_list = BllWarning().execute(SQL, {'warningType': warningType}).fetchall()
                return JsonResponse({'data': json.loads(Utils.resultAlchemyData(Utils.mysqlTable2Model(warning_obj_list)))})
            except Exception as e:
                logger.info('数据异常')
                return JsonResponse({'data': ''})
 #mxh_获取库存人员的详情记录
@require_http_methods(['GET'])
def homeDescription(request):
    if request.method == 'GET':
        CreateUserName = request.GET.get('CreateUserName', '')
        startDate = request.GET.get('startDate', '')
        endDate = request.GET.get('endDate', '')
        print('mxh_sssss',CreateUserName,startDate)
        if CreateUserName:
            return render(request, 'home/homeDescription.html', locals())
        else:
            logger.debug('没有传入详细数据')
            #可以返回页面，只是数据为空
            return render(request, 'home/homeDescription.html', locals())
            # return render(request, 'main.html', locals())

 #mxh_获取库存人员的详情记录返回json数据
@require_http_methods(['GET'])
def homeDescriptionJson(request):
    if request.method == 'GET':
        CreateUserName = request.GET.get('CreateUserName', '')
        startDate = request.GET.get('startDate', '')
        endDate = request.GET.get('endDate', '')
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        print('传过来的数据是，',CreateUserName,startDate,endDate)
        if CreateUserName:
            if startDate:
                if endDate:
                    sql1 = "(rms_medicamentrecord.CreateUserName =:CreateUserName) and (RMS_MedicamentRecord.CreateDate BETWEEN :startDate AND :endDate) ORDER BY RMS_MedicamentRecord.CreateDate desc"
                else:
                    sql1 = "(rms_medicamentrecord.CreateUserName =:CreateUserName) and (RMS_MedicamentRecord.CreateDate >:startDate) ORDER BY RMS_MedicamentRecord.CreateDate desc"
            else:
                if endDate:
                    sql1 = "(rms_medicamentrecord.CreateUserName =:CreateUserName) and (RMS_MedicamentRecord.CreateDate<:endDate) ORDER BY RMS_MedicamentRecord.CreateDate desc"
                else:
                    sql1 = "(rms_medicamentrecord.CreateUserName =:CreateUserName) ORDER BY RMS_MedicamentRecord.CreateDate desc"
        else:
            if startDate:
                if endDate:
                    sql1 = "(RMS_MedicamentRecord.CreateDate BETWEEN :startDate AND :endDate) ORDER BY RMS_MedicamentRecord.CreateDate desc"
                else:
                    sql1 = "(RMS_MedicamentRecord.CreateDate >:startDate) ORDER BY RMS_MedicamentRecord.CreateDate desc"
            else:
                if endDate:
                    sql1 = "(RMS_MedicamentRecord.CreateDate<:endDate) ORDER BY RMS_MedicamentRecord.CreateDate desc"
                else:
                    sql1 = ''
        try:
            print('开始：')
            SQL_all = "SELECT CreateDate,RecordType, RMS_Medicament.EnglishName, RMS_Medicament.Name, " \
                   "RMS_Medicament.BarCode, RMS_Medicament.ByUserName, RMS_Medicament.Purity,RecordRemain, RMS_Medicament." \
                   "`Status`, RMS_Medicament.Place, RMS_MedicamentRecord.CreateUserName, PutInUserName, CASNumber FROM `RMS_MedicamentRecord` INNER JOIN " \
                   " RMS_Medicament ON RMS_MedicamentRecord.MedicamentId = RMS_Medicament.MedicamentId WHERE (rms_medicamentrecord.RecordType=3) and "

            SQL = SQL_all + sql1 + " LIMIT {},{};".format((page-1)*limit, limit)
            SQL_Len = "SELECT COUNT(*) FROM (" + SQL_all + sql1 + ") s"
            print('sql 语句是',SQL, "1111111111111111111111111111111111111111111")
            desc_obj_list = BllWarning().execute(SQL, {'CreateUserName': CreateUserName,'startDate': startDate, 'endDate': endDate,}).fetchall()
            desc_obj_list_len = BllWarning().execute(SQL_Len, {'CreateUserName': CreateUserName,'startDate': startDate, 'endDate': endDate,}).fetchall()
            drug_obj_list_len = int(Utils.mysqlTable2Model(desc_obj_list_len)[0]["COUNT(*)"])
            print(drug_obj_list_len)
            data = json.dumps(dict({'data': json.loads(Utils.resultAlchemyData(Utils.mysqlTable2Model(desc_obj_list))), "code":0, "count": drug_obj_list_len}),  cls=DateEnconding)
            from django.shortcuts import HttpResponse
            print(data)
            return HttpResponse(data)
        except Exception as e:
            print('数据异常')
            logger.info('数据异常')
            return JsonResponse({'data': ''})

class DateEnconding(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.date):
            return o.strftime('%Y/%m/%d')
#mxh_获取库存人员的详情记录
@require_http_methods(['GET'])
def homeMedicamentDescription(request):
    if request.method == 'GET':
        medicamentName = request.GET.get('medicamentName', '')
        startDate = request.GET.get('startDate', '')
        endDate = request.GET.get('endDate', '')
        if medicamentName:
            return render(request, 'home/homeMedicamentDescription.html', locals())
        else:
            # 可以返回页面，只是数据为空
            logger.debug('没有传入详细数据')
            return render(request, 'home/homeMedicamentDescription.html', locals())
            # return render(request, 'main.html', locals())

 #mxh_获取库存人员的详情记录返回json数据
@require_http_methods(['GET'])
def homeMedicamentDescriptionJson(request):
    if request.method == 'GET':
        medicamentName = request.GET.get('medicamentName', '')
        startDate = request.GET.get('startDate', '')
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        endDate = request.GET.get('endDate', '')
        if medicamentName:
            if startDate:
                if endDate:
                    sql1 = "(rms_medicamentvariety.Name =:medicamentName) and (RMS_MedicamentRecord.CreateDate BETWEEN :startDate AND :endDate) ORDER BY RMS_MedicamentRecord.CreateDate desc"
                else:
                    sql1 = "(rms_medicamentvariety.Name =:medicamentName) and (RMS_MedicamentRecord.CreateDate >:startDate) ORDER BY RMS_MedicamentRecord.CreateDate desc"
            else:
                if endDate:
                    sql1 = "(rms_medicamentvariety.Name =:medicamentName) and (RMS_MedicamentRecord.CreateDate<:endDate) ORDER BY RMS_MedicamentRecord.CreateDate desc"
                else:
                    sql1 = "(rms_medicamentvariety.Name =:medicamentName) ORDER BY RMS_MedicamentRecord.CreateDate desc"
        else:
            if startDate:
                if endDate:
                    sql1 = "(RMS_MedicamentRecord.CreateDate BETWEEN :startDate AND :endDate) ORDER BY RMS_MedicamentRecord.CreateDate desc"
                else:
                    sql1 = "(RMS_MedicamentRecord.CreateDate >:startDate) ORDER BY RMS_MedicamentRecord.CreateDate desc"
            else:
                if endDate:
                    sql1 = "(RMS_MedicamentRecord.CreateDate<:endDate) ORDER BY RMS_MedicamentRecord.CreateDate desc"
                else:
                    sql1 = ''
        # try:
            # SQL_a = "SELECT * FROM rms_medicamentrecord LEFT JOIN rms_medicamentvariety ON rms_medicamentrecord.VarietyId=rms_medicamentvariety.VarietyId WHERE (RecordType=3) and "
        SQL_a = "SELECT rms_medicamentvariety.CASNumber,rms_medicamentvariety.Name,rms_medicamentvariety.EnglishName,rms_medicamentvariety.Purity,rms_medicamentrecord.RecordRemain,rms_medicamentrecord.CreateUserName,rms_medicamentrecord.RecordType,rms_medicamentvariety.Unit,rms_medicamentvariety.SpeciUnit,rms_medicamentrecord.ClientCode,rms_medicamentrecord.CreateDate FROM rms_medicamentrecord LEFT JOIN rms_medicamentvariety ON rms_medicamentrecord.VarietyId=rms_medicamentvariety.VarietyId WHERE (RecordType=3) and "
        SQL = SQL_a + sql1 + " LIMIT {},{};".format((page-1)*limit, limit)
        SQL_Len = "SELECT COUNT(*) FROM (" + SQL_a + sql1 + ") s"
        desc_obj_list = BllWarning().execute(SQL, {'medicamentName': medicamentName,'startDate': startDate, 'endDate': endDate,}).fetchall()
        drug_obj_list_len = BllWarning().execute(SQL_Len, {'medicamentName': medicamentName,'startDate': startDate, 'endDate': endDate,}).fetchall()
        drug_obj_list_len = int(Utils.mysqlTable2Model(drug_obj_list_len)[0]["COUNT(*)"])
        return JsonResponse({'data': json.loads(Utils.resultAlchemyData(Utils.mysqlTable2Model(desc_obj_list))), "code": 0, "count": drug_obj_list_len})
        # except Exception as e:
        #     logger.info('数据异常')
        #     return JsonResponse({'data': ''})

