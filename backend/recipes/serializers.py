from rest_framework import serializers

from django.db import transaction

from users.serializers import UserSerializer
from .fields import Base64ImageField
from .models import Ingredient, IngredientInRecipe, Recipe, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class IngrInRecipeSafeSerializer(serializers.ModelSerializer):
    name = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True,
        source="ingredient",
    )
    measurement_unit = serializers.SlugRelatedField(
        slug_field="measurement_unit",
        read_only=True,
        source="ingredient",
    )

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class IngrInRecipeUnsafeSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(
        slug_field="id",
        queryset=Ingredient.objects.all(),
        source="ingredient",
    )

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "amount")

    def to_representation(self, instance):
        serializer = IngrInRecipeSafeSerializer(instance=instance)
        return serializer.data


class RecipeShortPresentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class RecipeSafeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = IngrInRecipeSafeSerializer(
        many=True, source="ingredients_in_recipe"
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_is_favorited(self, recipe):
        current_user = self.context.get("request").user
        return recipe.in_favorites.filter(pk=current_user.id).exists()

    def get_is_in_shopping_cart(self, recipe):
        current_user = self.context.get("request").user
        return recipe.in_baskets.filter(pk=current_user.id).exists()


class RecipeUnsafeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    ingredients = IngrInRecipeUnsafeSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = "__all__"
        read_only_fields = ("in_favorites", "in_baskets")

    def populate_ingredients(self, valid_ingredients, recipe):
        ingredients_in_recipe = []

        for valid_ingredient in valid_ingredients:
            ingredient = valid_ingredient["ingredient"]
            amount = valid_ingredient["amount"]
            ingredient_in_recipe = IngredientInRecipe(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount,
            )
            ingredients_in_recipe.append(ingredient_in_recipe)

        return ingredients_in_recipe

    @transaction.atomic()
    def create(self, validated_data):
        tags = validated_data.pop("tags", None)
        valid_ingredients = validated_data.pop("ingredients", {})
        recipe = Recipe.objects.create(**validated_data)

        ingredients_in_recipe = self.populate_ingredients(
            valid_ingredients, recipe
        )
        IngredientInRecipe.objects.bulk_create(ingredients_in_recipe)
        recipe.tags.set(tags)

        recipe = (
            Recipe.objects.select_related("author")
            .prefetch_related("tags", "ingredients_in_recipe__ingredient")
            .get(pk=recipe.id)
        )
        return recipe

    @transaction.atomic()
    def update(self, recipe, validated_data):
        tags = validated_data.pop("tags", None)
        valid_ingredients = validated_data.pop("ingredients", {})

        for attr, value in validated_data.items():
            setattr(recipe, attr, value)
        recipe.save()

        old_ingredients = recipe.ingredients.all()
        old_ingredients.delete()
        ingredients_in_recipe = self.populate_ingredients(
            valid_ingredients, recipe
        )
        IngredientInRecipe.objects.bulk_create(ingredients_in_recipe)
        recipe.tags.set(tags)

        recipe = (
            Recipe.objects.select_related("author")
            .prefetch_related("tags", "ingredients_in_recipe__ingredient")
            .get(pk=recipe.id)
        )
        return recipe

    def validate_ingredients(self, ingredients):
        """Validate ingredients for uniqueness among themselves."""
        all_ingredients = []
        for ingredient in ingredients:
            all_ingredients.append(ingredient["ingredient"].pk)
        unique_ingredients = set(all_ingredients)
        if len(all_ingredients) != len(unique_ingredients):
            raise serializers.ValidationError(
                "В одном рецепте не может быть "
                "несколько одинаковых ингредиентов."
            )
        return ingredients

    def to_representation(self, instance):
        return RecipeSafeSerializer(
            instance=instance,
            context=self.context,
        ).data
