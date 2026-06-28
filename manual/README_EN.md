# Blender Work Timer
Time Tracking Add-on for Blender 4.5.x LTS

> **[ Purpose ]**
> This add-on is designed to help you **maintain motivation** by visualizing how much time you spend in Blender every day. It also helps you **prevent overworking** by objectively tracking whether you are spending too much time on specific tasks (like modeling).

![Main Interface](images/main_ui.png)

## How to Install

1. Download `BlenderWorkTimer.zip` from the latest **[Releases Page](https://github.com/HasciiCode/BlenderWorkTimer-Release/releases/latest)**. (*Do NOT extract the zip file.*)
2. Open Blender and go to `Edit` > `Preferences` from the top menu.

![Install Guide](images/install_guide_preference.png)

3. Select `Add-ons` from the left menu.
4. Click the `Install...` button at the top right, and select the downloaded `BlenderWorkTimer.zip`.

![Install Guide](images/install_guide_install.png)

5. Check the box next to "System: Blender Work Timer" in the list to enable it.

![Install Guide](images/install_guide_enable_BWT.png)

---

## Usage

1. Press the `N` key in the 3D Viewport to open the Sidebar.
2. Click the **Timer** tab to view the tracking panel.
3. The timer will start automatically as soon as you begin working.
4. To use Polo Mode, click the Start button in the "Polo Mode Timer" section.

---

## Features

### 1. Real-time Work Tracking
Automatically tracks your actual working time in Blender and displays it in the sidebar.
- **Idle Detection**: Automatically pauses the timer if no mouse or keyboard activity is detected for 2 minutes, ensuring only your actual working time is logged.
- **Today & Total Time**: Instantly view both your working time for the current day and the total accumulated time for the project.

![Install Guide](images/work_time.png)

### 2. Polo Mode (Pomodoro Timer)
A time management feature (Pomodoro Technique) designed to help you maintain deep focus without leaving Blender.

> **[ What is Polo Mode (Pomodoro Technique)? ]**
> It is a technique where you alternate between "short bursts of focused work" and "short breaks" to prevent brain fatigue and maintain high productivity for longer periods.
> While the traditional rule is "25 minutes of work + 5 minutes of break", you can freely customize it to fit your own focus span (e.g., 50 minutes + 10 minutes).

- **Reliable Notifications**: Alerts you with a popup screen when it's time to take a break or get back to work, creating a clear rhythm.
- **Customizable**: Freely adjust the duration of your work sessions and breaks.

![Polo Mode](images/polo_mode.png)

---

## Notes
- This add-on creates a hidden folder containing your time data in the same directory as your saved `.blend` file.
- It is designed to prevent data conflicts even if you open the same `.blend` file in multiple Blender instances simultaneously.
