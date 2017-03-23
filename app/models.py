#!/usr/bin/python
#-*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

class Account(models.Model):
    user = models.OneToOneField(User, unique=True, verbose_name='user_account')

    wx_unionid = models.CharField(max_length=100)
    wx_pc_openid = models.CharField(max_length=100)
    wx_wx_openid = models.CharField(max_length=100)

    user_pic = models.CharField(max_length=200)
    nickname = models.CharField(max_length=20)

    phone    = models.CharField(max_length=20)
    sex      = models.IntegerField(default=-1)
    info     = models.CharField(max_length=400)

    class Meta:
        db_table = u'account'

class QiniuFile(models.Model):
    title  = models.CharField(max_length=100)
    key    = models.CharField(max_length=200)
    bucket = models.CharField(max_length=50)
    domain = models.CharField(max_length=100)

    need_authority = models.BooleanField()

    size_int = models.IntegerField(default=0)
    size_str = models.CharField(max_length=50, default="0")

    video_time = models.IntegerField(default=0)

    chapter_num = models.IntegerField(default=-1)
    chapter_name = models.CharField(max_length=128, default="")

    release_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = u'qiniufile'

class Comment(models.Model):
    user = models.ForeignKey(Account, unique=False)

    def __get_user_pic(self):
        try:
            if self.user != None:
                return self.user.user_pic
        except Exception, e:
            print str(e)

        return None

    def __get_user_name(self):
        try:
            if self.user != None:
                return self.user.nickname
        except Exception, e:
            print str(e)

        return None

    user_name = property(__get_user_name)
    user_pic  = property(__get_user_pic)

    follow_id    = models.IntegerField()

    comment      = models.CharField(max_length=1024)
    release_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = u'comment'

class Tag(models.Model):
    name = models.CharField(max_length=20)
    class Meta:
        db_table = u'tag'


class Kind(models.Model):
    name = models.CharField(max_length=20)
    class Meta:
        db_table = u'kind'

class Video(models.Model):
    teacher = models.ForeignKey(Account, unique=False)
    def __get_teacher_name(self):
        try:
            if self.teacher != None:
                return self.teacher.nickname
        except Exception, e:
            print str(e)

        return None

    def __get_teacher_pic(self):
        try:
            if self.teacher != None:
                return self.teacher.user_pic
        except Exception, e:
            print str(e)

        return None

    def __get_teacher_info(self):
        try:
            if self.teacher != None:
                return self.teacher.info
        except Exception, e:
            print str(e)

        return None
    teacher_name = property(__get_teacher_name)
    teacher_pic  = property(__get_teacher_pic)
    teacher_info = property(__get_teacher_info)

    is_reverse = models.IntegerField(default=0)
    is_customize = models.IntegerField(default=0)

    title    = models.CharField(max_length=50)
    logo_img = models.CharField(max_length=200)

    kind_str = models.CharField(max_length=50)
    tags_str = models.CharField(max_length=100)

    money = models.FloatField(default=0.0)

    files = models.ManyToManyField(QiniuFile)
    def __get_files_num(self):
        try:
            if self.files != None:
                return self.files.count()
        except Exception, e:
            print str(e)

        return 0

    files_num = property(__get_files_num)


    watch_num    = models.IntegerField(default=0)
    like_num     = models.IntegerField(default=0)
    share_num    = models.IntegerField(default=0)

    comments     = models.ManyToManyField(Comment)

    def __get_comments_num(self):
        try:
            if self.comments != None:
                return self.comments.count()
        except Exception, e:
            print str(e)

        return 0
    comments_num = property(__get_comments_num)

    info = models.CharField(max_length=400, default="")
    valid_day = models.IntegerField(default=-1)

    release_date = models.DateTimeField(auto_now=False)
    class Meta:
        db_table = u'video'



class Order(models.Model):
    # -1: invalidate, 1: unpay, 2: paid,
    pay_state = models.IntegerField()

    order_num = models.CharField(max_length=32)
    name = models.CharField(max_length=20)
    wxpay_qrcode = models.CharField(max_length=200)
    pic  = models.CharField(max_length=200)

    account = models.ForeignKey(Account)
    order_valid_day = models.IntegerField(default=-1)

    video  = models.ForeignKey(Video)
    def __get_list_num(self):
        try:
            if self.video != None:
                return self.video.files_num
        except Exception, e:
            print str(e)

        return 0
    videos_num = property(__get_list_num)
    price   = models.FloatField()

    release_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = u'order'

class WatchHistory(models.Model):
    account = models.ForeignKey(Account)
    videos  = models.ManyToManyField(Video)
    def __get_list_num(self):
        try:
            if self.videos != None:
                return self.videos.count()
        except Exception, e:
            print str(e)

        return 0
    videos_num = property(__get_list_num)
    class Meta:
        db_table = u'watch_history'

class CollectVideos(models.Model):
    account = models.ForeignKey(Account)
    videos = models.ManyToManyField(Video)
    def __get_list_num(self):
        try:
            if self.videos != None:
                return self.videos.count()
        except Exception, e:
            print str(e)

        return 0
    videos_num = property(__get_list_num)
    class Meta:
        db_table = u'star_videos'


class IntrestVideos(models.Model):
    video = models.ForeignKey(Video)
    release_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = u'intrest_videos'

