import logging
import urllib.parse
import subprocess
import os
import json
import time
import pyautogui
from pathlib import Path
from executor.desktop_control import focus_window
import win32gui
import win32con
import win32process
import win32api

logger = logging.getLogger(__name__)

CONTACTS_FILE = Path("e:/SohanCore/sohan_ai_agent/projects/contacts.json")

def get_contact_number(name_or_number: str) -> str:
    if any(c.isalpha() for c in name_or_number):
        name = name_or_number.lower().strip()
        if not CONTACTS_FILE.exists():
            CONTACTS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
                json.dump({"bintii": "+8801700000000"}, f)
                
        try:
            with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
                contacts = json.load(f)
            return contacts.get(name, name_or_number)
        except:
            return name_or_number
    return name_or_number

def _force_focus(hwnd):
    try:
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.5)
            
                      
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, 
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        time.sleep(0.1)
        win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, 
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        
                                                            
        rect = win32gui.GetWindowRect(hwnd)
        click_x = rect[0] + 50
        click_y = rect[1] + 15
        pyautogui.click(click_x, click_y)
        
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.6)
        return True
    except Exception as e:
        logger.warning(f"_force_focus failed for hwnd {hwnd}: {e}")
        return False

def _find_window(keywords):
    results = []
    def cb(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return
        title = win32gui.GetWindowText(hwnd).lower()
        if any(k.lower() in title for k in keywords):
                                                         
            if "visual studio code" in title: return
            
                                                                                   
            if any(ex in title for ex in ["chrome", "edge", "browser"]):
                if not any(k.lower() in title for k in ["gmail", "google", "mail", "compose"]):
                    return

            logger.info(f"  Window found: '{win32gui.GetWindowText(hwnd)}' hwnd={hwnd}")
            results.append(hwnd)
    win32gui.EnumWindows(cb, None)
    return results[0] if results else None

async def send_email(to: str, subject: str = "", body: str = ""):
    import pythoncom
    import pyperclip
    import pyautogui
    import subprocess
    import time
    from executor.screen_vision import super_click, find_element_hybrid, bulk_find_elements
    
    pythoncom.CoInitialize()
    pyautogui.FAILSAFE = False
    logger.info(f"📧 send_email (Gmail Bulk Mode): to={to}, subject={subject}")

    try:
                                
        logger.info("Launching Gmail Browser...")
        import webbrowser
        webbrowser.open("https://mail.google.com")
        
                                        
        hwnd_main = None
        for _ in range(15):
            time.sleep(1.0)
            hwnd_main = _find_window(["Gmail", "Compose", "Inbox", "Chrome", "Edge"])
            if hwnd_main: break
            
        if not hwnd_main:
            raise Exception("Gmail failed to appear.")

        _force_focus(hwnd_main)
        time.sleep(4.0)
                                          
        pyautogui.press('esc')
        time.sleep(0.5)

                                             
        coords = await find_element_hybrid("Compose button")
        if coords:
            pyautogui.click(coords)
            time.sleep(4.0)                                  
        else:
            pyautogui.press('c')                    
            time.sleep(2.0)

                                                              
                                                           
        targets = ["To recipient field", "Subject field", "Message body area", "Blue Send button"]
        bulk_coords = await bulk_find_elements(targets)

                                
        to_field = bulk_coords.get("To recipient field")
        if to_field:
            pyautogui.click(to_field["x"], to_field["y"])
        else:
                                                                      
            logger.warning("Could not see To field, using fallback focus")
            
        logger.info(f"Writing Recipient: {to}")
        pyperclip.copy(to)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(0.5)

                              
        subj_field = bulk_coords.get("Subject field")
        if subj_field:
            pyautogui.click(subj_field["x"], subj_field["y"])
        else:
            pyautogui.press('tab')                       
            
        logger.info(f"Writing Subject: {subject}")
        pyperclip.copy(subject)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)

                           
        body_field = bulk_coords.get("Message body area")
        if body_field:
            pyautogui.click(body_field["x"], body_field["y"])
        else:
            pyautogui.press('tab')                       
            
        logger.info(f"Writing Body...")
        pyperclip.copy(body)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(1.0)

                      
        send_btn = bulk_coords.get("Blue Send button")
        if send_btn:
             pyautogui.click(send_btn["x"], send_btn["y"])
             logger.info(f"Physically clicked Send button at {send_btn}")
        else:
            logger.warning("Could not see Send button, using Ctrl+Enter")
            pyautogui.hotkey('ctrl', 'enter')

        return {"status": "success", "message": f"✅ Gmail successfully sent to {to}!"}

    except Exception as e:
        logger.error(f"send_email Error: {e}")
        return {"status": "error", "message": f"❌ Email failed: {str(e)}"}

def send_whatsapp(phone: str, text: str = ""):
    import pythoncom
    pythoncom.CoInitialize()
    try:
        phone = str(phone or "").strip()
        text = str(text or "")
        mapped_phone = get_contact_number(phone)
        is_contact_name = False
        if mapped_phone != phone:
            phone = mapped_phone
        elif any(c.isalpha() for c in phone):
            is_contact_name = True
            
        if not is_contact_name:
            clean_phone = ''.join(filter(str.isdigit, phone))
            safe_text = urllib.parse.quote(text)
            whatsapp_url = f"whatsapp://send?phone={clean_phone}&text={safe_text}"
            subprocess.Popen(f'start "" "{whatsapp_url}"', shell=True)
            time.sleep(4.0)
            focus_window("WhatsApp")
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(0.5)
            pyautogui.press('enter')
            return {"status": "success", "message": f"WhatsApp sent to {clean_phone}"}
        else:
            subprocess.Popen('start "" "whatsapp://"', shell=True)
            time.sleep(4.0)
            focus_window("WhatsApp")
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(0.5)
            pyautogui.write(phone)
            time.sleep(1.0)
            pyautogui.press('enter')
            time.sleep(0.5)
            if text:
                pyautogui.write(text)
                time.sleep(0.5)
                pyautogui.press('enter')
            return {"status": "success", "message": f"WhatsApp sent to {phone}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
