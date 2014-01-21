# -*- coding: utf-8 -*-
import time
import os
import hotshot

def profile(prefix):
    """Декоратор для оценки производительности сайта"""
    def wrapper(callback):
        def gen_name():
            pid = os.getpid()
            timestr = time.strftime("%Y-%m-%d-%H-%M-%S")
            return prefix + '.' + str(timestr) + '.' + str(pid) + '.prof'
        def generate_profile(*args, **kwargs):
            prof = hotshot.Profile(gen_name())
            prof.start()
            result = callback(*args, **kwargs)
            prof.stop()
            return result
        return generate_profile
    return wrapper
