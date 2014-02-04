# -*- coding: utf-8 -*-

import hashlib
from django.conf import settings


class RobokassaMixin(object):
    robokassa_field = 'status'
    robokassa_status = 1

    def set_status_paid(self):
        pass

    @property
    def mrchurl(self):
        return getattr(settings, 'ROBOKASSA_MRCHURL', 'https://auth.robokassa.ru/Merchant/Index.aspx')

    @property
    def mrchlogin(self):
        return getattr(settings, 'ROBOKASSA_MRCHLOGIN')

    @property
    def mrchpass1(self):
        return getattr(settings, 'ROBOKASSA_MRCHPASS1')

    @property
    def mrchpass2(self):
        return getattr(settings, 'ROBOKASSA_MRCHPASS2')

    @property
    def signature(self):
        md5 = hashlib.md5()
        signature = self.mrchlogin + ':' + str(self.price) + ':' + str(self.id) + ':' + self.mrchpass1
        md5.update(signature)
        return md5.hexdigest()

