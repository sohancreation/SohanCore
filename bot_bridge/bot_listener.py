import logging
import sys
import os
import json
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import Conflict
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.constants import ChatAction

                                               
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from brain.prompt_parser import parse_prompt, fallback_parse
from brain.task_planner import plan_task
from executor.file_manager import create_folder, write_file, read_file, delete_file, search_files
from executor.code_runner import run_command, run_python, run_python_snippet
from executor.desktop_control import open_app, type_text, click_position, take_screenshot, focus_window, set_volume, set_brightness, set_wallpaper, power_action, mute_volume, unmute_volume, adjust_volume, get_volume
from executor.browser_control import open_url, search_google, download_file, open_url_on_desktop, search_on_desktop, get_weather
from executor.screen_vision import extract_text_from_screen
from executor.screen_vision import capture_screen_state
from executor.messaging import send_email, send_whatsapp
from executor.system_monitor import get_system_stats, list_top_processes, kill_process
from memory.memory_manager import save_task, save_preference, get_chat_history, add_chat_message
from memory.experience_learning import store_experience
from safety.safety_guard import validate_task
from executor.agentic_loop import run_agent_loop

                                  
logger = logging.getLogger(__name__)

                    
CALLBACK_SEND = "msg_send"
CALLBACK_EDIT = "msg_edit"
CALLBACK_CANCEL = "msg_cancel"
CALLBACK_BUILD_YES = "build_yes"
CALLBACK_BUILD_NO = "build_no"

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    import traceback
    tb = "".join(traceback.format_exception(type(context.error), context.error, context.error.__traceback__))
    logger.error(f"ðŸš¨ Telegram Error:\n{tb}")
    if update and isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(f"âš ï¸ Internal Error: {str(context.error)[:200]}")
        except:
            pass


def is_allowed(user_id: int) -> bool:
    logger.info(f"User ID: {user_id} - is_allowed? Always TRUE in debug mode.")
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_allowed(user.id):
        logger.warning(f"Unauthorized /start attempt by User ID: {user.id}")
        await update.message.reply_text(f"Sorry, you are not authorized to use {config.AGENT_NAME}.")
        return

    await update.message.reply_text(
        f"Hello {user.first_name}! I'm {config.AGENT_NAME} - an autonomous coding & automation copilot. "
        "Ask me anything or send /help to see examples."
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Hereâ€™s what I can do:\n"
        "â€¢ Build/modify software projects (multi-file)\n"
        "â€¢ Research and summarize topics\n"
        "â€¢ Automate your desktop/browser\n"
        "â€¢ Run/debug code and fix errors\n\n"
        "Commands:\n"
        "/auto <goal> â€” launch full autonomous mode\n"
        "/status â€” show if a task is running\n"
        "/stop â€” cancel the current task\n"
        "/help â€” this message"
    )
    await update.message.reply_text(text)

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task = context.user_data.get('running_task')
    if task and not task.done():
        await update.message.reply_text("Iâ€™m working on your task right now. Send /stop to cancel.")
    else:
        await update.message.reply_text("No active tasks. What should we do next?")

async def screen_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO)
    shot = await asyncio.to_thread(capture_screen_state)
    if shot.get("status") != "success":
        await update.message.reply_text(f"Couldnâ€™t capture screen: {shot.get('message')}")
        return
    path = shot.get("path")
    text = shot.get("text", "").strip() or "(no text detected)"
    try:
        with open(path, "rb") as f:
            await update.message.reply_photo(photo=f, caption=f"OCR text:\n{text[:900]}")
    except Exception as e:
        await update.message.reply_text(f"OCR text:\n{text[:900]}\n(Note: failed to send image: {e})")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_allowed(user.id): return

    voice = update.message.voice
    logger.info(f"Received voice message from {user.id} ({voice.duration}s)")
    
    await update.message.reply_text("ðŸŽ¤ *Listening...* (Transcribing voice message)", parse_mode='Markdown')
    
    try:
                                 
        file = await context.bot.get_file(voice.file_id)
                                   
        os.makedirs("temp", exist_ok=True)
        temp_file = f"temp/voice_{voice.file_id}.ogg"
        await file.download_to_drive(temp_file)
        
                                                                           
        from openai import OpenAI
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        
        def _transcribe():
            with open(temp_file, "rb") as audio_file:
                return client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
        
        transcript = await asyncio.to_thread(_transcribe)
        text = transcript.text
        logger.info(f"Voice Transcription: {text}")
        
        await update.message.reply_text(f"ðŸ—£ï¸ *You said:* \"{text}\"", parse_mode='Markdown')
        
                                         
        update.message.text = text
        await handle_message(update, context)
        
                 
        if os.path.exists(temp_file): os.remove(temp_file)
        
    except Exception as e:
        logger.error(f"Voice transcription error: {e}")
        await update.message.reply_text(f"âŒ Failed to transcribe voice: {str(e)}")

                  
