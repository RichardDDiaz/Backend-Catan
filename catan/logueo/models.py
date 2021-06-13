from django.db import models
from rest_framework.authtoken.models import Token

# class User(models.Model):
#    name = models.CharField(max_length=100)
#    secret = models.CharField(max_length=100)

# class Session(models.Model):
#    user = models.OneToOneField(
#        User, on_delete=models.CASCADE, primary_key=True);
#token = models.OneToOneField(Token,on_delete=models.CASCADE, primary_key=True)
