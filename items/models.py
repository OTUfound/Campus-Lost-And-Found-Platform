from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if not self.email.endswith('@ostimteknik.edu.tr'):
            raise ValidationError('Email must end with @ostimteknik.edu.tr')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class EmailVerificationToken(models.Model):
    token = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='verification_tokens')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    def __str__(self):
        return f"Verification token for {self.user.email}"


class PasswordResetToken(models.Model):
    token = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='password_reset_tokens')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    def __str__(self):
        return f"Password reset token for {self.user.email}"


class LostFoundItem(models.Model):
    ITEM_CHOICES = [
        ('lost', 'Lost'),
        ('found', 'Found'),
    ]

    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('clothing', 'Clothing'),
        ('keys', 'Keys'),
        ('accessories', 'Accessories'),
        ('bags', 'Bags'),
        ('documents', 'Documents'),
        ('books', 'Books'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('claim_pending', 'Claim Pending'),
        ('resolved', 'Resolved'),
    ]

    DROPOFF_CHOICES = [
        ('security', 'Security'),
        ('student_affairs', 'Student Affairs'),
        ('library', 'Library'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    item_type = models.CharField(max_length=10, choices=ITEM_CHOICES)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    location = models.CharField(max_length=200)
    dropoff_location = models.CharField(max_length=50, choices=DROPOFF_CHOICES, blank=True, null=True, help_text="Where the item was dropped off (if any)")
    photo = models.ImageField(upload_to='items/')
    posted_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='items')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_item_type_display()} - {self.title}"


class Claim(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    CONTACT_METHOD_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
        ('phone', 'Phone'),
    ]

    item = models.ForeignKey(LostFoundItem, on_delete=models.CASCADE, related_name='claims')
    claimant = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='claims')
    proof_description = models.TextField(help_text='Describe details that prove ownership')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=CONTACT_METHOD_CHOICES,
        default='whatsapp',
        help_text='Preferred contact method for communication'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    contact_shared_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('item', 'claimant')

    def __str__(self):
        return f"Claim for {self.item.title} by {self.claimant.email}"
