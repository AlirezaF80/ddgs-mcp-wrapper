#!/usr/bin/env python3
"""
DDGS MCP Server - A Model Context Protocol server wrapping the DDGS search library.

This server exposes web search capabilities (text, images, videos, news, books)
through the MCP protocol for use by AI agents and assistants.
"""

import asyncio
import logging
from typing import Any, Optional
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import mcp.types as types

from ddgs import DDGS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ddgs-mcp-server")

# Create server instance
app = Server("ddgs-mcp-server")

# Store DDGS instance
ddgs_instance: Optional[DDGS] = None


def get_ddgs_instance(proxy: Optional[str] = None, timeout: int = 10) -> DDGS:
    """Get or create DDGS instance with optional proxy configuration."""
    global ddgs_instance
    if ddgs_instance is None or proxy:
        ddgs_instance = DDGS(proxy=proxy, timeout=timeout, verify=True)
    return ddgs_instance


# Resources are optional for search tools - we'll use Tools instead


@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available search tools."""
    return [
        Tool(
            name="ddgs_text_search",
            description="""Search the web for text content across multiple search engines.
            
Supports search operators:
- cats dogs: Results about cats OR dogs
- "exact phrase": Exact match
- cats -dogs: Fewer dogs in results
- cats +dogs: More dogs in results
- filetype:pdf: Specific file types
- site:example.com: Specific domain
- intitle:word: Word in page title
- inurl:word: Word in URL

