from rest_framework import serializers

from django.contrib.auth import get_user_model

from users.serializers import UserSerializer
from recipes.models import Recipe

User = get_user_model()


class SubscriptionRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class SubscriptionUserSerializer(UserSerializer):
    is_subscribed = serializers.BooleanField(default=True, read_only=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, user):
        limit = self.context.get("view").get_recipes_limit()
        queryset = user.own_recipes.all()[:limit]
        return SubscriptionRecipeSerializer(
            queryset,
            many=True,
            context=self.context,
        ).data


