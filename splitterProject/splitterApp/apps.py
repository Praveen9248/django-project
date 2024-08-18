from django.apps import AppConfig


class SplitterappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "splitterApp"

    def ready(self):
        import splitterApp.templatetags.custom_filters