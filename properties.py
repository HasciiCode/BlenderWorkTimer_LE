import bpy

def register():
    # プロパティの登録
    bpy.types.Scene.work_timer_total_elapsed = bpy.props.FloatProperty( # type: ignore
        name="Total Elapsed",
        default=0.0,
        options={'SKIP_SAVE'}
    )
    bpy.types.Scene.work_timer_last_activity = bpy.props.FloatProperty( # type: ignore
        name="Last Activity",
        default=0.0,
        options={'SKIP_SAVE'}
    )
    bpy.types.Scene.work_timer_daily_elapsed = bpy.props.FloatProperty( # type: ignore
        name="Daily Elapsed",
        default=0.0,
        options={'SKIP_SAVE'}
    )
    bpy.types.Scene.work_timer_current_date = bpy.props.StringProperty( # type: ignore
        name="Current Date",
        default="",
        options={'SKIP_SAVE'}
    )
    bpy.types.Scene.work_timer_is_deactivated = bpy.props.BoolProperty( # type: ignore
        name="Is Deactivated",
        default=False,
        options={'SKIP_SAVE'}
    )
    
    # ポロモード用プロパティの登録
    bpy.types.Scene.polo_mode_state = bpy.props.EnumProperty( # type: ignore
        name="Polo Mode State",
        items=[
            ('WORK', 'Work Time', ''),
            ('BREAK', 'Break Time', '')
        ],
        default='WORK',
        options={'SKIP_SAVE'}
    )
    bpy.types.Scene.polo_timer_running = bpy.props.BoolProperty( # type: ignore
        name="Polo Timer Running",
        default=False,
        options={'SKIP_SAVE'}
    )
    bpy.types.Scene.polo_timer_paused = bpy.props.BoolProperty( # type: ignore
        name="Polo Timer Paused",
        default=False,
        options={'SKIP_SAVE'}
    )
    bpy.types.Scene.polo_time_remaining = bpy.props.IntProperty( # type: ignore
        name="Polo Time Remaining",
        default=1500,
        options={'SKIP_SAVE'}
    )
    bpy.types.Scene.polo_setting_work_h = bpy.props.IntProperty( # type: ignore
        name="Polo Work Time Hour",
        default=0,
        min=0
    )
    bpy.types.Scene.polo_setting_work_m = bpy.props.IntProperty( # type: ignore
        name="Polo Work Time Min",
        default=25,
        min=0,
        max=59
    )
    bpy.types.Scene.polo_setting_break_h = bpy.props.IntProperty( # type: ignore
        name="Polo Break Time Hour",
        default=0,
        min=0
    )
    bpy.types.Scene.polo_setting_break_m = bpy.props.IntProperty( # type: ignore
        name="Polo Break Time Min",
        default=5,
        min=0,
        max=59
    )

def unregister():
    props_to_remove = [
        "work_timer_total_elapsed",
        "work_timer_last_activity",
        "work_timer_daily_elapsed",
        "work_timer_current_date",
        "work_timer_is_deactivated",
        "polo_mode_state",
        "polo_timer_running",
        "polo_timer_paused",
        "polo_time_remaining",
        "polo_setting_work_h",
        "polo_setting_work_m",
        "polo_setting_break_h",
        "polo_setting_break_m"
    ]
    for prop in props_to_remove:
        if hasattr(bpy.types.Scene, prop):
            delattr(bpy.types.Scene, prop)
