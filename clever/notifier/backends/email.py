# -*- coding: utf-8 -*-
from django.core.mail import EmailMessage


class DefaultEmailBackend(object):

    def __init__(self, template):
        self.template = template

    def send_message(self):

        to_emails = self.template.email_to.split(',')
        for to in to_emails:
            message = EmailMessage(self.template.subject, self.template.message, self.template.email_from, [to.strip()])
            message.content_subtype = 'html'
            message.send()
