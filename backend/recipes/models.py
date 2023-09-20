from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()


class BaseModel(models.Model):
    objects = models.Manager()

    class Meta:
        abstract = True


class Tag(BaseModel):
    name = models.CharField(
        verbose_name='Тег',
        max_length=200,
        unique=True,
        blank=False
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=7,
        unique=True
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=200,
        unique=True,
        db_index=True
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(BaseModel):
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=200,
        db_index=True,
        blank=False
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=200,
        blank=False
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(BaseModel):
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        blank=False,
        related_name='recipes'
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1), ],
        verbose_name='Время приготовления',
        help_text='минут'
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Aвтор',
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient')
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/',
        help_text='Изображение рецепта'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        constraints = [
            UniqueConstraint(fields=('name', 'author'),
                             name='unique_recipes')
        ]

    def __str__(self):
        return self.name


class RecipeIngredient(BaseModel):
    recipe = models.ForeignKey(
        Recipe,
        null=True,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        null=True,
        on_delete=models.SET_NULL,
        related_name='recipe_ingredients'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1), ],
        blank=False,
        null=False,
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            UniqueConstraint(fields=('ingredient', 'recipe'),
                             name='unique_recipe_ingredient')
        ]


class ShoppingCart(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты',
        related_name='shopping_cart'
    )

    class Meta:
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        constraints = [
            UniqueConstraint(fields=('user', 'recipe'),
                             name='unique_recipe'
                             )
        ]


class Favorite(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorite'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Рецепт в избранном',
        help_text='Рецепт в избранном'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            UniqueConstraint(fields=('user', 'recipe'),
                             name='unique_favorite'
                             )
        ]
