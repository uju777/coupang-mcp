# Coupang MCP

**No API Key Required.** Search Coupang products directly from Claude, Cursor, or Claude Code.

**API 키 없이 바로 사용.** Claude, Cursor, Claude Code에서 쿠팡 상품을 검색하세요.

## Features

- **Product Search** - Search Coupang products by keyword
- **Best Sellers** - Get best selling products by category
- **Gold Box** - Today's deals and discounts
- **Deep Link** - Convert Coupang URLs to short links

## Installation

### Claude Desktop / Cursor / Claude Code

Add to your MCP settings:

```json
{
  "mcpServers": {
    "coupang": {
      "command": "sh",
      "args": [
        "-c",
        "cd /path/to/coupang-mcp/client && uv run --with 'mcp[cli]' --with httpx python server.py"
      ]
    }
  }
}
```

### Usage

Just ask:
- "Search AirPods on Coupang"
- "Show me best sellers in electronics"
- "What's on Gold Box today?"

## Category IDs

| ID | Category |
|----|----------|
| 1001 | Women's Fashion |
| 1002 | Men's Fashion |
| 1010 | Beauty |
| 1012 | Food |
| 1016 | Electronics |
| 1017 | Sports/Leisure |
| 1024 | Health |
| 1029 | Pet Supplies |

## Keywords

MCP, Model Context Protocol, Coupang, Shopping, Korea, E-commerce, Claude, Cursor, Claude Code, AI Assistant, Product Search

## License

MIT
