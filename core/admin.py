from django.contrib import admin

from .models import ContactRequest


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ("full_name", "company", "service", "email", "phone", "created_at")
    list_filter = ("service", "created_at")
    search_fields = ("full_name", "company", "email", "phone", "location", "message")
    readonly_fields = ("created_at",)
