"""zapmail URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('',views.index),
    path('index/',views.index),
    path('login/',views.login),
    path('adminhome/',views.adminhome),
    path('register/',views.register),
    path('otp_verification', views.otp_verification, name='otp_verification'),
    path('userhome/',views.userhome),
    path('admin_view_user/',views.admin_view_user),
    path('user_view_profile/',views.user_view_profile),
    path('user_feedback/',views.user_feedback),
    path('admin_feedback/',views.admin_feedback),
    path('user_complaint/',views.user_complaint),
    path('admin_complaint/',views.admin_complaint),
    path('user_manage_emailacc/',views.user_manage_emailacc),
    path('user_add_emailacc/',views.user_add_emailacc),
    path('user_delete_email/<id>',views.user_delete_email),
    path('user_edit_emailacc/<id>',views.user_edit_emailacc),
    path('user_edit_profile',views.user_edit_profile),
    path('sedd',views.sedd),
    path('summary',views.summary),
    path('reply',views.reply_email),
    path('send_sms',views.sendsms),
    path('check/<int:id>/<str:mails>', views.check, name='check'),
    # path("whatsapp-webhook/", views.whatsapp_reply, name="whatsapp_webhook"),


    # ------------------------Andriod----------------------------
    path('and_login',views.and_login),
    path('and_user_register',views.and_user_register),
    path('add_rating',views.add_rating),
    path('add_complaint',views.add_rating),
    path('view_reply',views.add_rating),


    path('manage_mail',views.manage_mail),
    path('user_viewmails',views.user_viewmails),


]
