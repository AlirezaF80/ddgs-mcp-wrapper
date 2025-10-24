# Example MCP Client Configurations

## Claude Desktop Configuration

Location: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ddgs-search": {
      "command": "python",
      "args": ["d:\\MCP Servers\\ddgs-mcp-wrapper\\server.py"],
      "env": {
        "DDGS_PROXY": ""
      }
    }
  }
}
```

### With Tor Browser Proxy
```json
{
  "mcpServers": {
    "ddgs-search": {
      "command": "python",
      "args": ["d:\\MCP Servers\\ddgs-mcp-wrapper\\server.py"],
      "env": {
        "DDGS_PROXY": "socks5h://127.0.0.1:9150"
      }
    }
  }
}
```

### Using Virtual Environment
```json
{
  "mcpServers": {
    "ddgs-search": {
      "command": "d:\\MCP Servers\\ddgs-mcp-wrapper\\venv\\Scripts\\python.exe",
      "args": ["d:\\MCP Servers\\ddgs-mcp-wrapper\\server.py"]
    }
  }
}
```

## VS Code / Cline Configuration

Location: `.vscode/settings.json` in your project

```json
{
  "mcp.servers": {
    "ddgs-search": {
      "command": "python",
      "args": ["d:\\MCP Servers\\ddgs-mcp-wrapper\\server.py"]
    }
  }
}
```

## Environment Variables

You can set these environment variables for additional configuration:

### Windows PowerShell
```powershell
# Set proxy for all DDGS requests
$env:DDGS_PROXY = "socks5h://127.0.0.1:9150"

# Or HTTP proxy
$env:DDGS_PROXY = "http://proxy.example.com:8080"
```

### Windows Command Prompt
```cmd
set DDGS_PROXY=socks5h://127.0.0.1:9150
```

## Testing Your Configuration

### 1. Test the Server Directly
```powershell
cd "d:\MCP Servers\ddgs-mcp-wrapper"
python server.py
```

The server should start and wait for JSON-RPC messages on stdin.

### 2. Use MCP Inspector
```powershell
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Run inspector
mcp-inspector python server.py
```

This opens a web interface to test your MCP server interactively.

### 3. Test with a Simple Query

Once connected to your MCP client (Claude Desktop, Cline, etc.), try:

```
Search for "python machine learning tutorials" using the DDGS search tool
```

Or more specific:

```
Use ddgs_text_search to find PDF files about neural networks published in the last year
Query: "neural networks filetype:pdf"
Timelimit: "y"
Max results: 20
```

## Advanced Configuration Examples

### Multiple MCP Servers
```json
{
  "mcpServers": {
    "ddgs-search": {
      "command": "python",
      "args": ["d:\\MCP Servers\\ddgs-mcp-wrapper\\server.py"]
    },
    "another-server": {
      "command": "node",
      "args": ["path/to/another-server.js"]
    }
  }
}
```

### With Custom Python Path
```json
{
  "mcpServers": {
    "ddgs-search": {
      "command": "C:\\Python311\\python.exe",
      "args": ["d:\\MCP Servers\\ddgs-mcp-wrapper\\server.py"],
      "env": {
        "PYTHONPATH": "d:\\MCP Servers\\ddgs-mcp-wrapper",
        "DDGS_PROXY": ""
      }
    }
  }
}
```

### Development Mode (with Debug Logging)
Modify `server.py` to enable debug logging:
```python
logging.basicConfig(level=logging.DEBUG)
```

Then restart your MCP client.

## Troubleshooting Configuration

### Issue: "Command not found"
- Use absolute paths for both `command` and `args`
- Check that Python is in your PATH: `python --version`

### Issue: "Module not found"
- Ensure dependencies are installed: `pip install -r requirements.txt`
- Use virtual environment python path in config

### Issue: "Server not responding"
- Check server logs (if your MCP client provides them)
- Test server directly: `python server.py`
- Verify JSON syntax in config file

### Issue: "Connection timeout"
- Check proxy settings if using one
- Verify network connectivity
- Try without proxy first

## Example Usage Scenarios

### 1. Research Assistant
```
"Find recent academic papers about quantum computing"
Tool: ddgs_text_search
Query: "quantum computing filetype:pdf site:.edu"
Timelimit: "m"
Max_results: 15
```

### 2. News Aggregation
```
"Get latest news about artificial intelligence"
Tool: ddgs_news_search
Query: "artificial intelligence"
Timelimit: "d"
Max_results: 10
```

### 3. Image Collection
```
"Find high-resolution landscape photos"
Tool: ddgs_image_search
Query: "mountain landscape"
Size: "Wallpaper"
Type_image: "photo"
Max_results: 20
```

### 4. Book Research
```
"Find books by Isaac Asimov"
Tool: ddgs_book_search
Query: "Isaac Asimov Foundation"
Max_results: 10
```

### 5. Video Tutorials
```
"Find Python tutorial videos"
Tool: ddgs_video_search
Query: "Python programming tutorial"
Duration: "medium"
Resolution: "high"
Max_results: 15
```
