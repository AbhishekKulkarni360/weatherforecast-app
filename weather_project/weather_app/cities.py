# management/commands/import_cities.py

import json
from django.core.management.base import BaseCommand
from yourapp.models import City  # Replace 'yourapp' with your actual Django app name

class Command(BaseCommand):
    help = 'Imports city data from cities.json'

    def handle(self, *args, **options):
        with open('cities.json', 'r') as f:
            cities = json.load(f)
            for city in cities:
                City.objects.get_or_create(name=city['name'])

        self.stdout.write(self.style.SUCCESS('Cities imported successfully'))
