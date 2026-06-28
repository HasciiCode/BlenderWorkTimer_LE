import bpy

def get_scene(context=None):
    if context:
        scene = getattr(context, 'scene', None)
        if scene:
            return scene
            
    scene = getattr(bpy.context, 'scene', None)
    if not scene and bpy.data.scenes:
        scene = bpy.data.scenes[0]
    return scene

def format_time_str(seconds_total):
    hours = seconds_total // 3600
    minutes = (seconds_total % 3600) // 60
    seconds = seconds_total % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"