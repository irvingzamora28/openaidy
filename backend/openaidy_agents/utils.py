import re
import json

def parse_json_block(val):
    """
    Removes code fences and parses JSON. Handles both code-fenced and plain JSON strings.
    """
    if isinstance(val, str):
        # Remove code fences and parse JSON
        match = re.match(r"```json\n([\s\S]+?)```", val.strip())
        if match:
            json_str = match.group(1)
            try:
                return json.loads(json_str)
            except Exception:
                pass
        # Try to parse as plain JSON string if no code fence
        try:
            return json.loads(val)
        except Exception:
            pass
    return val

def deep_clean(obj):
    """
    Recursively cleans an object by parsing JSON blocks in strings and cleaning nested structures.
    """
    if isinstance(obj, dict):
        return {k: deep_clean(parse_json_block(v)) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [deep_clean(parse_json_block(i)) for i in obj]
    else:
        return parse_json_block(obj)
