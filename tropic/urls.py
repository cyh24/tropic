"""tropic URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^index/', 'app.views.index'),
    url(r'^$', 'app.views.index'),

    url(r'^login/', 'app.views.login_ui'),
    url(r'^login-do/', 'app.views.login_do'),
    url(r'^logout/', 'app.views.log_out'),

    url(r'^upload/', 'app.views.upload_ui'),
    url(r'^upload-post/', 'app.db_pro.upload_post'),
    url(r'^uptoken/', 'app.qiniu_pro.uptoken'),

    url(r'^videos/$', 'app.views.videos_ui'),
    url(r'^videos/play/$', 'app.views.play_ui'),
    url(r'^videos/manage/$', 'app.views.videos_manage'),

    url(r'^space/$', 'app.views.space_index'),
    url(r'^space/index/$', 'app.views.space_index'),

    url(r'^user/setprofile/$', 'app.views.setprofile'),
    url(r'^user/setavator/$', 'app.views.setavator'),
    url(r'^user/setbindsns/$', 'app.views.setbindsns'),

    url(r'^voteup/$', 'app.views.voteup'),
    url(r'^collect/$', 'app.views.collect'),
    url(r'^search/$', 'app.views.search_result'),
    url(r'^add-comment/$', 'app.views.comment_add'),

    url(r'^wechat-login/$', 'app.views.wechat_login'), 
    url(r'^wechat-share/$', 'app.views.wechat_share'), 

    url(r'^pay/$', 'app.views.pay_ui'), 

    url(r'^test/', 'app.views.test')
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
