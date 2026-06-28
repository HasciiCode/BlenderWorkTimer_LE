bl_info = {
    "name": "Blender Work Timer",
    "author": "Antigravity",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Timer Panel",
    "description": "Records real work time by monitoring user activity",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
    "category": "System",
}

import bpy
from . import common
from . import work_timer
from . import polo_timer

# 機能概要
# アドオン全体の登録
# 来歴
# - [VR001ID001-01] サイドバーへのリアルタイム時間表示
# - [VR001ID001-04] Blendファイルごとのデータ保存（隠しフォルダでの相対パス管理）
# 引数
# なし
# 戻り値: なし
def register():
    # プロパティの登録
    bpy.types.Scene.work_timer_session_elapsed = bpy.props.FloatProperty( # type: ignore
        name="Session Elapsed",
        default=0.0
    )
    bpy.types.Scene.work_timer_last_activity = bpy.props.FloatProperty( # type: ignore
        name="Last Activity",
        default=0.0
    )
    bpy.types.Scene.work_timer_session_daily_elapsed = bpy.props.FloatProperty( # type: ignore
        name="Session Daily Elapsed",
        default=0.0
    )
    bpy.types.Scene.work_timer_current_date = bpy.props.StringProperty( # type: ignore
        name="Current Date",
        default=""
    )
    bpy.types.Scene.work_timer_is_deactivated = bpy.props.BoolProperty( # type: ignore
        name="Is Deactivated",
        default=False
    )
    
    # ポロモード用プロパティの登録
    bpy.types.Scene.polo_mode_state = bpy.props.EnumProperty( # type: ignore
        name="Polo Mode State",
        items=[
            ('WORK', 'Work Time', ''),
            ('BREAK', 'Break Time', '')
        ],
        default='WORK'
    )
    bpy.types.Scene.polo_timer_running = bpy.props.BoolProperty( # type: ignore
        name="Polo Timer Running",
        default=False
    )
    bpy.types.Scene.polo_timer_paused = bpy.props.BoolProperty( # type: ignore
        name="Polo Timer Paused",
        default=False
    )
    bpy.types.Scene.polo_time_remaining = bpy.props.IntProperty( # type: ignore
        name="Polo Time Remaining",
        default=1500
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

    # 各モジュールの登録
    common.register()
    work_timer.register()
    polo_timer.register()

# 機能概要
# アドオン全体の解除（無効化時のクリーンアップ）
# 来歴
# - [VR001ID001-08] プラグイン無効化時の安全なクリーンアップ（クラッシュ防止）
# 引数
# なし
# 戻り値: なし
def unregister():
    # 各モジュールのクリーンアップ
    polo_timer.unregister()
    work_timer.unregister()
    common.unregister()

    # プロパティの削除
    props_to_remove = [
        "work_timer_session_elapsed",
        "work_timer_last_activity",
        "work_timer_session_daily_elapsed",
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
