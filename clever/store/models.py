# -*- coding: utf-8 -*-
from django.db import models
from django_fsm.db.fields import FSMField
from django_fsm.db.fields import transition
from clever.deferred import DeferredPoint
from clever.deferred.fields import DeferredForeignKey
from clever.deferred.fields import DeferredManyToManyField
from clever.deferred.models import DeferredModelMetaclass
from clever.deferred.models import DeferredMetaclass
from clever.core.models import TimestableMixin
from clever.catalog.models import Product
from clever.core.models import extend_meta
from decimal import Decimal

# ------------------------------------------------------------------------------
Order = DeferredPoint('Order')

# ------------------------------------------------------------------------------
Item = DeferredPoint('Item')

# ------------------------------------------------------------------------------
Delivery = DeferredPoint('Delivery')

# ------------------------------------------------------------------------------
Payment = DeferredPoint('Payment')


# ------------------------------------------------------------------------------
class DeliveryBase(models.Model):
    ''' способ доставки '''
    class Meta:
        abstract = True
    __metaclass__ = DeferredModelMetaclass.for_point(
        Delivery,
        extend_meta(
            verbose_name=u'Способ доставки',
            verbose_name_plural=u'Способы доставок'
        )
    )

    name = models.CharField(u'Название', max_length=255)
    sort = models.PositiveIntegerField(u'Сортировка', default=100)
    text = models.TextField(u'Краткое описание', blank=True)

    def __unicode__(self):
        return self.name


# ------------------------------------------------------------------------------
class PaymentBase(models.Model):
    ''' способ оплаты '''
    class Meta:
        abstract = True
    __metaclass__ = DeferredModelMetaclass.for_point(
        Payment,
        extend_meta(
            verbose_name=u'Способ оплаты',
            verbose_name_plural=u'Способы оплаты'
        )
    )

    # delivery = DeferredForeignKey(Delivery, verbose_name=u'Доставка', related_name='payments')
    name = models.CharField(u'Название', max_length=100)
    text = models.TextField(u'Краткое описание', blank=True)
    sort = models.PositiveIntegerField(u'Сортировка', default=100)

    def __unicode__(self):
        return self.name


# ------------------------------------------------------------------------------
class OrderBase(TimestableMixin, models.Model):
    ''' Базовый класс для информации о заказе '''
    class Meta:
        abstract = True
    __metaclass__ = DeferredModelMetaclass.for_point(
        Order,
        extend_meta(
            verbose_name=u'Заказ',
            verbose_name_plural=u'Заказы'
        )
    )

    # # Стандартные статусы
    # NEW = 'new'

    # # Названия статусов
    # STATUSES = (
    #     (NEW, u'Новый заказ'),
    # )

    # Информация о пользователе
    user_name = models.CharField(verbose_name=u'ФИО пользователя', max_length=300, blank=True)
    user_email = models.EmailField(verbose_name=u'Email пользователя', blank=True, null=True)
    user_phone = models.CharField(verbose_name=u'телефон пользователя', max_length=20)

    # Информация о оплате и доставке
    # status = FSMField(verbose_name=u'Статус заказа', default=NEW)
    delivery = DeferredForeignKey(Delivery, verbose_name=u'Способ доставки', blank=True, null=True)
    payment = DeferredForeignKey(Payment, verbose_name=u'Способ оплаты', blank=True, null=True)
    address = models.TextField(blank=True, verbose_name=u'Адрес')

    # delivery_date = models.DateField(verbose_name=u'Дата доставки', blank=True, null=True, max_length=100)
    delivery_time = models.CharField(verbose_name=u'Удобные дата и время для доставки', blank=True, max_length=100)

    # Информация об стоимости
    price = models.DecimalField(verbose_name=u'Общая стоимость заказа', default=Decimal(0.00), decimal_places=2, max_digits=10)
    delivery_price = models.DecimalField(verbose_name=u'Стоимость доставки', default=Decimal(0.00), decimal_places=2, max_digits=10, null=True)
    discount_price = models.DecimalField(verbose_name=u'Общая стоимость заказа с учетом скидки', default=Decimal(0.00), decimal_places=2, max_digits=10, null=True)

    discount_amount = models.DecimalField(verbose_name=u'Скидка в процентах', default=Decimal(0.00), decimal_places=2, max_digits=10, null=True, blank=True)
    discount_code = models.CharField(verbose_name=u'Код на скидку', max_length=50, null=True, blank=True)
    crated_at = models.DateField(auto_now_add=True)

    # Дополнительная информация о
    comment = models.TextField(blank=True, verbose_name=u'Комментарий к заказу')
    # to_1c = models.BooleanField(verbose_name=u'Экспортировать в 1С', default=False)
    # code = models.CharField(verbose_name=u'1С ID', max_length=50, blank=True)


# ------------------------------------------------------------------------------
class ItemBase(models.Model):
    ''' Базовый класс для информации о продукте в заказе '''
    class Meta:
        abstract = True
    __metaclass__ = DeferredModelMetaclass.for_point(
        Item,
        extend_meta(
            verbose_name=u'Товар',
            verbose_name_plural=u'Товары'
        )
    )

    product = DeferredForeignKey(Product, verbose_name=u'Товар')
    quantity = models.IntegerField(verbose_name=u'Количество', default=1)
    price = models.DecimalField(verbose_name=u"Цена", default=Decimal(0.00), decimal_places=2, max_digits=10)

    order = DeferredForeignKey(Order, verbose_name=u"Заказ", related_name='items')
