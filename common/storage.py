import bpy
import os
import json
import time
from datetime import datetime, timezone
import ctypes

# 機能概要
# 隠しフォルダ属性の付与
# 来歴
# - [VR001ID001-04] Blendファイルごとのデータ保存（隠しフォルダでの相対パス管理）
# 引数
# folder_path: 属性を付与するフォルダの絶対パス
# 戻り値: なし
def make_folder_hidden(folder_path):
    if os.name == 'nt' and os.path.exists(folder_path):
        try:
            # FILE_ATTRIBUTE_HIDDEN = 0x02
            ctypes.windll.kernel32.SetFileAttributesW(folder_path, 0x02)
        except Exception as e:
            print(f"Failed to set hidden attribute on {folder_path}: {e}")

# 機能概要
# .BlenderPlugins フォルダのパスを取得・生成する
# 来歴
# - [VR001ID001-04] Blendファイルごとのデータ保存（隠しフォルダでの相対パス管理）
# 引数
# なし
# 戻り値: フォルダの絶対パス (保存できない場合は None)
def get_plugin_data_dir():
    filepath = bpy.data.filepath
    if not filepath:
        return None
    
    base_dir = os.path.dirname(filepath)
    plugin_dir = os.path.join(base_dir, ".BlenderPlugins", "BlenderWorkTimer")
    
    if not os.path.exists(plugin_dir):
        try:
            os.makedirs(plugin_dir)
            # 親の .BlenderPlugins に隠し属性を付与
            parent_dir = os.path.join(base_dir, ".BlenderPlugins")
            make_folder_hidden(parent_dir)
        except Exception as e:
            print(f"Failed to create plugin directory: {e}")
            return None
            
    return plugin_dir


_cached_app_data = None
DEFAULT_APP_DATA = {
    "total_time_seconds": 0.0,
    "daily_time_seconds": 0.0,
    "last_updated_timestamp": 0.0,
    "last_active_date_local": ""
}

# 機能概要
# ディスク上の最新のapp.jsonを読み込む
# 来歴
# - [VR001ID001-04] Blendファイルごとのデータ保存（隠しフォルダでの相対パス管理）
# - [VR001ID001-07] 既存ファイルへの途中導入の考慮
# 引数
# なし
# 戻り値: 時間データが格納された辞書
def load_app_data():
    global _cached_app_data
    plugin_dir = get_plugin_data_dir()
    if not plugin_dir:
        _cached_app_data = DEFAULT_APP_DATA.copy()
        return _cached_app_data
        
    app_file = os.path.join(plugin_dir, "app.json")
    if os.path.exists(app_file):
        try:
            with open(app_file, "r", encoding="utf-8") as f:
                _cached_app_data = json.load(f)
                return _cached_app_data
        except Exception as e:
            print(f"Failed to load app.json: {e}")
            
    _cached_app_data = DEFAULT_APP_DATA.copy()
    return _cached_app_data

# 機能概要
# キャッシュされたapp.jsonデータを取得する。UI描画用
# 来歴
# - [VR001ID001-01]
# 引数
# なし
# 戻り値: 時間データの辞書
def get_cached_app_data():
    global _cached_app_data
    if _cached_app_data is None:
        return load_app_data()
    return _cached_app_data

