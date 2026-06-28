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
from . import properties
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
    properties.register()
    
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
    properties.unregister()
