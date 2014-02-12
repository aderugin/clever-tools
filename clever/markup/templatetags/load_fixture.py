from coffin import template
from clever import fixture
from clever.markup.metadata import FixtureFactory

fixture_factory = FixtureFactory()
register = template.Library()

def load_fixture(filename):
    fixture_data = fixture.load_fixture(filename)
    if fixture_data:
        return fixture_factory.convert(fixture_data)
    return fixture_data
register.object(load_fixture)
