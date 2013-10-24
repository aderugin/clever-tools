# -*- coding: utf-8 -*-
import urllib
import re
from django.conf import settings as sts


class SmsHostBackend(object):

    def __init__(self, template):
        self.template = template

    def send_message(self):
        to_phones = self.template.to
        text = self.template.message

        SMS_GATE_URL = u'http://gate.smsaero.ru/send/'

        performed_text = re.sub('\s+', '+', text)
        prepared_url = (unicode(SMS_GATE_URL) +
            u'?user=' + unicode(sts.SMS_USER) +
            u'&password=' + unicode(sts.SMS_PASSWORD) +
            u'&to=' + unicode(to_phones) +
            u'&text=' + unicode(performed_text) +
            u'&from=' + unicode(sts.DEFAULT_SMS_FROM)
        )
        urllib.urlopen(prepared_url.encode('utf-8'))
