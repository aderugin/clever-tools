# -*- coding: utf-8 -*-
#author: Semen Pupkov (semen.pupkov@gmail.com)
from __future__ import absolute_import
import urlparse
import re
from django.db import models
from django import forms
from django.utils.translation import ugettext_lazy as _
from clever.forms.phone import PhoneWidget


def validate_youtube_url(value):
    '''El patron lo saque de http://stackoverflow.com/questions/2964678/jquery-youtube-url-validation-with-regex'''
    pattern = r'^http:\/\/(?:www\.)?youtube.com\/watch\?(?=.*v=\w+)(?:\S+)?$'

    if value[:16] == u'http://youtu.be/':
        pass
        #lif re.match(r'\w+', value[16:]) is None:
        #if va
            #raise forms.ValidationError(_('Not a valid Youtube URL'))
    elif re.match(pattern, value) is None:
        raise forms.ValidationError(_('Not a valid Youtube URL'))


class YoutubeUrl(unicode):
    @property
    def video_id(self):
        parsed_url = urlparse.urlparse(self)
        if parsed_url.query == '':
            return parsed_url.path.strip('/')
        return urlparse.parse_qs(parsed_url.query)['v'][0]

    @property
    def embed_url(self):
        return 'http://youtube.com/embed/%s/' % self.video_id

    @property
    def thumb(self):
        return "http://img.youtube.com/vi/%s/2.jpg" % self.video_id

    @property
    def default_image(self):
        return "http://img.youtube.com/vi/%s/0.jpg" % self.video_id

    def __call__(self, *args, **kwargs):
        return unicode(self)

class YoutubeUrlField(models.URLField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        super(YoutubeUrlField, self).__init__(*args, **kwargs)
        self.validators.append(validate_youtube_url)

    def to_python(self, value):
        url = super(YoutubeUrlField, self).to_python(value)
        return YoutubeUrl(url)

    def get_prep_value(self, value):
        return unicode(value)


class FileSizeField(models.IntegerField):
    __metaclass__ = models.SubfieldBase

    validators = []
    units = ('b', 'kb', 'mb', 'gb', 'tb',)
    help_text = u'Возможные единицы измерения: b,kb,mb,gb,tb пример: 10mb'

    @staticmethod
    def parse(value):
        import re
        match = re.match(r'(\d+)(\w+)', value)
        if match:
            return {
                'value': match.groups()[0],
                'units': match.groups()[1],
            }
        else:
            return None

    class PythonConverted(int):
        def __unicode__(self):
            import decimal
            value = decimal.Decimal(self)
            for unit in FileSizeField.units:
                if value / 1024 > 1:
                    value /= 1024
                else:
                    return unicode(value) + unit

        def __int__(self):
            import decimal
            match = FileSizeField.parse(self)
            if not match:
                return self
            return int(decimal.Decimal(match['value']) * (1024 ** FileSizeField.units.index(match['units'])))

    def to_python(self, value):
        value = super(FileSizeField, self).to_python(value)
        return self.PythonConverted(value)

    def get_db_prep_value(self, value, connection, prepared=False):
        match = FileSizeField.parse(value)
        return int(value) if match else value


class PhoneField(models.CharField):
    phone_format = '+7 (999) 999-99-99'

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.pop('max_length', len(self.phone_format))

        super(PhoneField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        defaults = {
            'widget': PhoneWidget
        }
        defaults.update(kwargs)
        return super(PhoneField, self).formfield(**defaults)


# Import info for south
try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_introspection_rules([],  ["^clever\.core\.fields\.YoutubeUrlField",])
    add_introspection_rules([],  ["^clever\.core\.fields\.PhoneField",])
