from django.contrib import admin
from .models import Template
from .models import SmsTemplate
from .models import Notification
from .models import Variable
from django.conf import settings


class BaseTemplateAdmin(admin.ModelAdmin):

    class Media:
        js = (
            '%snotifier/notifier.js' % settings.STATIC_URL,
        )

        css = {
            'screen': ('%snotifier/notifier.css' % settings.STATIC_URL,),
        }


class VariableInline(admin.StackedInline):
    model = Variable
    extra = 1


class NotificationAdmin(admin.ModelAdmin):
    inlines = [VariableInline]
    list_display = ('name', 'slug')


class TemplateAdmin(BaseTemplateAdmin):
    list_display = ('subject', 'notification', 'active', 'email_from', 'email_to')
    list_filter = ('active',  'notification__name', )


class SmsTemplateAdmin(BaseTemplateAdmin):
    list_display = ('__unicode__', 'to', 'notification', 'active')
    list_filter = ('active',  'notification__name', )


admin.site.register(Notification, NotificationAdmin)
admin.site.register(Template, TemplateAdmin)
admin.site.register(SmsTemplate, SmsTemplateAdmin)
