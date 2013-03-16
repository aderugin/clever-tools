# -*- coding: utf-8 -*-
"""
:mod:`clever.store.models` -- Модели базовой корзины каталога
=============================================================

В данном модуле хранится базовый набор моделей для работы с корзиной каталога.

.. moduleauthor:: Василий Шередеко <piphon@gmail.com>
"""


import hashlib
from django.db import models


class StoreSettings(models.Model):
    class Meta:
        verbose_name = u'Настройки'
        verbose_name_plural = u'Настройки'

    def __unicode__(self):
        return u'Настройки модуля магазина'

    show_confirm_block = models.BooleanField(u'Блок подтверждения по телефону', default=True)
    confirm_no_label = models.CharField(u'Подтверждение не требуется: заголовок', blank=True, max_length=100)
    confirm_no_description = models.TextField(u'Подтверждение не требуется: описание', blank=True)
    confirm_yes_label = models.CharField(u'Подтверждение требуется: заголовок', blank=True, max_length=100)
    confirm_yes_description = models.TextField(u'Подтверждение требуется: описание', blank=True)


class OrderDiscount(models.Model):
    class Meta:
        verbose_name = u'скидка от стоимости заказа'
        verbose_name_plural = u'скидки от стоимости заказа'

    price = models.DecimalField(u'Сумма заказа', max_digits=10, decimal_places=2)
    value = models.PositiveIntegerField(u'Величина скидки в %', unique=True)

    def __unicode__(self):
        return u'суииа от ' + str(self.price) + u' / скидка: ' + str(self.value) + '%'

    active = None
    estimated = 0


class DeliveryLocation(models.Model):
    class Meta:
        verbose_name = u'местоположение для доставки'
        verbose_name_plural = u'местоположения для доставки'

    name = models.CharField(u'Название', max_length=100)
    sort = models.PositiveIntegerField(u'Сортировка', default=100)

    def __unicode__(self):
        return self.name


class Delivery(models.Model):

    class Meta:
        verbose_name = u'способ доставки'
        verbose_name_plural = u'способы доставки'

    # TYPE_CHOICES = (
    #     ('withpayment', u'С использованием алгоритма'),
    #     (None, u'Без использования алогоритма')
    # )

    # type = models.CharField(u'Тип', max_length=50, choices=TYPE_CHOICES)
    name = models.CharField(u'Название', max_length=255)
    sort = models.PositiveIntegerField(u'Сортировка', default=100)
    text = models.TextField(u'Краткое описание', blank=True)

    def __unicode__(self):
        return self.name


class LocationDeliveryCost(models.Model):

    class Meta:
        verbose_name = u'стоимость доставки'
        verbose_name_plural = u'стоимости доставки'

    delivery = models.ForeignKey(Delivery, related_name='locationdeliverycosts')
    location = models.ForeignKey(DeliveryLocation, related_name='locationdeliverycosts')
    price = models.DecimalField(u'Стоимость доставки', max_digits=10, decimal_places=2)
    free_delivery_from = models.DecimalField(u'Бесплатная доставка от', max_digits=10, decimal_places=2, blank=True, null=True)

    def __unicode__(self):
        return "[%s]" % self.location.name


class Payment(models.Model):
    class Meta:
        verbose_name = u'способ оплаты'
        verbose_name_plural = u'способы отплаты'

    PAYMENT_CHOISES = (
        ('', u'Без платежного шлюза'),
        ('Robokassa', u'Робокасса (тест)')
    )

    delivery = models.ManyToManyField(Delivery, verbose_name=u'Доставка', related_name='payments')
    gateaway = models.CharField(u'Платежный шлюз', max_length=50, choices=PAYMENT_CHOISES, blank=True)
    name = models.CharField(u'Название', max_length=100)
    text = models.TextField(u'Краткое описание', blank=True)
    sort = models.PositiveIntegerField(u'Сортировка', default=100)

    def __unicode__(self):
        return self.name


