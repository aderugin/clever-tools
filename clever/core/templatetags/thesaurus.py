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
def thesaurus_columns(thesaurus_dict, columns_count):
    letters_dict = thesaurus_dict['dictonary']
    if not len(letters_dict):
        return []

    letters_size = map(lambda x: 2 + len(x[1]), letters_dict.items())
    letters_size1, letters_size2 = itertools.tee(letters_size)
    letters_height = sum(letters_size1)
    letters_count = letters_height // columns_count + (1 if letters_height % columns_count else 0)

    columns = []

    current_iter = iter(letters_dict)
    current_letter = next(current_iter)
    current_list = iter(letters_dict[current_letter])
    is_first = True

    def create_letter(is_first):
        return {
            'is_first': is_first,
            'items': []
        }

    for i in xrange(0, columns_count):
        column = OrderedDict()
        column[current_letter] = create_letter(is_first)

        for j in xrange(0, letters_count):
            try:
                item = next(current_list)
            except StopIteration:
                try:
                    current_letter = next(current_iter)
                    is_first = True
                except StopIteration:
                    break
                column[current_letter] = create_letter(is_first)
                current_list = iter(letters_dict[current_letter])
            column[current_letter]['items'].append(item)
        is_first = False
        columns.append(column)
    return columns
