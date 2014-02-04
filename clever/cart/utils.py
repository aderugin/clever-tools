from urllib import urlencode


def generate_robokassa_url(order):
    url = order.mrchurl
    params = {
        'MrchLogin': str(order.mrchlogin),
        'OutSum': str(order.price),
        'InvId': str(order.id),
        'SignatureValue': str(order.signature),
    }
    return "%s?%s" % (url, urlencode(params))

