from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from functools import wraps

def role_required(required_role):
    """
    限制角色访问，并自动跳转用户所属角色首页
    :param required_role: 必须角色（如 'manager', 'reception', 'cleaner'）
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user_role = getattr(request.user, 'role', None)

            if user_role != required_role:
                # 角色不匹配，自动跳转用户自己的首页
                if user_role == 'manager':
                    return redirect('/manager')
                elif user_role == 'reception':
                    return redirect('/reception')
                elif user_role == 'cleaner':
                    return redirect('/cleaner')
                else:
                    # 如果无角色或未知角色，直接 403
                    raise PermissionDenied("无权限访问")
            # 角色匹配，正常执行视图
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
