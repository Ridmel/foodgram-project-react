from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Follow(models.Model):
    leader = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="followers",
        verbose_name="Лидер",
    )
    follower = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="leaders",
        verbose_name="Подписчик",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constrains = models.UniqueConstraint(
            fields=("leader", "follower"), name="follow_leader_follower"
        )

    def __str__(self):
        return (
            f"Лидер: {self.leader.username}; "
            f"Подписчик: {self.follower.username}"
        )
