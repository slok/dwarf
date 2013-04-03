from django.contrib import admin
from userprofile.models import Token, Profile

admin.site.register(Profile)
admin.site.register(Token)
