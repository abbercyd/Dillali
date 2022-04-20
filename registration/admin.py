from django.contrib import admin
from .models import *

admin.site.register(Tenants)
admin.site.register(Managers)
admin.site.register(Profile)
admin.site.register(RelatedRecords)
admin.site.register(UserNotifications)


