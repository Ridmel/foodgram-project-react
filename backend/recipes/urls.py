from rest_framework.routers import DefaultRouter

from .views import IngredientInRecipeViewSet, RecipeViewSet, TagViewSet

router = DefaultRouter()
router.register(
    "ingredients", IngredientInRecipeViewSet, basename="ingredient"
)
router.register("recipes", RecipeViewSet, basename="recipe")
router.register("tags", TagViewSet, basename="tag")
