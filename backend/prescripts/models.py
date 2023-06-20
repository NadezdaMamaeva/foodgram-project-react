from django.contrib.auth import get_user_model
from django.db import models
from django.template.defaultfilters import slugify


User = get_user_model()


class Tag(models.Model):
    slug = models.SlugField(max_length=64, unique=True,
                            verbose_name='Ссылка',)
    name = models.CharField(max_length=64, unique=True,
                            verbose_name='Имя',)
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
    tags = models.ManyToManyField(Tag, related_name='prescriptors',
                                  verbose_name='Теги',)
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления рецепта',)
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True,)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name} от {self.author}'
