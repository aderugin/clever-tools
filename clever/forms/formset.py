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

    Использование: унаследовать класс от FromserMixin, создать поле formsets
    типа dict (словарь), ключом этого словаря будет поле по которому потом
    будет доступен formset из объекта формы. В значенем данного элемента будет
    объект типа tuple (кортэж). В этом кортеже должны быть следующие элементы:
    1) Класс ФОРМЫ модели, объекты которой связаны по Foreignkey с текущим
    объектом
    2) Название поля типа Foregnkey дочерней модели (та, что привязывается по 
    данному полю)
    3) Объект типа dict, значения которого будут переданы как дополнительные
    аргументы при создании formset'a (**kwargs)
    Пример:
    formsets = {
        'included_files': (AttachedPhotosForm, 'offer', {'can_delete': True, 'extra': 0})
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
            meta = getattr(form_class, 'Meta', None)
            model = getattr(meta, 'model', None)
            if not model:
                raise RuntimeError(u'Незадана модель для formset\'а')

            # Создаем
            form_kwargs['form'] = form_class
            formset = inlineformset_factory(self.Meta.model, model, **form_kwargs)
            kwargs['instance'] = self.instance
            form = formset(**kwargs)
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
            formset.save()
        return instance