# 機能概要
# 現在の計測時間をディスクに保存（差分加算方式）する
# 来歴
# - [VR001ID001-04] Blendファイルごとのデータ保存（隠しフォルダでの相対パス管理）
# - [VR001ID001-06] Blender多重起動時の競合防止と安全性
# - [VR001ID001-10] 時差やサマータイム（タイムゾーン変更）への対応
# 引数
# total_diff: 今回のセッションで計測された合計時間の差分（秒）
# daily_diff: 今回のセッションで計測された本日時間の差分（秒）
# 戻り値: なし
def save_app_data(total_diff, daily_diff):
    plugin_dir = get_plugin_data_dir()
    if not plugin_dir:
        return
        
    app_file = os.path.join(plugin_dir, "app.json")
    
    # ディスク上の最新値を読み込む（競合対策）
    disk_data = load_app_data()
    total_time = disk_data.get("total_time_seconds", 0.0) + total_diff
    
    today_str = datetime.now().astimezone().strftime("%Y-%m-%d")
    disk_date = disk_data.get("last_active_date_local", "")
    
    if disk_date != today_str:
        daily_time = daily_diff
    else:
        daily_time = disk_data.get("daily_time_seconds", 0.0) + daily_diff
    
    # タイムゾーンに影響されない現在のタイムスタンプ(UNIX)と人間用時刻
    now_ts = time.time()
    now_utc_str = datetime.fromtimestamp(now_ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # ローカル時刻の文字列作成（タイムゾーン情報を付加）
    local_dt = datetime.now().astimezone()
    now_local_str = local_dt.strftime("%Y-%m-%dT%H:%M:%S%z")
    
    new_data = {
        "total_time_seconds": total_time,
        "daily_time_seconds": daily_time,
        "last_updated_timestamp": now_ts,
        "last_updated_utc": now_utc_str,
        "last_updated_local": now_local_str,
        "last_active_date_local": today_str
    }
    
    try:
        with open(app_file, "w", encoding="utf-8") as f:
            json.dump(new_data, f, indent=2)
    except Exception as e:
        print(f"Failed to save app.json: {e}")

# グローバル変数として、前回のセーブ時点でのセッション合計時間・本日時間を保持する
last_saved_session_time = 0.0
last_saved_daily_session_time = 0.0

# 機能概要
# 日付変更時にタイマー側から呼び出され、今回セッションのデイリー保存済み時間をリセットする
# 来歴
# - [VR001ID001-11] 本日作業時間の計測と表示
# 引数
# なし
# 戻り値: なし
def reset_daily_session():
    global last_saved_daily_session_time
    last_saved_daily_session_time = 0.0

# 機能概要
# Blender保存時のコールバックハンドラー
# 来歴
# - [VR001ID001-04] Blendファイルごとのデータ保存（隠しフォルダでの相対パス管理）
# 引数
# dummy: bpy.app.handlersからの引数
# 戻り値: なし
def on_save_pre(dummy):
    global last_saved_session_time, last_saved_daily_session_time
    scene = bpy.context.scene
    
    if hasattr(scene, "work_timer_session_elapsed") and hasattr(scene, "work_timer_session_daily_elapsed"):
        current_session = scene.work_timer_session_elapsed
        current_daily_session = scene.work_timer_session_daily_elapsed
        
        # 前回セーブ時からの差分だけを保存する
        diff = current_session - last_saved_session_time
        daily_diff = current_daily_session - last_saved_daily_session_time
        
        if diff > 0 or daily_diff > 0:
            save_app_data(diff, daily_diff)
            last_saved_session_time = current_session
            last_saved_daily_session_time = current_daily_session

# 機能概要
# オートセーブ用の処理
# 来歴
# - [VR001ID001-09] 合計時間の定期自動保存（オートセーブ）
# 引数
# なし
# 戻り値: なし
def auto_save_time():
    on_save_pre(None)

# 機能概要
# ファイルロード時のコールバックハンドラー
# 来歴
# - [VR001ID001-07] 既存ファイルへの途中導入の考慮
# 引数
# dummy: bpy.app.handlersからの引数
# 戻り値: なし
def on_load_post(dummy):
    global last_saved_session_time, last_saved_daily_session_time
    last_saved_session_time = 0.0
    last_saved_daily_session_time = 0.0
    # セッション時間はtimer側でリセットされる想定
    
    # 起動・ロード時に最新のデータをキャッシュしておく
    load_app_data()

# 機能概要
# ハンドラーの登録
# 来歴
# - [VR001ID001-04] Blendファイルごとのデータ保存（隠しフォルダでの相対パス管理）
# 引数
# なし
# 戻り値: なし
def register():
    if on_save_pre not in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.append(on_save_pre)
    if on_load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(on_load_post)

# 機能概要
# ハンドラーの解除
# 来歴
# - [VR001ID001-08] プラグイン無効化時の安全なクリーンアップ（クラッシュ防止）
# 引数
# なし
# 戻り値: なし
def unregister():
    if on_save_pre in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.remove(on_save_pre)
    if on_load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(on_load_post)
