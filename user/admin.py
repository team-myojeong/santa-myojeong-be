from django.contrib import admin

from user import models

admin.site.register(models.User)
admin.site.register(models.UserLike)
admin.site.register(models.DefaultQuestion)
