# -*- coding: utf-8 -*-
from django import template
register = template.Library()


@register.filter
def nearby(lst, obj, count=9):
    '''
    Поиску элементов находящихся около объекта obj в списке lst
    Source: http://lethain.com/a-filter-to-display-neighbors-in-a-list/
    '''
    import pprint
    pp = pprint.PrettyPrinter(indent=4, depth=6)
    pp.pprint((lst))

    lst = list(lst)
    l = len(lst)
    try:
        pos = lst.index(obj)
    except ValueError:
        pos = 0
    dist = count / 2

    # import pdb; pdb.set_trace()
    if l <= count:
        return lst
    elif pos <= dist:
        return lst[:count]
    elif pos >= l - dist:
        return lst[l-count:]
    else:
        return lst[pos-dist:pos+dist+1]
