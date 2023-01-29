from django.contrib import admin

from .models import Post, PostTransaction

# Register your models here.

admin.site.register(Post)
admin.site.register(PostTransaction)
