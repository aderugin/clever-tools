# -*- coding: utf-8 -*-
from coffin import template
from clever import fixture
from clever.markup.metadata import FixtureFactory

fixture_factory = FixtureFactory()
register = template.Library()

# def load_fixture(filename):
#     fixture_data = fixture.load_fixture(filename)
#     if fixture_data:
#         return fixture_factory.convert(fixture_data)
#     return fixture_data
# register.object(load_fixture)


@register.object
@register.filter
def phone_format(var, format):
    import pdb; pdb.set_trace()
    # try:
    #     primary_format = self.format.resolve(context)
    #     format = re.sub("[^# ]", "", primary_format)
    #     if primary_format != format:
    #         raise TemplateSyntaxError('Phone format must containts only whitespaces and symbol #')
    #     count = len(re.sub(" ", "", format))
    # except template.VariableDoesNotExist:
    #     return ''

    # # Retreive phone
    # try:
    #     phone = self.variable.resolve(context)
    #     phone = unicode(phone)
    #     phone = re.sub("[^0-9+]", "", phone)
    # except template.VariableDoesNotExist:
    #     return ''

    # # Self
    # format_groups = re.findall('#+', format)

    # # Phone extend
    # spaces = ' ' * (count - len(phone))
    # phone_extend = spaces + phone
    # formated = []
    # for group in format_groups:
    #     length = len(group)
    #     formated.append(phone_extend[0:length])
    #     phone_extend = phone_extend[length:]

    # "## ### ### ## ##"
