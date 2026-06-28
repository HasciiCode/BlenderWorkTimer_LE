import bpy
from ..common import storage

def _format_time(seconds_total):
    hours = seconds_total // 3600
    minutes = (seconds_total % 3600) // 60
    seconds = seconds_total % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

class WORKTIMER_PT_panel(bpy.types.Panel):
    bl_idname = "WORKTIMER_PT_panel"
    bl_label = "Work Timer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Timer"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # 時間の計算
        app_data = storage.get_cached_app_data()
        saved_total = app_data.get("total_time_seconds", 0.0)
        saved_daily = app_data.get("daily_time_seconds", 0.0)
        
        from datetime import datetime
        today_str = datetime.now().astimezone().strftime("%Y-%m-%d")
        disk_date = app_data.get("last_active_date_local", "")
        if disk_date != today_str:
            saved_daily = 0.0
            
        session_elapsed = getattr(scene, "work_timer_session_elapsed", 0.0)
        session_daily_elapsed = getattr(scene, "work_timer_session_daily_elapsed", 0.0)
        
        total_seconds = int(saved_total + session_elapsed)
        daily_seconds = int(saved_daily + session_daily_elapsed)
        
        total_str = _format_time(total_seconds)
        daily_str = _format_time(daily_seconds)

        # 表示
        col = layout.column()
        col.label(text="Total Work Time:")
        col.label(text=total_str, icon='TIME')
        col.separator()
        col.label(text="Today's Work Time:")
        col.label(text=daily_str, icon='TIME')

classes = [
    WORKTIMER_PT_panel,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
