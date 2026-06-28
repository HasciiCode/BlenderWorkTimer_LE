import bpy
from ..common import utils

class WORKTIMER_PT_panel(bpy.types.Panel):
    bl_idname = "WORKTIMER_PT_panel"
    bl_label = "Work Timer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Timer"

    def draw(self, context):
        layout = self.layout
        scene = utils.get_scene(context)
        if not scene:
            return

        # メモリ上で常に最新の時間が更新されているので、そのまま読み取る
        total_seconds = int(getattr(scene, "work_timer_total_elapsed", 0.0))
        daily_seconds = int(getattr(scene, "work_timer_daily_elapsed", 0.0))
        
        total_str = utils.format_time_str(total_seconds)
        daily_str = utils.format_time_str(daily_seconds)

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
