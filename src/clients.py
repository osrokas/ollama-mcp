from collections.abc import Iterator
import json
import ollama
from fastmcp import Client


class OllamaClient:
    def __init__(self, server_url: str, role: str = 'system', content: str = ''):
        self.server_url = server_url
        self.client_tools = []
        self.prompt = {'role': role, 'content': content}

    async def __aenter__(self):
        self.client = await Client(self.server_url).__aenter__()
        await self._append_tools()
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        await self.client.close()

    async def _append_tools(self):
        tools = await self.client.list_tools()
        for tool in tools:
            self.client_tools.append({
                'type': 'function',
                'function': {
                    'name': tool.name,
                    'description': tool.description,
                    'parameters': tool.inputSchema
                }
            })

    def chat(self, model: str, messages: list):
        response = ollama.chat(model=model, messages=messages, tools=self.client_tools, stream=True)
        return response
    
    async def handle_tool_calls(self, response: Iterator[ollama.ChatResponse]):
        tool_message = None
        assistant_chunks = []
        for chunk in response:
            if chunk.message.tool_calls:
                for tool in chunk.message.tool_calls:
                    print(f'Calling {tool.function.name}')
                    print(f'\tWith params: {tool.function.arguments}')

                    result = await self.client.call_tool(
                        name=tool.function.name,
                        arguments=tool.function.arguments
                    )

                    message = {
                        'role': 'tool',
                        'content': json.dumps(result, indent=2) if isinstance(result, dict) else str(result),
                        'name': tool.function.name,
                    }
                    return message
            elif chunk.message.content:
                message = {
                    'role': 'assistant',
                    'content': chunk.message.content,
                }

            
