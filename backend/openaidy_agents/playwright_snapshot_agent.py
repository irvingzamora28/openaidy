import json

def to_serializable(obj):
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    elif isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple, set)):
        return [to_serializable(x) for x in obj]
    elif hasattr(obj, 'dict') and callable(getattr(obj, 'dict')):
        return to_serializable(obj.dict())
    elif hasattr(obj, '__dict__'):
        return to_serializable(vars(obj))
    else:
        return str(obj)

async def snapshot_with_mcp(mcp_server, filename="snapshot.json"):
    """
    Directly calls the 'browser_snapshot' tool using the given MCP server and saves the result to a file.
    Args:
        mcp_server: MCP server instance for browser automation.
        filename (str): Where to save the snapshot (default: 'snapshot.json').
    Returns:
        dict: The snapshot structure (JSON-serializable)
    """
    snapshot = await mcp_server.call_tool("browser_snapshot")
    # Extract serializable content
    data = None
    if hasattr(snapshot, 'result'):
        data = snapshot.result
    elif hasattr(snapshot, 'data'):
        data = snapshot.data
    else:
        try:
            data = dict(snapshot)
        except Exception:
            data = str(snapshot)
    serializable_data = to_serializable(data)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(serializable_data, f, indent=2, ensure_ascii=False)
    return serializable_data
