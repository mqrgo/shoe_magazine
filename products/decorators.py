from django.http import HttpResponseForbidden

def is_user_staff(view):
    def inner(request, *ar, **kw):
        if not request.user.is_staff:
            return HttpResponseForbidden('Страницы не существует')
        return view(request, *ar, **kw)
    return inner