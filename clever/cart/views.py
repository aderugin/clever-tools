# -*- coding: utf-8 -*-

import hashlib
from django.http import HttpResponse
from django.views.generic import View
from django.views.generic import TemplateView


class RoboResultView(View):
    model = None
    
    def get(self, request, *args, **kwargs):
        InvId = request.GET.get('InvId', None)
        OutSum = request.GET.get('OutSum', None)
        remote_crc = request.GET.get('SignatureValue', '').upper()

        if (InvId == None):
            return HttpResponse('ERROR: NOT SET InvId')

        if (OutSum == None):
            return HttpResponse('ERROR: NOT SET OutSum')

        if (remote_crc == ''):
            return HttpResponse('ERROR: NOT SET SignatureValue')

        try:
            order_obj = self.model.objects.get(id=InvId, status=1)
            md5 = hashlib.md5()
            md5.update(str(OutSum) + ':' + str(InvId) + ':' + order_obj.mrchpass2)
            local_crc = md5.hexdigest().upper()
            if (local_crc == remote_crc):
                order_obj.set_status_paid()
                return HttpResponse('OK' + str(InvId))
            else:
                return HttpResponse('ERROR: CRC NOT VALID')
        except Exception, e:
            return HttpResponse('ERROR: %e' % e)


class RoboSuccessView(TemplateView):
    template_name = 'cart/succesful.html'
    model = None

    def get(self, request, *args, **kwargs):
        InvId = request.GET.get('InvId', None)
        OutSum = request.GET.get('OutSum', None)
        remote_crc = request.GET.get('SignatureValue', '').upper()
        order_obj = self.model.objects.get(id=InvId)
        md5 = hashlib.md5()
        md5.update(str(OutSum) + ':' + str(InvId) + ':' + order_obj.mrchpass2)
        local_crc = md5.hexdigest().upper()
        if (local_crc == remote_crc):
            context = self.get_context_data(**kwargs)
            context['object'] = order_obj
            return self.render_to_response(context)
        else:
            return HttpResponseNotFound()
