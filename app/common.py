import sys
import random
import datetime
import time
import string

def getRandomStr(num=4):

    current_time = time.strftime("%y%m%d%H%M%S", time.localtime())
    rand_str = ''.join(random.sample(string.ascii_letters + string.digits, num))

    return current_time + "-" + rand_str

def handle_uploaded_photo(path, f):
    with open( path, 'wb+') as info:
        for chunk in f.chunks():
            info.write(chunk)
    return f

def printError(e):
	print str(e)
