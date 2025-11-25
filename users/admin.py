from django.contrib import admin
from .models import UserToken


@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'is_active', 'access_token', 'created_at', 'updated_at', 'user_agent')
	list_filter = ('is_active', 'created_at', 'user')
	search_fields = ('user__username', 'user__email', 'access_token', 'refresh_token', 'user_agent')
	readonly_fields = ('created_at', 'updated_at')
	ordering = ('-created_at',)


