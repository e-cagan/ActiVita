from django.contrib import admin
from .models import User, Category, Donation, Event, Participation, Notification

# Register your models here.
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Donation)
admin.site.register(Event)
admin.site.register(Participation)
admin.site.register(Notification)