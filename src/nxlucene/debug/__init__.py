import sys

class DebugWrapper(object):

    def __init__(self, obj):
        self.obj = obj

    def __getattr__(self, name):
        print self.obj.__class__.__name__, self.obj.name, name
        sys.stdout.flush()
        return getattr(self.obj, name)

class DebugFactory(object):

    def __init__(self, klass):
        self.klass = klass

    def __call__(self, *args, **kw):
        instance = self.klass(*args, **kw)
        return DebugWrapper(instance)