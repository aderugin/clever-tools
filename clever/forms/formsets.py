from django import forms
from django.forms.models import inlineformset_factory


class FormsetMixin(forms.ModelForm):
    formset_classes = None
    formsets = None

    def __init__(self, *args, **kwargs):
        # initial formset
        self.formset_classes = getattr(self, 'formset_classes', [])
        self.formsets = {}

        # call super
        super(FormsetMixin, self).__init__(*args, **kwargs)

        # fill formsets
        parent_model = self._meta.model
        for form_class in self.formset_classes:
            # fetch formset name and model
            formset_model = form_class._meta.model
            formset_name = getattr(form_class, 'prefix', formset_model.__name__.lower())

            # create formset
            inline_factory = inlineformset_factory(parent_model, formset_model, form_class, can_delete=True, extra=0)
            formset = inline_factory(prefix=formset_name,
                                     data=self.data if any(self.data) else None,
                                     files=self.files if any(self.files) else None,
                                     instance=self.instance)

            # append formset to form formsets
            self.formsets[formset_name] = formset

    def clean(self):
        for formset in self.formsets.values():
            for form in formset:
                if form not in formset.deleted_forms and not form.is_valid():
                    for field_key, field_errors in form.errors.iteritems():
                        self.errors[form.prefix + '-' + field_key] = field_errors
        return super(FormsetMixin, self).clean()

    def save(self, *args, **kwargs):
        instance = super(FormsetMixin, self).save(*args, **kwargs)
        for formset in self.formsets.values():
            formset.save()
        return instance

    @property
    def media(self):
        # collect media from formsets
        form_media = super(FormsetMixin, self).media()
        for formset in self.formsets.values():
            formset_media = formset.empty_form.media
            if formset_media:
                form_media += formset_media
        return form_media
