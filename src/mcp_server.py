from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import create_agent
from agents.order_agent import create_order_agent
from agents.product_agent import create_product_agent
from agents.delivery_agent import create_delivery_agent

server = Server("cs-agent")

cs_agent = create_agent()
order_agent = create_order_agent()
product_agent = create_product_agent()
delivery_agent = create_delivery_agent()

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="cs_agent",
            description="무신사 FAQ 기반 일반 고객 문의 답변. 환불정책, 교환방법, 회원정보 등 일반적인 CS 문의에 사용하세요.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_input": {"type": "string", "description": "고객 문의 내용"}
                },
                "required": ["user_input"]
            }
        ),
        Tool(
            name="order_agent",
            description="주문 조회 및 확인. 주문번호(예: O00000001)가 포함된 문의에 사용하세요.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_input": {"type": "string", "description": "주문 관련 문의"}
                },
                "required": ["user_input"]
            }
        ),
        Tool(
            name="product_agent",
            description="상품 검색 및 정보 조회. 특정 상품명이나 브랜드 검색 문의에 사용하세요.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_input": {"type": "string", "description": "상품 관련 문의"}
                },
                "required": ["user_input"]
            }
        ),
        Tool(
            name="delivery_agent",
            description="배송 상태 조회. 주문번호(예: O00000001)로 배송 현황을 확인할 때 사용하세요.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_input": {"type": "string", "description": "배송 관련 문의"}
                },
                "required": ["user_input"]
            }
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    user_input = arguments["user_input"]
    state = {
        "user_input": user_input,
        "category": "",
        "search_results": [],
        "answer": "",
        "escalate": False
    }

    if name == "order_agent":
        result = order_agent.invoke(state)
    elif name == "product_agent":
        result = product_agent.invoke(state)
    elif name == "delivery_agent":
        result = delivery_agent.invoke(state)
    else:
        result = cs_agent.invoke(state)

    return [TextContent(type="text", text=result["answer"])]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())