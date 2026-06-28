from . import operator
from . import ui

def register():
    operator.register()
    ui.register()

def unregister():
    ui.unregister()
    operator.unregister()
