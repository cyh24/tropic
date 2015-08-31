from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

class Account(models.Model):
    user = models.OneToOneField(User, unique=True, verbose_name='user_account')

    openid   = models.CharField(max_length=100)


    user_pic = models.CharField(max_length=200)
    nickname = models.CharField(max_length=20)

    phone    = models.CharField(max_length=20)
    sex      = models.IntegerField(default=-1)
    info     = models.CharField(max_length=400)

    class Meta:
        db_table = u'account'

class QiniuFile(models.Model):
    key    = models.CharField(max_length=200)
    bucket = models.CharField(max_length=50)
    domain = models.CharField(max_length=100)

    need_authority = models.BooleanField()

    size_int = models.IntegerField(default=0)
    size_str = models.CharField(max_length=50, default="0")

    release_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

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

    comment      = models.CharField(max_length=2048)
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

class Video(QiniuFile):
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

    teacher_name = property(__get_teacher_name)
    teacher_pic  = property(__get_teacher_pic)


    title    = models.CharField(max_length=50)
    logo_img = models.CharField(max_length=200)

    kind_str = models.CharField(max_length=50)
    tags_str = models.CharField(max_length=100)
        

    video_time = models.CharField(max_length=20, default="00:00:00")
    money      = models.FloatField(default=0.0)

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

    class Meta:
        db_table = u'video'


    
