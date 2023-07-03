import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand, no_translations

from prescripts.models import Component, ComponentUnit


TABLES_FOR_LOAD = (('ingredients.csv', Component,),)

CSV_FILES_DIR = os.path.join(settings.BASE_DIR, '..', 'data')


class Command(BaseCommand):
    help = 'Загружает данные ингредиентов из csv'

    @no_translations
    def handle(self, *args, **options):
        csv_file_path = os.path.join(CSV_FILES_DIR, TABLES_FOR_LOAD[0][0])
        print(f'Пробуем загрузить таблицу {csv_file_path}')

        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            unit_dict = dict()
            reader = csv.reader(csvfile, delimiter=',')

            cnt = 0
            for row in reader:
                unit = row[1]
                if unit in unit_dict:
                    component_unit = unit_dict[unit]
                else:
                    component_unit = ComponentUnit.objects.get_or_create(
                        name=unit
                    )
                    unit_dict[unit] = component_unit
                name = row[0]
                data = {
                    'name': name,
                    'unit': component_unit[0],
                }
                print(Component.objects.get_or_create(**data))
                cnt += 1

        print(f'Загружена таблица {csv_file_path} - {cnt} записей')
