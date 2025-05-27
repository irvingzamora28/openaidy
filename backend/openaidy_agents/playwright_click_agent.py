"""
Custom Playwright click agent that uses the same MCP session to click on a discovered element.
"""

async def click_with_mcp(element_label, element_ref, mcp_server):
    """
    Calls the 'browser_click' tool on the MCP server for the specified element.
    Args:
        element_label (str): Human-readable description of the element (e.g., 'Sort by').
        element_ref (str): The reference string from element_discovery[label].
        mcp_server: MCP server instance for browser automation.
    Returns:
        str: Confirmation message or tool response.
    """
    if not element_ref:
        raise ValueError(f"No ref provided for element '{element_label}'")
    params = {
        "element": element_label,
        "ref": element_ref,
    }
    result = await mcp_server.call_tool("browser_click", params)
    return f"Clicked on '{element_label}' (ref={element_ref}). Tool result: {result}"
