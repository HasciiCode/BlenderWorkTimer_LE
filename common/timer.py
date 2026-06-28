import bpy
import time
from datetime import datetime
import threading
from . import storage
from ..dialog import popup

_last_timer_tick = 0.0
_is_idle = False
_last_auto_save_tick = 0.0
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
    global _last_timer_tick, _is_idle, _last_auto_save_tick, _polo_fraction
    
    # 登録解除されている場合など安全策
    if not hasattr(bpy.context, "scene"):
        return 1.0

    scene = bpy.context.scene
    now = time.monotonic()
    
    # 初回起動時の初期化
    if _last_timer_tick == 0.0:
        _last_timer_tick = now
        _last_auto_save_tick = now
        return 1.0
        
    # 前回の呼び出しからの経過時間
    delta = now - _last_timer_tick
    _last_timer_tick = now
    
    # オートセーブの実行（60秒ごと）
    if now - _last_auto_save_tick >= 60.0:
        storage.auto_save_time()
        _last_auto_save_tick = now

    # sceneのプロパティが存在しない場合は初期化
    for prop in ["work_timer_session_elapsed", "work_timer_session_daily_elapsed"]:
        if getattr(scene, prop, -1.0) == -1.0:
            setattr(scene, prop, 0.0)
    if getattr(scene, "work_timer_current_date", "") == "":
        scene.work_timer_current_date = datetime.now().astimezone().strftime("%Y-%m-%d")
    if getattr(scene, "work_timer_last_activity", 0.0) == 0.0:
        scene.work_timer_last_activity = now

    # 日付が変わったかチェック
    today_str = datetime.now().astimezone().strftime("%Y-%m-%d")
    if scene.work_timer_current_date != today_str:
        scene.work_timer_current_date = today_str
        scene.work_timer_session_daily_elapsed = 0.0
        storage.reset_daily_session()

    last_activity = scene.work_timer_last_activity
    is_deactivated = getattr(scene, "work_timer_is_deactivated", False)

    # 2分（120秒）以上操作がなかった場合、またはウィンドウが非アクティブな場合
    if is_deactivated or (now - last_activity > 120.0):
        if not _is_idle:
            # アイドル状態に突入した瞬間：
            # last_activityから今まで加算してしまっていた無操作時間分を減算する
            idle_duration = now - last_activity
            scene.work_timer_session_elapsed = max(0.0, scene.work_timer_session_elapsed - idle_duration)
            scene.work_timer_session_daily_elapsed = max(0.0, scene.work_timer_session_daily_elapsed - idle_duration)
            _is_idle = True
    else:
        if _is_idle:
            # アイドル状態からの復帰。復帰した瞬間は加算しない
            _is_idle = False
            # 復帰した瞬間に時間をリセット（無操作時間の差分加算を防ぐ）
            scene.work_timer_last_activity = now
        else:
            # 通常稼働時：経過時間を加算
            scene.work_timer_session_elapsed += delta
            scene.work_timer_session_daily_elapsed += delta
            
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
                _last_auto_save_tick = current_time
                scene.work_timer_last_activity = current_time
            else:
                scene.polo_time_remaining = new_time
            
    # UIの再描画（3Dビューポートのサイドバーパネルを更新）
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
                
    return 1.0

# 機能概要
# タイマーの登録と開始
# 来歴
# - [VR001ID001-02] 軽量なバックグラウンドタイマー処理
# 引数
# なし
# 戻り値: なし
def register():
    global _last_timer_tick, _is_idle, _last_auto_save_tick
    _last_timer_tick = 0.0
    _is_idle = False
    _last_auto_save_tick = time.monotonic()
    
    if not bpy.app.timers.is_registered(timer_callback):
        bpy.app.timers.register(timer_callback)

# 機能概要
# タイマーの解除
# 来歴
# - [VR001ID001-08] プラグイン無効化時の安全なクリーンアップ（クラッシュ防止）
# 引数
# なし
# 戻り値: なし
def unregister():
    if bpy.app.timers.is_registered(timer_callback):
        bpy.app.timers.unregister(timer_callback)
