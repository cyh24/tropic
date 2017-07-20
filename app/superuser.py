#!/usr/bin/python
#-*- coding: utf-8 -*-
from common import *
from db_pro import *
from qiniu_pro import *
from wechat_pro import *
import random
import datetime

@super_user
def superuser_manage(request):
    each_page_num = 20
    msg = init_msg(request)


    users = User.objects.filter(is_superuser=True).all()
    orders = Account.objects.filter(user__in=users).exclude(id=1).all()
    # orders = Account.objects.filter(user__in=users).all()

    total_page = (getLen(orders)+each_page_num-1)/each_page_num
    subOrders, cur_page = paginator_show(request, orders, each_page_num)

    for i in range(getLen(subOrders)):
        subOrders[i].user_name = subOrders[i].user.username
        subOrders[i].nickname = subOrders[i].nickname
        # subOrders[i].user_password = subOrders[i].user.password

    pages_before, pages_after = paginator_bar(cur_page, total_page)

    msg['orders']     = subOrders
    msg['orders_len'] = len(orders)
    msg['cur_page']   = cur_page
    msg['pages_before'] = pages_before
    msg['pages_after']  = pages_after
    msg['pre_page']   = cur_page - 1
    msg['after_page'] = cur_page + 1
    return render_to_response('superuser-manage.html', msg)
