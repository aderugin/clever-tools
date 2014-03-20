def prepare_fields_from(instance):
    fields = {x.name: None for x in instance._meta.fields}
    for field in fields:
        fields[field] = getattr(instance, field)
    if hasattr(instance, 'get_notifier_context'):
        fields = instance.get_notifier_context(fields)
    return fields

def send_message(slug, variables, **kwargs):
    from .models import Notification
    Notification.send(slug, variables, **kwargs)