async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user: return
    if not is_allowed(user.id):
        await update.message.reply_text("Access denied for /stop.")
        return

    task = context.user_data.get('running_task')
    if task and not task.done():
        task.cancel()
        context.user_data['running_task'] = None
        await update.message.reply_text("ðŸ›‘ Stopped the running autonomous task.")
    else:
        await update.message.reply_text("â„¹ï¸ No autonomous task is currently running.")

async def handle_update_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user:
        logger.info(f"--- UPDATE: User {update.effective_user.id} sent: {update.message.text if update.message else 'non-text message'}")
    else:
        logger.info(f"--- UPDATE: No user or non-message update: {update}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user: return
    
    original_text = (update.message.text or "").strip()
    text_lower = original_text.lower()
    
                                                    
    fast_parse = fallback_parse(original_text)
    is_fast_intent = fast_parse.get("intent") != "general_request"
    
    if not is_fast_intent:
        thinking_msg = await update.message.reply_text("Thinking...")
    else:
        try: await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        except: pass
        thinking_msg = None
    
                       
    if not is_allowed(user.id):
        logger.warning(f"Unauthorized message attempt by User ID: {user.id}")
        await update.message.reply_text(f"Access Denied. Your ID: {user.id}")
        if thinking_msg: await thinking_msg.delete()
        return

    logger.info(f"Received message from authorized user {user.id}: {original_text}")
    add_chat_message(user.id, "user", original_text)

                                 
    stop_keywords = ["stop", "cancel", "halt", "kill", "terminate", "exit", "shut down"]
    if any(kw == text_lower or f"/{kw}" == text_lower or text_lower.startswith(f"{kw} ") for kw in stop_keywords):
        active_task = context.user_data.get('running_task')
        if active_task and not active_task.done():
            logger.info(f"Cancelling active task for user {user.id}")
            active_task.cancel()
            context.user_data['running_task'] = None
            await update.message.reply_text("ðŸ›‘ *Emergency Stop Triggered!* Stopping all operations immediately...", parse_mode='Markdown')
            return
        else:
            await update.message.reply_text("â„¹ï¸ No active task is currently running.")
            return

                                                           
    existing_task = context.user_data.get('running_task')
    if existing_task and not existing_task.done():
        if "stop" not in text_lower:
            await update.message.reply_text("â³ I'm already busy with a goal! Please wait or send 'stop' to cancel it.")
            return

                                     
    if context.user_data.get('state') == 'awaiting_edit':
        pending = context.user_data.get('pending_task')
        if pending and 'plan' in pending:
                                                    
            for step in pending['plan']:
                if step.get('action') in ['send_whatsapp', 'send_email']:
                    if step.get('action') == 'send_whatsapp':
                        step['text'] = original_text
                    else:
                        step['body'] = original_text
            
                                       
            context.user_data['state'] = None
            await ask_for_confirmation(update, context, pending['plan'], pending['intent'])
            return
        else:
            context.user_data['state'] = None

    if context.user_data.get('state') == 'awaiting_build_changes':
        context.user_data['state'] = None
        await update.message.reply_text(f"ðŸ—ï¸ *Applying changes...*\nProcessing: `{original_text}`", parse_mode='Markdown')

                                                            
    history = get_chat_history(user.id, limit=6)

    try:
                                                            
        parsed_command = await parse_prompt(original_text, history=history)
        intent = parsed_command.get('intent', 'unknown')
        
                          
        plan = await plan_task(parsed_command, user_id=user.id)
        
                                                               
        if len(plan) == 1 and plan[0].get("action") == "reply":
            if thinking_msg: await thinking_msg.edit_text(plan[0].get("message", "Done."), parse_mode='Markdown')
            else: await update.message.reply_text(plan[0].get("message", "Done."), parse_mode='Markdown')
            add_chat_message(user.id, "assistant", plan[0].get("message", ""))
            return

                                                  
        plan_summary = f"ðŸ§  *Plan*\nIntent: `{intent.replace('_', ' ').title()}`\n\n"
        for i, step in enumerate(plan, 1):
            if step.get('action') == 'error':
                plan_summary += f"âŒ {step.get('message')}\n"
            else:
                action_name = step.get('action', '').replace('_', ' ').title()
                plan_summary += f"{i}. {action_name}\n"
        
        if thinking_msg:
            await thinking_msg.edit_text(plan_summary, parse_mode='Markdown')

                                                   
        is_messaging = any(step.get('action') in ['send_whatsapp', 'send_email'] for step in plan)
        if is_messaging:
            logger.info("TEST_DEBUG: Calling ask_for_confirmation")
            context.user_data['pending_task'] = {'plan': plan, 'intent': intent, 'original_prompt': original_text}
            await ask_for_confirmation(update, context, plan, intent)
            logger.info("TEST_DEBUG: ask_for_confirmation returned")
            return

                              
        logger.info("TEST_DEBUG: Starting execute_plan")
        if not is_fast_intent:
            await update.message.reply_text("ðŸš€ Starting execution...", parse_mode='Markdown')
        
                                                    
        exec_task = asyncio.create_task(execute_plan(update, context, plan, intent, original_text))
        context.user_data['running_task'] = exec_task
        
        try:
            await exec_task
        except asyncio.CancelledError:
            logger.info("Task execution was cancelled by user stop command.")
                                                           
            try: await msg_handle.reply_text("ðŸ›‘ *Execution Terminated.* All active processes stopped.")
            except: pass
        finally:
            context.user_data['running_task'] = None
            
    except Exception as e:
        logger.error(f"Error in handle_message: {e}", exc_info=True)
        try:
            await update.message.reply_text(f"âš ï¸ Error: {str(e)}")
        except Exception:
            pass

async def ask_for_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE, plan: list, intent: str):
    msg_preview = ""
    for step in plan:
        if step.get('action') == 'send_whatsapp':
            msg_preview = f"ðŸ“± *WhatsApp to:* `{step.get('phone')}`\n*Message:* {step.get('text')}"
            break
        elif step.get('action') == 'send_email':
            msg_preview = f"ðŸ“§ *Email to:* `{step.get('to')}`\n*Subject:* {step.get('subject')}\n*Body:* {step.get('body')}"
            break
            
    if len(msg_preview) > 3000:
        msg_preview = msg_preview[:3000] + "\n... [PREVIEW TRUNCATED]"
    
    keyboard = [
        [
            InlineKeyboardButton("âœ… Send Now", callback_data=CALLBACK_SEND),
            InlineKeyboardButton("âœï¸ Edit Text", callback_data=CALLBACK_EDIT),
        ],
        [InlineKeyboardButton("âŒ Cancel", callback_data=CALLBACK_CANCEL)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    confirm_text = f"ðŸ¤– *Personal Assistant Check*\n\nI've drafted the following for you:\n\n{msg_preview}\n\n*Would you like me to send this message, or should we make changes?*"
    
    if update.callback_query:
        try:
            await update.callback_query.edit_message_text(confirm_text, reply_markup=reply_markup, parse_mode='Markdown')
        except Exception as e:
            logger.warning(f"Markdown parse error in confirmation: {e}")
            await update.callback_query.edit_message_text(confirm_text.replace("*", "").replace("`", ""), reply_markup=reply_markup)
    else:
        try:
            await update.message.reply_text(confirm_text, reply_markup=reply_markup, parse_mode='Markdown')
        except Exception as e:
            logger.warning(f"Markdown parse error in confirmation: {e}")
            await update.message.reply_text(confirm_text.replace("*", "").replace("`", ""), reply_markup=reply_markup)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    pending = context.user_data.get('pending_task')
    
    if not pending:
        await query.edit_message_text("No pending task found.")
        return

    if data == CALLBACK_SEND:
        await query.edit_message_text("ðŸš€ *Executing your request immediately...*", parse_mode='Markdown')
                                  
        exec_task = asyncio.create_task(execute_plan(update, context, pending['plan'], pending['intent'], pending['original_prompt']))
        context.user_data['running_task'] = exec_task
        context.user_data['pending_task'] = None
    elif data == CALLBACK_EDIT:
        context.user_data['state'] = 'awaiting_edit'
        await query.edit_message_text("ðŸ“ *Understood!* Please type the new message content exactly as you want it sent:")
    elif data == CALLBACK_CANCEL:
        context.user_data['pending_task'] = None
        context.user_data['state'] = None
        await query.edit_message_text("ðŸ—‘ï¸ *Cancelled.* I've discarded the draft. What else can I do for you?")
    elif data == CALLBACK_BUILD_YES:
        context.user_data['state'] = 'awaiting_build_changes'
        await query.edit_message_text("ðŸ› ï¸ *Great!* Please describe the changes or improvements you'd like to make to the project:")
    elif data == CALLBACK_BUILD_NO:
        context.user_data['state'] = None
        await query.edit_message_text("ðŸ *Perfect!* Your project is ready and the live preview is open. Let me know if you need anything else!")

async def execute_plan(update: Update, context: ContextTypes.DEFAULT_TYPE, plan: list, intent: str, original_text: str):
    msg_handle = update.message if update.message else update.callback_query.message
    result = {"status": "none", "message": "No steps executed"}

    for i, step in enumerate(plan, 1):
        action = step.get("action")
        
                                        
        is_safe, safety_msg = validate_task(step)
        if not is_safe:
            await msg_handle.reply_text(f"ðŸ›¡ï¸ *Safety Guard Blocked this action!*\nReason: {safety_msg}", parse_mode='Markdown')
            logger.warning(f"Safety Block on Step {i}: {safety_msg}")
            break

        result = {"status": "error", "message": f"Unknown action: {action}"}
        
                                                
        if action == "create_folder":
            result = create_folder(step.get("path"))
        elif action == "write_file":
            content = step.get("content", "# No content provided in plan")
            file_path = step.get("file")
            result = write_file(file_path, content)
        elif action == "open_app":
            result = await asyncio.to_thread(open_app, step.get("target"))
        elif action == "type_text":
            result = await asyncio.to_thread(type_text, step.get("text"))
        elif action == "click_position":
            result = await asyncio.to_thread(click_position, step.get("x"), step.get("y"))
        elif action == "take_screenshot":
            result = await asyncio.to_thread(take_screenshot, step.get("file", "screenshot.png"))
            if result.get("status") == "success":
                try:
                    await msg_handle.reply_photo(photo=result.get("path"), caption="ðŸ“¸ Here is your screenshot!")
                except Exception as e:
                    logger.error(f"Telegram API Error sending photo: {e}")
                    result["message"] += f" (Note: Failed to upload picture to Telegram - {e})"
        elif action == "focus_window":
            result = focus_window(step.get("target"))
        elif action == "set_volume":
            result = await asyncio.to_thread(set_volume, step.get("level", 50))
        elif action == "mute_volume":
            result = await asyncio.to_thread(mute_volume)
        elif action == "unmute_volume":
            result = await asyncio.to_thread(unmute_volume)
        elif action == "adjust_volume":
            result = await asyncio.to_thread(adjust_volume, step.get("delta", 10))
        elif action == "get_volume":
            result = await asyncio.to_thread(get_volume)
        elif action == "set_brightness":
            result = await asyncio.to_thread(set_brightness, step.get("level"))
        elif action == "set_wallpaper":
            result = set_wallpaper(step.get("path"))
        elif action == "run_command":
            result = await run_command(step.get("cmd"))
        elif action == "run_python":
            result = await run_python(step.get("file"))
        elif action == "log":
            result = {"status": "success", "message": step.get("message")}
        elif action == "reply":
            result = {"status": "success", "message": step.get("message")}
            reply_text = step.get("message")
            await msg_handle.reply_text(f"ðŸ’¬ {reply_text}")
            try:
                user_id = update.effective_user.id if update.effective_user else None
                if user_id: add_chat_message(user_id, "assistant", reply_text)
            except Exception:
                pass
            continue
        elif action == "open_url":
            result = await open_url_on_desktop(step.get("url"))
        elif action == "search_google":
            result = await search_on_desktop(step.get("query"))
        elif action == "download_file":
            result = await download_file(step.get("url"), step.get("filename"))
        elif action == "wait":
            seconds = step.get("seconds", 2)
            await asyncio.sleep(seconds)
            result = {"status": "success", "message": f"Waited {seconds} seconds."}
        elif action == "vision_click":
            from executor.screen_vision import super_click
            result = await super_click(step.get("text"))
        elif action == "read_screen":
            text_extracted = await asyncio.to_thread(extract_text_from_screen)
            result = {"status": "success", "message": "Extracted text from screen", "content": text_extracted}
        elif action in ["build_software", "run_agentic_loop"]:
            from executor.agentic_loop import run_agent_loop
            async def progress(m): 
                try: await msg_handle.reply_text(m, parse_mode='Markdown')
                except: await msg_handle.reply_text(m.replace("*", "").replace("`", ""))
            result = await run_agent_loop(step.get("prompt", original_text), progress_callback=progress)
        elif action == "send_email":
            result = await send_email(step.get("to"), step.get("subject", ""), step.get("body", ""))
        elif action == "send_whatsapp":
            result = await asyncio.to_thread(send_whatsapp, step.get("phone"), step.get("text", ""))
        elif action == "get_stats":
            result = get_system_stats()
        elif action == "list_procs":
            result = list_top_processes()
        elif action == "kill_proc":
            result = kill_process(step.get("target"))
        elif action == "power_action":
            result = power_action(step.get("sub_action"))
        elif action == "search_files":
            result = search_files(step.get("query"))
        elif action == "get_weather":
            result = await get_weather(step.get("city", "Dhaka"))

                            
        icon = "âœ…" if result.get("status") == "success" else "âŒ"
        human_action = action.replace("_", " ").title()
        msg = f"{icon} {human_action}\n"
        if "message" in result:
            msg += f"{result['message']}\n"
        
        if "results" in result:
            msg += "\nðŸ”Ž Highlights:\n"
            for res in result["results"]:
                msg += f"â€¢ {res}\n"
        
        if "content" in result:
            msg += f"\nðŸ“„ Snippet:\n{result['content']}..."

        if "stdout" in result and result["stdout"]:
            msg += f"```\n{result['stdout']}\n```"
        if "stderr" in result and result["stderr"]:
            msg += f"âš ï¸ Error Output:\n```\n{result['stderr']}\n```"
        
        try:
            await msg_handle.reply_text(msg, parse_mode='Markdown')
        except:
            await msg_handle.reply_text(msg.replace("`", "").replace("*", ""))
        
        if result.get("status") == "error":
            await msg_handle.reply_text("ðŸ›‘ *Execution halted due to error.*", parse_mode='Markdown')
            break
    else:
        await msg_handle.reply_text("âœ¨ *Execution completed successfully!*", parse_mode='Markdown')
        
                                                         
        if intent in ["software_engineering", "build_software"]:
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            keyboard = [
                [
                    InlineKeyboardButton("âœ… Yes, make changes", callback_data=CALLBACK_BUILD_YES),
                    InlineKeyboardButton("âŒ No, I'm done", callback_data=CALLBACK_BUILD_NO)
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await msg_handle.reply_text("ðŸ—ï¸ *Build complete!* Would you like to change or improve anything?", reply_markup=reply_markup, parse_mode='Markdown')
    
                                         
        if result.get("status") == "success" and intent != "general_request" and len(plan) > 0:
            store_experience(original_text, plan, "success")

def run_bot():
    token = config.TELEGRAM_BOT_TOKEN
    
    if not token or token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        logger.error("Please set your TELEGRAM_BOT_TOKEN in config.py.")
        return

    # Python 3.11+ can have no current loop on MainThread after prior loop shutdowns.
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    from telegram.request import HTTPXRequest
    t_request = HTTPXRequest(connect_timeout=30)
    application = ApplicationBuilder().token(token).request(t_request).build()
    application.add_handler(MessageHandler(filters.ALL, handle_update_all), group=-1) 
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("status", status_cmd))
    application.add_handler(CommandHandler("screen", screen_cmd))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info(f"Starting {config.AGENT_NAME} Telegram Bot listener...")
                                          
    application.add_error_handler(error_handler)
    
                                                                         
    # Let PTB create/manage the loop lifecycle (Python 3.13 compatibility).
    try:
        application.run_polling(drop_pending_updates=True)
    except Conflict as e:
        # Usually means another bot process is already polling this token.
        raise RuntimeError(f"TELEGRAM_CONFLICT: {e}") from e


if __name__ == '__main__':
    run_bot()

