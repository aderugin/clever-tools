from mptt.models import MPTTModel
from django.db import models


def create_mptt_class(orm_class, base_class):
    class MPTTMigrateModel(MPTTModel):
        class Meta:
            app_label = 'catalog'
            db_table = orm_class._meta.db_table

        class MPTTMeta:
            parent_attr = base_class._mptt_meta.parent_attr

    fields = {}
    for field in MPTTMigrateModel._meta.fields:
        fields[field.name] = True


    for field in orm_class._meta.fields:
        if not fields.get(field.name, False) and not isinstance(field, models.AutoField):
            MPTTMigrateModel.add_to_class(field.name, field)
    return MPTTMigrateModel
