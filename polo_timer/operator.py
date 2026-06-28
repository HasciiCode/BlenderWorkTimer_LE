import bpy

# 機能概要
# ポロモードタイマーのStart/Stop/Resumeトグル機能
# 来歴
# - [VR001ID003-02] タイマーUIの構成と状態表示
# 引数
# context: bpy.context
# 戻り値: 実行結果 {'FINISHED'}
class WORKTIMER_OT_polo_toggle(bpy.types.Operator):
    bl_idname = "worktimer.polo_toggle"
    bl_label = "Toggle Polo Timer"

    def execute(self, context):
        scene = context.scene
        
        if not scene.polo_timer_running:
            # Start
            scene.polo_timer_running = True
            scene.polo_timer_paused = False
            
            # 残り時間が0以下なら初期値をセット
            if scene.polo_time_remaining <= 0:
                if scene.polo_mode_state == 'WORK':
                    scene.polo_time_remaining = scene.polo_setting_work_h * 3600 + scene.polo_setting_work_m * 60
                else:
                    scene.polo_time_remaining = scene.polo_setting_break_h * 3600 + scene.polo_setting_break_m * 60
        else:
            if not scene.polo_timer_paused:
                # Stop (Pause)
                scene.polo_timer_paused = True
            else:
                # Resume
                scene.polo_timer_paused = False
                
        return {'FINISHED'}

# 機能概要
# ポロモードタイマーの残り時間を設定値にリセットする機能
# 来歴
# - [VR001ID003-02] タイマーUIの構成と状態表示
# 引数
# context: bpy.context
# 戻り値: 実行結果 {'FINISHED'}
class WORKTIMER_OT_polo_reset(bpy.types.Operator):
    bl_idname = "worktimer.polo_reset"
    bl_label = "Reset Polo Timer"

    def execute(self, context):
        scene = context.scene
        if scene.polo_mode_state == 'WORK':
            scene.polo_time_remaining = scene.polo_setting_work_h * 3600 + scene.polo_setting_work_m * 60
        else:
            scene.polo_time_remaining = scene.polo_setting_break_h * 3600 + scene.polo_setting_break_m * 60
        return {'FINISHED'}

# 機能概要
# ポロモードタイマーの時間設定ダイアログの表示および保存機能
# 来歴
# - [VR001ID003-03] タイマー設定機能 (Settings Dialog)
# 引数
# context: bpy.context
# 戻り値: 実行結果 {'FINISHED'}
class WORKTIMER_OT_polo_settings(bpy.types.Operator):
    bl_idname = "worktimer.polo_settings"
    bl_label = "Polo Timer Settings"
    
    work_time_h: bpy.props.StringProperty(name="", maxlen=2) # type: ignore
    work_time_m: bpy.props.StringProperty(name="", maxlen=2) # type: ignore
    break_time_h: bpy.props.StringProperty(name="", maxlen=2) # type: ignore
    break_time_m: bpy.props.StringProperty(name="", maxlen=2) # type: ignore

    def invoke(self, context, event):
        self.work_time_h = str(context.scene.polo_setting_work_h)
        self.work_time_m = str(context.scene.polo_setting_work_m)
        self.break_time_h = str(context.scene.polo_setting_break_h)
        self.break_time_m = str(context.scene.polo_setting_break_m)
        return context.window_manager.invoke_props_dialog(self, width=220)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        
        # Work Time
        split = col.split(factor=0.4)
        split.label(text="Work Time:")
        
        # 右側を テキストボックス : コロン : テキストボックス に分割
        right_area = split.split(factor=0.45)
        right_area.prop(self, "work_time_h", text="")
        
        colon_area = right_area.split(factor=0.18)
        colon_row = colon_area.row()
        colon_row.alignment = 'CENTER'
        colon_row.label(text=":")
        
        colon_area.prop(self, "work_time_m", text="")
        
        # Break Time
        split = col.split(factor=0.4)
        split.label(text="Break Time:")
        
        right_area = split.split(factor=0.45)
        right_area.prop(self, "break_time_h", text="")
        
        colon_area = right_area.split(factor=0.18)
        colon_row = colon_area.row()
        colon_row.alignment = 'CENTER'
        colon_row.label(text=":")
        
        colon_area.prop(self, "break_time_m", text="")

    def _to_int(self, val_str, default_val=0):
        # 全角数字を半角数字に
        zen = "０１２３４５６７８９"
        han = "0123456789"
        trans = str.maketrans(zen, han)
        s = val_str.translate(trans)
        import re
        s = re.sub(r'\D', '', s)
        if not s:
            return default_val
        return int(s)

    def execute(self, context):
        scene = context.scene
        
        scene.polo_setting_work_h = self._to_int(self.work_time_h)
        scene.polo_setting_work_m = min(59, self._to_int(self.work_time_m))
        scene.polo_setting_break_h = self._to_int(self.break_time_h)
        scene.polo_setting_break_m = min(59, self._to_int(self.break_time_m))
            
        # 停止中なら現在状態の残り時間も更新
        if not scene.polo_timer_running or scene.polo_timer_paused:
            if scene.polo_mode_state == 'WORK':
                scene.polo_time_remaining = scene.polo_setting_work_h * 3600 + scene.polo_setting_work_m * 60
            else:
                scene.polo_time_remaining = scene.polo_setting_break_h * 3600 + scene.polo_setting_break_m * 60
                
        return {'FINISHED'}

