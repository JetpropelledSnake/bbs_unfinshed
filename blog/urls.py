from django.conf.urls import url
from blog import views


urlpatterns = [
    url(r'(.*)/article/(\d+)/$', views.article_detail),
    url(r'(.*)/(category|tag|archive)/(.*)/$', views.home),
    url(r'(.*)/$', views.home),
]