class FieldsetMixin(object):
    fieldsets = {}
    
    def __init__(self, *args, **kwargs):
        super(FieldsetMixin, self).__init__(*args, **kwargs)
        fields_by_name = {field.name: field for field in self.visible_fields()}
        for set_name, set_fields in self.fieldsets.iteritems():
            setattr(self, 'fieldset_' + set_name, [fields_by_name[field] for field in set_fields])
