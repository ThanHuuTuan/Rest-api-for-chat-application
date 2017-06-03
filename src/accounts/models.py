from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
# Create your models here.


class AccountManager(models.Manager):
    pass


class Account(models.Model):
    
    user = models.OneToOneField(User,on_delete=models.CASCADE, primary_key=True)
    tagline = models.CharField(max_length=140, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AccountManager()

    def __str__(self):
        return self.tagline


    def clean_password(self, username, password, check_password, email): #clean data works like this 

        if password!=check_password:
            # raise ValidationError("Passwords must match")
            print ('pass does not match')

        username_qs = User.objects.filter(username=username)
        email_qs = User.objects.filter(email=email)
        if username_qs.exists() or email_qs.exists():
            # raise ValidationError("this username is already registered")
            print ('user already exists')

        return True
