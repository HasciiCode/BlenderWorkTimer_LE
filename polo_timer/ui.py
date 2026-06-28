import bpy

# 機能概要
# サイドバーに表示するポロモードタイマーのUIパネル
# 来歴
# - [VR001ID003-01] UIの配置場所
# - [VR001ID003-02] タイマーUIの構成と状態表示
# 引数
# context: bpy.context
# 戻り値: なし
class WORKTIMER_PT_polo_panel(bpy.types.Panel):
    bl_idname = "WORKTIMER_PT_polo_panel"
    bl_label = "Polo Mode Timer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Timer"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # 状態の表示
        state_str = "Work Time:" if scene.polo_mode_state == 'WORK' else "Break Time:"
        col = layout.column(align=True)
        col.label(text=state_str)
        
        # 残り時間の表示
        rem_sec = scene.polo_time_remaining
        time_str = f"{rem_sec // 3600:02d}:{(rem_sec % 3600) // 60:02d}:{rem_sec % 60:02d}"
        col.label(text=time_str, icon='TIME')
        
        col.separator()
        
        # ボタン行
        row = col.row(align=True)
        
        # Toggle
        toggle_text = "Start"
        toggle_icon = 'PLAY'
        if scene.polo_timer_running:
            if not scene.polo_timer_paused:
                toggle_text = "Stop"
                toggle_icon = 'PAUSE'
            else:
                toggle_text = "Resume"
                toggle_icon = 'PLAY'
        row.operator("worktimer.polo_toggle", text=toggle_text, icon=toggle_icon)
        
        # Reset
        reset_row = row.row(align=True)
        # Pause状態のときのみ活性
        if not (scene.polo_timer_running and scene.polo_timer_paused):
            reset_row.enabled = False
        reset_row.operator("worktimer.polo_reset", text="Reset", icon='FILE_REFRESH')
        
        # Settings
        settings_row = row.row(align=True)
        # 実行中は非活性
        if scene.polo_timer_running and not scene.polo_timer_paused:
            settings_row.enabled = False
        settings_row.operator("worktimer.polo_settings", text="Settings", icon='PREFERENCES')

classes = [
    WORKTIMER_PT_polo_panel,
]

# 機能概要
# polo_timerのUIクラス群を登録する
# 来歴
# - なし
# 引数
# なし
# 戻り値: なし
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

# 機能概要
# polo_timerのUIクラス群の登録を解除する
# 来歴
# - なし
# 引数
# なし
# 戻り値: なし
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
