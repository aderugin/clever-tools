# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
class DeferredPoint(object):
    '''
    Базовый класс для предоставления создания 'отложенных точек' - абстрактных
    классов для последующего использования в проектах
    '''
    def __init__(self, name):
        self.__dict__['__consumers'] = []
        self.__dict__['__instance'] = None
        self.__dict__['__name'] = name

    def resolve_deferred_point(self, target_model):
        if self.__dict__['__instance']:
            raise RuntimeError('Deffered point already is resolved')
        self.__dict__['__instance'] = target_model

        # Обновляем потребителей данной точки
        for consumer in self.__dict__['__consumers']:
            consumer.resolve_deferred_point(target_model)
        self.__dict__['__consumers'] = []

    def resolve_deferred_consumer(self, consumer):
        # Обновляем потребителя если модель уже установленна
        if self.__dict__['__instance']:
            consumer.resolve_deferred_point(self.__dict__['__instance'])
        # Иначе добавляем в список ждущих потребителей
        else:
            self.__dict__['__consumers'].append(consumer)

    def connect_deferred_consumer(self, consumer):
        # self.__dict__['__consumers'].append(consumer)
        pass

    def get_deferred_instance(self):
        if not self.__dict__['__instance']:
            name = self.__dict__['__name']
            raise RuntimeError("Не найден конкретный класс для %s" % name)
        return self.__dict__['__instance']

    @property
    def deferred_instance(self):
        ''' Найден ли конкретный класс '''
        if not self.__dict__['__instance']:
            return False
        return True

    def __getattr__(self, name):
        instance = self.get_deferred_instance()
        return getattr(instance, name)

    def __setattr__(self, name, value):
        instance = self.get_deferred_instance()
        return setattr(instance, name, value)

    def __call__(self, *args, **kwargs):
        instance = self.get_deferred_instance()
        return instance(*args, **kwargs)


# ------------------------------------------------------------------------------
class DeferredConsumer(object):
    ''' Объект использующий `отложенную точку` '''
    def __init__(self, point):
        self.point = point
        self.point.connect_deferred_consumer(self)
        self.consumer_name = ''
        self.consumer_model = None

    def resolve_deferred_point(self, target_model):
        raise NotImplementedError()


# ------------------------------------------------------------------------------
class DeferredMetaclass(type):
    ''' Строчка для подготовки магии отложенных ключей '''
    def __init__(meta, name, bases, attribs):
        super(DeferredMetaclass, meta).__init__(name, bases, attribs)

        consumers = []

        # Подготовка аттрибутов
        for name, consumer in attribs.items():
            if isinstance(consumer, DeferredConsumer):
                consumer.consumer_model = meta
                consumer.consumer_name = name
                consumers.append(consumer)

        # Расширение отложенной точки до оригинального класса
        if not getattr(meta, '_meta', None) or not getattr(meta._meta, 'abstract', False):
            point = getattr(meta, 'point', None)
            if point:
                point.resolve_deferred_point(meta)

        # Попытка создать реальные данные
        for consumer in consumers:
            consumer.point.resolve_deferred_consumer(consumer)

    @classmethod
    def for_consumer(self, *bases):
        class ConsumerDeferredMetaclass(DeferredMetaclass):
            pass
        ConsumerDeferredMetaclass.__bases__ += tuple(bases)
        return ConsumerDeferredMetaclass

    @classmethod
    def for_point(self, point, *bases):
        class PointDeferredMetaclass(DeferredMetaclass):
            pass
        PointDeferredMetaclass.point = point
        PointDeferredMetaclass.__bases__ += tuple(bases)
        return PointDeferredMetaclass


# ------------------------------------------------------------------------------
class DefferedObject(object):
    __metaclass__ = DeferredMetaclass


# ------------------------------------------------------------------------------
def deferred_object(point):
    def deferred_wrapper(cls):
        point.resolve_deferred_point(cls)
        return cls
    return deferred_wrapper
