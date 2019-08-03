from django.test import TestCase

# Create your tests here.

import os
if not os.environ.get("DJANGO_SETTINGS_MODULE"):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings.dev")

import django
django.setup()

from users.models import User

if __name__ == "__main__":
    user = User.objects.get(username='adv_admin')


from rest_framework import status
