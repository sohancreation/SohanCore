filepath = 'e:/SohanCore/sohan_ai_agent/bot_bridge/bot_listener.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

target = '''        elif step.get('action') == 'send_email':
            msg_preview = f"📧 *Email to:* `{step.get('to')}`\\n*Subject:* {step.get('subject')}\\n*Body:* {step.get('body')}"
            break'''

replacement = '''        elif step.get('action') == 'send_email':
            msg_preview = f"📧 *Email to:* `{step.get('to')}`\\n*Subject:* {step.get('subject')}\\n*Body:* {step.get('body')}"
            break
            
    if len(msg_preview) > 3000:
        msg_preview = msg_preview[:3000] + "\\n... [PREVIEW TRUNCATED]"'''

if target in content:
    content = content.replace(target, replacement)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Replaced msg_preview formatting successfully.")
else:
    print("Target string not found in file!")
