# bAIsh

A Python-based console chat application powered by LangChain, supporting Azure OpenAI, OpenAI, and Anthropic. It safely executes bash commands (e.g., `ls`, `find`, `grep`) using a whitelist and logs attempts. Ideal for developers seeking a secure, AI-driven command-line assistant.

## Features
- Console-based chat interface with AI assistance from Azure OpenAI, OpenAI, or Anthropic.
- Safe execution of bash commands validated against a regex-based whitelist.
- Configurable system messages loaded from files.
- Environment variables managed via a `.env` file.
- Command execution logging to `command_log.txt`.
- Multi-provider support selectable via `--provider` argument (default: Azure).

## Project Structure
```
baish/
├── src/
│   └── baish.py               # Main application script
├── system-messages/
│   └── default-sm.txt         # Default system message
├── white-list/
│   └── default-wl.txt         # Default whitelist regex file
├── .env.example               # Example environment variable file
├── .gitignore                 # Git ignore file
├── LICENSE                    # MIT License
├── README.md                  # This file
├── requirements.txt           # Python dependencies
└── command_log.txt            # Log file (created at runtime)
```

## Prerequisites
- Python 3.9+
- API credentials for chosen AI provider(s):
    - Azure OpenAI: API key, endpoint, deployment name
    - OpenAI: API key
    - Anthropic: API key
- Git (for cloning and contributing)

## Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/ukman/baish.git
   cd baish
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file**:
   Copy `.env.example` to `.env` and fill in your AI provider credentials:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your credentials, e.g.:
   ```env
   # Azure OpenAI (required for --provider azure)
   AZURE_OPENAI_API_KEY=your_azure_api_key
   AZURE_OPENAI_ENDPOINT=your_azure_endpoint
   AZURE_OPENAI_DEPLOYMENT_NAME=your_azure_deployment_name
   AZURE_OPENAI_API_VERSION=2024-02-01

   # OpenAI (required for --provider openai)
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_MODEL_NAME=gpt-4

   # Anthropic (required for --provider anthropic)
   ANTHROPIC_API_KEY=your_anthropic_api_key
   ANTHROPIC_MODEL_NAME=claude-3-sonnet-20240229
   ```

4. **Ensure system message and whitelist files exist**:
    - Default system message: `system-messages/default-sm.txt`
    - Default whitelist: `white-list/default-wl.txt`

5. **Run the application**:
   ```bash
   python src/baish.py --provider azure
   ```
   Or use another provider:
   ```bash
   python src/baish.py --provider openai
   python src/baish.py --provider anthropic
   ```
   Specify custom paths if needed:
   ```bash
   python src/baish.py --provider openai --system-message system-messages/default-sm.txt --whitelist white-list/default-wl.txt
   ```

## Usage
- Launch the application and interact via the console.
- Example inputs:
    - "List files in /home": Executes `ls /home` if allowed by the whitelist.
    - "How much disk space do I have?": Executes `df -h`.
    - "Find all .txt files in /docs": Executes `find /docs -type f -name "*.txt"`.
- Type `exit` to quit.
- Command attempts are logged to `command_log.txt`.

## Whitelist Configuration
The `white-list/default-wl.txt` file defines regex patterns for allowed bash commands:
```
^ls( -[a-zA-Z0-9]+)?(\s+[-/\w\.]+)?$
^pwd$
^df -h$
^whoami$
^date$
^echo .+$
^find\s+[-/\w.\]+\s+-type\s+[fd]\s+-name\s+['"][\w\.\*]+['"]$
^grep\s+-[a-zA-Z0-9]+\s+['"][\w\.\*]+['"]\s+[-/\w\.]+$
# Comment: Allowed safe commands: ls, pwd, df -h, whoami, date, echo, find (search by name/type), grep (search in files)
```

## Similar Projects
bAIsh is unique in combining console-based AI chat, safe bash command execution with whitelisting, and multi-provider support. Related projects include:
- **[langchain-ai/chat-langchain](https://github.com/langchain-ai/chat-langchain)**: A LangChain-based chatbot for documentation Q&A, but lacks bash command execution and multi-provider support.
- **LangChain ShellTool**: Enables shell command execution but lacks safeguards and isn’t a full chat application.
- **RAG Chatbot Tutorials**: Use LangChain and multi-provider support for RAG-based chatbots, but focus on web UIs and data retrieval, not command execution.

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Security Notes
- The application restricts bash commands to a whitelist, preventing dangerous commands like `rm`.
- Validate `white-list/default-wl.txt` to ensure only safe commands are allowed.
- Do not share your `.env` file or API credentials.

## Contact
For issues or questions, open an issue on GitHub or contact [your contact info].