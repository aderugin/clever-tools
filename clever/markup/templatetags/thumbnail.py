from sorl.thumbnail.shortcuts import get_thumbnail
from coffin.template import Library
register = Library()

@register.object()
def thumbnail(file_, geometry_string, **options):
    try:
        im = get_thumbnail(file_, geometry_string, **options)
    except IOError:
        im = None
    return im
