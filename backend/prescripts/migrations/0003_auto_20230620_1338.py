# Generated by Django 3.2.16 on 2023-06-20 08:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('prescripts', '0002_component_componentunit'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='component',
            options={'ordering': ('name',), 'verbose_name': 'Ингредиент', 'verbose_name_plural': 'Ингредиенты'},
        ),
        migrations.AlterModelOptions(
            name='componentunit',
            options={'ordering': ('name',), 'verbose_name': 'Единица измерения', 'verbose_name_plural': 'Единицы измерения'},
        ),
        migrations.AlterField(
            model_name='component',
            name='name',
            field=models.CharField(max_length=264, unique=True, verbose_name='Ингредиент'),
        ),
        migrations.AlterField(
            model_name='componentunit',
            name='name',
            field=models.CharField(max_length=64, unique=True, verbose_name='Единица измерения'),
        ),
        migrations.CreateModel(
            name='PrescriptorComponent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveSmallIntegerField(verbose_name='Количество ингредиента в данном рецепте')),
                ('component', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='prescripts.component')),
                ('prescriptor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='prescripts.prescriptor')),
            ],
        ),
        migrations.AddField(
            model_name='prescriptor',
            name='components',
            field=models.ManyToManyField(through='prescripts.PrescriptorComponent', to='prescripts.Component', verbose_name='Ингредиенты'),
        ),
        migrations.AddConstraint(
            model_name='prescriptorcomponent',
            constraint=models.UniqueConstraint(fields=('prescriptor', 'component'), name='unique_PrescriptorComponent'),
        ),
    ]
