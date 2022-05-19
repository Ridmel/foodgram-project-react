from colorfield.fields import ColorField

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Recipe(models.Model):
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="own_recipes",
        verbose_name="Автор",
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Название",
    )
    text = models.TextField(
        verbose_name="Описание",
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления",
        validators=(MinValueValidator(1),),
    )
    tags = models.ManyToManyField(
        to="Tag",
        related_name="recipes",
        verbose_name="Тег",
    )
    image = models.ImageField(
        verbose_name="Изображение",
    )
    in_favorites = models.ManyToManyField(
        to=User,
        related_name="favor_recipes",
        verbose_name="В избранных",
    )
    in_baskets = models.ManyToManyField(
        to=User,
        related_name="basket_recipes",
        verbose_name="В корзинах",
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Время публикации",
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        constraints = (
            models.CheckConstraint(
                check=models.Q(cooking_time__gte=1), name="recipe_minvalue_1"
            ),
        )

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        related_name="ingredients",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        to="Ingredient",
        on_delete=models.PROTECT,
        related_name="ingredients",
        verbose_name="Ингредиент",
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество",
        validators=(MinValueValidator(1),),
    )

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"
        constraints = (
            models.CheckConstraint(
                check=models.Q(amount__gte=1), name="ingredient_minvalue_1"
            ),
            models.UniqueConstraint(
                fields=("recipe", "ingredient"),
                name="ingredientinrecipe_unique",
            ),
        )

    def __str__(self):
        return f"{self.ingredient} ({self.amount})"


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Название",
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name="Единицы измерения",
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Tag(models.Model):
    COLOR_PALETTE = [
        ("#FFFFFF", "white"),
        ("#000000", "black"),
    ]

    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Название",
    )
    color = ColorField(
        samples=COLOR_PALETTE,
        unique=True,
        verbose_name="Цвет",
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name="Слаг",
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name
