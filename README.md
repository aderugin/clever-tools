Clever Tools
============

Базовый функционал для использования в проектах Clever Promo основных на Django.

Компоненты для внутреннего использования
----------------------------------------

* `clever.core` - Базовый функционал для остальных компонентов пакета
* `clever.bem` - Функционал для использования BEM-шаблонов в качестве базовых файлов [NOT WORKED]
* `clever.fabric` - Функционал для скриптов развертывания [NOT WORKED]

Базовый функционал для модулей сайта
------------------------------------

* `clever.catalog` - Функционал для каталога интернет-магазина [NOT TESTED]
* `clever.search` - Функционал для поиска по сайту
* `clever.store` - Функционал для корзины товаров в интернет-магазине [NOT WORKED]

Программы для использования
---------------------------

* `clever-install-python` - Установка Python 2.7 в виртуальном окружении
* `clever-install-redis` - Установка key-value базы данных Redis в виртуальном окружении
* `clever-install-xapian` - Установка поискового движка Xapian в виртуальном окружении

Добавилась поддержка фильтрации по атрибутам подкатегорий

Различные помошники и миксины для моделей
-----------------------------------------

* **generate\_upload\_name** (`clever.core.models.generate_upload_name`)
    - Генерация пути для загруженного файла в папке MEDIA_ROOT

            image = models.ImageField(upload_to=generate_upload_name, verbose_name=u'Изображение', null=True, blank=True)

* **TimestableMixin** (`clever.core.models.TimestableMixin`)
    - Добавление даты создания и изминения в модель
    - `created_at` - Дата создания экземпляра модели
    - `updated_at` - Дата обновления экземпляра модели

* **ActivableMixin** (`clever.core.models.ActivableMixin`)
    - Добавление поля об активности (`active`)

* **TitleMixin** (`clever.core.models.TitleMixin`)
    - Добавление заголовка и фрагмента ЧПУ в модель
    - `title` - Заголовок экземпляра модели
    - `slug` - Фрагмент ЧПУ экземпляра модели, генерируемый на основе `title

* **PageMixin** (`clever.core.models.TitleMixin`)
    - `image` - Изображение экземпляра модели (главное)
    - `text` - Текст экземпляра модели

Удаление мусора
---------------

Для удаления мусора из папки с превью изображений (`MEDIA_ROOT/thumbs`) можно
надо добавить в `INSTALLED_APPS` приложение `clever.cleanup`

Настройки сайта
---------------

Для хранения настроек сайта в БД можно воспользоваться приложением `clever.settings`

Установка приложения:

* Добавить `clever.settings` в `INSTALLED_APPS`
* Добавить в даш админки (`dashboard.py`) ссылку в список ссылок (`modules.LinkList`):

        {
            'title': _(u'Настройки сайта'),
            'url': reverse('admin:site_settings'),
            'external': False,
        }
* Имена полей в любой модели унаследованной от `clever.settings.base.SettingsModel`
  будет доступны ка названия параметра.
* В коде Python'а параметр можно получить с помощью функции `clever.settings.get_option`,
  принимающей в качестве аргумента имя параметра.

Пример модели (`models.py`):

    from clever.settings import base as settings
    from django.db import models

    class ContactSettings(settings.SettingsModel):
        class Meta:
            verbose_name = u"Контактные настройки"
        contact_email = models.EmailField(u'Контактный email', default=u'info@dragee.ru')

Использование (допустим в `view.py`):

    from clever.settings import get_option
    contact_email = get_option('contact_email')

Отправка email и sms при помощи Notifier.
---------------------------

После подключения приложения в `settings.py`, для отправки сообщения необходимо сделать три вещи:

* Создать событие. Событие - не сущность(буквально это не событие), а просто строка, к которой привязываются шаблоны.
* Создать шаблоны, у email и sms у каждого свои классы для шаблонов


У шаблонов есть свои переменные. В тексте шаблона их надо вызывать как `#VAR_NAME#`, при отправке писем
их надо передавать в виде словаря `vars = {'VAR_NAME': var_value, }`

Непосредственно отправка писем идет как `Notification.send('notification_name', variable_dictionary)`