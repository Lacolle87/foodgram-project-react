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


class IngredientEditSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Количество ингредиента должно быть больше 1!'
            )
        return value


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    ingredients = IngredientEditSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'name', 'image',
                  'text', 'ingredients', 'cooking_time',)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        cooking_time = validated_data.pop('cooking_time')
        author = self.context['request'].user
        new_recipe = Recipe.objects.create(
            author=author,
            cooking_time=cooking_time,
            **validated_data
        )
        new_recipe.tags.set(tags)
        self.add_ingredients(new_recipe, ingredients)
        return new_recipe

    def update(self, recipe, validated_data):
        if validated_data.get('ingredients'):
            ingredients = validated_data.pop('ingredients')
            recipe.ingredient_recipes.all().delete()
            self.add_ingredients(recipe, ingredients)
        tags = validated_data.pop('tags')
        recipe.tags.set(tags)
        return super().update(recipe, validated_data)

    def add_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            ) for ingredient in ingredients])

    def validate_ingredient(self, data):
        ingredients = data['ingredients']
        if not ingredients:
            raise serializers.ValidationError(
                'Необходим хотя бы 1 ингредиент.')
        unique_ingredients = set()
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in unique_ingredients:
                raise serializers.ValidationError('Такой ингредиент уже есть.')
            unique_ingredients.add(ingredient_id)
        return data

    def validate_time(self, data):
        cooking_time = data['cooking_time']
        if int(cooking_time) <= 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 1.')
        return data


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
