from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from recipes.models import Recipe

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "password",
        )
        extra_kwargs = {
            "email": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
            "password": {"write_only": True},
        }

    def get_is_subscribed(self, user):
        current_user = self.context.get("request").user
        if not current_user.is_authenticated:
            return False
        if hasattr(user, "is_subscribed"):
            return user.is_subscribed
        return (
            current_user != user
            and user.subscribers.filter(pk=current_user.pk).exists()
        )

    def validate(self, data):
        user = User(**data)
        password = data.get("password")
        errors = {}
        try:
            validate_password(password, user=user)
        except ValidationError as e:
            errors["password"] = e.messages
        if errors:
            raise serializers.ValidationError(errors)
        return super().validate(data)


class RecipeForSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class UserForSubscriptionSerializer(UserSerializer):
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
        return RecipeForSubscriptionSerializer(
            queryset,
            many=True,
            context=self.context,
        ).data
