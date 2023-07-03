from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

from .validators import validate_username


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)

    USER = 'user'
    ADMIN = 'admin'

    ROLE_CHOICES = (
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор'),
    )

    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        blank=False,
        validators=(validate_username, )
    )
    password = models.CharField(
        'Пароль',
        max_length=150,
        blank=False,
    )
    email = models.EmailField(
        'Адрес электронной почты',
        max_length=254,
        unique=True,
        blank=False,
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=False,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=False,
    )
    role = models.CharField(
        'Роль',
        max_length=20,
        choices=ROLE_CHOICES,
        default=USER,
        blank=False,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('role', 'username',)

    @property
    def is_user(self):
        return self.role == self.USER

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.ADMIN
        return super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False, null=False,
        verbose_name='Автор',
        related_name='subscribing',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False, null=False,
        verbose_name='Подписчик',
        related_name='subscriber',
    )

    class Meta:
        ordering = ('author',)
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'user',), name='unique_Subscription'
            ),
        )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def clean(self):
        if self.author == self.user:
            raise ValidationError('Нельзя подписаться на себя')

    def __str__(self) -> str:
        return f'{self.user} подписан на {self.author}'
