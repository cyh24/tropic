#!/usr/bin/python
#-*- coding: utf-8 -*-
from common import *
from models import *
#Terry add import
from wxknife import handler as HD
from wxknife.backends.dj import Helper, sns_userinfo
from wxknife import WeixinHelper, JsApi_pub, WxPayConf_pub, UnifiedOrder_pub, OrderQuery_pub, Notify_pub, catch

import qrcode
import base64

def generate_qrcode(code_url):
    qr = qrcode.QRCode(version = 2, 
            error_correction = qrcode.constants.ERROR_CORRECT_L,
            box_size = 10, border = 1)
    qr.add_data(code_url)
    qr.make(fit = True)
    img = qr.make_image()
    return img

def get_wxpay_qrcode(order):
    
    outfile = "/static/images/banner.png"
    
    unifiedOrder = UnifiedOrder_pub()
    unifiedOrder.setParameter("body",order.name.encode("utf-8"))
    unifiedOrder.setParameter("total_fee","1")#str(int(order.price*100)))
    unifiedOrder.setParameter("out_trade_no",order.order_num)
    unifiedOrder.setParameter("notify_url",WxPayConf_pub.NOTIFY_URL)
    unifiedOrder.setParameter("trade_type","NATIVE")

    result = unifiedOrder.getResult()
    if result["return_code"] == "SUCCESS":
        if result["result_code"] == "SUCCESS":

            code_url = unifiedOrder.result["code_url"]
            img = generate_qrcode(code_url)
            APP_PATH = os.path.dirname(os.path.dirname(__file__))
            STATIC_PATH = os.path.join(APP_PATH, 'app/static/storage/qrcode/').replace('\\','/')
            img_name = getRandomStr()+".png"
            outfile = os.path.join(STATIC_PATH, img_name) 
            img.save(outfile)
            outfile = '/static/storage/qrcode/'+img_name
            #base64_code = base64.encode(img)
        else:
            print result["err_code"]
    else:
        print result["return_msg"]
    return outfile

def check_pay(request):
    result = {}
    try:
        if request.GET.has_key('out_trade_no'):
            out_trade_no = request.GET['out_trade_no']
        
        orderQuery = OrderQuery_pub()
        orderQuery.setParameter("out_trade_no", out_trade_no)#"1217752501201407033233368056")
    
        result = orderQuery.getResult()
        #print result
    except Exception, e:
        printError(e)

    return JsonResponse(result)

def check_pay_by_order_num(order_num):
    try:
        orderQuery = OrderQuery_pub()
        orderQuery.setParameter("out_trade_no", order_num)#"1217752501201407033233368056")
        result = orderQuery.getResult()
        print result
        if result['trade_state'] == "SUCCESS":
            return True

    except Exception, e:
        print "check_pay_by_trade_no: ", str(e) 
    
    return False

def pay_result(request):
    msg = init_msg(request)
    try:
        if request.GET.has_key('paid_order_id'):
            paid_order_id = request.GET['paid_order_id']
            paid_orders = Order.objects.filter(id=paid_order_id)
            paid_order = paid_orders[0]
            paid_order.pay_state = 2
            remove_file(paid_order.wxpay_qrcode)
            paid_order.save()
            msg['paid_order'] = paid_order
    except Exception, e:
        printError(e)
    ###应添加订单状态处理
    return render_to_response('pay/notice.html', msg)

def payback(request):
    print "fuck wechat"
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

#@sns_userinfo
def jsapi_pay(request):
    response = render_to_response("WxPay/JsPay.html")
    #response.set_cookie("openid", Helper.sign_cookie(request.openid))
    return response

