import csv

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from django.contrib.auth import get_user_model
from django.db.models import Q, Sum
from django.http import HttpResponse

from users.paginators import CustomNumberPagination
from users.permissions import IsOwnerOrReadOnlyForObject
from .mixins import ListRetrieveGenericViewSet
from .models import Ingredient, Recipe, Tag
from .serializers import (
    IngredientSerializer,
    RecipeFavoriteSerializer,
    RecipeSafeSerializer,
    RecipeShoppingCartSerializer,
    RecipeUnsafeSerializer,
    TagSerializer,
)

User = get_user_model()


class IngredientViewSet(ListRetrieveGenericViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)

    SearchFilter.search_param = "name"
    filter_backends = (SearchFilter,)
    search_fields = ("^name",)


class TagViewSet(ListRetrieveGenericViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = CustomNumberPagination
    http_method_names = ("get", "post", "patch", "delete")
    additional_methods = (
        "favorite",
        "favorite_delete",
        "shopping_cart",
        "shopping_cart_delete",
    )

    def get_permissions(self):
        if self.action in RecipeViewSet.additional_methods:
            return (IsAuthenticated(),)
        return IsAuthenticatedOrReadOnly(), IsOwnerOrReadOnlyForObject()

    def get_serializer_class(self):
        if self.action in ("shopping_cart", "shopping_cart_delete"):
            return RecipeShoppingCartSerializer
        if self.action in ("favorite", "favorite_delete"):
            return RecipeFavoriteSerializer
        if self.action in ("list", "retrieve"):
            return RecipeSafeSerializer
        return RecipeUnsafeSerializer

    def get_queryset(self):
        if self.action in RecipeViewSet.additional_methods:
            return Recipe.objects.all()
        queryset = Recipe.objects.select_related("author").prefetch_related(
            "ingredients_in_recipe__ingredient", "tags"
        )
        if self.action == "list":
            return self.apply_query_param_filters(queryset)
        return queryset

    def apply_query_param_filters(self, queryset):
        is_authenticated = self.request.user.is_authenticated
        author = self.request.query_params.get("author")
        if author and author.isdigit():
            queryset = queryset.filter(Q(author=int(author)))

        is_favorited = self.request.query_params.get("is_favorited")
        if is_authenticated and is_favorited and is_favorited == "1":
            queryset = queryset.filter(Q(in_favorites=self.request.user))

        is_in_cart = self.request.query_params.get("is_in_shopping_cart")
        if is_authenticated and is_in_cart and is_in_cart == "1":
            queryset = queryset.filter(Q(in_baskets=self.request.user))

        tags = self.request.query_params.getlist("tags")
        if tags:
            filter_tags = Q(tags__slug=tags[0])
            for tag in tags[1:]:
                filter_tags = filter_tags | Q(tags__slug=tag)
            queryset = queryset.filter(filter_tags)
        return queryset.distinct()

    @action(detail=True, methods=("post",))
    def favorite(self, request, pk=None):
        serializer = self.get_serializer(data={"recipe_id": pk})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @favorite.mapping.delete
    def favorite_delete(self, request, pk=None):
        serializer = self.get_serializer(data={"recipe_id": pk})
        serializer.is_valid(raise_exception=True)
        serializer.instance.in_favorites.remove(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=("post",))
    def shopping_cart(self, request, pk=None):
        serializer = self.get_serializer(data={"recipe_id": pk})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @shopping_cart.mapping.delete
    def shopping_cart_delete(self, request, pk=None):
        serializer = self.get_serializer(data={"recipe_id": pk})
        serializer.is_valid(raise_exception=True)
        serializer.instance.in_baskets.remove(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False)
    def download_shopping_cart(self, request):
        current_user = request.user
        ingredient_amount = (
            Ingredient.objects.filter(
                ingredients_in_recipe__recipe__in_baskets=current_user
            )
            .values_list("name", "measurement_unit")
            .annotate(amount=Sum("ingredients_in_recipe__amount"))
        )
        response = HttpResponse(content_type="text/csv")
        response[
            "Content-Disposition"
        ] = "attachment; filename=ingredients.csv"
        writer = csv.writer(response)
        for name, unit, amount in ingredient_amount:
            writer.writerow([name, amount, unit])
        return response
