# Blender Work Timer
適用於 Blender 4.5.x LTS 的工作時間追蹤擴充套件

> **[ 目的 ]**
> 本擴充套件旨在透過視覺化您每天在 Blender 中花費的時間來幫助您**保持動力**。它還能客觀地記錄您是否在特定任務（如建模）上花費了過多時間，進而幫助您**防止過度勞累**。

![Main Interface](images/main_ui.png)

## 如何安裝 (How to Install)

1. 從最新的 **[Releases 頁面](https://github.com/HasciiCode/BlenderWorkTimer-Release/releases/latest)** 下載 `BlenderWorkTimer.zip`。（*請勿解壓縮該 zip 檔案。*）
2. 打開 Blender，從頂部選單進入 `編輯 (Edit)` > `偏好設定 (Preferences)`。

![Install Guide](images/install_guide_preference.png)

3. 從左側選單選擇 `附加元件 (Add-ons)`。
4. 點擊右上角的 `安裝... (Install...)` 按鈕，然後選擇已下載的 `BlenderWorkTimer.zip`。

![Install Guide](images/install_guide_install.png)

5. 在列表中勾選 "System: Blender Work Timer" 旁邊的核取方塊以啟用它。

![Install Guide](images/install_guide_enable_BWT.png)

---

## 使用方法 (Usage)

1. 在 3D 視圖中按 `N` 鍵打開側邊欄。
2. 點擊 **Timer** 標籤查看追蹤面板。
3. 當您開始工作時，計時器將自動開始計時。
4. 若要使用番茄鐘模式（Polo Mode），請點擊 "Polo Mode Timer" 區域的 Start 按鈕。

---

## 主要功能 (Features)

### 1. 即時工作追蹤
自動追蹤您在 Blender 中的實際工作時間，並在側邊欄中顯示。
- **無操作偵測**：如果 2 分鐘內未偵測到滑鼠或鍵盤活動，計時器將自動暫停，確保僅記錄您的實際工作時間。
- **今日與總時間**：即時查看您當天的總工作時間以及該專案的累計總時間。

![Install Guide](images/work_time.png)

### 2. 番茄鐘模式 (Pomodoro Timer)
基於番茄工作法的時間管理功能，旨在幫助您在不離開 Blender 的情況下保持深度專注。

> **[ 什麼是番茄鐘模式？(Pomodoro Technique) ]**
> 這項技巧透過在「短時間的高強度工作」與「短暫休息」之間交替，來防止大腦疲勞並長時間保持高生產力。
> 雖然傳統的規則是「25分鐘工作 + 5分鐘休息」，但您可以根據自己的專注力自由客製化（例如 50分鐘 + 10分鐘）。

- **可靠的通知**：當該休息或恢復工作時，透過彈出視窗提醒您，建立清晰的節奏。
- **可自訂**：自由調整工作與休息的時長。

![Polo Mode](images/polo_mode.png)

---

## 注意事項 (Notes)
- 本擴充套件會在您儲存 `.blend` 檔案的同一個目錄下建立一個隱藏資料夾，用於包含您的時間數據。
- 經過專門設計，即使您同時在多個 Blender 實例中打開同一個 `.blend` 檔案，也能防止數據衝突。
