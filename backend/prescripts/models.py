from django.contrib.auth import get_user_model
from django.db import models
from django.template.defaultfilters import slugify


User = get_user_model()


class ComponentUnit(models.Model):
    slug = models.SlugField(max_length=64, unique=True,
                            verbose_name='Ссылка',)
    name = models.CharField(
        max_length=64, unique=True, verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'Единица измерения'
        verbose_name_plural = 'Единицы измерения'
        ordering = ('name',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        self.name = self.name.strip().lower()
        return super().save(*args, **kwargs)


class Component(models.Model):
    name = models.CharField(
        max_length=264, unique=True, verbose_name='Ингредиент',
    )
    unit = models.ForeignKey(
        ComponentUnit, on_delete=models.CASCADE, related_name='components',
        verbose_name='Единица измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} ({self.unit})'


class Tag(models.Model):
    slug = models.SlugField(max_length=64, unique=True,
                            verbose_name='Ссылка',)
    name = models.CharField(max_length=64, unique=True,
                            verbose_name='Тег',)
    color = models.CharField(max_length=16, verbose_name='Цвет',)

    class Meta:
        ordering = ('name', 'color',)
        constraints = (models.UniqueConstraint(
                       fields=('name', 'color'),
                       name='unique_tag'),)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)


class Prescriptor(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='prescriptors',
        verbose_name='Автор публикации',)
    name = models.CharField(max_length=100, verbose_name='Название рецепта',)
    image = models.ImageField(
        upload_to='prescriptors/images/', null=True, blank=True,
        verbose_name='Изображение рецепта', default=None)
    text = models.TextField(verbose_name='Описание рецепта',)
    ingredients = models.ManyToManyField(Component,
                                        through='PrescriptorComponent',
                                        verbose_name='Ингредиенты',)
    tags = models.ManyToManyField(Tag, related_name='prescriptors',
                                  verbose_name='Теги',)
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления рецепта',)
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True,)

    class Meta:
        ordering = ('-pub_date',)
        constraints = (models.UniqueConstraint(
                       fields=('name', 'author'),
                       name='unique_prescriptor'),)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name} от {self.author}'


class PrescriptorComponent(models.Model):
    prescriptor = models.ForeignKey(
        Prescriptor, on_delete=models.CASCADE,
        related_name='prescriptor_component',
    )
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента в данном рецепте',)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('prescriptor', 'component'),
                name='unique_PrescriptorComponent'
            ),
        )

    def __str__(self):
        return f'{self.prescriptor}: {self.component} - {self.amount}'

class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites',
        verbose_name='Пользователь, выбравший рецепт',
    )
    prescriptor = models.ForeignKey(
        Prescriptor, on_delete=models.CASCADE, 
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'prescriptor'),
                name='unique_Favorite'
            ),
        )
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.user} отметил {self.prescriptor}'
