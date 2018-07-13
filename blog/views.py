from django.shortcuts import render, HttpResponse, redirect
from blog import forms, models
from django.contrib import auth
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from geetest import GeetestLib
import logging

logger = logging.getLogger(__name__)
collect_logger = logging.getLogger("collect")

pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"


# 滑动验证码加载需要的视图函数
def pcgetcaptcha(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)


def login(request):
    form_obj = forms.LoginForm()
    if request.method == "POST":
        ret = {"code": 0}
        username = request.POST.get("username")
        password = request.POST.get("password")
        v_code = request.POST.get("v_code", "")

        if v_code.upper() == request.session.get("v_code", ""):
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                ret["data"] = "/index/"
            else:
                ret["code"] = 1
                ret["data"] = "用户名密码错误"
        else:
            ret["code"] = 1
            ret["data"] = "验证码错误"
        return JsonResponse(ret)

    return render(request, "login.html", {"form_obj": form_obj})


def login2(request):
    form_obj = forms.LoginForm()
    if request.method == "POST":
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, "")
        validate = request.POST.get(gt.FN_VALIDATE, "")
        seccode = request.POST.get(gt.FN_SECCODE, "")
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        user_id = request.session["user_id"]
        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)

        if result:
            ret = {"code": 0}
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = auth.authenticate(username=username, password=password)
            if user:
                ret["data"] = "/index/"
            else:
                ret["code"] = 1
                ret["data"] = "用户名或者密码错误"

            return JsonResponse(ret)

    return render(request, "login2.html", {"form_obj": form_obj})


@never_cache
def v_code(request):
    from PIL import Image, ImageDraw, ImageFont
    import random

    def get_color():
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    img_obg = Image.new(
        "RGB",
        (250, 35),
        color=get_color()
    )

    draw_obj = ImageDraw.Draw(img_obg)

    font_obj = ImageFont.truetype("static/font/kumo.ttf", size=28)

    tmp_list = []
    for i in range(5):
        n = str(random.randint(0, 9))
        lo = chr(random.randint(97, 122))
        u = chr(random.randint(65, 90))
        r = random.choice([n, lo, u])
        tmp_list.append(r)
        draw_obj.text(
            (i * 48 + 20, 0),
            r,
            get_color(),
            font=font_obj
        )

    v_code_str = "".join(tmp_list)

    request.session["v_code"] = v_code_str.upper()

    # width = 250
    # height = 35
    # for i in range(2):
    #     x1 = random.randint(0, width)
    #     x2 = random.randint(0, width)
    #     y1 = random.randint(0, height)
    #     y2 = random.randint(0, height)
    #
    # for i in range(2):
    #     draw_obj.point([random.randint(0, width), random.randint(0, height)], fill=get_color())
    #     x = random.randint(0, width)
    #     y = random.randint(0, height)
    #     draw_obj.arc((x, y, x + 4, y + 4), 0, 90, fill=get_color())

    # with open("xx.png","wb") as f:
    #     img_obg.save(f, "png")
    # print("验证码图片已经生成")
    # with open("xx.png","rb") as f:
    #     return HttpResponse(data,content_type="image/png")

    from io import BytesIO
    tmp = BytesIO()
    img_obg.save(tmp, "png")

    data = tmp.getvalue()
    return HttpResponse(data, content_type="image/png")


def index(request):
    data = models.Article.objects.all()
    return render(request, "index.html", {"article_list": data})


def reg(request):
    logger.info("小伙子，又来了！")
    collect_logger.info("小伙子，又走了！")

    if request.method == "POST":
        ret = {"code": 0}
        form_obj = forms.RegForm(request.POST)
        logger.debug(request.FILES)

        if form_obj.is_valid():
            logger.debug(form_obj.cleaned_data)
            avatar_obj = request.FILES.get("avatar")

            form_obj.cleaned_data.pop("re_password", "")
            models.UserInfo.objects.create_user(
                **form_obj.cleaned_data,
                avatar=avatar_obj
            )
            ret["data"] = "/login/"
        else:
            ret["code"] = 1
            ret["data"] = form_obj.errors

        return JsonResponse(ret)

    form_obj = forms.RegForm()
    return render(request, "reg.html", {"form_obj": form_obj})


def logout(request):
    auth.logout(request)
    return redirect("/login/")


def home(request, username, *args):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    if not user_obj:
        return HttpResponse("404")
    else:
        blog = user_obj.blog

    if not args:
        data = models.Article.objects.filter(user__username=username)
    else:
        if args[0] == "category":
            data = models.Article.objects.filter(user=user_obj).filter(category__title=args[1])
        elif args[0] == "tag":
            data = models.Article.objects.filter(user=user_obj).filter(tag__tilte=args[1])
        else:
            year, month = args[1].split("-")
            data = models.Article.objects.filter(user=user_obj).filter(create_time__year=year, create_time__month=month)

    total_num = data.count()
    current_page = request.GET.get("page")
    url_prefix = request.path_info.strip("/")

    from utils import mypage
    page_obj = mypage.Page(total_num, current_page, url_prefix, per_page=1)
    data = data[page_obj.data_start:page_obj.data_end]
    page_html = page_obj.page_html()

    return render(request, "home.html", {
        "username": username,
        "blog": blog,
        "article_list": data,
        "page_html": page_html
    })


def get_panel(username):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    if not user_obj:
        return HttpResponse("404")
    else:
        blog = user_obj.blog

    from django.db.models import Count
    category_list = models.Category.objects.filter(blog=blog).annotate(num=Count("article")).values("title", "num")
    tag_list = models.Tag.objects.filter(blog=blog)
    archive_list = models.Article.objects.filter(user=user_obj).extra(
        select={"ym": "DATE_FORMAT(create_time,'%%Y-%%m')"}
    ).values("ym").annotate(num=Count("nid")).values("ym", "num")

    return user_obj, blog, category_list, tag_list, archive_list


def article_detail(request, username, article_id):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    if not user_obj:
        return HttpResponse("404")
    else:
        blog = user_obj.blog

    article_obj = models.Article.objects.filter(pk=article_id).first()
    comment_list = models.Comment.objects.filter(article_id=article_id)

    return render(
        request,
        "article_detail.html",
        {
            "username": username,
            "blog": blog,
            "article": article_obj,
            "comment_list": comment_list
        }
    )


def test(request):
    return render(request, "test.html", {"name": "dsb", "age": 18})


def updown(request):
    ret = {"code": 0}
    is_up = request.POST.get("is_up")
    article_id = request.POST.get("article_id")
    user_id = request.POST.get("user_id")

    is_up = True if is_up.upper() == "TRUE" else False

    if models.Article.objects.filter(nid=article_id, user_id=user_id):
        ret["code"] = 1
        ret["data"] = "不可以点赞自己的博客" if is_up else "不可以踩自己的博客"
    else:
        is_exist = models.ArticleUpDown.objects.filter(user_id=user_id, article_id=article_id).first()
        if is_exist:
            ret["code"] = 1
            ret["data"] = "已经点赞过" if is_exist.is_up else "已经反对过"
        else:
            from django.db import transaction
            from django.db.models import F
            with transaction.atomic():
                models.ArticleUpDown.objects.create(
                    is_up=is_up,
                    article_id=article_id,
                    user_id=user_id
                )

                if is_up:
                    models.Article.objects.filter(nid=article_id).update(up_count=F("up_count") + 1)
                else:
                    models.Article.objects.filter(nid=article_id).update(down_count=F("down_count") + 1)
            ret["data"] = "点赞！" if is_up else "反对！"

    return JsonResponse(ret)
