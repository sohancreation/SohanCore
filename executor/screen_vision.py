import logging
import os
import time
import json
import re
import pyautogui
import pytesseract
from PIL import Image, ImageEnhance, ImageDraw, ImageGrab
import numpy as np
import cv2
import difflib
import asyncio
from pathlib import Path
from pywinauto import Desktop
from utils.llm_client import call_vision_llm

                   
logger = logging.getLogger(__name__)

                       
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

VISION_DIR = Path("e:/SohanCore/sohan_ai_agent/projects/vision")
VISION_DIR.mkdir(parents=True, exist_ok=True)
SCREEN_DIR = Path("e:/SohanCore/sohan_ai_agent/temp/screens")
SCREEN_DIR.mkdir(parents=True, exist_ok=True)

                                            
pyautogui.FAILSAFE = False

async def find_element_hybrid(target: str):
    clean_target = target.lower().replace("icon", "").replace("button", "").replace("the ", "").strip()
    logger.info(f"🔍 Super-Scan started for: '{clean_target}'")
    
    screen_path = str(VISION_DIR / "current_screen.png")
    
    for attempt in range(2):
                                
        result = await _uia_scan(clean_target)
        if result: return result

                                               
        pyautogui.screenshot().save(screen_path)

                            
        result = await _ai_scan(target, screen_path)
        if result: return result

                      
        result = _find_text_location_ocr(clean_target, screen_path)
        if result: return result
        
        if attempt == 0: await asyncio.sleep(0.5)
    return None

