from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password,check_password

from myadmin.models import Users,Types,Goods

# Create your views here.
# 首页
def index(request):
    data = Types.objects.filter(pid=0)

    for i in data:
        i.sub = Types.objects.filter(pid=i.id)

    goods = Goods.objects.filter()
    data.goods = goods

    cont = {'typeslist':data}
    return render(request, 'home/index.html',cont)


#  列表
def list(request,tid):
    data = Types.objects.get(id=tid)

    if data.pid == 0:
        data.sub = Types.objects.filter(pid=data.id)
        data.goods = Goods.objects.filter(tid__in=data.sub)
    else:
        data.sub = Types.objects.filter(pid=data.pid)
        data.goods = Goods.objects.filter(tid=data.id)

    cont = {'data':data}


    return render(request, 'home/list.html',cont)


#  详情
def info(request,gid):
    data = Goods.objects.get(id=gid)
    data.clicknum += 1
    data.save()

    return render(request, 'home/info.html',{'data':data})


#  注册
def register(request):
    if request.method == 'GET':
        # 返回一个注册 表单页面
        return render(request, 'home/register.html')
    elif request.method == 'POST':
        # 执行注册
        try:

            # 接受数据
            data = request.POST.dict()

            # 先检测验证码是否正确
            # if str(data['vcode']) != str(request.session['code']):
            #     return HttpResponse('<script>alert("验证码错误");history.back(-1);</script>')

            data.pop('csrfmiddlewaretoken')
            # data.pop('vcode')

            # 密码加密
            data['password'] = make_password(data['password'], None, 'pbkdf2_sha256')

            # 创建数据对象
            Users.objects.create(**data)

            return HttpResponse('<script>alert("注册成功，请登录");location.href="/login/"</script>')
        except:
            return HttpResponse('<script>alert("注册失败，请联系管理员");history.back(-1);</script>')


#  登录
def login(request):
    if request.method == "GET":
        return render(request, 'home/login.html')
    elif request.method == 'POST':
        # 接受数据
        data = request.POST.dict()
        data.pop('csrfmiddlewaretoken')

        try:
            ob = Users.objects.get(phone=data['phone'])
            # 再比对密码
            if (check_password(data['password'], ob.password)):
            # 把用户的数据信息,写入session
                request.session['VipUser'] = {'uid': ob.id, 'username': ob.username, 'pic': ob.pic}
                # 成功
                return HttpResponse('<script>alert("欢迎登录");location.href="/"</script>')
        except:
            pass

        return HttpResponse('<script>alert("账号或密码错误");history.back(-1)</script>')


# 退出登录
def logout(request):
    request.session['VipUser'] = ''

    return HttpResponse('<script>alert("退出成功,欢迎下次登录");location.href="/"</script>')


# 发送短信验证码
def sendSMS(request):
    import random
    # 接受手机号
    phone = request.GET.get('phone')

    # 生成验证码
    code = random.randint(11111, 99999)
    # 存储到session中
    request.session['code'] = code

    print(code)

    # 调用方法 发送短信验证
    from dysms import demo_sms_send
    res = demo_sms_send.send(code, phone)

    return HttpResponse(res)