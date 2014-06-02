from compressor.filters.base import CompilerFilter
import os


class RequireFilter(CompilerFilter):
    def __init__(self, content, *args, **kwargs):
        super(RequireFilter, self).__init__(content, '$(npm bin)/r.js -o {infile}', **kwargs)

    def input(self, **kwargs):
        dir = os.path.dirname(self.filename)
        current_dir = os.getcwd()
        try:
            os.chdir(dir)
            result = super(RequireFilter, self).input(**kwargs)
            # import ipdb; ipdb.set_trace()
            return result
        finally:
            os.chdir(current_dir)