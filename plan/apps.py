from django.apps import AppConfig


class PlanConfig(AppConfig):
    name = 'plan'

    def ready(self):
        import plan.signals
