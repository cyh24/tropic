from common import RedisUtil
from collections import deque
class TropicMiddleware(object):
    # def __init__(self, get_response):
        # self.get_response = get_response

    # def __call__(self, request):
        # print request.get_full_path()
        # response = self.get_response(request)

        # return response
    def process_view(self, request, view_func, view_args, view_kwargs):
        try:
            req_path = str(request.get_full_path())
            cli_ip = request.META['REMOTE_ADDR']

            RedisUtil.set(cli_ip+'_redirect', '/space/')

            url_list = RedisUtil.get(cli_ip)
            deq = deque()
            if url_list:
                for val in url_list.split(',,,')[-4:]:
                    deq.append(val)
            deq.append(req_path)
            RedisUtil.set(cli_ip, ',,,'.join(deq))
            url_list = RedisUtil.get(cli_ip).split(',,,')

            if req_path == '/space/':
                if url_list and len(url_list) >= 4:
                    if url_list[-2].split('=')[0] == '/?code':
                        if url_list[-3] == '/wechat-login/':
                            RedisUtil.set(cli_ip+'_redirect', url_list[-4])
            # if req_path.split('=')[0] == '/?code':
                # pass
            # print "|||||||||", req_path
        except Exception as e:
            print('MIDEELEWAER: ', str(e))
        return view_func(request, *view_args, **view_kwargs)
