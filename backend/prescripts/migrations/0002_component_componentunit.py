# Generated by Django 3.2.16 on 2023-06-20 08:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('prescripts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ComponentUnit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(max_length=64, unique=True, verbose_name='Ссылка')),
                ('name', models.CharField(max_length=64, unique=True, verbose_name='Название ингредиента')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Component',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=264, unique=True, verbose_name='Ингридиент в рецепте')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='components', to='prescripts.componentunit', verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'Ингридиент в рецепте',
                'verbose_name_plural': 'Ингридиенты в рецепте',
                'ordering': ('name',),
            },
        ),
    ]