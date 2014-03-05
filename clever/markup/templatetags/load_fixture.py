import logging
from coffin import template
from clever import fixture
from clever.markup.metadata import fixture_factory
from clever.markup.metadata import MetadataError

register = template.Library()

def load_fixture(filename):
    log = logging.getLogger('clever.markup')

    # Load fixture
    log.info("Load fixture from '%s'", filename)
    fixture_data = fixture.load_fixture(filename)
    if fixture_data:
        try:
            log.error("Convert fixture from '%s'", filename)
            return fixture_factory.convert(fixture_data)
        except MetadataError as e:
            log.error("Convert fixture from '%s' is failed with error %s", filename, e.message)
            e.message = "%s in '%s'" % (e.message, filename)
            raise
    return fixture_data
register.object(load_fixture)
