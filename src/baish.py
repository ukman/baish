import os
import subprocess
import argparse
import re
from langchain_openai import AzureChatOpenAI
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# Load environment variables from .env file
load_dotenv()

# Function to load whitelist regex patterns from a file
def load_whitelist(file_path: str) -> list:
    """Loads regex patterns for allowed bash commands from a specified file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Read lines, strip whitespace, and ignore empty lines or comments
            patterns = [line.strip() for line in file if line.strip() and not line.strip().startswith('#')]
            return [re.compile(pattern) for pattern in patterns]
    except FileNotFoundError:
        print(f"Error: Whitelist file '{file_path}' not found. Using default patterns.")
        return [re.compile(r'^(ls|pwd|df -h|whoami|date|echo .+)$')]  # Default safe commands

# Define a tool for executing bash commands
@tool
def execute_bash_command(command: str) -> str:
    """Executes a bash command and returns the output."""

    print(f"Execute '{command}'")

    whitelist_patterns = load_whitelist(os.getenv("WHITELIST_PATH", "./white-list/default-wl.txt"))

    # Check if the command matches any whitelist pattern
    if not any(pattern.match(command) for pattern in whitelist_patterns):
        return f"Error: Command '{command}' is not allowed."

    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error executing command: {e.stderr}"

# Function to load system message from a file
def load_system_message(file_path: str) -> str:
    """Loads the system message from a specified file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        return f"Error: System message file '{file_path}' not found. Using default message.\n" + \
               "You are a helpful AI assistant that can answer questions and execute bash commands when requested."

# Initialize the language model based on provider
def initialize_llm(provider: str, model: str, deployment: str, temperature: float):
    """Initializes the language model based on the specified provider, model, deployment, and temperature."""
    if provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY is not set in .env file")
        return ChatOpenAI(
            model=model or os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"),
            temperature=temperature or float(os.getenv("OPENAI_TEMPERATURE", 0.7))
        )
    elif provider == "azure":
        if not all([os.getenv("AZURE_OPENAI_API_KEY"), os.getenv("AZURE_OPENAI_ENDPOINT")]):
            raise ValueError("Azure OpenAI credentials are not fully set in .env file")
        return AzureChatOpenAI(
            deployment_name=deployment or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", ""),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
            temperature=temperature or float(os.getenv("AZURE_OPENAI_TEMPERATURE", 0.7))
        )
    elif provider == "anthropic":
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise ValueError("ANTHROPIC_API_KEY is not set in .env file")
        return ChatAnthropic(
            model=model or os.getenv("ANTHROPIC_MODEL_NAME", "claude-3-5-sonnet-20241022"),
            temperature=temperature or float(os.getenv("ANTHROPIC_TEMPERATURE", 0.7))
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}. Use 'openai', 'azure', or 'anthropic'.")


# Main function with argument parsing
def main():
    parser = argparse.ArgumentParser(description="AI Chat with Bash Command Execution")
    parser.add_argument(
        "--system-message",
        type=str,
        default="./system-messages/default.txt",
        help="Path to the system message file"
    )
    parser.add_argument(
        "--whitelist",
        type=str,
        default="./white-list/default-wl.txt",
        help="Path to the whitelist regex file"
    )
    parser.add_argument(
        "--verbose",
        type=bool,
        default=False,
        help="Verbose mode"
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="openai",
        choices=["openai", "azure", "anthropic"],
        help="Language model provider (openai, azure, or anthropic)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Model name for OpenAI or Anthropic (e.g., gpt-4o-mini, claude-3-5-sonnet-20241022)"
    )
    parser.add_argument(
        "--deployment",
        type=str,
        default=None,
        help="Deployment name for Azure OpenAI"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=None,
        help="Temperature for the language model (e.g., 0.7)"
    )
    args = parser.parse_args()

    # Load system message
    system_message = load_system_message(args.system_message)

    # Initialize the Azure OpenAI model
    llm = initialize_llm(args.provider, args.model, args.deployment, args.temperature)


    # Define the tools
    tools = [execute_bash_command]

    verbose = args.verbose

    # Create a prompt template with MessagesPlaceholder for agent_scratchpad
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        MessagesPlaceholder(variable_name="chat_history"),  # Stores previous questions and answers
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),  # For tool-calling agent
    ])
    # Initialize in-memory chat history
    history = InMemoryChatMessageHistory()

    # Create the agent
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=verbose)

    # Wrap the agent with message history
    agent_with_history = RunnableWithMessageHistory(
        agent_executor,
        lambda session_id: history,
        input_messages_key="input",
        history_messages_key="chat_history",
        max_messages=10  # Store up to 10 interactions (equivalent to k=10)
    )

    print("Welcome to the AI Chat with Bash Command Execution!")
    print("Type 'exit' to quit.")

    # Use a fixed session_id for simplicity
    session_id = "default-session"

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        # Invoke the agent with user input and session_id
        response = agent_with_history.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": session_id}}
        )
        print("\nAI:", response["output"])

if __name__ == "__main__":
    main()