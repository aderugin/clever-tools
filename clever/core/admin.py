# -*- coding: utf-8 -*-

from sorl.thumbnail import get_thumbnail
from django.conf import settings


def thumbnail_column(size='106x80', **kwargs):
    """
    Формирование картинки для анонса в админке
    """

    field = kwargs.pop('field', 'image')
    crop = kwargs.pop('crop', 'center')
    quality = kwargs.pop('quality', 99)

    def real_decorator(function):
        def wrapper(self, inst):
            # Собираем изображения для вывода в админке
            images = []
            images.append(getattr(inst, field, None))
            result = function(self, inst)
            if result is not None:
                if isinstance(result, list) or isinstance(result, tuple):
                    images.extend(result)
                else:
                    images.append(result)

            # Импортируем лог для ошибок
            import logging
            logger = logging.getLogger(__name__)

            for image in images:
                try:
                    if image:
                        im = get_thumbnail(image, size, crop=crop, quality=quality)
                        return u'<img src="%s" width="%d" height="%d" />' % (im.url, im.width, im.height)
                except Exception as e:
                    logger.debug(e)
            return u'(Картинки нет)'

        # Дополнительные параметры для поля
        wrapper.admin_order_field = field
        wrapper.allow_tags = True
        wrapper.short_description = kwargs.pop('short_description', u'Изображение')
        for key, value in kwargs.items():
            setattr(wrapper, key, value)
        return wrapper
    return real_decorator


class AdminMixin(object):
    """Данный класс упрощает работу с AdminModel"""

    def _insert_list(self, name, values, before=False):
        result = getattr(self, name, [])
        if result:
            result = list(result)
        else:
            result = []
        if before:
            result = list(values) + result
        else:
            result = result + list(values)
        setattr(self, name, result)

    def insert_fields(self, fields, before=False):
        self._insert_list('fields', fields, before=before)

    def insert_list_display(self, list_display, before=False):
        self._insert_list('list_display', list_display, before=before)

    def insert_list_display_links(self, list_display_links, before=False):
        self._insert_list('list_display_links', list_display_links, before=before)

    def insert_inlines(self, inlines, before=False):
        self._insert_list('inlines', inlines, before=before)

    def insert_exclude(self, exclude, before=False):
        self._insert_list('exclude', exclude, before=before)

    def insert_filter_horizontal(self, filter_horizontal, before=False):
        self._insert_list('filter_horizontal', filter_horizontal, before=before)

    def insert_filter_vertical(self, filter_vertical, before=False):
        self._insert_list('filter_vertical', filter_vertical, before=before)

    def insert_search_fields(self, search_fields, before=False):
        self._insert_list('search_fields', search_fields, before=before)

    def insert_list_filter(self, list_filter, before=False):
        self._insert_list('list_filter', list_filter, before=before)

    def insert_dict(self, dict):
        for key, list in dict.items():
            self._insert_list(key, list)


class AdminFieldsetsMixin(object):
    primary_fieldsets = None

    def get_primary_fieldsets(self, request, obj=None):
        return self.primary_fieldsets

    def get_fieldsets(self, request, obj=None):
        primary_fieldsets = self.get_primary_fieldsets(request, obj)
        if primary_fieldsets:
            form = self.get_form(request, obj, fields=None)
            fields = list(form.base_fields) + list(self.get_readonly_fields(request, obj))

            for fieldset_name, fieldset_params in primary_fieldsets:
                for field in fieldset_params.get('fields', []):
                    fields.remove(field)

            return list(primary_fieldsets) + [
                (None, {'fields': fields})
            ]
        return super(AdminFieldsetsMixin, self).get_fieldsets(self, request, obj)
