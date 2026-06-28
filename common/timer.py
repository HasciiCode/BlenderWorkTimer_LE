import bpy
import time
from datetime import datetime
import threading
from . import storage
from ..dialog import popup
from . import utils

_last_timer_tick = 0.0
_is_idle = False
_polo_fraction = 0.0

# 機能概要
# 1秒ごとに呼び出されるタイマーコールバック。時間の加算とアイドル検知を行う。
# 来歴
# - [VR001ID001-02] 軽量なバックグラウンドタイマー処理
# - [VR001ID001-03] 無操作状態（アイドル）の検知と時間補正
# - [VR001ID001-09] 合計時間の定期自動保存（オートセーブ）
# - [VR001ID001-10] 時差やサマータイム（タイムゾーン変更）への対応
# 引数
# なし
# 戻り値: 次に呼び出されるまでの秒数 (float)。Noneを返すとタイマー終了。
def timer_callback():
    try:
        return _timer_callback_logic()
    except Exception as e:
        print(f"BlenderWorkTimer callback error: {e}")
        return 1.0

def _timer_callback_logic():
    global _last_timer_tick, _is_idle, _polo_fraction
    
    # 登録解除されている場合など安全策
    if not bpy.data.scenes:
        return 1.0

    # アクティブなシーンを取得
    scene = utils.get_scene(bpy.context)
    if not scene:
        return 1.0
    now = time.monotonic()
    
    # 初回起動時の初期化
    if _last_timer_tick == 0.0:
        _last_timer_tick = now
        
        # 起動時・ロード時にディスクから前回までの時間を読み込んでメモリ上に展開する
        disk_data = storage.load_app_data()
        scene.work_timer_total_elapsed = disk_data.get("total_time_seconds", 0.0)
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        disk_date = disk_data.get("last_active_date_local", "")
        if disk_date != today_str:
            scene.work_timer_daily_elapsed = 0.0
        else:
            scene.work_timer_daily_elapsed = disk_data.get("daily_time_seconds", 0.0)
        
        if hasattr(scene, "work_timer_is_deactivated"):
            scene.work_timer_is_deactivated = False
            
        scene.work_timer_last_activity = now
        
        return 1.0
        
    # 前回の呼び出しからの経過時間
    delta = now - _last_timer_tick
    _last_timer_tick = now

    # sceneのプロパティが存在しない場合は初期化
    for prop in ["work_timer_total_elapsed", "work_timer_daily_elapsed"]:
        if getattr(scene, prop, -1.0) == -1.0:
            setattr(scene, prop, 0.0)
    if getattr(scene, "work_timer_current_date", "") == "":
        scene.work_timer_current_date = datetime.now().strftime("%Y-%m-%d")
    if getattr(scene, "work_timer_last_activity", 0.0) == 0.0:
        scene.work_timer_last_activity = now

    # 日付が変わったかチェック
    today_str = datetime.now().strftime("%Y-%m-%d")
    if scene.work_timer_current_date != today_str:
        scene.work_timer_current_date = today_str
        scene.work_timer_daily_elapsed = 0.0
        storage.reset_daily_session()

    last_activity = scene.work_timer_last_activity
    is_deactivated = getattr(scene, "work_timer_is_deactivated", False)

    # 2分（120秒）以上操作がなかった場合、またはウィンドウが非アクティブな場合
    if is_deactivated or (now - last_activity > 120.0):
        if not _is_idle:
            # アイドル状態に突入した瞬間：
            # last_activityから今まで加算してしまっていた無操作時間分を減算する
            idle_duration = now - last_activity
            scene.work_timer_total_elapsed = max(0.0, scene.work_timer_total_elapsed - idle_duration)
            scene.work_timer_daily_elapsed = max(0.0, scene.work_timer_daily_elapsed - idle_duration)
            _is_idle = True
    else:
        if _is_idle:
            # アイドル状態からの復帰。復帰した瞬間は加算しない
            _is_idle = False
            # 復帰した瞬間に時間をリセット（無操作時間の差分加算を防ぐ）
            scene.work_timer_last_activity = now
        else:
            # 通常稼働時：経過時間を加算
            scene.work_timer_total_elapsed += delta
            scene.work_timer_daily_elapsed += delta
            
    # === ポロモードタイマー処理 ===
    if getattr(scene, "polo_timer_running", False) and not getattr(scene, "polo_timer_paused", False):
        _polo_fraction += delta
        if _polo_fraction >= 1.0:
            sec_to_sub = int(_polo_fraction)
            _polo_fraction -= sec_to_sub
            
            new_time = scene.polo_time_remaining - sec_to_sub
            if new_time <= 0:
                scene.polo_time_remaining = 0
                scene.polo_timer_running = False
                
                # ポップアップダイアログ呼び出し (ブロッキングされる)
                # ブロッキングされるとBlenderのUI全体が固まるが、timer_callback内でのブロッキングは
                # Blenderのイベントループ自体を止めることになるため、別スレッドでポップアップを起動するか、
                # またはメインスレッドでそのままブロックするか検討が必要。
                # ここでは要求仕様（ブロッキングによるダイアログ重複防止とOK検知）に従い、
                # 敢えてメインスレッドでブロッキング実行するが、もしBlenderが描画も完全に停止してしまい問題になる場合、
                # フォールバックすることも可能である。
                
                if scene.polo_mode_state == 'WORK':
                    popup.show_native_popup("Blender Work Timer (Polo Mode Timer)", "Time's up! Take a break.", "WORK_DONE", bpy.context)
                else:
                    popup.show_native_popup("Blender Work Timer (Polo Mode Timer)", "Break is over. Back to work.", "BREAK_DONE", bpy.context)
                    
                # ダイアログ表示でブロッキングされていた間の時間を「無かったこと」にするため、
                # タイマーの基準時刻を現在時刻にリセットする。
                # これを行わないと、次回の timer_callback 呼び出し時に delta が巨大になり、
                # 次のタイマー（休憩時間など）が一気に消費されてしまう。
                current_time = time.monotonic()
                _last_timer_tick = current_time
                scene.work_timer_last_activity = current_time
            else:
                scene.polo_time_remaining = new_time
            
    # UIの再描画（3Dビューポートのサイドバーパネルを更新）
    if getattr(bpy.context, "window_manager", None):
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
                
    return 1.0

