from rest_framework import serializers
from drf_base64.fields import Base64ImageField
from recipes.models import (
    Tag,
    Recipe,
    RecipeIngredient,
    Ingredient,
    Favorite
)
from users.models import User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(many=True,
                                             source='recipe_ingredients')
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = '__all__'


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        min_value=1,
        error_messages={
            'min_value': 'Должно быть позитивное число больше 0.'
        }
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientCreateSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('name', 'cooking_time', 'text', 'tags', 'ingredients')

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance = super().create(validated_data)

        for ingredient_data in ingredients:
            RecipeIngredient(
                recipe=instance,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount']
            ).save()

            instance.save()
            return instance


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Favorite
        fields = ('user', 'recipe',)
