from django import forms


class FormsetMixin(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.formset_classes = []
        self.form_list = []
        super(FormsetMixin, self).__init__(*args, **kwargs)

    def clean(self):
        for form_class in self.formset_classes:
            factory = forms.formsets.formset_factory(form_class, can_delete=True)
            formset = factory(prefix=getattr(form_class, 'prefix', form_class._meta.model.__name__.lower()),
                              data=self.data, files=self.files)
            for form in formset:
                self.form_list.append(form)
                if not form.is_valid():
                    for field_key, field_errors in form.errors.iteritems():
                        self.errors[form.prefix + '-' + field_key] = field_errors
        return super(FormsetMixin, self).clean()

    def save(self, *args, **kwargs):
        for form in self.form_list:
            form.save()
        super(FormsetMixin, self).save(*args, **kwargs)
