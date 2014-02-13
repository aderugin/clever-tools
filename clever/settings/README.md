Настройки для сайта
===================

Шаблоные тэги и фильтры
-----------------------


* `get_option` - Получение значения настройки из базы данныхЖ
    * `name`    - Имя настройки
    * `default` - Значение по умолчанию, [None]

Использование в шаблонах Django:
--------------------------------

    {% load settings_tags %}

    {{ 'contact_phone' | get_option() }}
    {{ 'contact_phone' | get_option("83433422334") }}

Использование в шаблонах Jinja
------------------------------

    {% set phone = get_option('contact_phone') %}
    {% set phone = get_option('contact_phone', "83433422334") %}
