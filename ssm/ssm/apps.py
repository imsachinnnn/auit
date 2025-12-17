from django.contrib.auth.apps import AuthConfig as DefaultAuthConfig

class AuthConfig(DefaultAuthConfig):
    verbose_name = "Security & Access"
