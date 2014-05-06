# -*- coding: utf-8 -*-
from django.contrib.sites.models import Site
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Don't use "from appname.models import ModelName". 
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.

        content_type = ContentType.objects.get_for_model(Site)
        Permission.objects.create(codename='can_edit_settings', name='Can edit site settings', content_type=content_type)

    def backwards(self, orm):
        "Write your backwards methods here."

    models = {
        
    }

    complete_apps = ['settings']
    symmetrical = True
