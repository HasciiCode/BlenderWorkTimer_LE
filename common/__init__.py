from . import storage
from . import timer

def register():
    storage.register()
    timer.register()

def unregister():
    timer.unregister()
    storage.unregister()