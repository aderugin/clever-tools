Модуль верстки
==============

Шаблоные тэги и фильтры
-----------------------

* `load_fixture` - Загрузка данныз с рыбой
    * `name`     - Путь до файла с рыбой

Использование в шаблонах Jinja
------------------------------

    {% set products = load_fixture("test.yaml") %}
