#!/usr/bin/python
#-*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse

from django.http import HttpResponse,HttpResponseRedirect, JsonResponse 
from django.shortcuts import render_to_response 
from django.template import RequestContext 
from django.views.decorators.csrf import csrf_exempt 
from django.views.decorators.csrf import csrf_protect 
from django.template.context_processors import csrf
from django.template import loader

from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout


from models import *
import time
import os
import sys

#Terry add import
import time
from django.shortcuts import HttpResponse, render_to_response, redirect

from wxknife import handler as HD
from wxknife.backends.dj import Helper, sns_userinfo
from wxknife import WeixinHelper, JsApi_pub, WxPayConf_pub, UnifiedOrder_pub, OrderQuery_pub, Notify_pub, catch

#from app.wechat_pay import NativeLink_pub, UnifiedOrder_pub, OrderQuery_pub, JsApi_pub

import qrcode
from cStringIO import StringIO
import random
import string

HOMEPAGE = 'http://terry.tunnel.mobi'

@csrf_exempt 

@csrf_protect 
def paginator_show(request, msg_list, page_size=16):
    #after_range_num  = 5
    #before_range_num = 6
    try:
        page = 1
        #page = int(request.GET.get("page", 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    paginator = Paginator(msg_list, page_size)
    
    try:
        msg_list = paginator.page(page)
    except(EmptyPage, PageNotAnInteger):
        msg_list = paginator.page(1)

    #if page >= after_range_num:
    #    page_range = paginator.page_range[page - after_range_num: page + before_range_num]
    #else:
    #    page_range = paginator.page_range[0: int(page) + before_range_num]

    #template_var["page_objects"] = msg_list
    #template_var["page_range"]   = page_range
    return msg_list



def init_msg(request):
    msg = {}
    msg['login_state'] = False
    if request.user.is_authenticated():
        msg['login_state'] = True

    msg['next'] = '/'
    if request.GET.has_key('next'):
        msg['next'] = request.GET['next']

    return msg


#二维码

def getRandomStr(num=5):#随机名
    
    current_time = time.strftime("%y%m%d%H%M%S", time.localtime())
    rand_str = ''.join(random.sample(string.ascii_letters + string.digits, num))

    return current_time + "-" + rand_str

def generate_qrcode(code_url):#生成二维码图片
    qr = qrcode.QRCode(version = 2,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size = 10, border = 1
    )
    qr.add_data(code_url)
    qr.make(fit=True)
    img = qr.make_image()
    return img

def wechat_pay(request):

    msg = init_msg(request)
    
    unifiedOrder = UnifiedOrder_pub()

    unifiedOrder.setParameter("body", "Ipad mini3  128G")
    unifiedOrder.setParameter("total_fee", "1")
    unifiedOrder.setParameter("out_trade_no", "1217752501201407033233368066")
    unifiedOrder.setParameter("notify_url", WxPayConf_pub.NOTIFY_URL) #通知地址 
    unifiedOrder.setParameter("trade_type", "NATIVE") #交易类型
    result = unifiedOrder.getResult()

    if result["return_code"] == "SUCCESS":
        msg['return_code'] = "SUCCESS"
        if result["result_code"] == "SUCCESS":
            msg['result_code'] = "SUCCESS"
            code_url = unifiedOrder.result["code_url"]

            #print code_url #为啥调了3次啊我擦擦。
            
            #二维码生成
            img = generate_qrcode(code_url)
            APP_PATH = os.path.dirname(os.path.dirname(__file__))
            STATIC_PATH = os.path.join(APP_PATH, 'app/static/images/').replace('\\','/')

            img_name = getRandomStr()+".png"
            msg['img_name'] = img_name
            outfile = os.path.join(STATIC_PATH, img_name) 
            img.save(outfile)
        else:
            msg['result_code'] = result["err_code"]
    else:
        msg['return_code'] = result["return_msg"]

    return render_to_response('WxPay/WxPay.html', msg)

def check_pay(request):
    orderQuery = OrderQuery_pub()
    orderQuery.setParameter("out_trade_no", "1217752501201407033233368066")
    
    result = orderQuery.getResult()
    #print result
    return JsonResponse(result)

def pay_result(request):
    msg = init_msg(request)
    ###应添加订单状态处理
    return render_to_response('WxPay/Notice.html', msg)

def payback(request):
    #虽然收不到微信支付回调，但貌似还是做一个返回好一点
    xml = request.body#.raw_post_data
    #使用通用通知接口
    notify = Notify_pub()
    notify.saveData(xml)
    print xml


    FAIL, SUCCESS = "FAIL", "SUCCESS"
    #验证签名，并回应微信。
    #对后台通知交互时，如果微信收到商户的应答不是成功或超时，微信认为通知失败，
    #微信会通过一定的策略（如30分钟共8次）定期重新发起通知，
    #尽可能提高通知的成功率，但微信不保证通知最终能成功
    if not notify.checkSign():
        notify.setReturnParameter("return_code", FAIL) #返回状态码
        notify.setReturnParameter("return_msg", "签名失败") #返回信息
    else:
        result = notify.getData()

        if result["return_code"] == FAIL:
            notify.setReturnParameter("return_code", FAIL)
            notify.setReturnParameter("return_msg", "通信错误")
        elif result["result_code"] == FAIL:
            notify.setReturnParameter("return_code", FAIL)
            notify.setReturnParameter("return_msg", result["err_code_des"])
        else:
            notify.setReturnParameter("return_code", SUCCESS)
            out_trade_no = result["out_trade_no"] #商户系统的订单号，与请求一致。
            ###检查订单号是否已存在,以及业务代码(业务代码注意重入问题)

    return  HttpResponse(notify.returnXml())

@sns_userinfo
def jsapi_pay(request):
    response = render_to_response("WxPay/JsPay.html")
    response.set_cookie("openid", Helper.sign_cookie(request.openid))
    return response

@sns_userinfo
@catch
def paydetail(request):
    """获取支付信息"""
    openid = request.openid
    money = request.POST.get("money") or "0.01"
    money = int(float(money)*100)

    print openid
    jsApi = JsApi_pub()
    unifiedOrder = UnifiedOrder_pub()
    unifiedOrder.setParameter("openid",openid) #商品描述########################
    

    unifiedOrder.setParameter("body","Ipad mini3  128G") #商品描述
    timeStamp = time.time()
    out_trade_no = "{0}{1}".format(getRandomStr(), int(timeStamp*100))
    unifiedOrder.setParameter("out_trade_no", out_trade_no) #商户订单号
    unifiedOrder.setParameter("total_fee", str(money)) #总金额
    unifiedOrder.setParameter("notify_url", WxPayConf_pub.NOTIFY_URL) #通知地址 
    unifiedOrder.setParameter("trade_type", "JSAPI") #交易类型
    unifiedOrder.setParameter("attach", "6666") #附件数据，可分辨不同商家(string(127))
    try:
        prepay_id = unifiedOrder.getPrepayId()
        jsApi.setPrepayId(prepay_id)
        jsApiParameters = jsApi.getParameters()
    except Exception as e:
        print(e)
    else:
        print jsApiParameters
        return HttpResponse(jsApiParameters)
