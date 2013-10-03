# -*- coding: utf-8 -*-
from django.forms.models import inlineformset_factory


class FormsetMixin(object):
    '''
    Миксин для добавления поддержки Formset'ов

    Заполнить аттрибут класса formsets:

        class ProductForm(FormsetMixin, forms.ModelForm)
            formsets = {
                'images_1': (ImageForm, 'product', {}),
                'images_2': [ImageForm, 'product', {}],
                'images_3': (ImageForm, 'product'),
                'images_4': [ImageForm, 'product'],
            }

    '''
    formsets = {}

    def __init__(self, *args, **kwargs):
        super(FormsetMixin, self).__init__(*args, **kwargs)

        formsets_params = self.formsets
        self.formsets = {}
        for name, formoption in formsets_params.items():
            # Приводим в порядок
            formoption = list(formoption)
            formoption[1] = formoption[1] if len(formoption) > 1 else None
            formoption[2] = formoption[2] if len(formoption) > 2 else None
            form_class, fk_name, form_kwargs = formoption

            if not form_class:
                raise RuntimeError(u'Незадана форма для formset\'а')
            if not fk_name:
                raise RuntimeError(u'Незадано имя ForeignKey для главной формы у formset\'а')

            # Базовые параметры
            form_kwargs.setdefault('extra', 1)
            model = form_kwargs.get('form', None)
            if not model:
                meta = getattr(form_class, 'Meta', None)
                model = getattr(meta, 'model', None)
                if not model:
                    raise RuntimeError(u'Незадана модель для formset\'а')

            # Создаем
            #import pdb; pdb.set_trace()
            formset = inlineformset_factory(self.Meta.model, model,
                    form=form_class)
            if 'data' in kwargs:
                form = formset(kwargs.get('data'), kwargs.get('files'), instance=self.instance)
            else:
                form = formset(instance=self.instance)
            self.formsets[name] = (form, fk_name, model)

    def __getattr__(self, name):
        if name in self.formsets:
            return self.formsets[name][0]
        return getattr(super(FormsetMixin, self), name)

    def is_valid(self):
        return super(FormsetMixin, self).is_valid() and all([formset[0].is_valid() for name, formset in self.formsets.items()])

    def save(self, commit=True):
        instance = super(FormsetMixin, self).save(commit=commit)
        for name, formset_option in self.formsets.items():
            formset, fk_name, formset_model = formset_option
            for formset_form in formset.cleaned_data:
                if len(formset_form):
                    formset_form[fk_name] = instance
                    formset_instance = formset_model(**formset_form)
                    save_handler = getattr(self, 'save_' + name, None)
                    if save_handler:
                        save_handler(formset, formset_instance, formset_form, commit)
                    formset_instance.save()
        return instance
