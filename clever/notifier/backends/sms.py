# -*- coding: utf-8 -*-
import urllib
import re


class SmsHostBackend(object):

    def __init__(self, template):
        self.template = template

    def send_message(self):
        print 'sms sending'
        to_phones = self.template.to
        text = self.template.message

        API_ID = 'd4dc9702-f056-9684-2507-fcfbc161b238'
        SMS_GATE_URL = 'http://sms.ru/sms/send'

        performed_text = re.sub('\s+', '+', text)
        prepared_url = SMS_GATE_URL + '?api_id=' + API_ID + '&to=' + to_phones + '&text=' + performed_text
        print prepared_url
        urllib.urlopen(prepared_url)
