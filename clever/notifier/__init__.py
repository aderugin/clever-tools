def send_message(slug, variables, **kwargs):
    from .models import Notification
    Notification.send(slug, variables, **kwargs)