Regions: us-en, uk-en, cn-zh, etc.
Backends: auto, bing, brave, duckduckgo, google, mojeek, yahoo, wikipedia""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query with optional operators"
                    },
                    "region": {
                        "type": "string",
                        "description": "Region code (e.g., us-en, uk-en)",
                        "default": "us-en"
                    },
                    "safesearch": {
                        "type": "string",
                        "enum": ["on", "moderate", "off"],
                        "description": "Safe search level",
                        "default": "moderate"
                    },
                    "timelimit": {
                        "type": "string",
                        "enum": ["d", "w", "m", "y"],
                        "description": "Time limit (d=day, w=week, m=month, y=year)"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 100
                    },
                    "backend": {
                        "type": "string",
                        "description": "Comma-separated list of backends or 'auto'",
                        "default": "auto"
                    },
                    "proxy": {
                        "type": "string",
                        "description": "Proxy URL (http/https/socks5) or 'tb' for Tor"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="ddgs_image_search",
            description="Search for images with advanced filtering options",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Image search query"
                    },
                    "region": {
                        "type": "string",
                        "description": "Region code",
                        "default": "us-en"
                    },
                    "safesearch": {
                        "type": "string",
                        "enum": ["on", "moderate", "off"],
                        "default": "moderate"
                    },
                    "timelimit": {
                        "type": "string",
                        "enum": ["d", "w", "m", "y"]
                    },
                    "max_results": {
                        "type": "integer",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 100
                    },
                    "size": {
                        "type": "string",
                        "enum": ["Small", "Medium", "Large", "Wallpaper"]
                    },
                    "color": {
                        "type": "string",
                        "enum": ["color", "Monochrome", "Red", "Orange", "Yellow", "Green", 
                                "Blue", "Purple", "Pink", "Brown", "Black", "Gray", "Teal", "White"]
                    },
                    "type_image": {
                        "type": "string",
                        "enum": ["photo", "clipart", "gif", "transparent", "line"]
                    },
                    "layout": {
                        "type": "string",
                        "enum": ["Square", "Tall", "Wide"]
                    },
                    "license_image": {
                        "type": "string",
                        "enum": ["any", "Public", "Share", "ShareCommercially", 
                                "Modify", "ModifyCommercially"]
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="ddgs_video_search",
            description="Search for videos with filtering options",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Video search query"
                    },
                    "region": {
                        "type": "string",
                        "default": "us-en"
                    },
                    "safesearch": {
                        "type": "string",
                        "enum": ["on", "moderate", "off"],
                        "default": "moderate"
                    },
                    "timelimit": {
                        "type": "string",
                        "enum": ["d", "w", "m"]
                    },
                    "max_results": {
                        "type": "integer",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 100
                    },
                    "resolution": {
                        "type": "string",
                        "enum": ["high", "standard"]
                    },
                    "duration": {
                        "type": "string",
                        "enum": ["short", "medium", "long"]
                    },
                    "license_videos": {
                        "type": "string",
                        "enum": ["creativeCommon", "youtube"]
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="ddgs_news_search",
            description="Search for news articles from multiple sources",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "News search query"
                    },
                    "region": {
                        "type": "string",
                        "default": "us-en"
                    },
                    "safesearch": {
                        "type": "string",
                        "enum": ["on", "moderate", "off"],
                        "default": "moderate"
                    },
                    "timelimit": {
                        "type": "string",
                        "enum": ["d", "w", "m"]
                    },
                    "max_results": {
                        "type": "integer",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 100
                    },
                    "backend": {
                        "type": "string",
                        "description": "Backend: auto, bing, duckduckgo, yahoo",
                        "default": "auto"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="ddgs_book_search",
            description="Search for books across Anna's Archive",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Book search query (title, author, ISBN, etc.)"
                    },
                    "max_results": {
                        "type": "integer",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 100
                    }
                },
                "required": ["query"]
            }
        )
    ]


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    """Handle tool execution requests."""
    try:
        if name == "ddgs_text_search":
            return await handle_text_search(arguments)
        elif name == "ddgs_image_search":
            return await handle_image_search(arguments)
        elif name == "ddgs_video_search":
            return await handle_video_search(arguments)
        elif name == "ddgs_news_search":
            return await handle_news_search(arguments)
        elif name == "ddgs_book_search":
            return await handle_book_search(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        import traceback
        traceback.print_exc()
        return [TextContent(
            type="text",
            text=f"Error executing search: {str(e)}"
        )]


async def handle_text_search(arguments: dict[str, Any]) -> list[types.TextContent]:
    """Handle text search requests."""
    try:
        query = arguments["query"]
        region = arguments.get("region", "us-en")
        safesearch = arguments.get("safesearch", "moderate")
        timelimit = arguments.get("timelimit")
        max_results = arguments.get("max_results", 10)
        backend = arguments.get("backend", "auto")
        proxy = arguments.get("proxy")  # Can be None or a string
        
        logger.info(f"Text search: query='{query}', region={region}, max_results={max_results}, backend={backend}")
        
        # Clean backend parameter - remove any quotes that might have been passed
        if backend:
            backend = backend.strip().strip("'\"")
        
        # Default to duckduckgo if auto fails
        if not backend or backend == "auto":
            backend = "duckduckgo"
        
        logger.info(f"Using backend: {backend}")
        
        # Handle proxy - only use if it's a non-empty string
        proxy_value = None
        if proxy and isinstance(proxy, str) and proxy.strip() and proxy.strip() != '':
            proxy_value = proxy.strip()
            logger.info(f"Using proxy: {proxy_value}")
        
        # Create a fresh DDGS instance for each search to avoid state issues
        ddgs = DDGS(proxy=proxy_value, timeout=10, verify=True)
        
        # Run the search synchronously using asyncio.to_thread for better async compatibility
        try:
            results = await asyncio.to_thread(
                ddgs.text,
                query=query,
                region=region,
                safesearch=safesearch,
                timelimit=timelimit,
                max_results=max_results,
                page=1,
                backend=backend
            )
        except Exception as search_error:
            logger.error(f"DDGS search failed: {search_error}")
            return [TextContent(
                type="text",
                text=f"Search failed: {str(search_error)}\nTry a simpler query or different parameters."
            )]
        
        # Format results
        if not results:
            return [TextContent(type="text", text="No results found.")]
        
        formatted_results = []
        for i, result in enumerate(results, 1):
            # Safely extract URL - handle relative URLs
            url = result.get('href', 'N/A')
            if url and url != 'N/A' and not url.startswith(('http://', 'https://')):
                url = f"https://{url}" if not url.startswith('//') else f"https:{url}"
            
            formatted_results.append(
                f"{i}. {result.get('title', 'No title')}\n"
                f"   URL: {url}\n"
                f"   {result.get('body', 'No description')}\n"
            )
        
        return [TextContent(
            type="text",
            text=f"Found {len(results)} results:\n\n" + "\n".join(formatted_results)
        )]
    except Exception as e:
        logger.error(f"Error in text search handler: {e}")
        import traceback
        traceback.print_exc()
        return [TextContent(
            type="text",
            text=f"Search error: {str(e)}\nPlease try again with different parameters."
        )]


async def handle_image_search(arguments: dict[str, Any]) -> list[types.TextContent]:
    """Handle image search requests."""
    query = arguments["query"]
    region = arguments.get("region", "us-en")
    safesearch = arguments.get("safesearch", "moderate")
    timelimit = arguments.get("timelimit")
    max_results = arguments.get("max_results", 10)
    size = arguments.get("size")
    color = arguments.get("color")
    type_image = arguments.get("type_image")
    layout = arguments.get("layout")
    license_image = arguments.get("license_image")
    
    logger.info(f"Image search: query='{query}', max_results={max_results}")
    
    ddgs = get_ddgs_instance()
    results = ddgs.images(
        query=query,
        region=region,
        safesearch=safesearch,
        timelimit=timelimit,
        max_results=max_results,
        size=size,
        color=color,
        type_image=type_image,
        layout=layout,
        license_image=license_image
    )
    
    if not results:
        return [TextContent(type="text", text="No images found.")]
    
    formatted_results = []
    for i, result in enumerate(results, 1):
        formatted_results.append(
            f"{i}. **{result.get('title', 'No title')}**\n"
            f"   Image: {result.get('image', 'N/A')}\n"
            f"   Thumbnail: {result.get('thumbnail', 'N/A')}\n"
            f"   Source: {result.get('url', 'N/A')}\n"
            f"   Dimensions: {result.get('width', '?')}x{result.get('height', '?')}\n"
        )
    
    return [TextContent(
        type="text",
        text=f"Found {len(results)} images:\n\n" + "\n".join(formatted_results)
    )]


async def handle_video_search(arguments: dict[str, Any]) -> list[types.TextContent]:
    """Handle video search requests."""
    query = arguments["query"]
    region = arguments.get("region", "us-en")
    safesearch = arguments.get("safesearch", "moderate")
    timelimit = arguments.get("timelimit")
    max_results = arguments.get("max_results", 10)
    resolution = arguments.get("resolution")
    duration = arguments.get("duration")
    license_videos = arguments.get("license_videos")
    
    logger.info(f"Video search: query='{query}', max_results={max_results}")
    
    ddgs = get_ddgs_instance()
    results = ddgs.videos(
        query=query,
        region=region,
        safesearch=safesearch,
        timelimit=timelimit,
        max_results=max_results,
        resolution=resolution,
        duration=duration,
        license_videos=license_videos
    )
    
    if not results:
        return [TextContent(type="text", text="No videos found.")]
    
    formatted_results = []
    for i, result in enumerate(results, 1):
        formatted_results.append(
            f"{i}. **{result.get('title', 'No title')}**\n"
            f"   URL: {result.get('content', 'N/A')}\n"
            f"   Duration: {result.get('duration', 'N/A')}\n"
            f"   Publisher: {result.get('publisher', 'N/A')}\n"
            f"   Published: {result.get('published', 'N/A')}\n"
            f"   Description: {result.get('description', 'No description')[:200]}...\n"
        )
    
    return [TextContent(
        type="text",
        text=f"Found {len(results)} videos:\n\n" + "\n".join(formatted_results)
    )]


async def handle_news_search(arguments: dict[str, Any]) -> list[types.TextContent]:
    """Handle news search requests."""
    query = arguments["query"]
    region = arguments.get("region", "us-en")
    safesearch = arguments.get("safesearch", "moderate")
    timelimit = arguments.get("timelimit")
    max_results = arguments.get("max_results", 10)
    backend = arguments.get("backend", "auto")
    
    logger.info(f"News search: query='{query}', max_results={max_results}")
    
    ddgs = get_ddgs_instance()
    results = ddgs.news(
        query=query,
        region=region,
        safesearch=safesearch,
        timelimit=timelimit,
        max_results=max_results,
        backend=backend
    )
    
    if not results:
        return [TextContent(type="text", text="No news found.")]
    
    formatted_results = []
    for i, result in enumerate(results, 1):
        formatted_results.append(
            f"{i}. **{result.get('title', 'No title')}**\n"
            f"   Source: {result.get('source', 'N/A')}\n"
            f"   Date: {result.get('date', 'N/A')}\n"
            f"   URL: {result.get('url', 'N/A')}\n"
            f"   {result.get('body', 'No description')}\n"
        )
    
    return [TextContent(
        type="text",
        text=f"Found {len(results)} news articles:\n\n" + "\n".join(formatted_results)
    )]


async def handle_book_search(arguments: dict[str, Any]) -> list[types.TextContent]:
    """Handle book search requests."""
    query = arguments["query"]
    max_results = arguments.get("max_results", 10)
    
    logger.info(f"Book search: query='{query}', max_results={max_results}")
    
    ddgs = get_ddgs_instance()
    results = ddgs.books(
        query=query,
        max_results=max_results
    )
    
    if not results:
        return [TextContent(type="text", text="No books found.")]
    
    formatted_results = []
    for i, result in enumerate(results, 1):
        formatted_results.append(
            f"{i}. **{result.get('title', 'No title')}**\n"
            f"   Author: {result.get('author', 'N/A')}\n"
            f"   Publisher: {result.get('publisher', 'N/A')}\n"
            f"   Info: {result.get('info', 'N/A')}\n"
            f"   URL: {result.get('url', 'N/A')}\n"
        )
    
    return [TextContent(
        type="text",
        text=f"Found {len(results)} books:\n\n" + "\n".join(formatted_results)
    )]


async def main():
    """Run the MCP server."""
    logger.info("Starting DDGS MCP Server...")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="ddgs-mcp-server",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
