from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

class Teacher(models.Model):
    name = models.CharField(max_length=20)
    pic  = models.CharField(max_length=200)

    info = models.CharField(max_length=400)

    class Meta:
        db_table = u'teacher'

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
    #video_id     = models.IntegerField()

    user_name    = models.CharField(max_length=20)
    user_pic     = models.CharField(max_length=200)

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
    #teacher = models.ForeignKey(Teacher, unique=False)
    teacher_name = models.CharField(max_length=20)

    title    = models.CharField(max_length=50)
    logo_img = models.CharField(max_length=200)

    kind_str = models.CharField(max_length=50)
    tags_str = models.CharField(max_length=100)
        

    video_time = models.CharField(max_length=20, default="00:00:00")
    money      = models.FloatField(default=0.0)

    watch_num    = models.IntegerField(default=0)
    like_num     = models.IntegerField(default=0)
    share_num    = models.IntegerField(default=0)
    comments_num = models.IntegerField(default=0)

    comments     = models.ManyToManyField(Comment)
    

    info = models.CharField(max_length=400, default="")

    class Meta:
        db_table = u'video'


    
