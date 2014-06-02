

from django.core.files.images import ImageFile
from django.core.files.storage import get_storage_class
from coffin.template.library import Library
from django.conf import settings
import os
register = Library()


@register.filter
def static_image(path):
    """
    {% thumbnail "img/default_avatar.png"|static_image "50x50" as img %}
        <img src="{{ MEDIA_URL }}{{img}}"/>
    {% endthumbnail %}
    """
    storage_class = get_storage_class(settings.STATICFILES_STORAGE)
    storage = storage_class()
    path = os.path.join(settings.STATIC_ROOT, path)
    image = ImageFile(storage.open(path))
    image.storage = storage
    return image