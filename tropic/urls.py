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
from django.views.generic.base import RedirectView
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/images/favicon.ico')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^index/',     'app.show.index'),
    url(r'^mobile-index/',     'app.show.mobile_index'),
    url(r'^$',          'app.show.index'),

    url(r'^videos/$',   'app.show.videos_ui'),
    url(r'^search/$',   'app.show.search_result'),

    url(r'^login/',     'app.views.login_ui'),
    url(r'^login-do/',  'app.views.login_do'),
    url(r'^logout/',    'app.views.log_out'),

    url(r'^register/',  'app.views.wechat_login'),


    url(r'^upload-course-post/', 'app.db_pro.upload_course_post'),
    url(r'^update-course-post/', 'app.db_pro.update_course_post'),
    url(r'^index-info-post/',    'app.db_pro.index_info_post'),
    url(r'^uptoken/',       'app.qiniu_pro.uptoken'),

    url(r'^update-course/$',        'app.videomanage.update_course_ui'),
    url(r'^videos/manage/$',        'app.videomanage.videos_manage'),
    url(r'^manage/index-info/$',    'app.videomanage.index_info'),
    url(r'^manage/$',               'app.videomanage.videos_manage'),
    url(r'^delete-video/$',         'app.videomanage.delete_video'),
    url(r'^delete-intrestvideo/$',  'app.videomanage.delete_intrestvideo'),
    url(r'^add-intrestvideo/$',     'app.videomanage.add_intrestvideo'),
    url(r'^upload/course/$',        'app.videomanage.upload_course_ui'),

    url(r'^videos/data-manage/$',        'app.videomanage.videos_data'),


    url(r'^pay/$',          'app.playui.pay_ui'),
    url(r'^ready-pay/$',    'app.playui.ready_pay'),
    url(r'^videos/play/$',  'app.playui.play_ui'),
    url(r'^voteup/$',       'app.playui.voteup'),
    url(r'^collect/$',      'app.playui.collect'),
    url(r'^add-comment/$',  'app.playui.comment_add'),
    url(r'^del-comment/$',  'app.playui.comment_delete'),

    url(r'^add-watch-history/$',  'app.playui.watch_history_add'),


    url(r'^space/$',                'app.space.space_index'),
    url(r'^space/index/$',          'app.space.space_index'),
    url(r'^space/collect/$',        'app.space.space_collect'),
    url(r'^space/paid/$',           'app.space.space_paid'),
    url(r'^space/shopping-cart/$',  'app.space.space_shopping_cart'),

    url(r'^user/setprofile/$',      'app.space.setprofile'),
    url(r'^user/setavator/$',       'app.space.setavator'),
    url(r'^user/setbindsns/$',      'app.space.setbindsns'),
    url(r'^user/random-pic/$',      'app.space.random_pic'),

    url(r'^del-history/$',          'app.space.history_del'),
    url(r'^del-collect/$',          'app.space.collect_del'),
    url(r'^del-unpay/$',            'app.space.unpay_del'),

    url(r'^upload-userpic/$',       'app.space.update_pic'),
    url(r'^user/update-profile/$',  'app.space.update_profile'),


    url(r'^wechat-login/$', 'app.views.wechat_login'),
    url(r'^wechat-share/$', 'app.views.wechat_share'),


    url(r'^wechat-pay/$', 'app.wxpay.payback'),
    url(r'^ajax_check/$', 'app.wxpay.check_pay'),
    url(r'^pay_result/$', 'app.db_pro.pay_result'),

    url(r'^paydetail/$', 'app.db_pro.paydetail'),

    url(r'^download/$', 'app.views.download'),

    url(r'^alipay/$', 'app.ali_pay.alipay'),
    url(r'^alipay_notify/$', 'app.ali_pay.alipay_notify'),
    url(r'^alipay_return/$', 'app.ali_pay.alipay_return'),
    url(r'^info_wait/', 'app.db_pro.info_wait'),
    url(r'^test/', 'app.views.test')
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
