from django.contrib import admin
from .models import *

# Register Lector model
class LectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'surname', 'email', 'lector_id','password')  # Fields to display in the admin list view
    search_fields = ('name', 'surname', 'email', 'lector_id','password')  # Fields to search in the admin

# Register Student model
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'surname', 'email', 'student_id','password')  # Fields to display in the admin list view
    search_fields = ('name', 'surname', 'email', 'student_id','password')  # Fields to search in the admin

# Register models with custom admin options
admin.site.register(Lector, LectorAdmin)
admin.site.register(Student, StudentAdmin)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'lector')
    filter_horizontal = ('students',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('group', 'author', 'created_at')
    readonly_fields = ('created_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at')
    readonly_fields = ('created_at',)

@admin.register(GroupChatMessage)
class GroupChatMessageAdmin(admin.ModelAdmin):
    list_display = ('group', 'sender', 'timestamp')
    readonly_fields = ('timestamp',)

@admin.register(PrivateChat)
class PrivateChatAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'timestamp')
    readonly_fields = ('timestamp',)

@admin.register(Point)
class PointAdmin(admin.ModelAdmin):
    list_display = ('student', 'group', 'lector', 'value', 'point_type', 'created_at')
    list_filter = ('point_type', 'group', 'lector')
    search_fields = ('student__name', 'lector__name')
    ordering = ('-created_at',)    
