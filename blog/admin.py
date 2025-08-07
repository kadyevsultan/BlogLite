from django.contrib import admin

from blog.models import Post, SubPost

# Register your models here.
admin.site.register(Post)
admin.site.register(SubPost)