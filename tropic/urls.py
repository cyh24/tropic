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

    url(r'^videos/data-manage/$',   'app.videomanage.videos_data'),
    url(r'^manage/order-manage/$',  'app.videomanage.order_manage'),
    url(r'^modify-order-post/',     'app.db_pro.modify_order_post'),

    url(r'^modify-card-order-post/',     'app.db_pro.modify_card_order_post'),

    url(r'^manage/superuser-manage', 'app.superuser.superuser_manage'),
    url(r'^modify-superuser-post/',     'app.db_pro.modify_superuser_post'),


    url(r'^pay/$',          'app.playui.pay_ui'),
    url(r'^ready-pay/$',    'app.playui.ready_pay'),
    url(r'^videos/play/$',  'app.playui.play_ui'),
    url(r'^videos/play_auth/$',  'app.playui.play_ui_auth'),
    url(r'^voteup/$',       'app.playui.voteup'),
    url(r'^collect/$',      'app.playui.collect'),
    url(r'^add-comment/$',  'app.playui.comment_add'),
    url(r'^del-comment/$',  'app.playui.comment_delete'),

    url(r'^add-watch-history/$',  'app.playui.watch_history_add'),

    url(r'^card-pay/$',          'app.card_pro.card_pay_ui'),
    url(r'^card-ready-pay/$',    'app.card_pro.card_ready_pay'),
    url(r'^manage/card-order-manage/$',  'app.card_pro.card_order_manage'),


    url(r'^space/$',                'app.space.space_index'),
    url(r'^space/index/$',          'app.space.space_index'),
    url(r'^space/collect/$',        'app.space.space_collect'),
    url(r'^space/paid/$',           'app.space.space_paid'),
    url(r'^space/customize/$',      'app.space.space_customize'),
    url(r'^space/groups/$',         'app.space.space_groups'),
    url(r'^space/cards/$',          'app.space.space_cards'),
    url(r'^space/apply_group/$',   'app.space.space_apply_group'),
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

    url(r'^offline/', 'app.offline_pro.offline'),
    url(r'^offline-detail/$', 'app.offline_pro.offline_detail'),
    url(r'^offline-upload/$', 'app.offline_pro.offline_upload'),
    url(r'^offline-upload-post/$', 'app.offline_pro.offline_upload_post'),
    url(r'^offline-update/$', 'app.offline_pro.offline_update'),
    url(r'^offline-update-post/$', 'app.offline_pro.offline_update_post'),
    url(r'^offline-delete/$', 'app.offline_pro.offline_delete'),
    url(r'^offline-manage/$', 'app.offline_pro.offline_manage'),

    url(r'^create-exam/$', 'app.exam_pro.createExam'),
    url(r'^exam-upload-post/$', 'app.exam_pro.exam_upload_post'),
    url(r'^exam-update-post/$', 'app.exam_pro.exam_update_post'),
    url(r'^upload-exam/$', 'app.exam_pro.upload_exam'),
    url(r'^update-exam/$', 'app.exam_pro.update_exam'),
    url(r'^delete-exam/$', 'app.exam_pro.delete_exam'),
    url(r'^show-exam/$', 'app.exam_pro.showExam'),

    url(r'^group-create/$', 'app.exam_pro.group_create'),
    url(r'^group-update/$', 'app.exam_pro.group_update'),
    url(r'^group-delete/$', 'app.exam_pro.group_delete'),
    url(r'^group-create-post/$', 'app.exam_pro.group_create_post'),
    url(r'^group-update-post/$', 'app.exam_pro.group_update_post'),

    url(r'^kaoshi/groups/$', 'app.exam_pro.kaoshi_groups'),
    url(r'^kaoshi/exams/$', 'app.exam_pro.kaoshi_exams'),

    url(r'^cards/$', 'app.card_pro.cards'),
    url(r'^card-create/$', 'app.card_pro.card_create'),
    url(r'^card-update/$', 'app.card_pro.card_update'),
    url(r'^card-delete/$', 'app.card_pro.card_delete'),
    url(r'^card-create-post/$', 'app.card_pro.card_create_post'),
    url(r'^card-update-post/$', 'app.card_pro.card_update_post'),

    url(r'^membership-card/$', 'app.card_pro.membership_card'),

    url(r'^exam/$', 'app.exam_pro.goto_exam'),
    url(r'^submit-exam-post/$', 'app.exam_pro.submit_exam_post'),
    url(r'^contestRoom/$', 'app.exam_pro.contestRoom'),
    url(r'^examSummary/$', 'app.exam_pro.exam_summary'),
    url(r'^onlineExam/question$', 'app.exam_pro.single_select'),

    url(r'^management/exam-data/$', 'app.data_manage.exam_data'),

    url(r'^banji-course/$', 'app.banji.banji_course'),
    url(r'^banji/application/$', 'app.banji.application'),
    url(r'^banji/banji-list/$', 'app.banji.banji_list'),
    url(r'^modify-application-post/',     'app.db_pro.modify_application_post'),
    url(r'^banji/courses/$', 'app.banji.courses'),
    url(r'^banji/upload-banji-course/$', 'app.banji.upload_banji_course_ui'),
    url(r'^banji/upload-banji-course-post/', 'app.banji.upload_banji_course_post'),
    url(r'^banji/user_progress/$', 'app.banji.user_progress'),

    url(r'^watch-status/update/', 'app.watch_status.watch_status_update'),

    url(r'^test_2/', 'app.views.test_2'),
    url(r'^test/', 'app.views.test')
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
