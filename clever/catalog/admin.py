# -*- coding: utf-8 -*-

from django.contrib import admin
from feincms.admin import editor
from django import forms
from ckeditor.widgets import CKEditorWidget
from clever.core.admin import thumbnail_column
from clever.core.admin import AdminMixin
from clever.catalog import models
from clever.catalog import tasks
from clever.catalog.forms import FilterForm
from clever.catalog.attributes import AttributeManager
from clever.magic.classmaker import classmaker
from clever.seo.admin import inject_seo_inline
from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

# ------------------------------------------------------------------------------
from mptt.forms import TreeNodeChoiceField


class SectionParamsIterator(forms.models.ModelChoiceIterator):
    def __init__(self, inline, field, section):
        self.section = section
        self.inline = inline

        super(SectionParamsIterator, self).__init__(field)

    def __iter__(self):
        related_manager = self.inline.related_model.objects

        # Получение родительских элементов
        parents = [self.section]  # self.get_parents()

        # Поиск элементов присуствующих в данном разделе
        field_name = self.inline.filter_field + '__in'
        filter = {
            field_name: parents
        }
        items_ids = related_manager.filter(**filter).values_list('id', flat=True).distinct()

        # Поиск значений для вывода
        if (len(items_ids)):
            items_used = related_manager.filter(id__in=items_ids)
            items_nonused = related_manager.exclude(id__in=items_ids)
            if items_used.count():
                # yield (u'', None),
                yield (u'Используемые', [(item.id, unicode(item),) for item in items_used])
                yield (u'Неиспользуемые', [(item.id, unicode(item),) for item in items_nonused])
                return

        # Возвращаем значения по умолчанию
        for item in related_manager.all():
            yield (item.id, unicode(item),)


# ------------------------------------------------------------------------------
class SectionParamsInline(admin.TabularInline):
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        value = super(SectionParamsInline, self).get_formset(request, obj, **kwargs)
        if obj:
            value.form.base_fields[self.field_name].choices = SectionParamsIterator(
                self,
                value.form.base_fields[self.field_name],
                obj
            )
        return value


# ------------------------------------------------------------------------------
class SectionForm(forms.ModelForm):
    class Meta:
        widgets = {
            'text': CKEditorWidget(config_name='default')
        }

# ------------------------------------------------------------------------------
@inject_seo_inline()
class BrandAdmin(AdminMixin, admin.ModelAdmin):
    def __init__(self, model, *args, **kwargs):
        super(BrandAdmin, self).__init__(model, *args, **kwargs)

        self.insert_list_display(['admin_thumbnail', 'active'], before=True)
        self.insert_list_display(['slug'])

        self.insert_list_display_links(['admin_thumbnail', '__unicode__', '__str__'])

    @thumbnail_column(size='106x80')
    def admin_thumbnail(self, inst):
        """ Выводит картинку а админке """
        return [inst.image]


# ------------------------------------------------------------------------------
@inject_seo_inline()
class SectionAdmin(AdminMixin, editor.TreeEditor):
    """
    ..todo: Протестировать все!
    """
    form = SectionForm

    def __init__(self, model, *args, **kwargs):
        super(SectionAdmin, self).__init__(model, *args, **kwargs)

        self.insert_list_display(['admin_thumbnail', 'active'], before=True)
        self.insert_list_display(['slug'])

        self.insert_list_display_links(['admin_thumbnail', '__unicode__', '__str__'])

        inlines_objects = []
        # Создание inline редактора для свойств товара
        if models.SectionBrand.deferred_instance:
            brand_inline = type(model.__name__ + "_SectionBrandInline", (SectionParamsInline,), {
                'model': models.SectionBrand,
                'field_name': 'brand',
                'related_model': models.Brand,
                'filter_field': 'products__section',
            })
            inlines_objects.append(brand_inline)

        if models.SectionAttribute.deferred_instance:
            attribute_inline = type(model.__name__ + "_SectionAttributeInline", (SectionParamsInline,), {
                'model': models.SectionAttribute,
                'field_name': 'attribute',
                'related_model': models.Attribute,
                'filter_field': 'values__product__section',
            })
            inlines_objects.append(attribute_inline)

        self.insert_inlines(inlines_objects, before=True)

    @thumbnail_column(size='106x80')
    def admin_thumbnail(self, inst):
        """ Выводит картинку а админке """
        return [inst.image]

    def clear_cache(self, request):
        tasks.invalidate_catalog.delay()
        return redirect(reverse('admin:catalog_section_changelist'))

    def get_urls(self):
        urls = super(SectionAdmin, self).get_urls()

        my_urls = patterns(
            '',
            url(r'^clear_cache/$', self.clear_cache, name='catalog_clear_cache'),
        )
        return my_urls + urls


# ------------------------------------------------------------------------------
class AttributeForm(forms.ModelForm):
    def clean_control(self):
        # Хак для проверки типа для диапазона типов
        control = self.cleaned_data['control']
        type = self.cleaned_data['type']
        if control == u'range' and type not in [u'integer', u'float']:
            raise forms.ValidationError("Диапазон значений может использоваться только с числовыми типами")
        return control


