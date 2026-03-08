import logging
import os
import time
import subprocess
import pyautogui
import ctypes
import screen_brightness_control as sbc
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL

                   
logger = logging.getLogger(__name__)

                               
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.0                               

def open_app(target: str):
    logger.info(f"Opening request: {target}")
    target_lower = target.lower().strip()
    
                                          
                                                                
    uri_apps = {
        "camera": "microsoft.windows.camera:",
        "calculator": "calculator:",
        "mail": "outlookmail:",
        "calendar": "outlookcal:",
        "weather": "bingweather:",
        "maps": "bingmaps:",
        "photos": "ms-photos:",
        "paint": "ms-paint:",
        "store": "ms-windows-store:",
        "settings": "ms-settings:",
        "bluetooth": "ms-settings:bluetooth",
        "wifi": "ms-settings:network-wifi",
        "display": "ms-settings:display",
        "whatsapp": "whatsapp:",
        "clock": "ms-clock:",
        "notepad": "notepad.exe"
    }

    if target_lower in uri_apps:
        executable = uri_apps[target_lower]
        logger.info(f"Launching via URI: {executable}")
        subprocess.Popen(f'start {executable}', shell=True)
        return {"status": "success", "message": f"Launched built-in app: {target}"}

                        
    if target.startswith(("http://", "https://", "www.")):
        import webbrowser
        webbrowser.open(target)
        return {"status": "success", "message": f"Opened website: {target}"}

                                           
    common_apps = {
        "chrome": "chrome.exe",
        "edge": "msedge.exe",
        "vs code": "code",
        "vscode": "code",
        "word": "winword",
        "excel": "excel",
        "powerpoint": "powerpnt",
        "explorer": "explorer",
        "task manager": "taskmgr",
        "capcut": "capcut.exe",
        "vlc": "vlc.exe",
        "spotify": "spotify.exe"
    }
    
    executable = common_apps.get(target_lower, target)
    
    try:
                                                 
        if os.path.exists(executable):
            os.startfile(executable)
            return {"status": "success", "message": f"Opened path: {executable}"}
        
                                   
        subprocess.Popen(f'start "" "{executable}"', shell=True)
    except:
        pass

                                                            
                                                                                
    try:
        logger.info(f"Using Deep Search fallback for: {target}")
                                 
        pyautogui.hotkey('win', 's')
        time.sleep(1.0)                        
        pyautogui.write(target, interval=0.02)
        time.sleep(1.2)                               
        pyautogui.press('enter')
        time.sleep(0.5)
        pyautogui.press('enter')                                           
        return {"status": "success", "message": f"Applied Deep Search for '{target}'."}
    except Exception as e:
        return {"status": "error", "message": f"Final search failed: {str(e)}"}