# 機能概要
# ポロモードタイマーの作業・休憩完了ダイアログのOKボタン処理
# 来歴
# - [VR001ID003-04] 完了時のポップアップ通知
# 引数
# context: bpy.context
# 戻り値: 実行結果 {'FINISHED'}
class WORKTIMER_OT_polo_popup_ok(bpy.types.Operator):
    bl_idname = "worktimer.polo_popup_ok"
    bl_label = "OK"
    
    mode: bpy.props.StringProperty() # type: ignore
    
    def execute(self, context):
        # ネイティブダイアログに失敗した時のフォールバックとして呼ばれた場合、
        # このOKボタンが押されたタイミングで状態遷移を実行する。
        scene = context.scene
        if self.mode == "WORK_DONE":
            scene.polo_mode_state = 'BREAK'
            scene.polo_time_remaining = scene.polo_setting_break_h * 3600 + scene.polo_setting_break_m * 60
            # 作業完了後の休憩は自動スタートする
            scene.polo_timer_running = True
            scene.polo_timer_paused = False
        elif self.mode == "BREAK_DONE":
            scene.polo_mode_state = 'WORK'
            scene.polo_time_remaining = scene.polo_setting_work_h * 3600 + scene.polo_setting_work_m * 60
            # 休憩完了後の作業は待機状態（Start待ち）にする
            scene.polo_timer_running = False
            scene.polo_timer_paused = False
            
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
                    
        return {'FINISHED'}

# 機能概要
# ポロモードタイマーの作業・休憩完了時に表示されるポップアップ通知機能
# 来歴
# - [VR001ID003-04] 完了時のポップアップ通知
# 引数
# context: bpy.context
# 戻り値: 実行結果 {'FINISHED'}
class WORKTIMER_OT_polo_popup(bpy.types.Operator):
    bl_idname = "worktimer.polo_popup"
    bl_label = "Blender Work Timer (Polo Mode Timer)"
    
    message: bpy.props.StringProperty() # type: ignore
    mode: bpy.props.StringProperty() # type: ignore

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=220)
        
    def draw(self, context):
        layout = self.layout
        layout.label(text=self.message)
        layout.separator()
        row = layout.row()
        row.alignment = 'RIGHT'
        op = row.operator("worktimer.polo_popup_ok", text="OK")
        op.mode = self.mode
        
    def execute(self, context):
        return {'FINISHED'}

classes = [
    WORKTIMER_OT_polo_toggle,
    WORKTIMER_OT_polo_reset,
    WORKTIMER_OT_polo_settings,
    WORKTIMER_OT_polo_popup_ok,
    WORKTIMER_OT_polo_popup,
]

# 機能概要
# polo_timerのオペレーター群を登録する
# 来歴
# - なし
# 引数
# なし
# 戻り値: なし
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

# 機能概要
# polo_timerのオペレーター群の登録を解除する
# 来歴
# - なし
# 引数
# なし
# 戻り値: なし
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