async def _uia_scan(clean_target: str):
    try:
        logger.info("Layer 1: Scanning Windows UI Tree...")
        all_windows = Desktop(backend="uia").windows()
                                                                      
        if any(kw in clean_target for kw in ["person", "profile", "chrome", "google"]):
            all_windows = [w for w in all_windows if "chrome" in w.window_text().lower()] + \
                         [w for w in all_windows if "chrome" not in w.window_text().lower()]

        for win in all_windows[:5]:                                    
            try:
                                                    
                for ctrl in ["ListItem", "Button", "MenuItem"]:
                    els = win.descendants(control_type=ctrl)
                    for el in els:
                        name = (el.element_info.name or "").lower()
                        if clean_target in name or (clean_target == "person 1" and "user 1" in name):
                            rect = el.rectangle()
                            if rect.width() > 0:
                                return (rect.left + rect.width() // 2, rect.top + rect.height() // 2)
            except: continue
        return None
    except: return None

async def _ai_scan(target: str, screenshot_path: str):
    try:
        logger.info("Layer 2: AI Visual Scan...")
        profile_hint = "HINT: Looking for circular profile icons." if "person" in target.lower() else ""
        prompt = f"Find pixel center (x, y) for: '{target}'. {profile_hint} Return ONLY JSON {{\"x\": int, \"y\": int}}"
        
        ai_response = await call_vision_llm(prompt, screenshot_path)
        match = re.search(r'\{.*\}', ai_response)
        if match:
            coords = json.loads(match.group(0))
            return (int(coords['x']), int(coords['y']))
    except: return None


def _find_text_location_ocr(clean_target: str, img_path: str):
    try:
        logger.info("Layer 3: OCR Scan...")
        
        passes = [
            {'upscale': 2, 'contrast': 3.0, 'psm': 3},                  
            {'upscale': 2, 'contrast': 2.0, 'psm': 11}               
        ]
        
        target_words = clean_target.split()
        
        for p in passes:
                                    
            img_pil = Image.open(img_path).convert('L')
            img_pil = ImageEnhance.Contrast(img_pil).enhance(p['contrast'])
            img_pil = img_pil.resize((img_pil.width * p['upscale'], img_pil.height * p['upscale']), Image.Resampling.LANCZOS)
            
                                                       
            if p['psm'] == 3:
                data = pytesseract.image_to_data(img_pil, output_type=pytesseract.Output.DICT, config=f"--psm {p['psm']} -c tessedit_do_invert=0")
            else:
                img_cv = np.array(img_pil)
                img_cv = cv2.adaptiveThreshold(img_cv, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
                data = pytesseract.image_to_data(img_cv, output_type=pytesseract.Output.DICT, config=f"--psm {p['psm']} -c tessedit_do_invert=0")
            
                                                     
            full_text = " ".join([t for t in data['text'] if t.strip()]).lower()
            if clean_target in full_text:
                                  
                words = [t.lower() for t in data['text']]
                for i in range(len(words) - len(target_words) + 1):
                    if words[i:i+len(target_words)] == target_words:
                        x = data['left'][i] // p['upscale']
                        y = data['top'][i] // p['upscale']
                        w = sum(data['width'][i:i+len(target_words)]) // p['upscale']
                        h = max(data['height'][i:i+len(target_words)]) // p['upscale']
                        logger.info(f"✅ OCR EXACT PHRASE MATCH: '{clean_target}'")
                        return (x + w//2, y + h//2)

                                                         
            for i in range(len(data['text'])):
                word = data['text'][i].strip().lower()
                if not word or len(word) < 2: continue
                
                ratio = difflib.SequenceMatcher(None, clean_target, word).ratio()
                if ratio > 0.9 or (len(clean_target) > 3 and clean_target in word):
                    x = data['left'][i] // p['upscale']
                    y = data['top'][i] // p['upscale']
                    w_el = data['width'][i] // p['upscale']
                    h_el = data['height'][i] // p['upscale']
                    logger.info(f"✅ OCR FUZZY MATCH: '{word}' for '{clean_target}' at ({x}, {y})")
                    return (x + w_el // 2, y + h_el // 2)
                                                      
            joined_target = clean_target.replace(" ", "")
            if joined_target in full_text.replace(" ", ""):
                                                                             
                for i in range(len(words)):
                    if target_words[0] in words[i]:
                        x = data['left'][i] // p['upscale']
                        y = data['top'][i] // p['upscale']
                        return (x + (data['width'][i]//p['upscale'])//2, y + (data['height'][i]//p['upscale'])//2)

                                                                         
            if len(target_words) > 1:
                for i in range(len(data['text'])):
                    w1 = data['text'][i].lower()
                    if target_words[0] in w1:
                                           
                        x1, y1 = data['left'][i], data['top'][i]
                        for j in range(len(data['text'])):
                            if i == j: continue
                            w2 = data['text'][j].lower()
                            if target_words[1] in w2:
                                x2, y2 = data['left'][j], data['top'][j]
                                                                     
                                if abs(x1 - x2) < 150 and abs(y1 - y2) < 50:
                                    x = (x1 + x2) // (2 * p['upscale'])
                                    y = (y1 + y2) // (2 * p['upscale'])
                                    logger.info(f"✅ OCR PROXIMAL MATCH: '{target_words[0]}' and '{target_words[1]}'")
                                    return (x, y)

        return None
    except Exception as e:
        logger.error(f"OCR Error: {e}")
        return None

async def bulk_find_elements(targets: list[str]):
    logger.info(f"🚀 Performing Bulk Visual Scan for: {targets}")
    try:
        screenshot_path = str(VISION_DIR / "bulk_ai_scan.png")
        pyautogui.screenshot().save(screenshot_path)
        
        prompt = f"""
        TASK: Find the exact center (x, y) coordinates for THESE EXACT elements: {targets}.
        
        INSTRUCTIONS:
        1. Identify each element from the screenshot.
        2. Determine the pixel coordinates (center) of each.
        3. If an element is not found, return null for it.
        4. Return ONLY a valid JSON object mapping each target name to its {{'x': int, 'y': int}}.
        
        EXAMPLE: {{"Compose button": {{"x": 100, "y": 200}}, "Send button": null}}
        """
        
        ai_response = await call_vision_llm(prompt, screenshot_path)
        coord_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
        if coord_match:
            data = json.loads(coord_match.group(0))
            logger.info(f"✅ BULK MATCH RESULTS: {data}")
            return data
    except Exception as e:
        logger.error(f"Bulk Scan failed: {e}")
        return {}
    return {}

async def super_click(target: str, double=True):
    coords = await find_element_hybrid(target)
    
    if not coords:
                                     
        shortcuts = {
            "start": "win",
            "search": "win+s",
            "browser": "win+1",                           
            "settings": "win+i"
        }
        for key, val in shortcuts.items():
            if key in target.lower():
                logger.info(f"Visual failed, using shortcut fallback for {key}: {val}")
                pyautogui.hotkey(*val.split('+'))
                return {"status": "success", "message": f"I used a system shortcut to access {target} since vision was blocked."}
        
        return {"status": "error", "message": f"Visual scan failed for '{target}'. Target might be covered or off-screen."}

    x, y = coords
    try:
                      
        pyautogui.moveTo(x, y, duration=0.0)
        
                             
        if double:
            pyautogui.click(clicks=2, interval=0.0)
        else:
            pyautogui.click()
            
        return {"status": "success", "message": f"Direct hit on '{target}' at ({x}, {y})."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def extract_text_from_screen():
    try:
        img_path = str(VISION_DIR / "full_screen_ocr.png")
                                                                   
        screenshot = await asyncio.to_thread(pyautogui.screenshot)
        await asyncio.to_thread(screenshot.save, img_path)
        
        def _ocr():
            img = Image.open(img_path).convert('L')
            img = ImageEnhance.Contrast(img).enhance(2.0)
            return pytesseract.image_to_string(img, config='--psm 3').strip()
            
        return await asyncio.to_thread(_ocr)
    except Exception as e:
        return f"Vision Error: {e}"

async def capture_screen_state():
    filename = SCREEN_DIR / f"screen_{int(time.time())}.png"
    try:
        def _capture():
            img = ImageGrab.grab()
            img.save(filename)
            text = pytesseract.image_to_string(img)
            return {"status": "success", "path": str(filename), "text": text}
            
        return await asyncio.to_thread(_capture)
    except Exception as e:
        logger.error(f"capture_screen_state failed: {e}")
        return {"status": "error", "message": str(e)}
