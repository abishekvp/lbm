from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Profile)
admin.site.register(Library)
admin.site.register(Department)
admin.site.register(Rack)
admin.site.register(Image)
admin.site.register(File)
admin.site.register(Book)