class Order(models.Model):

    class Meta:
        verbose_name = u'Заказ'
        verbose_name_plural = u'Заказы'
        ordering = ['-id', ]

    # TODO: Статусы сделать с помощью state machine

    NEW = 'new'
    CONFIRM = 'confirm'
    CONFIRM_WAIT_ONLINE_PAYMENT = 'confirm_wait_online_payment'
    CONFIRM_ONLINE_PAYMENT = 'confirm_online_payment'
    COMPLETED = 'completed'
    CANCELED = 'canceled'

    STATUS_CHOICES = (
        (NEW, u'Принят, ожидает подтверждения'),
        (CONFIRM, u'Подтвержден'),
        (CONFIRM_WAIT_ONLINE_PAYMENT, u'Подтвержден, ожидается онлайн оплата'),
        (CONFIRM_ONLINE_PAYMENT, u'Подтвержден и оплачен онлайн'),
        (COMPLETED, u'Выполнен'),
        (CANCELED, u'Отменен'),
    )

    status = models.CharField(u'Статус', max_length=50, choices=STATUS_CHOICES)

    user_name = models.CharField(max_length=300, blank=True, verbose_name=u'ФИО пользователя')
    user_email = models.EmailField(u'Email пользователя', blank=True)
    user_phone = models.CharField(max_length=20, blank=True, verbose_name=u'телефон пользователя')
    #user = models.ForeignKey('users.CleverUser', blank=True, null=True, verbose_name=u'Пользователь')

    delivery = models.ForeignKey(Delivery, verbose_name=u'Способоб доставки')
    payment = models.ForeignKey(Payment, verbose_name=u'Способо оплаты')
    location = models.CharField(verbose_name=u'Местоположение', max_length=200, blank=True)
    adress = models.CharField(max_length=255, verbose_name=u'Адрес')
    delivery_cost = models.DecimalField(verbose_name=u'Стоимость доставки', max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(verbose_name=u'Общая стоимость заказа', max_digits=10, decimal_places=2, default=0)
    total_cost_with_sale = models.DecimalField(verbose_name=u'Общая стоимость заказа с учетом скидки', max_digits=10, decimal_places=2, default=0)
    delivery_date = models.CharField('Дата доставки', blank=True, max_length=100)
    delivery_time = models.CharField('Время доставки', blank=True, max_length=100)
    need_confirm = models.BooleanField('Требуется подтверждение', default=False)
    comment = models.TextField(blank=True, verbose_name=u'Комментарий к заказу')
    created_at = models.DateTimeField(auto_now=True, verbose_name=u'Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name=u'Дата обновления')
    to_1c = models.BooleanField(verbose_name=u'Экспортировать в 1С', default=False)
    code = models.CharField(verbose_name=u'1С ID', max_length=50, blank=True)

    @property
    def is_confirmed(self):
        return self.status == self.CONFIRM

    @property
    def is_new(self):
        return self.status == self.NEW

    def signature(self):
        md5 = hashlib.md5()
        signature = self.mrchlogin + ':' + str(self.total_cost_with_sale) + ':' + str(self.id) + ':' + self.mrchpass1
        md5.update(signature)
        return md5.hexdigest()

    def __unicode__(self):
        return str(self.pk)


#class OrderItem(models.Model):

    #class Meta:
        #verbose_name = u'товар'
        #verbose_name_plural = u'товары'

    #catalog_item = models.ForeignKey(Item, verbose_name=u'Товар')
    #quantity = models.IntegerField(u'Количество', default=1)
    #price = models.DecimalField(u'Цена', max_digits=9, decimal_places=2)
    #order = models.ForeignKey(Order, related_name='order_items')
    #sale = models.PositiveIntegerField(verbose_name=u'Размер скидки', blank=True, default=0, help_text=u'В процентах')
    #on_request = models.BooleanField(verbose_name=u'Под заказ', default=False)


class OrderStatusHistory(models.Model):
    """ Save order history, for control change statuses """

    class Meta:
        ordering = ['-pk']

    order = models.ForeignKey(Order)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now=True, verbose_name=u'Дата создания')

    @classmethod
    def get_last_order_status(cls, order):
        """ Find last order row """
        try:
            return OrderStatusHistory.objects.filter(order=order)[:1][0]
        except:
            return None


class OrderStatus(models.Model):
    """
    Дополнительная информаци об отдельном статусе заказа
    """
    status = models.CharField(u'Статус', max_length=50, choices=Order.STATUS_CHOICES, unique=True)
    message = models.TextField(verbose_name=u'Текст', help_text=u'Текст в пользовательском профиле')

    class Meta:
        verbose_name = u'Статус заказа'
        verbose_name_plural = u'Статусы заказа'
        ordering = ['status', ]