# 機能概要
# ファイルロード時にタイマーのセッション時間と非アクティブ状態をリセットするハンドラー
# 来歴
# - [VR001ID001-14] ファイルロード後のタイマー停止と時間二重加算バグ修正
# - [VR001ID001-15] load_post時のコンテキスト不在によるリセット失敗を修正
# 引数
# dummy: bpy.app.handlersからの引数
# 戻り値: なし
@bpy.app.handlers.persistent
def on_load_post_timer(dummy):
    global _is_idle, _last_timer_tick
    
    # ファイルロード時に必ず初回化処理が走るようにリセット
    _last_timer_tick = 0.0
    
    # load_post時は bpy.context が不完全な場合があるため、bpy.data.scenes を直接操作する
    for scene in bpy.data.scenes:
        # メモリ上の時間を保持するためリセットしない
        if hasattr(scene, "work_timer_total_elapsed"):
            pass # 今後はここでリセットしない
        if hasattr(scene, "work_timer_daily_elapsed"):
            pass # 今後はここでリセットしない
            
        # 非アクティブ状態を強制リセット
        if hasattr(scene, "work_timer_is_deactivated"):
            scene.work_timer_is_deactivated = False
            
        # 最終アクティビティ時間を現在時刻にリセット
        scene.work_timer_last_activity = time.monotonic()
        
        # ポロモードのプロパティを強制リセット（.blendファイルに保存されてしまっていた古い情報を破棄）
        if hasattr(scene, "polo_timer_running"):
            scene.polo_timer_running = False
            scene.polo_timer_paused = False
            scene.polo_mode_state = 'WORK'
            
            work_h = getattr(scene, "polo_setting_work_h", 0)
            work_m = getattr(scene, "polo_setting_work_m", 25)
            scene.polo_time_remaining = work_h * 3600 + work_m * 60
        
    _is_idle = False
    
    # ファイルロード時にタイマーが解除されるのを防ぐため、既にpersistent=Trueで登録しているが、念のため
    if not bpy.app.timers.is_registered(timer_callback):
        bpy.app.timers.register(timer_callback, persistent=True)

# 機能概要
# タイマーの登録と開始
# 来歴
# - [VR001ID001-02] 軽量なバックグラウンドタイマー処理
# 引数
# なし
# 戻り値: なし
def register():
    global _last_timer_tick, _is_idle
    _last_timer_tick = 0.0
    _is_idle = False
    
    if not bpy.app.timers.is_registered(timer_callback):
        bpy.app.timers.register(timer_callback, persistent=True)
    if on_load_post_timer not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(on_load_post_timer)

# 機能概要
# タイマーの解除
# 来歴
# - [VR001ID001-08] プラグイン無効化時の安全なクリーンアップ（クラッシュ防止）
# 引数
# なし
# 戻り値: なし
def unregister():
    if on_load_post_timer in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(on_load_post_timer)
    if bpy.app.timers.is_registered(timer_callback):
        bpy.app.timers.unregister(timer_callback)
