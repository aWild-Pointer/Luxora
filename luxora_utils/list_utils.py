from django.core.paginator import Paginator


def paginate(request, list, per_page):
    """
    通用分页函数
    :param request: Django request 对象
    :param list: 需要分页的 list
    :param per_page: 每页显示的条数
    :return: 分页后的 page_obj
    """
    paginator = Paginator(list, per_page)
    page_number = request.GET.get("page", 1)
    print(page_number)
    page_obj = paginator.get_page(page_number)
    return page_obj