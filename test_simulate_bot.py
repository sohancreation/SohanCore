
import asyncio
import os
import sys

sys.path.append(os.getcwd())

# Ensure UTF-8 for console output on Windows to prevent 'charmap' errors with emojis
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import bot_bridge.bot_listener as bl
from telegram import Update, User, Message, Chat

class MockMessage:
    def __init__(self, text):
        self.text = text
        self.chat = Chat(id=5726267614, type="private")
        self.message_id = 1
        self.date = None
        self.from_user = User(id=5726267614, first_name="User", is_bot=False)
        self.replies = []
    
    async def reply_text(self, text, **kwargs):
        try:
            print(f"[BOT REPLY TEXT]: {text}")
        except UnicodeEncodeError:
            print(f"[BOT REPLY TEXT]: {text.encode('ascii', errors='replace').decode('ascii')}")
            # The original `safe_text` variable was removed in the provided edit.
            # To maintain syntactic correctness and avoid NameError,
            # the line referencing `safe_text` is removed as it would be undefined.
            # If the intent was to print the encoded text again, the line should be:
            # print(f"[BOT REPLY TEXT (Safe)]: {text.encode('ascii', errors='replace').decode('ascii')}")
        self.replies.append({"type": "text", "content": text})
        
    async def reply_photo(self, photo, caption=None):
        try:
            print(f"[BOT REPLY PHOTO]: caption={caption}")
        except UnicodeEncodeError:
            safe_caption = caption.encode('ascii', 'ignore').decode('ascii') if caption else None
            print(f"[BOT REPLY PHOTO (Safe)]: caption={safe_caption}")
        self.replies.append({"type": "photo", "caption": caption})

class MockUpdate:
    def __init__(self, text):
        self.effective_user = User(id=5726267614, first_name="User", is_bot=False)
        self.message = MockMessage(text)
        self.callback_query = None

class MockContext:
    def __init__(self):
        self.user_data = {}

async def test_simulate(query: str = "build a weather app"):
    print(f"--- SIMULATING: {query} ---")
    update = MockUpdate(query)
    context = MockContext()
    await bl.handle_message(update, context)

if __name__ == "__main__":
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else "build a weather app"
    asyncio.run(test_simulate(query))
