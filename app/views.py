from django.shortcuts import render
from django.http import HttpResponse

from django.http import HttpResponse,HttpResponseRedirect 
from django.shortcuts import render_to_response 
from django.template import RequestContext 
from django.views.decorators.csrf import csrf_exempt 
from django.views.decorators.csrf import csrf_protect 
from django.template import loader

from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger

import simplejson

from models import *
import time
import os
import sys


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


def index(request):

    return render_to_response('index.html')

