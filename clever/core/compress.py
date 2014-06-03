from compressor.filters.base import CompilerFilter
import os


class RequireFilter(CompilerFilter):
    def __init__(self, content, *args, **kwargs):
        super(RequireFilter, self).__init__(content, '$(npm bin)/r.js -o {infile}', **kwargs)

        self.dirname = os.path.dirname(self.filename)
        self.filename = os.path.basename(self.filename)

    def input(self, **kwargs):
        current_dir = os.getcwd()
        try:
            os.chdir(self.dirname)
            return super(RequireFilter, self).input(**kwargs)
        finally:
            os.chdir(current_dir)