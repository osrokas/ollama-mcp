import os
import asyncio
import logging

from dotenv import load_dotenv

from src.clients import OllamaClient

if os.path.exists('.env'):
    load_dotenv('.env', override=True, verbose=True)

# Load MCP server URL from environment variable or use default
MCP_SERVER = os.getenv('MCP_SERVER', 'http://localhost:8050/sse')
    
    
async def main(model: str):
    print(f'Running with model={model}. Type "/quit" to exit.')

    # Initialize Ollama client with MCP server tools
    async with OllamaClient(MCP_SERVER, role='system', content='You are a helpfull assistant. Use tools if possible to get the latest data.') as llm_client:
    
        # Available tools
        print('Available tools:')
        for t in llm_client.client_tools:
            print(f"\t- {t['function']['name']}: {t['function']['description']}")
        print('---')

        # System prompt
        prompt = [llm_client.prompt]

        # Chat loop
        while True:
            try:
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

                # Call tools if needed
                message = await llm_client.handle_tool_calls(response)
                        
                # Append tool response to prompt
                prompt.append(message)

                # Run chat again with tool response
                response = llm_client.chat(model, messages=prompt)

                # Append ollama response
                prompt.append({
                    'role': 'assistant',
                    'content': response.message.content,
                })
                print(response.message.content)
            except Exception as e:
                logging.error(f"Error during chat: {e}")


if __name__ == "__main__":
    asyncio.run(main(
        model='mistral'
    ))