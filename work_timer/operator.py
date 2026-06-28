import bpy
import time

import bpy
import time

# 機能概要
# ユーザーの操作（マウス移動やキー入力）を監視し、最終操作時刻を記録する
# 来歴
# - [VR001ID001-03] 無操作状態（アイドル）の検知と時間補正
# - [VR001ID001-10] 時差やサマータイム（タイムゾーン変更）への対応
# 引数
# context: bpy.context
# 戻り値: なし
class WORKTIMER_OT_activity_monitor(bpy.types.Operator):
    bl_idname = "worktimer.activity_monitor"
    bl_label = "Activity Monitor"
    bl_description = "ユーザーの操作をバックグラウンドで監視します"

    _timer = None

    def modal(self, context, event):
        if not context.window:
            return {'FINISHED'}
            
        if not hasattr(context, "scene") or not context.scene:
            return {'PASS_THROUGH'}

        # ウィンドウのフォーカス状態を判定
        if event.type == 'WINDOW_DEACTIVATE':
            context.scene.work_timer_is_deactivated = True
            return {'PASS_THROUGH'}
            
        if event.type == 'WINDOW_ACTIVATE':
            context.scene.work_timer_is_deactivated = False
            return {'PASS_THROUGH'}

        # 除外する非操作（ノイズ）イベントのリスト
        ignored_events = {
            'TIMER',
            'MOUSEMOVE',
            'INBETWEEN_MOUSEMOVE',
            'WINDOW_DEACTIVATE',
            'WINDOW_ACTIVATE',
            'NONE'
        }

        # 物理的な操作イベントのみを検知して最終操作時刻を更新
        if event.type not in ignored_events:
            context.scene.work_timer_last_activity = time.monotonic()
            context.scene.work_timer_is_deactivated = False

        # 他のアドオンやBlender自体のショートカットを妨害しないよう常にスルーする
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        # 起動時に最初の時間を記録
        context.scene.work_timer_last_activity = time.monotonic()
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

classes = [
    WORKTIMER_OT_activity_monitor,
]

# 機能概要
# モニタータイマーを開始する
# 来歴
# - なし
# 引数
# なし
# 戻り値: 成功時にNone、失敗時に再試行待機秒数（1.0）
def _start_monitor_timer():
    if not hasattr(bpy.context, "window_manager") or not bpy.context.window_manager.windows:
        return 1.0 # 画面の準備ができるまで待機
    
    win = bpy.context.window_manager.windows[0]
    
    try:
        # Blender 3.2+ 用のコンテキストオーバーライド
        with bpy.context.temp_override(window=win):
            bpy.ops.worktimer.activity_monitor('INVOKE_DEFAULT')
        return None # 成功したらタイマー終了
    except Exception as e:
        print("Activity monitor start failed:", e)
        return 1.0

# 機能概要
# work_timerのオペレーター群を登録する
# 来歴
# - [VR001ID001-03] 無操作状態（アイドル）の検知と時間補正
# 引数
# なし
# 戻り値: なし
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    if not bpy.app.timers.is_registered(_start_monitor_timer):
        bpy.app.timers.register(_start_monitor_timer)

# 機能概要
# work_timerのオペレーター群の登録を解除する
# 来歴
# - [VR001ID001-08] プラグイン無効化時の安全なクリーンアップ（クラッシュ防止）
# 引数
# なし
# 戻り値: なし
def unregister():
    if bpy.app.timers.is_registered(_start_monitor_timer):
        bpy.app.timers.unregister(_start_monitor_timer)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
