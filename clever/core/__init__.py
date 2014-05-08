# -*- coding: utf-8 -*-
from sorl.thumbnail.shortcuts import get_thumbnail


def fail_safe_thumbnail(image, geometry_string, **options):
    """ fail safe get_thumbnail """
    try:
        return get_thumbnail(image, geometry_string, **options).url
    except:
        return None


def make_a_tree(obj_list, parent_obj_attr, tree_index_attr='id'):
    """
    создает структурированный словарь списков
        obj_list: генератор
        parent_obj_attr: аттрибут в котором хранится ссылка на родительский объект
        tree_index_attr: аттрибут родительского объекта, использующийся как идентификатор в словаре
    """
    tree = {}
    for obj in obj_list:
        parent_obj = getattr(obj, parent_obj_attr)
        tree_index = getattr(parent_obj, tree_index_attr, 0)
        if tree_index not in tree:
            tree[tree_index] = []
        tree[tree_index].append(obj)
    return tree


class TreeMixin(object):
    tree_dict = {}
    tree_index_attr = 'id'

    def get_from_tree(self):
        return type(self).tree_dict[getattr(self, self.tree_index_attr)]
