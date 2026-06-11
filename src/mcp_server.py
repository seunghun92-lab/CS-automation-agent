from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import create_agent

# MCP 서버 생성
server = Server("cs-agent")
agent = create_agent()

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="cs_agent",
            description="무신사 고객센터 AI 에이전트입니다. 고객 문의를 입력하면 FAQ 기반으로 답변합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_input": {
                        "type": "string",
                        "description": "고객 문의 내용"
                    }
                },
                "required": ["user_input"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "cs_agent":
        user_input = arguments["user_input"]
        
        result = agent.invoke({
            "user_input": user_input,
            "category": "",
            "search_results": [],
            "answer": "",
            "escalate": False
        })
        
        return [TextContent(type="text", text=result["answer"])]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())