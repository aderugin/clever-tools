from django.forms import TextInput

class PhoneWidget(TextInput):
    class Media:
        js = ('js/jquery.maskedinput-1.3.min.js', 'admin/js/phone.js')

    def __init__(self, attrs=None):
        if not attrs:
            attrs = {}
        attrs['class'] = (attrs.pop('class', '') + ' phone').strip()
        super(TextInput, self).__init__(attrs)
