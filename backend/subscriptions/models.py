from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


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
        constrains = models.UniqueConstraint(
            fields=("subscribed", "subscriber"),
            name="subscription_subscribed_subscriber",
        )

    def __str__(self):
        return (
            f"Лидер: {self.subscribed.username}; "
            f"Подписчик: {self.subscriber.username}"
        )
