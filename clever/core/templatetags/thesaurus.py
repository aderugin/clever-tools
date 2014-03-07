# -*- coding: utf-8 -*-
from coffin import template
from collections import OrderedDict
import itertools

register = template.Library()

class ThesaurusError(Exception):
    pass

@register.object
def thesaurus(input_list, field):
    result = {}

    russian = set()
    english = set()
    numbers = set()

    for items in input_list:
        # find first leter and add to national list
        try:
            title = getattr(items, field).strip() # This exception is not error
        except AttributeError:
            raise ThesaurusError(u'Field `%s` not found in element of input list' % field)

        if not len(title):
            continue

        letter = title[0].upper()
        if letter.isdigit():
            letter = ''.join(list(itertools.takewhile(lambda t: t.isdigit(), items.title)))
            numbers.add(letter)
        elif u'А' <= letter and letter <= u'Я':
            russian.add(letter)
        else:
            english.add(letter)

        # create new letter in result
        if not letter in result:
            result[letter] = []

        # append items to result
        result[letter].append(items)

    # sort listes
    russian = sorted(russian)
    english = sorted(english)
    numbers = sorted(numbers)

    # reorder result dictanary
    ordered = OrderedDict()
    for letter in itertools.chain(russian, english, numbers):
        ordered[letter] = None
    ordered.update(result)

    # return result
    return {
        'letters': [russian, english, numbers],
        'dictonary': ordered,
    }



@register.object
def thesaurus_columns(thesaurus_dict, size):
    letters_list = thesaurus_dict['dictonary']
    import ipdb; ipdb.set_trace()
    # height = sum(map(lambda x: 2 + len(x), letters_list))

