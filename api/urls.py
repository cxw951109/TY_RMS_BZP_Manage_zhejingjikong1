from django.conf.urls import url

from . import views

app_name = 'api'

urlpatterns = [

    # 获取试剂Json数据
    url(r'^getDrugList/$', views.getDrugList, name='getDrugList'),

    # 获取用户列表
    url(r'^getUserList/$', views.getUserList, name='getUserList'),
    url(r'^form_total/', views.form_total, name='form_total'),
    url(r'^usage_record/', views.usage_record, name='usage_record'),
    # 获取用户流转记录
    url(r'^getDrugRecordList/$', views.getDrugRecordList, name='getDrugRecordList'),
    # 申购提醒
    url(r'^getWantPurchaseList/$', views.getWantPurchaseList,
        name='getWantPurchaseList'),
    # 待入库提醒
    url(r'^getAcceptance/$', views.getAcceptance, name='getAcceptance'),
    # 报表数据统计数（今日入库，今日领用， 今日归还， 采购到货）
    url(r'^getStatisticalData/$', views.getStatisticalData, name='getStatisticalData'),
    # 库存量
    url(r'^getAllStockCount/$', views.getAllStockCount, name='getAllStockCount'),
    # 常用试剂
    url(r'^getOftenUse/$', views.getOftenUse, name='getOftenUse'),
    # 大屏页面
    url(r'^index/$', views.index, name='index'),
    # 获取预警Json数据
    url(r'getWarningListJson/', views.getWarningListJson, name='getWarningListJson'),
    # 获取温度echarts展示数据
    url(r'^getTemperatureEchartsJson/.*$', views.getTemperatureEchartsJson, name='getTemperatureEchartsJson'),

]
