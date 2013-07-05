from rollyourown.seo.admin import get_inline
from clever.seo.settings import CLEVER_SEO_CLASS
from clever.magic import load_class


def inject_seo_inline():
    def outer_wrapper(cls):
        metadata_class = load_class(CLEVER_SEO_CLASS)

        inlines = list(getattr(cls, 'inlines', []))
        inlines.append(get_inline(metadata_class))
        cls.inlines = inlines
        return cls
    return outer_wrapper
