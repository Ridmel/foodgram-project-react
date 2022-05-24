from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField("Электронная почта", unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("username",)


class Subscription(models.Model):
    subscribed = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="subscribers",
        verbose_name="Лидер",
    )
    subscriber = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="subscribed",
        verbose_name="Подписчик",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = (
            models.UniqueConstraint(
                fields=("subscribed", "subscriber"),
                name="subscription_subscribed_subscriber",
            ),
            models.CheckConstraint(
                check=~models.Q(subscribed__exact=models.F("subscriber")),
                name="subscription_subscribed_not_equals_subscriber",
            ),
        )

    def __str__(self):
        return (
            f"автор: {self.subscribed.username}; "
            f"подписчик: {self.subscriber.username}"
        )
