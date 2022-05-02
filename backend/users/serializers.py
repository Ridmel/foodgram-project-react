from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

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

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        if not user.is_authenticated:
            return False
        return user != obj and user.subscribed.filter(id=obj.id).exists()

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
