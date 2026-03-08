import re

filepath = r"e:\SohanCore\sohan_ai_agent\executor\messaging.py"
with open(filepath, "r", encoding="utf-8") as f:
    code = f.read()

start_marker = "        # ── STEP 1: Launch Outlook (Mail) ─────────────────────────────"
end_marker = "        # ── STEP 5: Write Mail Address ────────────────────────────────"

replacement = """        # ── STEP 1: Launch Outlook (Mail) ─────────────────────────────
        logger.info("Launching Outlook(Mail)...")
        subprocess.Popen('start outlookmail:', shell=True)
        
        # ── Wait for Mail window to actually exist ────────────────────
        hwnd_main = None
        for attempt in range(12): # wait up to 12 seconds
            time.sleep(1.0)
            hwnd_main = _find_window(["Mail", "Outlook"])
            if hwnd_main:
                break
                
        if not hwnd_main:
            raise Exception("Outlook completely failed to pop up on the screen in time.")

        # ── STEP 2: Guarantee Focus on Mail Window ────────────────────
        logger.info("Locating mail window to seize control...")
        _click_to_focus(hwnd_main)
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
            # We didn't detect a separate compose window by name, but Ctrl+N may have
            # simply opened the composer inside the same window (inline).
            # We strictly prevent 'mailto:' so we NEVER open a browser like Chrome.
            logger.info("Compose window might be inline. Maintaining focus on main window.")
            _click_to_focus(hwnd_main)
            
        # Ensure focus is solid before ANY typing occurs
        time.sleep(1.5)
        
        # --- CRITICAL SAFETY CHECK ---
        hwnd_active = win32gui.GetForegroundWindow()
        active_title = win32gui.GetWindowText(hwnd_active) if hwnd_active else ""
        allowed_titles = ["Mail", "Outlook", "Message", "Draft", "Untitled", "New message", "Inbox"]
        if not any(k.lower() in active_title.lower() for k in allowed_titles):
            raise Exception(f"CRITICAL SAFETY ABORT: Another app ({active_title}) stole focus. Aborting email typing.")
        
        # ── STEP 5: Write Mail Address ────────────────────────────────\n"""

start_idx = code.find(start_marker)
end_idx = code.find(end_marker)

if start_idx != -1 and end_idx != -1:
    new_code = code[:start_idx] + replacement + code[end_idx+len(end_marker)+1:]  # +1 for newline
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_code)
    print("Code successfully updated!")
else:
    print("Could not find markers.")