def click_position(x: int, y: int, clicks: int = 1):
    try:
        pyautogui.click(x=x, y=y, clicks=clicks)
        return {"status": "success", "message": f"Clicked at ({x}, {y})"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def _get_master_volume_interface():
    devices = AudioUtilities.GetSpeakers()
    endpoint_volume = getattr(devices, "EndpointVolume", None)
    if endpoint_volume is not None:
        return endpoint_volume
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return interface.QueryInterface(IAudioEndpointVolume)

def set_volume(level: int):
    try:
        volume = _get_master_volume_interface()
        normalized = max(0, min(100, int(level)))
        volume.SetMasterVolumeLevelScalar(normalized / 100.0, None)
        volume.SetMute(0, None)                              
        return {"status": "success", "message": f"Volume set to {normalized}%"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def mute_volume():
    try:
        volume = _get_master_volume_interface()
        volume.SetMute(1, None)
        return {"status": "success", "message": "System audio muted."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def unmute_volume():
    try:
        volume = _get_master_volume_interface()
        volume.SetMute(0, None)
        return {"status": "success", "message": "System audio unmuted."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def adjust_volume(delta: int):
    try:
        volume = _get_master_volume_interface()
        current = int(volume.GetMasterVolumeLevelScalar() * 100)
        new_level = max(0, min(100, current + delta))
        volume.SetMasterVolumeLevelScalar(new_level / 100.0, None)
        volume.SetMute(0, None)
        return {"status": "success", "message": f"Volume {'increased' if delta > 0 else 'decreased'} to {new_level}%"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_volume():
    try:
        volume = _get_master_volume_interface()
        level = int(volume.GetMasterVolumeLevelScalar() * 100)
        muted = bool(volume.GetMute())
        status = f"Volume: {level}% {'(Muted)' if muted else '(Active)'}"
        return {"status": "success", "message": status, "level": level, "muted": muted}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def set_brightness(level: int):
    try:
        sbc.set_brightness(level)
        return {"status": "success", "message": f"Brightness set to {level}%"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def set_wallpaper(image_path: str):
    try:
        if not os.path.exists(image_path):
            return {"status": "error", "message": "Image path does not exist"}
        ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 0)
        return {"status": "success", "message": "Wallpaper updated"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def type_text(text: str):
    try:
        pyautogui.write(text, interval=0.01)
        return {"status": "success", "message": "Typed text"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def press_key(key: str):
    try:
        pyautogui.press(key)
        return {"status": "success", "message": f"Pressed {key}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def take_screenshot(file_name: str = "screenshot.png"):
    if not file_name or not isinstance(file_name, str):
        file_name = "screenshot.png"
    from pathlib import Path
    save_path = Path("e:/SohanCore/sohan_ai_agent/projects") / file_name
    save_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(save_path)
        return {"status": "success", "message": "Screenshot saved", "path": str(save_path)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def focus_window(window_title: str):
    import pygetwindow as gw
    import time
    try:
                                                          
                                                              
        windows = gw.getWindowsWithTitle(window_title)
        if not windows:
                                                                     
            all_titles = gw.getAllTitles()
            for t in all_titles:
                if window_title.lower() in t.lower():
                    windows = [gw.getWindowsAt(0, 0)[0]]                                        
                    windows = gw.getWindowsWithTitle(t)
                    break
        
        if windows:
            win = windows[0]
            if win.isMinimized:
                win.restore()
            win.activate()
            logger.info(f"Focused window using pygetwindow: {win.title}")
            return {"status": "success", "message": f"Focused: {win.title}"}

                                                           
        from pywinauto import Desktop
        import pythoncom
        pythoncom.CoInitialize()
        spec = Desktop(backend="win32").window(title_re=f".*{window_title}.*")
        window = spec.wait('exists', timeout=3)
        window.set_focus()
        return {"status": "success", "message": f"Focused with pywinauto: {window_title}"}

    except Exception as e:
        logger.warning(f"Focus failed for '{window_title}': {e}")
        return {"status": "error", "message": str(e)}

def power_action(action: str):
    try:
        if action == "shutdown":
            os.system("shutdown /s /t 1")
            return {"status": "success", "message": "🖥️ System shutting down..."}
        elif action == "restart":
            os.system("shutdown /r /t 1")
            return {"status": "success", "message": "🔄 System restarting..."}
        elif action == "lock":
            ctypes.windll.user32.LockWorkStation()
            return {"status": "success", "message": "🔒 Computer locked."}
        elif action == "sleep":
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return {"status": "success", "message": "🌙 System entering sleep mode."}
        return {"status": "error", "message": f"Unknown power action: {action}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def toggle_bluetooth(state: bool):
    command = f"""
    $radio = Get-TnpRadio | Where-Object {{ $_.RadioType -eq 'Bluetooth' }}
    if ($radio) {{
        if ("{state}".ToLower() -eq "true") {{ $radio.Enable() }} else {{ $radio.Disable() }}
        return "Bluetooth set to {state}"
    }} else {{
        Start-Process "ms-settings:bluetooth"
        return "Manual toggle required"
    }}
    """
    try:
                                                                                
                                                                     
        subprocess.Popen("start ms-settings:bluetooth", shell=True)
        time.sleep(1.2)
        pyautogui.press('tab')
        time.sleep(0.1)
        pyautogui.press('space')
        time.sleep(0.5)
        os.system("taskkill /f /im SystemSettings.exe")
        return {"status": "success", "message": f"Bluetooth toggle attempted (State: {state})"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def toggle_wifi(state: bool):
    try:
        action = "enable" if state else "disable"
                                                                   
        subprocess.run(f'netsh interface set interface name="Wi-Fi" admin={action}', shell=True)
        return {"status": "success", "message": f"WiFi {action}d."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
