from django.shortcuts import render, HttpResponse

# Create your views here.
from rbac.models import User
from rbac.service.permissions import initial_session


def login(request):
    if request.method == 'POST':
        user = request.POST.get("user")
        pwd = request.POST.get("pwd")

        user = User.objects.filter(name=user, pwd=pwd).first()

        if user:
            # 登录成功
            request.session["user_id"] = user.pk
            # 注册权限到session中
            initial_session(user, request)
            return HttpResponse("登录成功")

    return render(request, "login.html", locals())
