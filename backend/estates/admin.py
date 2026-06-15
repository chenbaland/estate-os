from django.contrib import admin

from estates.models import Block, Estate, Unit


@admin.register(Estate)
class EstateAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "city", "tier", "is_active", "total_units")
    list_filter = ("estate_type", "tier", "is_active", "country")
    search_fields = ("name", "slug", "city")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "estate", "floor_count", "is_active")
    list_filter = ("is_active",)


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("unit_number", "estate", "block", "unit_type", "occupancy_status", "owner")
    list_filter = ("unit_type", "occupancy_status", "is_active")
    search_fields = ("unit_number",)
