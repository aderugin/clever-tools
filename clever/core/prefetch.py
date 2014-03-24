# -*- coding: utf-8 -*-
import uuid

# Empty object
class UndefinedClass:
    pass
Undefined = UndefinedClass()


def create_prefetch(prefetch_func, default=None):
    # генерация ключа для хранения вычесляемого свойства
    cache_id = unicode(uuid.uuid4())

    # Обертка для создания объекта
    def wrapper(self):
        value = getattr(self, cache_id, Undefined)
        if value is Undefined:
            manager = self.__class__.objects
            result = prefetch_func(self.__class__, manager.filter(pk=self.pk))
            try:
                value = [i for i in next(result)[1]]
            except StopIteration:
                value = default
            setattr(self, cache_id, value)
        return value
    return wrapper


def prefetch_property(prefetch_func):
    '''
    Данный декоратор создает свойство с возможность получения отдельного вычесляемого
    значения, как отдельного экземпляра модели, так и для результата запроса.
    '''
    return property(create_prefetch(prefetch_func, default=None))


def prefetch_collection(prefetch_func):
    '''
    Данный декоратор создает свойство с возможность получения списка вычесляемых значений,
    как отдельного экземпляра модели, так и для результата запроса.
    '''

    # Обертка для свойства
    return property(create_prefetch(prefetch_func, default=[]))
