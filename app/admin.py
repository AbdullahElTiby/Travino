from django.contrib import admin
from .models import CustomUser,Category,Place,Description,Audio

# Register your models here.

admin.site.register(CustomUser),
admin.site.register(Place),
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'suggestion', 'description']

admin.site.register(Category, CategoryAdmin)
admin.site.register(Description),
admin.site.register(Audio),



