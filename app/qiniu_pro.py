from django.http import HttpResponse
from django.shortcuts import render, render_to_response

import json
from qiniu import Auth

BUCKET_NAME = "tropic"
ACCESS_KEY = "5l1vOZHVwsQDFoADsN0Xwxo1OEdDhwsG1vMi7QHj"
SECRET_KEY = "UM7t8H3_3KzCy0CqXVVJVJ_wC6-kWkIUbn471WUa"
DOMAIN     = "http://7xklh2.media1.z0.glb.clouddn.com/"

#class Qiniu():

q = Auth(ACCESS_KEY, SECRET_KEY)

def upload_ui(request):
    data = {}
    data['domain']       = DOMAIN
    data['uptoken_url']  = 'uptoken'
    return render_to_response('upload/upload.html', data)

def uptoken(request):
    key = ""
    if request.GET.has_key("key"):
        key = request.GET["key"]
    try:
        token = q.upload_token(BUCKET_NAME, key)
    except Exception, e:
        print str(e)
    data = {}
    data['uptoken'] = token
    print token
    return HttpResponse(json.dumps(data), content_type="application/json")
