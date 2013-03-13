#coding: utf-8


def update_offers_quantity(order):
    """
    Update quantity in items
    item storage cant be minus val
    """
    for order_item in order.order_items.all():
        if order_item.catalog_item.storage >= order_item.quantity:
            order_item.catalog_item.storage = order_item.catalog_item.storage - order_item.quantity
        else:
            order_item.catalog_item.storage = 0
        order_item.catalog_item.save()
