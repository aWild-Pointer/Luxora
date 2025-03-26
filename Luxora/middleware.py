# 获取当前用户ip
# 如果使用 Django 2.0 及以上版本，建议使用基于类的中间件写法：
class LogIPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 获取请求的 IP 地址
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
        # 可能需要提取代理服务器转发的真实 IP（在有代理的情况下）
        if ip:
            ip = ip.split(',')[0]  # 获取第一个 IP 地址

        request.ip = ip  # 将 IP 地址添加到请求中
        response = self.get_response(request)  # 调用视图或下一中间件
        return response
