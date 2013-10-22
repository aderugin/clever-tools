# -*- coding: utf-8 -*-
from rollyourown import seo


class SeoMetadata(seo.Metadata):
    title = seo.Tag(head=True, max_length=1000)
    description = seo.MetaTag(max_length=1000)
    keywords = seo.KeywordTag()
    heading = seo.Tag(name="h1", max_length=1000)

    class Meta:
        use_sites = False
        use_i18n = False
        use_cache = False

        seo_models = tuple()
        seo_views = tuple()
        backends = ('path', 'modelinstance', 'model', 'view')

        verbose_name = "СЕО параметр"
        verbose_name_plural = "СЕО параметры"
