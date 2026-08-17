from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    class UserType(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        BUSINESS = "business", "Business"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    file = models.ImageField(
        upload_to="profiles/",
        blank=True,
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )
    tel = models.CharField(
        max_length=30,
        blank=True,
        default="",
    )
    description = models.TextField(
        blank=True,
        default="",
    )
    working_hours = models.CharField(
        max_length=50,
        blank=True,
        default="",
    )
    type = models.CharField(
        max_length=10,
        choices=UserType.choices,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.user.username
