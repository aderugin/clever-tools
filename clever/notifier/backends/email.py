# -*- coding: utf-8 -*-
from django.core.mail import EmailMessage
from django.core.validators import validate_email

class DefaultEmailBackend(object):

    def __init__(self, template):
        self.template = template

    def send_message(self):

        to_emails = self.template.email_to.split(',')
        for to in to_emails:
            email_to = to.strip()
            try:
                validate_email(email_to)
                validate_email( self.template.email_from )
                message = EmailMessage(self.template.subject, self.template.message, self.template.email_from, [email_to])
                message.content_subtype = 'html'
                message.send()
            except:
                pass