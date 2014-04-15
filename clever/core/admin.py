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

    def insert_raw_id_fields(self, raw_id_fields, before=False):
        self._insert_list('raw_id_fields', raw_id_fields, before=before)

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
            form = super(AdminFieldsetsMixin, self).get_form(request, obj, fields=None)
            fields = list(form.base_fields) + list(self.get_readonly_fields(request, obj))

            for fieldset_name, fieldset_params in primary_fieldsets:
                for field in fieldset_params.get('fields', []):
                    fields.remove(field)

            return list(primary_fieldsets) + [
                (None, {'fields': fields})
            ]
        return super(AdminFieldsetsMixin, self).get_fieldsets(self, request, obj)


class TabPanel:
    label = None
    inlines = []
    fieldsets = []

    is_active = False

    def __init__(self, label, fieldsets=[], inlines=[], **kwargs):
        self.label = label
        self.fieldsets = fieldsets
        self.inlines = inlines


class AdminTabbedMixin(object):
    tabs = []
    change_form_template = 'admin/tabbed/change_form.html'

    def __init__(self, *args, **kwargs):
        super(AdminTabbedMixin, self).__init__(*args, **kwargs)

    @property
    def media(self):
        base_media = super(AdminTabbedMixin, self).media
        base_media.add_css({
            'all': [
                'css/admin.css'
            ]
        })
        return base_media

    def find_inlines(self, inline_declr, inline_formsets):
        inlines = []

        def isinline(name):
            def wrapper(formset):
                formset_name = formset.opts.__class__.__name__
                return name == formset_name
            return wrapper

        for name in inline_declr:
            for x in filter(isinline(name), inline_formsets):
                inlines.append(x)

        return inlines

    def find_fieldsets(self, fieldset_declr, adminform):
        fieldsets = []

        def isfieldset(name):
            def wrapper(fieldset):
                return fieldset.name == name
            return wrapper

        for name in fieldset_declr:
            for x in filter(isfieldset(name), adminform):
                fieldsets.append(x)
        return fieldsets

    def get_tabs(self, inline_admin_formsets, adminform):
        tabs = []
        for tab in self.tabs:
            label = tab[0]
            params = tab[1]

            fieldsets = self.find_fieldsets(params.get('fieldsets',[]), adminform)
            inlines = self.find_inlines(params.get('inlines', []), inline_admin_formsets)
            panel = TabPanel(label, fieldsets, inlines)
            if not tabs:
                panel.is_active = True
            tabs.append(panel)
        return tabs

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update({
            'admintabs': self.get_tabs(context.get('inline_admin_formsets'), context.get('adminform'))
        })
        return super(AdminTabbedMixin, self).render_change_form(request, context, add, change, form_url, obj)