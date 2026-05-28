from django.contrib import admin
from .models import Business, FacebookPage, Conversation, Message

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'created_at')
    search_fields = ('name', 'owner__email')

@admin.register(FacebookPage)
class FacebookPageAdmin(admin.ModelAdmin):
    list_display = ('id', 'page_name', 'page_id', 'business', 'bot_enabled', 'human_handover_enabled', 'is_active')
    list_filter = ('bot_enabled', 'human_handover_enabled', 'is_active', 'business')
    search_fields = ('page_name', 'page_id')

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'facebook_page', 'customer_psid', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'facebook_page')
    search_fields = ('customer_psid',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender_type', 'text_preview', 'external_message_id', 'created_at')
    list_filter = ('sender_type', 'conversation__facebook_page')
    search_fields = ('text', 'external_message_id')

    def text_preview(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Text'
