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
        constraints = (
            models.UniqueConstraint(
                fields=("subscribed", "subscriber"),
                name="subscription_subscribed_subscriber"
            ),
            models.CheckConstraint(
                check=~models.Q(subscribed__exact=models.F("subscriber")),
                name="subscription_subscribed_not_equals_subscriber"
            ),
        )

    def __str__(self):
        return (
            f"Лидер: {self.subscribed.username}; "
            f"Подписчик: {self.subscriber.username}"
        )
