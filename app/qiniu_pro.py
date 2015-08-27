from django.http import HttpResponse
from django.shortcuts import render, render_to_response

import json
from qiniu import Auth
import requests
from models import *

from config import *

q = Auth(ACCESS_KEY, SECRET_KEY)

class QiniuPro():
    def __init__(self):
        self.auth = Auth(ACCESS_KEY, SECRET_KEY)

    def download_private_url(self, key, expires=7200):
        base_url = '%s/%s' % (DOMAIN, key)
        private_url = self.auth.private_download_url(base_url, expires)
        return private_url

Qiniu = QiniuPro()


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