class DataInfo(models.Model):
    title     = models.CharField(max_length=100, unique=True)
    filename  = models.CharField(max_length=100)
    modify_datetime = models.CharField(max_length=100)

    class Meta:
        db_table = u'data_info'

class UserWatchInfo(models.Model):
    account = models.ForeignKey(Account)
    video   = models.ForeignKey(Video)

    # if pc login, flag=1, else 0
    pc_flag   = models.IntegerField()

    release_date = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = u'user_watch_info'

class UserOrderInfo(models.Model):
    account = models.ForeignKey(Account)
    order   = models.ForeignKey(Order)
    price   = models.FloatField()
    pay_state = models.IntegerField()

    # if pc login, flag=1, else 0
    pc_flag   = models.IntegerField()

    release_date = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = u'user_order_info'

class IndexInfo(models.Model):
    img_num = models.IntegerField()
    img_path = models.CharField(max_length=200)
    jump_url = models.CharField(max_length=200)

    release_date = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = u'index_info'

class Offline(models.Model):
    title       = models.CharField(max_length=200)
    status      = models.CharField(max_length=20)
    img_path    = models.CharField(max_length=200)

    short_info  = models.CharField(max_length=1000)
    start_time  = models.CharField(max_length=100)
    course_time = models.CharField(max_length=100)
    price       = models.CharField(max_length=100)


    detail_intro = models.CharField(max_length=1000)
    course_intro = models.CharField(max_length=1000)
    outlet_intro = models.CharField(max_length=1000)
    prelearn_intro = models.CharField(max_length=1000)

    release_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = u'offline'

class Choice(models.Model):
    correct_flag = models.BooleanField(default=False)
    choice_info  = models.CharField(max_length=1000)
    img_path     = models.CharField(max_length=200)
    class Meta:
        db_table = u'choice'

class Question(models.Model):
    kind  = models.IntegerField()
    score = models.DecimalField(max_digits=5, decimal_places=2)
    question_info = models.CharField(max_length=1000)
    img_path      = models.CharField(max_length=200)

    choices   = models.ManyToManyField(Choice)
    def __get_choices_num(self):
        try:
            if self.choices != None:
                return self.choices.count()
        except Exception, e:
            print str(e)
        return 0

    choices_num = property(__get_choices_num)
    class Meta:
        db_table = u'question'

class Group(models.Model):
    group_name   = models.CharField(max_length=100)
    detail_intro = models.CharField(max_length=1000)
    img_path     = models.CharField(max_length=200)

    allow_accounts = models.ManyToManyField(Account)
    def __get_allow_accounts_num(self):
        try:
            if self.allow_accounts != None:
                return self.allow_accounts.count()
        except Exception, e:
            print str(e)
        return 0
    allow_accounts_num = property(__get_allow_accounts_num)

    release_date = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = u'groups'

class Exam(models.Model):
    title       = models.CharField(max_length=100)
    detail_intro = models.CharField(max_length=1000)
    img_path    = models.CharField(max_length=200)

    start_time  = models.CharField(max_length=100)
    end_time    = models.CharField(max_length=100)

    exam_mins   = models.IntegerField()


    exam_excel_content = models.CharField(max_length=1000000)
    exam_excel_file = models.CharField(max_length=200)

    # questions   = models.ManyToManyField(Question)
    # def __get_questions_num(self):
        # try:
            # if self.questions != None:
                # return self.questions.count()
        # except Exception, e:
            # print str(e)
        # return 0
    # questions_num = property(__get_questions_num)

    single_score = models.DecimalField(max_digits=5, decimal_places=2)
    single_num   = models.IntegerField()
    multi_score  = models.DecimalField(max_digits=5, decimal_places=2)
    multi_num    = models.IntegerField()

    max_retry_num = models.IntegerField(default=2)
    # allow_accounts = models.ManyToManyField(Account)

    group = models.ManyToManyField(Group)
    def __get_allow_accounts_num(self):
        try:
            if len(self.group.all()) > 0:
                return self.group.all()[0].allow_accounts_num
        except Exception, e:
            print str(e)
        return 0

    def __get_allow_group_name(self):
        try:
            if len(self.group.all()) > 0:
                return self.group.all()[0].group_name
        except Exception, e:
            print str(e)
        return u"所有人员"

    allow_accounts_num = property(__get_allow_accounts_num)
    allow_group_name = property(__get_allow_group_name)

    public_flag = models.BooleanField()

    total_score = models.DecimalField(max_digits=5, decimal_places=2)

    release_date = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = u'exam'

class Kaoshi(models.Model):
    exam = models.ForeignKey(Exam, unique=False)
    account = models.ForeignKey(Account, unique=False)

    submit_flag = models.BooleanField(default=False)
    submit_use_time = models.IntegerField(default=0)

    single_q = models.CharField(max_length=500)
    single_answer = models.CharField(max_length=500)
    multi_q  = models.CharField(max_length=500)
    multi_answer  = models.CharField(max_length=500)

    score = models.DecimalField(max_digits=5, decimal_places=2, default=-1)

    use_time = models.CharField(max_length=50, default="00:00:00")
    total_q_num = models.IntegerField(default=0)
    correct_q_num = models.IntegerField(default=0)
    submit_answer = models.CharField(max_length=10240, default="")

    release_date = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = u'kaoshi'
