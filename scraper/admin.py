from django.contrib import admin
from .models import Tasks, Account, MaxConcurrency, Result, ImportAccountFile

# Register your models here.

admin.site.register(Tasks)
admin.site.register(Account)
admin.site.register(MaxConcurrency)
admin.site.register(Result)
admin.site.register(ImportAccountFile)
