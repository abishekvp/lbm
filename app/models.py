from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=15)
    image = models.TextField()

class Stock(models.Model):
    name = models.CharField(max_length=64)
    quantity = models.IntegerField()
    is_available = models.BooleanField(default=True)
    isbn = models.CharField(max_length=13, null=True, unique=True)
    author = models.CharField(max_length=128, null=True)
    publication = models.CharField(max_length=256, null=True)
    release = models.DateField(null=True)
    updated = models.DateTimeField(auto_now=True)
    uploaded = models.DateTimeField(auto_now_add=True)
    image = models.ForeignKey('Image', on_delete=models.PROTECT, null=True)

class Ledger(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Stock, on_delete=models.CASCADE, null=True, blank=True)
    isbn = models.CharField(max_length=126, null=True)
    checkout_date = models.DateField(auto_now_add=True)
    approved_date = models.DateField(null=True)
    rejected_date = models.DateField(null=True)
    checkin_date = models.DateField(null=True)
    is_checked_out = models.BooleanField(default=True)
    is_checked_in = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    is_pending = models.BooleanField(default=True)
    is_overdue = models.BooleanField(default=False)

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
