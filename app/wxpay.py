#!/usr/bin/python
#-*- coding: utf-8 -*-
from common import *

#Terry add import
from wxknife import handler as HD
from wxknife.backends.dj import Helper, sns_userinfo
from wxknife import WeixinHelper, JsApi_pub, WxPayConf_pub, UnifiedOrder_pub, OrderQuery_pub, Notify_pub, catch


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
