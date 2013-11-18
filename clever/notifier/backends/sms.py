# -*- coding: utf-8 -*-
import urllib
import re
from django.conf import settings


class SmsHostBackend(object):

    def __init__(self, template):
        self.template = template

    def send_message(self):
        to_phones = self.template.to
        text = self.template.message

 
        SMS_GATE_URL = u'http://sms.ru/sms/send'

        performed_text = re.sub('\s+', '+', text)
        prepared_url = (unicode(SMS_GATE_URL)
                + u'?api_id=' + unicode(settings.API_ID)
                + u'&to=' + unicode(to_phones)
                + u'&text=' + unicode(performed_text)
        )
        urllib.urlopen(prepared_url.encode('utf-8'))
