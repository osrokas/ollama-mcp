import os
import asyncio
import json
import argparse

from dotenv import load_dotenv

from src.clients import OllamaClient

if os.path.exists('.env'):
    load_dotenv('.env', override=True, verbose=True)

# Load MCP server URL from environment variable or use default
MCP_SERVER = os.getenv('MCP_SERVER', 'http://localhost:8050/sse')
    
    
async def main(model: str):
    print(f'Running with model={model}. Type "/quit" to exit.')
    
    # Initialize Ollama client with MCP server tools
    async with OllamaClient(MCP_SERVER, role='system', content='You must return the tool response exactly as received.') as llm_client:
        # Available tools
        print('Available tools:')
        for t in llm_client.client_tools:
            print(f"\t- {t['function']['name']}: {t['function']['description']}")
        print('---')
        
        # System prompt
        prompt = [llm_client.prompt]
        
        # Chat loop
        while True:
            # Get user input
            user_input = input('>> ').strip()
            if user_input.startswith('/'):
                break
            elif not user_input:
                continue
            
            # Append user message to prompt
            prompt.append({'role': 'user', 'content': user_input})
            
            # Generate response from ollama
            response = llm_client.chat(model, messages=prompt)
            
            # Handle the response
            tool_called = False
            for chunk in response:
                if chunk.message.tool_calls:
                    tool_called = True
                    for tool in chunk.message.tool_calls:
                        print(f'Calling {tool.function.name}')
                        print(f'\tWith params: {tool.function.arguments}')
                        result = await llm_client.client.call_tool(
                            name=tool.function.name,
                            arguments=tool.function.arguments
                        )
                        message = {
                            'role': 'tool',
                            'content': json.dumps(result, indent=2) if isinstance(result, dict) else str(result),
                            'name': tool.function.name,
                        }
                        prompt.append(message)
                    break
                elif chunk.message.content:
                    # Print assistant response
                    print(chunk.message.content, end='', flush=True)
                    
                    # Append to prompt for next iteration
                    prompt.append({
                        'role': 'assistant',
                        'content': chunk.message.content,
                    })
            
            # If tools were called, get the LLM's follow-up response
            if tool_called:
                response = llm_client.chat(model, messages=prompt)
                for chunk in response:
                    if chunk.message.content:
                        print(chunk.message.content, end='', flush=True)
                        prompt.append({
                            'role': 'assistant',
                            'content': chunk.message.content,
                        })
            
            print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Ollama Client with MCP Tools')
    parser.add_argument('--model', type=str, default='gpt-oss:latest', help='Model to use (default: gpt-oss:latest)')
    args = parser.parse_args()
    asyncio.run(
        main(model=args.model)
    )