from common import RedisUtil
from collections import deque
class TropicMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        try:
            req_path = str(request.get_full_path())
            cli_ip = request.META['REMOTE_ADDR']

            RedisUtil.set(cli_ip+'_redirect', '/space/')

            url_list = RedisUtil.get(cli_ip)
            deq = deque()
            if url_list:
                for val in url_list.split(',,,')[-5:]:
                    deq.append(val)
            deq.append(req_path)
            RedisUtil.set(cli_ip, ',,,'.join(deq))
            url_list = RedisUtil.get(cli_ip).split(',,,')
            print(url_list)

            if req_path == '/space/':
                if url_list and len(url_list) >= 3:
                    for ii in range(len(url_list)):
                        i = len(url_list) - ii - 1
                        if '/wechat-login' in url_list[i]:
                            for jj in range(i):
                                j = i - jj - 1
                                if '/videos' in url_list[j]:
                                    RedisUtil.set(cli_ip+'_redirect', url_list[j])
                                    break
                            break

            # if req_path == '/space/':
                # if url_list and len(url_list) >= 4:
                    # if '/wechat-login/' in url_list[-2] or '/?code' in url_list[-2]:
                        # if '/wechat-login/' in url_list[-3]:
                            # RedisUtil.set(cli_ip+'_redirect', url_list[-4])
        except Exception as e:
            print('MIDEELEWAER: ', str(e))
        return view_func(request, *view_args, **view_kwargs)
