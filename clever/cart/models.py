# -*- coding: utf-8 -*-

import hashlib
from django.conf import settings


class RobokassaMixin(object):
    class Meta:
        abstract = True

    def set_status_paid(self):
        pass

    @property
    def mrchlogin(self):
        return getattr(settings, 'MRCHLOGIN')

    @property
    def mrchpass1(self):
        return getattr(settings, 'MRCHPASS1')

    @property
    def mrchpass2(self):
        return getattr(settings, 'MRCHPASS2')

    def signature(self):
        md5 = hashlib.md5()
        signature = self.mrchlogin + ':' + str(self.price) + ':' + str(self.id) + ':' + self.mrchpass1
        md5.update(signature)
        return md5.hexdigest()

