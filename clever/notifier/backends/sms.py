# -*- coding: utf-8 -*-
import urllib
import re


class SmsHostBackend(object):

    def __init__(self, template):
        self.template = template

    def send_message(self):
        to_phones = self.template.to
        text = self.template.message

 
        API_ID = u'd4dc9702-f056-9684-2507-fcfbc161b238'
        SMS_GATE_URL = u'http://sms.ru/sms/send'

        performed_text = re.sub('\s+', '+', text)
        prepared_url = unicode(SMS_GATE_URL) + u'?api_id=' + unicode(API_ID) + u'&to=' + unicode(to_phones) + u'&text=' + unicode(performed_text)
        urllib.urlopen(prepared_url.encode('utf-8'))
