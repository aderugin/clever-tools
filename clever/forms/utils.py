# -*- coding: utf-8 -*-


class FilterFieldMixin(object):
    def filter(self, value):
        """
        Filter value before validate
        """
        raise NotImplementedError()

    def clean(self, value):
        """
        Validates the given value and returns its "cleaned" value as an
        appropriate Python object.

        Raises ValidationError for any errors.
        """
        value = self.to_python(value)
        value = self.filter(value)
        self.validate(value)
        self.run_validators(value)
        return value
