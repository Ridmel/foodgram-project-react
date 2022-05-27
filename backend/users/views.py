from rest_framework import mixins, status, validators, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db.models import Count, Exists, OuterRef, Prefetch

from recipes.models import Recipe
from .models import Subscription
from .paginators import CustomNumberPagination
from .serializers import (
    AddSubscriptionSerializer,
    DelSubscriptionSerializer,
    UserForSubscriptionSerializer,
    UserSerializer,
)

User = get_user_model()


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    pagination_class = CustomNumberPagination

    def perform_create(self, serializer):
        password = serializer.validated_data.pop("password")
        hash_password = make_password(password)
        serializer.save(password=hash_password)

    def get_permissions(self):
        if self.action == "list" or self.action == "create":
            return (AllowAny(),)
        return (IsAuthenticated(),)

    def get_serializer_class(self):
        if self.action == "subscriptions":
            return UserForSubscriptionSerializer
        if self.action == "subscribe":
            return AddSubscriptionSerializer
        if self.action == "subscribe_delete":
            return DelSubscriptionSerializer
        return UserSerializer

    def get_queryset(self):
        current_user = self.request.user
        recipes = Recipe.objects.all()
        prefetch_recipes = Prefetch("own_recipes", queryset=recipes)
        if self.action == "subscriptions":
            return (
                User.objects.filter(subscribers__subscriber=current_user)
                .annotate(recipes_count=Count("own_recipes"))
                .prefetch_related(prefetch_recipes)
                .order_by("id")
            )
        if self.action == "list":
            if not current_user.is_authenticated:
                return User.objects.all()
            is_subscribed = Exists(
                Subscription.objects.filter(
                    subscribed=OuterRef("pk"), subscriber=current_user
                )
            )
            return User.objects.annotate(is_subscribed=is_subscribed)
        return User.objects.all()

    def get_recipes_limit(self):
        limit = self.request.query_params.get("recipes_limit", None)
        if limit and limit.isdigit() and int(limit) < 20:
            return int(limit)
        return 20

    @action(detail=False)
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(instance=user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=("post",))
    def subscribe(self, request, pk=None):
        serializer = self.get_serializer(
            data={"subscriber": request.user.id, "subscribed": pk}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @subscribe.mapping.delete
    def subscribe_delete(self, request, pk=None):
        serializer = self.get_serializer(
            data={"subscriber": request.user.id, "subscribed": pk}
        )
        serializer.is_valid(raise_exception=True)
        serializer.subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False)
    def subscriptions(self, request):
        return self.list(request)
