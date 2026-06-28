# Blender Work Timer
适用于 Blender 4.5.x LTS 的工作时间追踪插件

> **[ 目的 ]**
> 本插件旨在通过可视化您每天在 Blender 中花费的时间来帮助您**保持动力**。它还能客观地记录您是否在特定任务（如建模）上花费了过多时间，从而帮助您**防止过度劳累**。

![Main Interface](images/main_ui.png)

## 如何安装 (How to Install)

1. 从最新的 **[Releases 页面](https://github.com/HasciiCode/BlenderWorkTimer-Release/releases/latest)** 下载 `BlenderWorkTimer.zip`。（*请勿解压该 zip 文件。*）
2. 打开 Blender，从顶部菜单进入 `编辑 (Edit)` > `偏好设置 (Preferences)`。

![Install Guide](images/install_guide_preference.png)

3. 从左侧菜单选择 `插件 (Add-ons)`。
4. 点击右上角的 `安装... (Install...)` 按钮，然后选择已下载的 `BlenderWorkTimer.zip`。

![Install Guide](images/install_guide_install.png)

5. 在列表中勾选 "System: Blender Work Timer" 旁边的复选框以启用它。

![Install Guide](images/install_guide_enable_BWT.png)

---

## 使用方法 (Usage)

1. 在 3D 视图中按 `N` 键打开侧边栏。
2. 点击 **Timer** 选项卡查看追踪面板。
3. 当您开始工作时，计时器将自动开始计时。
4. 若要使用番茄钟模式（Polo Mode），请点击 "Polo Mode Timer" 区域的 Start 按钮。

---

## 主要功能 (Features)

### 1. 实时工作追踪
自动追踪您在 Blender 中的实际工作时间，并在侧边栏中显示。
- **无操作检测**：如果 2 分钟内未检测到鼠标或键盘活动，计时器将自动暂停，确保仅记录您的实际工作时间。
- **今日与总时间**：即时查看您当天的总工作时间以及该项目的累计总时间。

![Install Guide](images/work_time.png)

### 2. 番茄钟模式 (Pomodoro Timer)
基于番茄工作法的时间管理功能，旨在帮助您在不离开 Blender 的情况下保持深度专注。

> **[ 什么是番茄钟模式？(Pomodoro Technique) ]**
> 这一技巧通过在“短时间的高强度工作”与“短暂休息”之间交替，来防止大脑疲劳并长时间保持高生产力。
> 虽然传统的规则是“25分钟工作 + 5分钟休息”，但您可以根据自己的专注时长自由定制（例如 50分钟 + 10分钟）。

- **可靠的通知**：当该休息或恢复工作时，通过弹出屏幕提醒您，建立清晰的节奏。
- **可自定义**：自由调整工作与休息的时长。

![Polo Mode](images/polo_mode.png)

---

## 注意事项 (Notes)
- 本插件会在您保存 `.blend` 文件的同一目录下创建一个隐藏文件夹，用于包含您的时间数据。
- 经过专门设计，即使您同时在多个 Blender 实例中打开同一个 `.blend` 文件，也能防止数据冲突。
