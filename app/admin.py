from django.contrib import admin
from app import models

class AccountAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.Account, AccountAdmin)

class CommentAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.Comment, CommentAdmin)

class TagAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.Tag, TagAdmin)

class KindAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.Kind, KindAdmin)

class VideoAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.Video, VideoAdmin)

class OrderAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.Order, OrderAdmin)

class WatchHistoryAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.WatchHistory, WatchHistoryAdmin)

class CollectVideosAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.CollectVideos, CollectVideosAdmin)

class DataInfoAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.DataInfo, DataInfoAdmin)

class UserWatchInfoAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.UserWatchInfo, UserWatchInfoAdmin)

class UserOrderInfoAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.UserOrderInfo, UserOrderInfoAdmin)

class IndexInfoAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.IndexInfo, IndexInfoAdmin)

class OfflineAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.Offline, OfflineAdmin)

class ExamAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.Exam, ExamAdmin)

class QuestionAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.Question, QuestionAdmin)

class ChoiceAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.Choice, ChoiceAdmin)

class KaoshiAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.Kaoshi, KaoshiAdmin)

class GroupAdmin(admin.ModelAdmin):
    pass
admin.site.register(models.Group, GroupAdmin)
