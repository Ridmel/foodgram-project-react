from django.contrib import admin

from .models import Ingredient, IngredientInRecipe, Recipe, Tag


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe


class TagInline(admin.TabularInline):
    model = Tag.recipes.through


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)
    list_filter = ("name",)
    ordering = ("name",)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "pub_date")
    list_display_links = ("name",)
    search_fields = ("name",)
    list_filter = ("name", "author", "tags")
    ordering = ("-pub_date",)
    exclude = ("tags",)
    inlines = (IngredientInRecipeInline, TagInline)
    readonly_fields = ("get_count", "pub_date")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "author",
                    "name",
                    "text",
                    "cooking_time",
                    "image",
                    "pub_date",
                    "get_count",
                )
            },
        ),
    )

    @admin.display(description="Добавили в избранное")
    def get_count(self, recipe):
        return recipe.in_favorites.count()


class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
