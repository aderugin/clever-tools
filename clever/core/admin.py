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
                #try:
                if image:
                    im = get_thumbnail(image, size, crop=crop, quality=quality)
                    return u'<img src="%s%s" />' % (settings.MEDIA_URL, im)
                #except Exception, e:
                #    logger.debug(e)
            return u'(Картинки нет)'

        # Дополнительные параметры для поля
        wrapper.admin_order_field = field
        wrapper.allow_tags = True
        wrapper.short_description = kwargs.pop('short_description', u'Изображение')
        for key, value in kwargs.items():
            setattr(wrapper, key, value)
        return wrapper
    return real_decorator


def insert_in_list(self, name, values, before=False):
    result = list(getattr(self, name, []))
    if before:
        result = list(values) + result
    else:
        result = result + list(values)
    setattr(self, name, result)


class AdminMixin:
    """Данный класс упрощает работу с AdminModel"""

    def insert_list_display(self, list_display, before=False):
        insert_in_list(self, 'list_display', list_display, before=before)

    def insert_list_display_links(self, list_display_links, before=False):
        insert_in_list(self, 'list_display_links', list_display_links, before=before)

    def insert_inlines(self, inlines, before=False):
        insert_in_list(self, 'inlines', inlines, before=before)
