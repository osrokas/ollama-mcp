import requests
from src.tools import get_weather
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="MyMCPServer",
    port=8050,
)

@mcp.tool(name="add", description="Adds two integers.")
def add(a: int, b: int) -> int:
    """Returns the sum of two integers."""
    return a + b

@mcp.tool(name="get_weather", description="Fetches weather information for a given city.")
def get_weather_tool(city: str) -> str:
    """Returns weather information for the specified city."""
    return get_weather(city)

@mcp.tool(name='read_file', description='Reads the content of a text file from the given file path.')
def read_file(file_path: str) -> str:
    """Reads and returns the content of a text file."""
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    except Exception as e:
        return f"Error reading file: {e}"
    
@mcp.tool(name='write_file', description='Writes content to a text file at the given file path.')
def write_file(file_path: str, content: str) -> str:
    """Writes content to a text file."""
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        return f"Content written to {file_path} successfully."
    except Exception as e:
        return f"Error writing to file: {e}"
    
@mcp.tool(name='update_file', description='Updates a text file by appending content to it at the given file path.')
def update_file(file_path: str, content: str) -> str:
    """Appends content to a text file."""
    try:
        with open(file_path, 'a') as file:
            file.write(f"\n{content}")
        return f"Content appended to {file_path} successfully."
    except Exception as e:
        return f"Error updating file: {e}"
    
@mcp.tool(name='list_files', description='Lists all files in the specified directory path.')
def list_files(directory_path: str) -> str:
    """Lists all files in the specified directory."""
    import os
    try:
        files = os.listdir(directory_path)
        return "\n".join(files)
    except Exception as e:
        return f"Error listing files: {e}"           

if __name__ == "__main__":
    mcp.run(transport="sse")