import re

filepath = r"e:\SohanCore\sohan_ai_agent\executor\messaging.py"
with open(filepath, "r", encoding="utf-8") as f:
    code = f.read()

start_marker = "    try:"
end_marker = "    except Exception as e:\n        logger.error(f\"send_email failed: {e}\")"

replacement = """    try:
        # ── STEP 1: Launch Outlook (Mail) ─────────────────────────────
        logger.info("Launching Outlook(Mail)...")
        subprocess.Popen('start outlookmail:', shell=True)
        time.sleep(6.0)

        # ── STEP 2: Guarantee Focus on Mail Window ────────────────────
        logger.info("Locating mail window to seize control...")
        hwnd_main = _find_window(["Mail", "Outlook"])
        if hwnd_main:
            _click_to_focus(hwnd_main)
            time.sleep(1.0)
        else:
            focus_window("Mail")
            time.sleep(1.0)
            
        # ── STEP 3: Click 'New' via safe hotkey ───────────────────────
        logger.info("Activating 'New Mail' composition...")
        # Avoid arbitrary X,Y mouse clicks that accidentally background the window.
        # Use native 'New' shortcut
        pyautogui.hotkey('ctrl', 'n')
        time.sleep(4.0)
        
        # ── STEP 4: Force compose window focus ────────────────────────
        hwnd_compose = _find_window(["Untitled", "New message", "Message", "Draft"])
        if hwnd_compose:
            _click_to_focus(hwnd_compose)
        else:
            # Fallback: forcefully pop a native compose window if Ctrl+N failed
            logger.warning("No compose window detected! Using native mailto fallback...")
            subprocess.Popen('start mailto:', shell=True)
            time.sleep(3.0)
            hwnd_compose_fb = _find_window(["Untitled", "New message", "Message", "Draft"])
            if hwnd_compose_fb:
                _click_to_focus(hwnd_compose_fb)
            
        # Ensure focus is solid before ANY typing occurs
        time.sleep(1.5)
        
        # ── STEP 5: Write Mail Address ────────────────────────────────
        logger.info(f"Writing mail address: {to}")
        pyperclip.copy(to)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(0.5)

        # ── STEP 6: Write Subject ─────────────────────────────────────
        logger.info(f"Writing subject: {subject}")
        # Move down to subject using Tab
        pyautogui.press('tab')
        time.sleep(0.4)
        pyautogui.press('tab')
        time.sleep(0.4)
        
        pyperclip.copy(subject)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)
        
        # ── STEP 7: Write Body ────────────────────────────────────────
        logger.info("Writing body...")
        pyautogui.press('tab')
        time.sleep(0.4)
        pyautogui.press('tab') # Sometimes an extra tab is needed in Windows Mail body
        time.sleep(0.2)

        pyperclip.copy(body)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.8)

        # ── STEP 8: Send it ───────────────────────────────────────────
        logger.info("Sending email...")
        # Main Send shortcut
        pyautogui.hotkey('ctrl', 'enter')
        time.sleep(1.0)
        # Alternate Send shortcut
        pyautogui.hotkey('alt', 's')

        logger.info(f"✅ Email sent to {to}")
        return {"status": "success", "message": f"✅ Email sent to {to}!"}

"""

start_idx = code.find(start_marker)
end_idx = code.find(end_marker)

if start_idx != -1 and end_idx != -1:
    new_code = code[:start_idx] + replacement + code[end_idx:]
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_code)
    print("Code successfully updated!")
else:
    print("Could not find markers.")
