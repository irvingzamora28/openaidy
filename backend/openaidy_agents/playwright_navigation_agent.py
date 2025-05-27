async def navigate_with_mcp(url, mcp_server):
    """
    Directly calls the 'browser_navigate' tool using the given MCP server.
    Args:
        url (str): The page URL to navigate to.
        mcp_server: MCP server instance for browser automation.
    Returns:
        str: Confirmation message.
    """
    await mcp_server.call_tool("browser_navigate", {"url": url})
    return f"Navigation to {url} complete."
