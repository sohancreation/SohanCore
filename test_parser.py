from brain.prompt_parser import fallback_parse
import json

text = "build a tic tac toe games in python"
result = fallback_parse(text)
print(json.dumps(result, indent=2))
