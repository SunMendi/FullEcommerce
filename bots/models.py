from django.db import models
from django.conf import settings

class Business(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='businesses')
    name = models.CharField(blank=False, max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class FacebookPage(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='facebook_pages')
    page_id = models.CharField(blank=False, max_length=100, unique=True)
    page_name = models.CharField(blank=False, max_length=100)
    access_token = models.TextField(blank=False)  # We will encrypt this in a future hardening phase!
    system_prompt = models.TextField(blank=True, default="You are a helpful customer assistant.")
    bot_enabled = models.BooleanField(default=True)
    human_handover_enabled = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.page_name} ({self.page_id})"

class ConversationStatus(models.TextChoices):
    BOT_ACTIVE = 'bot_active', 'Bot Active'
    HUMAN_REQUIRED = 'human_required', 'Human Required'
    CLOSED = 'closed', 'Closed'

class Conversation(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='conversations')
    facebook_page = models.ForeignKey(FacebookPage, on_delete=models.CASCADE, related_name='conversations')
    customer_psid = models.CharField(blank=False, max_length=100)  # Page-Scoped ID
    status = models.CharField(
        max_length=20, 
        choices=ConversationStatus.choices, 
        default=ConversationStatus.BOT_ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('facebook_page', 'customer_psid')

    def __str__(self):
        return f"Chat with {self.customer_psid} on {self.facebook_page.page_name}"

class SenderType(models.TextChoices):
    CUSTOMER = 'customer', 'Customer'
    BOT = 'bot', 'Bot'
    HUMAN = 'human', 'Human'

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender_type = models.CharField(
        max_length=10, 
        choices=SenderType.choices
    )
    text = models.TextField(blank=False)
    external_message_id = models.CharField(max_length=255, unique=True, blank=True, null=True)  # Idempotency key
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender_type}: {self.text[:30]}"