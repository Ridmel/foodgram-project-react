from rest_framework import mixins, permissions, viewsets

from django.contrib.auth import get_user_model
from django.db.models import Count, Prefetch

from users.paginators import CustomNumberPagination
from recipes.models import Recipe
from .serializers import SubscriptionUserSerializer

User = get_user_model()


class SubscriptionListViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = SubscriptionUserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomNumberPagination

    def get_recipes_limit(self):
        limit = self.request.query_params.get("recipes_limit", None)
        if limit and limit.isdigit() and int(limit) < 20:
            return int(limit)
        return 20

    def get_queryset(self):
        if self.action == "list":
            current_user = self.request.user
            recipes = Recipe.objects.order_by("-pub_date")
            prefetch_recipes = Prefetch("own_recipes", queryset=recipes)
            return (
                User.objects.filter(subscribers__subscriber=current_user)
                .annotate(recipes_count=Count("own_recipes"))
                .prefetch_related(prefetch_recipes)
                .order_by("id")
            )

# class SubscriptionCreateDeleteViewSet(
#     mixins.CreateModelMixin,
#     mixins.DestroyModelMixin,
#     viewsets.GenericViewSet,
# ):