# ------------------------------------------------------------------------------
class AttributeAdmin(AdminMixin, admin.ModelAdmin):
    form = AttributeForm

    def __init__(self, model, admin_site, *args, **kwargs):
        list_display_items = ['code', 'group', 'type', 'control']
        list_filter_items = ['group', 'type', 'control']

        if not models.AttributeGroup.deferred_instance:
            list_display_items.remove('group')
            list_filter_items.remove('group')

        self.insert_list_display(list_display_items)
        self.insert_list_filter(list_filter_items)
        self.insert_search_fields(['title'])

        super(AttributeAdmin, self).__init__(model, admin_site, *args, **kwargs)


# ------------------------------------------------------------------------------
class ProductAttributeInline(AdminMixin, admin.TabularInline):
    extra = 0

    def __init__(self, *args, **kwargs):
        super(ProductAttributeInline, self).__init__(*args, **kwargs)

        exclude = []
        for type_name, type in AttributeManager.get_types():
            exclude.append(type.field_name)
        self.insert_exclude(exclude)
        self.insert_fields(['attribute', 'raw_value', 'real_value'])

    def get_readonly_fields(self, request, obj=None):
        return list(super(ProductAttributeInline, self).get_readonly_fields(request, obj)) + ['real_value']

    def real_value(self, instance):
        return instance.value
    real_value.short_description = u'Реальное значение'


# ------------------------------------------------------------------------------
class ProductForm(forms.ModelForm):
    class Meta:
        widgets = {
            'text': CKEditorWidget(config_name='default')
        }


# ------------------------------------------------------------------------------
@inject_seo_inline()
class ProductAdmin(AdminMixin, admin.ModelAdmin):
    """
    ..todo: Протестировать все!
    """
    form = ProductForm

    def __init__(self, model, admin_site, *args, **kwargs):
        # Добавляем базовые элементы в админку
        self.insert_list_display(['admin_thumbnail'], before=True)
        list_display_items = ['active', 'section', 'brand', 'price', 'code']
        list_filter_items = ['brand', 'section']

        if not models.Section.deferred_instance:
            list_display_items.remove('section')
            list_filter_items.remove('section')

        if not models.Brand.deferred_instance:
            list_display_items.remove('brand')
            list_filter_items.remove('brand')

        self.insert_list_display(list_display_items)
        self.insert_list_filter(list_filter_items)
        self.insert_list_display_links(['admin_thumbnail', '__unicode__', '__str__'])
        self.insert_search_fields(['title'])

        # Создание inline редактора для свойств товара
        if models.ProductAttribute.deferred_instance:
            product_attribute_inline = type(model.__name__ + "_ProductAttributeInline", (ProductAttributeInline,), {
                'model': models.ProductAttribute,
            })
            self.insert_inlines([product_attribute_inline])

        super(ProductAdmin, self).__init__(model, admin_site, *args, **kwargs)

    @thumbnail_column(size='106x80')
    def admin_thumbnail(self, inst):
        """ Выводит картинку а админке """
        return [inst.image]


# ------------------------------------------------------------------------------
class PseudoSectionValueInline(AdminMixin, admin.TabularInline):
    # form = PseudoSectionValueForm
    extra = 1

    def __init__(self, *args, **kwargs):
        super(PseudoSectionValueInline, self).__init__(*args, **kwargs)

        exclude = []
        for type_name, type in AttributeManager.get_types():
            exclude.append(type.field_name)
        self.insert_exclude(exclude)
        self.insert_fields(['attribute', 'raw_value', 'raw_value_to', 'real_value', 'real_value_to'])

    def get_readonly_fields(self, request, obj=None):
        return list(super(PseudoSectionValueInline, self).get_readonly_fields(request, obj)) + [
            'real_value',
            'real_value_to'
        ]

    def real_value(self, instance):
        return instance.value
    real_value.short_description = u'Реальное значение'

    def real_value_to(self, instance):
        return instance.value_to
    real_value.short_description = u'Реальное значение'


# ------------------------------------------------------------------------------
class PseudoSectionBrandInline(admin.TabularInline):
    extra = 1


# ------------------------------------------------------------------------------
class PseudoSectionForm(forms.ModelForm):
    class Meta:
        widgets = {
            'text': CKEditorWidget(config_name='default')
        }


# ------------------------------------------------------------------------------
@inject_seo_inline()
class PseudoSectionAdmin(AdminMixin, admin.ModelAdmin):
    form = PseudoSectionForm

    def __init__(self, model, admin_site, *args, **kwargs):
        super(PseudoSectionAdmin, self).__init__(model, admin_site, *args, **kwargs)

        # Добавляем базовые элементы в админку
        self.insert_list_display(['active', 'section', 'slug'])
        self.insert_list_display_links(['admin_thumbnail', '__unicode__', '__str__'])
        # self.insert_fields(['brand'])

        # Создание inline редактора для свойств товара
        pseudo_section_value_inline = type(model.__name__ + "_PseudoSectionValueInline", (PseudoSectionValueInline,), {
            'model': models.PseudoSectionValue,
        })
        product_attribute_inline = type(model.__name__ + "_PseudoSectionBrandInline", (PseudoSectionBrandInline,), {
            'model': models.PseudoSectionBrand,
        })

        self.insert_inlines([
            pseudo_section_value_inline,
            product_attribute_inline
        ])
