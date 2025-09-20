# home/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Zone, Official, NewsCategory, NewsEvent, TYMAImage, ContactSubmission, NewsletterSubscriber

# Custom User Admin
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_verified')
    list_filter = ('is_staff', 'is_superuser', 'is_verified')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

# Zone Admin
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

# Official Admin
class OfficialAdmin(admin.ModelAdmin):
    list_display = ('name', 'official_type', 'position', 'zone', 'is_active')
    list_filter = ('official_type', 'position', 'zone', 'is_active')
    search_fields = ('name', 'email', 'phone')
    raw_id_fields = ('user',)
    list_editable = ('is_active', 'position')

# News Category Admin
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

# News Event Admin
class NewsEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'news_type', 'published_at', 'is_featured', 'views')
    list_filter = ('news_type', 'categories', 'is_featured', 'published_at')
    search_fields = ('title', 'short_description', 'content')
    filter_horizontal = ('categories',)
    raw_id_fields = ('author', 'featured_image')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'

# TYMA Image Admin
class TYMAImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'image_type', 'content_type', 'object_id', 'created_at')
    list_filter = ('image_type', 'content_type', 'created_at')
    search_fields = ('title', 'caption', 'alt_text')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('content_type')

# Contact Submission Admin
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'submitted_at', 'is_responded')
    list_filter = ('subject', 'is_responded', 'submitted_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('submitted_at',)
    list_editable = ('is_responded',)
    date_hierarchy = 'submitted_at'

# Newsletter Subscriber Admin
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'subscribed_at', 'unsubscribed_at')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email',)
    readonly_fields = ('subscribed_at', 'unsubscribed_at')
    date_hierarchy = 'subscribed_at'

# Register your models here
admin.site.register(User, CustomUserAdmin)
admin.site.register(Zone, ZoneAdmin)
admin.site.register(Official, OfficialAdmin)
admin.site.register(NewsCategory, NewsCategoryAdmin)
admin.site.register(NewsEvent, NewsEventAdmin)
admin.site.register(TYMAImage, TYMAImageAdmin)
admin.site.register(ContactSubmission, ContactSubmissionAdmin)
admin.site.register(NewsletterSubscriber, NewsletterSubscriberAdmin)