from django.conf.urls import url

from . import views

app_name = 'Hazardous'

urlpatterns = [
    url(r'^PutInTemplate/$', views.PutInTemplate, name='PutInTemplate'),
    url(r'^Use/$', views.UseView, name='UseView'),
    url(r'^Return/$', views.ReturnView, name='ReturnView'),
    url(r'^getUpanTemplateFile/$', views.getUpanTemplateFile, name='getUpanTemplateFile'),
    url(r'^getHazardousTemplateListJson/$', views.getHazardousTemplateListJson, name='getHazardousTemplateListJson'),
    # 添加模板
    url(r'^HazardousTemplateForm/$', views.HazardousTemplateForm, name='HazardousTemplateForm'),
    url(r'^HazardousListJson/$', views.HazardousListJson, name='HazardousListJson'),
    url(r'^PutInView/$', views.PutInView, name='PutInView'),
    url(r'^RFID_bind/$', views.RFID_bind, name='RFID_bind'),
    # # 归还页面
    # url(r'^shelfReturn/$', views.shelfReturn, name='shelfReturn'),
    # 归还视图
    url(r'^HazardousReturnView/$', views.HazardousReturnView, name='HazardousReturnView'),
    # 领用页面
    url(r'^shelfUse/$', views.shelfUse, name='shelfUse'),
    # 领用视图
    url(r'^HazardousUseView/$', views.HazardousUseView, name='HazardousUseView'),
    # 钥匙管理
    url(r'^KeyManagement/$', views.KeyManagement, name='KeyManagement'),
    url(r'^GetKeyListJson/$', views.GetKeyListJson, name='GetKeyListJson'),
    url(r'^key_form/$', views.key_form, name='key_form'),
    url(r'^key_barCode/$', views.key_barCode, name='key_barCode'),
    url(r'^getSelectStatusListJson/$', views.getSelectStatusListJson, name='getSelectStatusListJson'),
    url(r'^deleteKey/$', views.deleteKey, name='deleteKey'),
    url(r'^getKeyRecordListJson/$', views.getKeyRecordListJson, name='getKeyRecordListJson'),
    url(r'^KeyRecord/$', views.KeyRecord, name='KeyRecord'),
]
