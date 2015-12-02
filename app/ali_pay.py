#!/usr/bin/env python
# encoding: utf-8
from alipay.alipay import *
import urllib
from models import Order
from django.http import HttpResponse,HttpResponseRedirect, JsonResponse
from db_pro import get_order_given_ordernum, get_video_by_ordernum
from django.shortcuts import render_to_response

def alipay(request):
    if request.GET.has_key('order_num'):
        order_num = request.GET['order_num']

    order = get_order_given_ordernum(order_num)

    url=create_direct_pay_by_user(order_num, order.name, order.name,  order.price)
    return HttpResponseRedirect(url)

def alipay_return(request):
    print "return..."
    """
    Handler for synchronous updating billing information.
    """
    msg = {}
    if notify_verify(request.GET):
        tn = request.GET.get('out_trade_no')
        video = get_video_by_ordernum(tn)
        trade_no = request.GET.get('trade_no')
        trade_status = request.GET.get('trade_status')
        print tn, trade_no, trade_status
        url=send_goods_confirm_by_platform (trade_no)
        print "url: ", url
        req=urllib.urlopen (url)
        print "req: ", req

        order = get_order_given_ordernum(tn)
        order.pay_state = 2
        order.save()
        return render_to_response('/videos/play/?video-id=%d'%video.id, msg)

    return render_to_response('/videos/play/?video-id=%d'%video.id, msg)

def alipay_notify (request):
    """
    Handler for notify_url for asynchronous updating billing information.
    Logging the information.
    """
    print "notify..."
    if request.method == 'POST':
        if notify_verify(request.POST):
            tn = request.POST.get('out_trade_no')
            trade_status = request.POST.get('trade_status')
            trade_no=request.POST.get('trade_no')
            print tn, trade_status, trade_no
            if trade_status == 'WAIT_SELLER_SEND_GOODS':
                url = send_goods_confirm_by_platform (trade_no)
                req=urllib.urlopen (url)
                print req
                print "success"
                return HttpResponseRedirect (reverse ('payment_success'))
            else:
                print "fail"
                return HttpResponseRedirect (reverse ('payment_error'))
        else:
            return HttpResponseRedirect (reverse ('payment_error'))
