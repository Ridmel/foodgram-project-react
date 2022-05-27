from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.shortcuts import get_object_or_404

from .models import Subscription

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
            and user.subscribers.filter(subscriber=current_user).exists()
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
        from recipes.serializers import RecipeShortPresentSerializer

        limit = self.context.get("view").get_recipes_limit()
        queryset = user.own_recipes.all()[:limit]
        return RecipeShortPresentSerializer(
            queryset,
            many=True,
            context=self.context,
        ).data


class AddSubscriptionSerializer(serializers.Serializer):
    subscriber = serializers.IntegerField()
    subscribed = serializers.IntegerField()

    def validate(self, data):
        subscriber_id = data.get("subscriber")
        subscribed_id = data.get("subscribed")
        get_object_or_404(User, pk=subscribed_id)
        if subscriber_id == subscribed_id:
            raise ValidationError(
                {"errors": "Нельзя подписаться на самого себя."}
            )
        if Subscription.objects.filter(
            subscribed_id=subscribed_id, subscriber_id=subscriber_id
        ).exists():
            raise ValidationError(
                {"errors": "Вы уже подписаны на этого пользователя."}
            )
        return data

    def create(self, validated_data):
        subscriber_id = validated_data.get("subscriber")
        subscribed_id = validated_data.get("subscribed")
        Subscription.objects.create(
            subscribed_id=subscribed_id,
            subscriber_id=subscriber_id,
        )
        user = User.objects.annotate(recipes_count=Count("own_recipes")).get(
            pk=subscribed_id
        )
        user.is_subscribed = True
        return user

    def to_representation(self, instance):
        return UserForSubscriptionSerializer(
            instance=instance,
            context=self.context,
        ).data


class DelSubscriptionSerializer(serializers.Serializer):
    subscriber = serializers.IntegerField()
    subscribed = serializers.IntegerField()

    def validate(self, data):
        subscriber_id = data.get("subscriber")
        subscribed_id = data.get("subscribed")
        get_object_or_404(User, pk=subscribed_id)
        subscription = Subscription.objects.filter(
            subscriber=subscriber_id, subscribed=subscribed_id
        ).first()
        if not subscription:
            raise ValidationError(
                {"errors": "Вы не подписаны на этого пользователя."}
            )
        self.subscription = subscription
        return data
