from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=15)
    image = models.TextField()

class Library(models.Model):
    name = models.CharField(max_length=64)

class Department(models.Model):
    name = models.CharField(max_length=64)
    library = models.ForeignKey(Library, on_delete=models.CASCADE)

class Rack(models.Model):
    name = models.CharField(max_length=64)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

class Image(models.Model):
    name = models.TextField()
    image = models.BinaryField()
    extension = models.CharField(max_length=8, null=True)

class File(models.Model):
    name = models.TextField()
    file = models.BinaryField()

class Book(models.Model):
    name = models.CharField(max_length=256)
    author = models.CharField(max_length=128)
    publication = models.CharField(max_length=256, null=True)
    release = models.DateField(null=True)
    uploaded = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    image = models.ForeignKey(Image, on_delete=models.PROTECT, null=True)
    file = models.ForeignKey(File, on_delete=models.PROTECT)
    rack = models.ForeignKey(Rack, on_delete=models.PROTECT)
