
#!/usr/bin/python
#-*- coding: utf-8 -*-

import sys
import random
import datetime
import time
import string
import re
import StringIO
import qrcode
import base64, zlib
import os

from django.shortcuts import render
from django.http import HttpResponse

from django.http import HttpResponse,HttpResponseRedirect, JsonResponse
from django.shortcuts import render_to_response 
from django.template import RequestContext 
from django.views.decorators.csrf import csrf_exempt 
from django.views.decorators.csrf import csrf_protect 
from django.template.context_processors import csrf
from django.template import loader

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout


from models import *

from django.core.cache import cache
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger

USER_PIC_FOLD = "app/static/storage/user-pic/"
LOGO_FOLD = "app/static/storage/logo-images/"

def printError(e):
    print "Error: ", str(e)

def getLen(List):
    length = 0
    try:
        if List == None:
            length = 0
        else:
            length = len(List)

    except Exception, e:      
        printError("getLen(): " + str(e))

    return length

def init_msg(request):
    msg = {}
    msg['login_state'] = False
    if request.user.is_authenticated():
        try:
            msg['login_state'] = True
            account = Account.objects.filter(user=request.user).all()[0]
            msg['account'] = account
        except Exception, e:
            printError(e)

    msg['next'] = '/'
    if request.GET.has_key('next'):
        msg['next'] = request.GET['next']

    return msg

def paginator_show(request, msg_list, page_size):
    page = 1
    try:
        if request.GET.has_key('page'):
            page = int(request.GET['page'])
        if page < 1:
            page = 1

        total_page = (getLen(msg_list) + page_size - 1)/page_size
        if page > total_page:
            page = total_page
    except ValueError:
        page = 1

    
    try:
        paginator = Paginator(msg_list, page_size)
        msg_list = paginator.page(page)
    except(EmptyPage, PageNotAnInteger):
        msg_list = paginator.page(1)

    return msg_list, page

def paginator_bar(cur_page, total_page):
    pages_before = []
    pages_after  = []
    Num = 5

    try:

        if total_page <= Num:
            for i in range(cur_page-1):
                pages_before.append(i+1)
            for i in range(cur_page+1, total_page+1):
                pages_after.append(i)
        elif cur_page <= Num/2:
            for i in range(cur_page-1):
                pages_before.append(i+1)
            for i in range(cur_page, cur_page+Num/2+1):
                pages_after.append(i+1)
        elif (total_page - cur_page) <= Num/2:
            for i in range(total_page - Num, cur_page-1):
                pages_before.append(i+1)
            for i in range(cur_page, total_page):
                pages_after.append(i+1)
        else:
            for i in range(cur_page-Num/2-1, cur_page-1):
                pages_before.append(i+1)
            for i in range(cur_page, cur_page + Num/2):
                pages_after.append(i+1)
    
    except Exception, e:
        printError(e)

    return pages_before, pages_after

def getRandomStr(num=4):

    current_time = time.strftime("%y%m%d%H%M%S", time.localtime())
    rand_str = ''.join(random.sample(string.ascii_letters + string.digits, num))

    return current_time + rand_str

def handle_uploaded_photo(path, f):
    with open( path, 'wb+') as info:
        for chunk in f.chunks():
            info.write(chunk)
    return f


def checkMobile(request):
    try:
        userAgent = request.META['HTTP_USER_AGENT']
        print ""
        print userAgent

        _long_matches = r'googlebot-mobile|android|avantgo|blackberry|blazer|elaine|hiptop|ip(hone|od)|kindle|midp|mmp|mobile|o2|opera mini|palm( os)?|pda|plucker|pocket|psp|smartphone|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce; (iemobile|ppc)|xiino|maemo|fennec'
        _long_matches = re.compile(_long_matches, re.IGNORECASE)

        _short_matches = r'1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|e\-|e\/|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(di|rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|xda(\-|2|g)|yas\-|your|zeto|zte\-'
        _short_matches = re.compile(_short_matches, re.IGNORECASE)
 
        if _long_matches.search(userAgent) != None:
            print "...User from mobile..."
            return True
        user_agent = userAgent[0:4]
        if _short_matches.search(user_agent) != None:
            print "...User from mobile..."
            return True

    except Exception, e:
        printError(e)

    print "...User from pc...\n"

    return False

def get_qrcode(url):
    try:
        img = qrcode.make(url)
        rdn_str = getRandomStr()
        path = "app/static/storage/qrcode/" + rdn_str + ".png"

        img.save(path)

        return "/static/storage/qrcode/" + rdn_str + ".png"

    except Exception, e:
        printError(e)

    return None

def remove_file(filename):
    try:
        filename = "/home/www/tropic/app/"+filename
        if(os.path.exists(filename)):
            os.remove(filename)
        else:
            print filename + "is not exist"
    except Exception, e:
        printError(e)




