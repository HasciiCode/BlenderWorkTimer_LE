import bpy
import os
import json
import time
from datetime import datetime, timezone
import hashlib
from . import utils

DEFAULT_APP_DATA = {
    "total_time_seconds": 0.0,
    "daily_time_seconds": 0.0,
    "last_updated_timestamp": 0.0,
    "last_active_date_local": ""
}

TEXT_BLOCK_NAME = "BWT.json"

# 機能概要
# 旧仕様の外部JSONファイルが存在するか確認し、存在すればそのパスを返す
# 来歴
# - [VR001ID001-04] Blendファイルへの直接保存（テキストデータブロック管理）移行措置
# 引数: なし
# 戻り値: 旧JSONファイルの絶対パス または None
def _get_legacy_app_file_path():
    filepath = bpy.data.filepath
    if not filepath:
        return None
    
    base_dir = os.path.dirname(filepath)
    plugin_dir = os.path.join(base_dir, ".BlenderPlugins", "BlenderWorkTimer")
    
    if not os.path.exists(plugin_dir):
        return None
        
    filename = os.path.basename(filepath)
    hashed_name = hashlib.md5(filename.encode('utf-8', errors='replace')).hexdigest()
    hashed_file = os.path.join(plugin_dir, f"{hashed_name}.json")
    if os.path.exists(hashed_file):
        return hashed_file
        
    old_app_file = os.path.join(plugin_dir, "app.json")
    if os.path.exists(old_app_file):
        return old_app_file
        
    return None

# 機能概要
# テキストデータブロックからJSONデータを読み込む。なければ旧ファイルからの移行を試みる。
# 来歴
# - [VR001ID001-04] Blendファイルへの直接保存（テキストデータブロック管理）
# - [VR001ID001-07] 既存ファイルへの途中導入の考慮
# 引数
# なし
# 戻り値: 時間データが格納された辞書
def load_app_data():
    try:
        # まずはテキストデータブロックを探す
        if TEXT_BLOCK_NAME in bpy.data.texts:
            text_block = bpy.data.texts[TEXT_BLOCK_NAME]
            content = text_block.as_string()
            if content.strip():
                try:
                    return json.loads(content)
                except json.JSONDecodeError as e:
                    print(f"Failed to parse BWT.json: {e}")
                    # パース失敗時はデフォルトを返す（壊れている場合）
                    return DEFAULT_APP_DATA.copy()
        
        # テキストデータブロックが無い場合は、旧バージョンの外部ファイルからの移行を試みる
        legacy_file = _get_legacy_app_file_path()
        if legacy_file:
            try:
                with open(legacy_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data
            except Exception as e:
                print(f"Failed to load legacy app data: {e}")
                
    except Exception as e:
        print(f"Safe fallback in load_app_data due to error: {e}")
        
    return DEFAULT_APP_DATA.copy()


# 機能概要
# 計測した時間データをJSON形式でテキストデータブロックへ保存する。
# 来歴
# - [VR001ID001-01]
# - [VR001ID001-04] Blendファイルへの直接保存（テキストデータブロック管理）
# 引数
# なし
# 戻り値: なし
def save_app_data():
    scene = utils.get_scene(bpy.context)
        
    if not scene:
        return
        
    total_time = getattr(scene, "work_timer_total_elapsed", 0.0)
    daily_time = getattr(scene, "work_timer_daily_elapsed", 0.0)
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    now_ts = time.time()
    now_utc_str = datetime.fromtimestamp(now_ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    now_local_str = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    
    new_data = {
        "original_filename": os.path.basename(bpy.data.filepath) if bpy.data.filepath else "Untitled",
        "total_time_seconds": total_time,
        "daily_time_seconds": daily_time,
        "last_updated_timestamp": now_ts,
        "last_updated_utc": now_utc_str,
        "last_updated_local": now_local_str,
        "last_active_date_local": today_str
    }
    
    try:
        if TEXT_BLOCK_NAME not in bpy.data.texts:
            text_block = bpy.data.texts.new(TEXT_BLOCK_NAME)
        else:
            text_block = bpy.data.texts[TEXT_BLOCK_NAME]
            
        text_block.clear()
        text_block.write(json.dumps(new_data, indent=2))
        text_block.use_fake_user = True
    except Exception as e:
        print(f"Failed to save BWT.json: {e}")

# セッション時間の同期はtimer側で直接行い、このファイルでの保持は行わない

# 機能概要
# 日付変更時にタイマー側から呼び出され、今回セッションのデイリー保存済み時間をリセットする
# 来歴
# - [VR001ID001-11] 本日作業時間の計測と表示
# 引数
# なし
# 戻り値: なし
def reset_daily_session():
    scene = getattr(bpy.context, "scene", None)
    if not scene and bpy.data.scenes:
        scene = bpy.data.scenes[0]
    if scene and hasattr(scene, "work_timer_daily_elapsed"):
        scene.work_timer_daily_elapsed = 0.0

# 機能概要
# Blender保存前のコールバックハンドラー
# 来歴
# - [VR001ID001-04] Blendファイルへの直接保存（テキストデータブロック管理）
# 引数
# dummy: bpy.app.handlersからの引数
# 戻り値: なし
@bpy.app.handlers.persistent
def on_save_pre_handler(dummy):
    save_app_data()


# 機能概要
# ハンドラーの登録
# 来歴
# - [VR001ID001-04] Blendファイルへの直接保存（テキストデータブロック管理）
# 引数
# なし
# 戻り値: なし
def register():
    if on_save_pre_handler not in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.append(on_save_pre_handler)

# 機能概要
# ハンドラーの解除
# 来歴
# - [VR001ID001-08] プラグイン無効化時の安全なクリーンアップ（クラッシュ防止）
# 引数
# なし
# 戻り値: なし
def unregister():
    if on_save_pre_handler in bpy.app.handlers.save_pre:
        bpy.app.handlers.save_pre.remove(on_save_pre_handler)
