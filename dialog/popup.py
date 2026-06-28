import platform
import subprocess
import bpy

# 機能概要
# タイマー終了時の状態遷移（モード切替）処理
# 来歴
# - [VR001ID003-04] 完了時のポップアップ通知に基づく状態遷移
# 引数
# scene: bpy.types.Scene
# mode: "WORK_DONE" または "BREAK_DONE"
# 戻り値: なし
def switch_polo_mode(scene, mode):
    if mode == "WORK_DONE":
        scene.polo_mode_state = 'BREAK'
        scene.polo_time_remaining = scene.polo_setting_break_h * 3600 + scene.polo_setting_break_m * 60
        scene.polo_timer_running = True
        scene.polo_timer_paused = False
    elif mode == "BREAK_DONE":
        scene.polo_mode_state = 'WORK'
        scene.polo_time_remaining = scene.polo_setting_work_h * 3600 + scene.polo_setting_work_m * 60
        scene.polo_timer_running = False
        scene.polo_timer_paused = False
        
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

# 機能概要
# OSネイティブのダイアログを表示し、OK押下後に状態遷移を行う
# エラー時はBlender標準のダイアログへフォールバックする
# 来歴
# - [VR001ID003-04] 完了時のポップアップ通知（OSネイティブ化）
# 引数
# title: タイトル
# message: メッセージ
# mode: モード ("WORK_DONE", "BREAK_DONE")
# context: bpy.context
# 戻り値: なし
def show_native_popup(title, message, mode, context):
    os_name = platform.system()
    
    try:
        if os_name == "Windows":
            import ctypes
            # MessageBoxWの横幅はメッセージ長に依存するため、タイトルが見切れないように
            # メッセージの末尾にノーブレークスペース(\u00A0)などを追加して横幅を強制的に広げる。
            # "Blender Work Timer (Polo Mode Timer)" というタイトルを収めるために約50文字分の幅を確保
            padded_message = message + "\u00A0" * 40
            
            # MB_SYSTEMMODAL (0x1000) + MB_ICONINFORMATION (0x40) = 0x1040
            ctypes.windll.user32.MessageBoxW(0, padded_message, title, 0x1040)
            
        elif os_name == "Darwin": # macOS
            script = f'display dialog "{message}" with title "{title}" buttons {{"OK"}} default button "OK"'
            subprocess.run(["osascript", "-e", script], check=True)
            
        elif os_name == "Linux":
            subprocess.run(["zenity", "--info", f"--title={title}", f"--text={message}"], check=True)
            
        else:
            raise Exception("Unsupported OS")
            
        # OSネイティブダイアログがOK押下（またはクローズ）でリターンしたら状態遷移を実行
        switch_polo_mode(context.scene, mode)
            
    except Exception as e:
        print(f"[BlenderWorkTimer] Failed to show native dialog: {e}")
        # フォールバックとしてBlender標準ダイアログを呼び出す
        # この場合、状態遷移は `WORKTIMER_OT_polo_popup.execute` 側で行われる
        bpy.ops.worktimer.polo_popup('INVOKE_DEFAULT', message=message, mode=mode)
