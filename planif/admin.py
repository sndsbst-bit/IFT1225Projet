from django.apps import apps
from django.contrib import admin

# TEMP(données): administration automatique pour peupler le monde simulé
for model in apps.get_app_config("planif").get_models():
    admin.site.register(model)
