from django.db.models import get_apps
import importlib


class FixtureManager:
    fixtures = []
    is_loaded = False

    def register_fixture(self, cls, title=None, count=100):
        self.fixtures.append({
            'fixture': cls,
            'count': count,
            'title': title
        })

    def load_fixtures(self):
        if not self.is_loaded:
            self.is_loaded = True
            for app in get_apps():
                app_module = '.'.join((app.__name__).split('.')[:-1])
                try:
                    fixture_module = importlib.import_module("%s.%s" % (app_module, "fixture"))
                except ImportError as e:
                    pass
        return self.fixtures


_fixture = FixtureManager()
register_fixture = _fixture.register_fixture
load_fixtures = _fixture.load_fixtures
