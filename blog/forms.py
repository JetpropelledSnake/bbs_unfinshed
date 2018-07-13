from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from blog import models


class LoginForm(forms.Form):
    username = forms.CharField(
        label="用户名",
        min_length=3,
        max_length=12,
        error_messages={
            "required": "用户名不能为空",
            "min_length": "用户名最短3位",
            "max_length": "用户名最长12位",
        },
        widget=forms.widgets.TextInput(
            attrs={"class": "form-control c1"}
        )
    )

    password = forms.CharField(
        label="密码",
        min_length=4,
        max_length=12,
        error_messages={
            "required": "用户名不能为空",
            "min_length": "用户密码最短4位",
            "max_length": "用户密码最长12位",
        },
        widget=forms.widgets.PasswordInput(
            attrs={"class": "form-control"}
        )
    )


class RegForm(forms.Form):
    username = forms.CharField(
        label="用户名",
        min_length=3,
        max_length=12,
        error_messages={
            "required": "用户名不能为空",
            "min_length": "密码最短4位",
            "max_length": "密码最长12位"
        },
        widget=forms.widgets.TextInput(
            attrs={"class": "form-control"}
        )
    )

    password = forms.CharField(
        label="密码",
        min_length=4,
        max_length=12,
        error_messages={
            "required": "密码不能为空",
            "min_length": "密码最短4位",
            "max_length": "密码最长12位"
        },
        widget=forms.widgets.PasswordInput(
            attrs={"class": "form-control"}
        )
    )

    re_password = forms.CharField(
        label="确认密码",
        min_length=4,
        max_length=12,
        error_messages={
            "required": "密码不能为空",
            "min_length": "密码最短4位",
            "max_length": "密码最长12位",
        },
        widget=forms.widgets.PasswordInput(
            attrs={"class": "form-control"}
        )
    )

    phone = forms.CharField(
        label="手机号",
        min_length=11,
        max_length=11,
        validators=[
            RegexValidator(r'^\d{11}$', "手机号必须是数字"),
            RegexValidator(r'^1[356789][0-9]{9}$', "手机号格式不正确")
        ],
        error_messages={
            "required": "手机号不能为空",
            "min_length": "手机号码11位",
            "max_length": "手机号码11位",
        },
        widget=forms.widgets.TextInput(
            attrs={"class": "form-control"}
        )
    )

    # 局部钩子
    def clean_username(self):
        value = self.cleaned_data.get("username", "")
        if "金瓶梅" in value:
            raise ValidationError("金瓶梅是敏感字")
        elif models.UserInfo.objects.filter(username=value):
            raise ValidationError("该用户已经注册")

    # 全局钩子
    def clean(self):
        pwd = self.cleaned_data.get("password", "")
        re_pwd = self.cleaned_data.get("re_password", "")

        if re_pwd and pwd == re_pwd:
            return self.cleaned_data
        else:
            err_msg = "两次输入的密码不一致"
            self.add_error("re_password", err_msg)
            raise ValidationError(err_msg)
