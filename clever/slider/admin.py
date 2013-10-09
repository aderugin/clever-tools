from django.contrib import admin
from .models import Item
from .models import Slider
from clever.core.admin import thumbnail_column
from .settings import CLEVER_SLIDER_HAS_EDIT
from .settings import CLEVER_SLIDER_HAS_DELETE


# admin.StackedInline
class ItemInline(admin.TabularInline):
    model = Item
    readonly_fields = ('admin_thumbnail',)
    fields = ('admin_thumbnail', 'active', 'sort', 'title', 'url', 'image')
    extra = 0

    @thumbnail_column(size='200x150')
    def admin_thumbnail(self, inst):
        return [inst.image]


class SliderAdmin(admin.ModelAdmin):
    readonly_fields = ('slug', )
    list_display = ['title', 'slug', 'active', 'created_at']
    inlines = (ItemInline, )

    def has_add_permission(self, request, obj=None):
        return CLEVER_SLIDER_HAS_EDIT

    def has_delete_permission(self, request, obj=None):
        return CLEVER_SLIDER_HAS_DELETE

admin.site.register(Slider, SliderAdmin)
