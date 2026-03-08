import json

filepath = 'e:/SohanCore/sohan_ai_agent/bot_bridge/bot_listener.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

target = '''                params = {k: v for k, v in step.items() if k != 'action'}
                plan_summary += f"{i}. `{step.get('action')}`: {json.dumps(params)}\\n"'''

replacement = '''                params = {k: v for k, v in step.items() if k != 'action'}
                step_str = json.dumps(params)
                if len(step_str) > 700: step_str = step_str[:700] + "... [TRUNCATED]"
                plan_summary += f"{i}. `{step.get('action')}`: {step_str}\\n"
        
        if len(plan_summary) > 4000:
            plan_summary = plan_summary[:4000] + "\\n... [PLAN TRUNCATED]"'''

if target in content:
    content = content.replace(target, replacement)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Replaced plan_summary formatting successfully.")
else:
    print("Target string not found in file!")
