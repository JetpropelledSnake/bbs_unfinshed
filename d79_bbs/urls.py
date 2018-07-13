"""d79_bbs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from blog import views
from django.views.static import serve
from django.conf import settings
from blog import urls as blog_urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/', views.login),
    url(r'^index/', views.index),
    url(r'^v_code/', views.v_code),
    url(r'^login2/', views.login2),
    # 极验科技 获取验证码的url
    url(r'^pcgetcaptcha/', views.pcgetcaptcha),

    url(r'^reg/$', views.reg),


    url(r'logout/', views.logout),
    url(r'^blog/', include(blog_urls)),

    url(r'media/(?P<path>.*)$', serve, {"document_root":settings.MEDIA_ROOT}),

    url(r'test/', views.test),
    url(r'updown/', views.updown),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
