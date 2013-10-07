# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Slider'
        db.create_table(u'slider_slider', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('updated_at', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=50, populate_from='title', unique_with=())),
        ))
        db.send_create_signal(u'slider', ['Slider'])

        # Adding model 'Item'
        db.create_table(u'slider_item', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('model_utils.fields.AutoCreatedField')(default=datetime.datetime.now)),
            ('updated_at', self.gf('model_utils.fields.AutoLastModifiedField')(default=datetime.datetime.now)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('slider', self.gf('django.db.models.fields.related.ForeignKey')(related_name='items', to=orm['slider.Slider'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('image', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'slider', ['Item'])


    def backwards(self, orm):
        # Deleting model 'Slider'
        db.delete_table(u'slider_slider')

        # Deleting model 'Item'
        db.delete_table(u'slider_item')


    models = {
        u'slider.item': {
            'Meta': {'object_name': 'Item'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created_at': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'slider': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': u"orm['slider.Slider']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'updated_at': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'slider.slider': {
            'Meta': {'object_name': 'Slider'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created_at': ('model_utils.fields.AutoCreatedField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "'title'", 'unique_with': '()'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated_at': ('model_utils.fields.AutoLastModifiedField', [], {'default': 'datetime.datetime.now'})
        }
    }

    complete_apps = ['slider']