from django import template
from blog import models

register = template.Library()


@register.inclusion_tag("left_tag.html")
def left_panel(username):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog

    from django.db.models import Count
    category_list = models.Category.objects.filter(blog=blog).annotate(
        num=Count("article")).values("title", "num")

    tag_list = models.Tag.objects.filter(blog=blog)

    archive_list = models.Article.objects.filter(user=user_obj).extra(
        select={"ym": "DATE_FORMAT(create_time,'%%Y-%%m')"}
    ).values("ym").annotate(num=Count("nid")).values("ym", "num")

    # archive_list = models.Article.objects.filter(user=user_obj).extra(
    #     select={"ym":"DATE_FORMAT(create_time,'%%y-%%m')"}
    # ).values("ym").annotate(num=Count("nid")).values("ym","num")
    #
    # archive_list = models.Article.objects.filter(user=user_obj).extra(
    #     select={"ym":"DATE_FORMAT(create_time,'%%Y-%%m')"}
    # ).values("ym").annotate(num=Count("nid")).values("ym","num")

    return {
        "username": username,
        "category_list": category_list,
        "tag_list": tag_list,
        "archive_list": archive_list,
    }
