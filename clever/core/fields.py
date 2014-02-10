# -*- coding: utf-8 -*-
#author: Semen Pupkov (semen.pupkov@gmail.com)
from __future__ import absolute_import
import urlparse
import re
from django.db import models
from django import forms
from django.utils.translation import ugettext_lazy as _


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
            return parsed_url.path
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

# Import info for south
try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_introspection_rules([],  ["^clever\.core\.fields\.YoutubeUrlField",])
