from django.contrib import admin
from .models import Company, Report, TotalCount, Province

# Register your models here.

admin.site.register(Company)
admin.site.register(Report)
admin.site.register(TotalCount)
admin.site.register(Province)
