# cli_assistant
Python based command line interface for prompted conversation using ChatGPT API


[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Overview

**ChatGPT-CLI Tool** is a Python-based command-line interface (CLI) tool that allows users to interact with OpenAI's ChatGPT API efficiently. This tool provides several powerful features, including automated system role selection, code identification, and the ability to save identified code snippets as separate scripts. Additionally, the tool can scan previous conversation history for context and includes basic chain of thought tracking in prompts. Whether you're looking for insightful conversations, code suggestions, or a simple chat interface, this CLI tool streamlines your interactions with the ChatGPT API.

## Key Features

- **Automated System Role Selection**: Automatically assign system roles for your ChatGPT interaction, optimizing the model's responses based on your desired use case (e.g., compbio, investor, artist).
- **Code Detection**: The tool automatically identifies code snippets in the responses from the ChatGPT model and formats them properly.
- **Save Code as Separate Scripts**: Detected code snippets can be saved as separate script files in your working directory for future use or execution.
- **Flexible Command-Line Interface**: Simple, yet powerful, CLI commands allow easy interaction with the OpenAI ChatGPT API.
- **Contextual History Integration**: The tool can scan and incorporate previous conversation history from text files for added context in current requests.
- **Chain of Thought Tracking**: Adds prompts that track reasoning and thought process, improving responses in scenarios requiring step-by-step reasoning.


## Table of Contents

1. [Installation](#installation)
2. [Setup](#setup)
3. [Usage](#usage)
   - [System Role Selection](#system-role-selection)
   - [Identify and Save Code Snippets](#identify-code-snippets)
   - [Scanning Conversation History for Context](#scanning-conversation-history-for-context)
   - [Chain of Thought Tracking](#chain-of-thought-tracking)
5. [Contributing](#contributing)
6. [License](#license)


## Installation

First, ensure you have Python 3.10+ installed on your system. You can install the ChatGPT-CLI tool directly from the repository.

Clone the repository:

```bash
git clone https://github.com/mjenior/cli_assistant.git
cd cli_assistant
```

Install the OpenAI API python package:
```bash
pip install openai
```

Install the package:

```bash
python setup.py install
```


## Setup

Before using the tool, you need to set up your OpenAI API key.

Set the OPENAI_API_KEY as an environment variable:
```bash
export OPENAI_API_KEY="your_openai_api_key"
```


## Usage

Once installed, you can invoke the ChatGPT CLI tool directly from the terminal.

Example:
```bash
assistant --prompt "Help me compose an agenda for a week-long trip to Tokyo."
```

```
REQUIRED
prompt : str
    User prompt text, request that is sent to ChatGPT

OPTIONAL
role : str
    System role text, predefines system behaviours or type of expertise
    Built-in shortcut options include: compbio, investor, artist, story
    Default is "You are a helpful AI assistant."
model : str
    ChatGPT model to interact with
    Default is gpt-4o-mini
thought : bool
    Include chain of thought enforcement in user prompt.
    Default is True
save_code : bool
    Save detected code in responses as individual scripts.
    Default is True
history : str
    Directory to search for previous chat history files.
    May also be set to False
    Default is current working directory
dimensions : str
    Image dimensions for Dall-e image generation
    Default is 1024x1024
api_key : str
    User-specific OpenAI API key. 
    Default looks for pre-set OPENAI_API_KEY environmental variable.
verbose : bool
    Print all information to StdOut
    Default is False
```

### System Role Selection

The --role option allows you to specify a system role for ChatGPT, which will optimize its responses based on the role you choose. Any text that does not match one of the existing role shortcuts will be submitted as a new custom role.

Available role shortcuts:

    default: "You are a helpful AI assistant."
    compbio: Expertise in bioinformatics and systems biology. Knowledgeable in commonly used computational biology platforms.
    investor: Experience in technology stock investment and wealth management. Provides analyses for new stocks to invest in.
    artist: Creates an images described by the prompt, default style leans toward illustrations

Example:
```bash
assistant --role compbio --prompt "Generate a Python script to align DNA sequences and analyze the data. Add code to generate at least 2 figures summarizing the results."
```

### Identify Code Snippets

The CLI tool automatically detects code snippets within ChatGPT's responses and formats them properly.

Example:
```bash
assistant --save_code True --prompt "Show me a Python function to find the maximum element in a list."
```

Output:
```python
def find_max(lst):
    return max(lst)
```

This assistant will then automatically save the generated code into find_max.py in the current working directory. Set to [True] by default.

### Scanning Conversation History for Context

You can scan previous chat conversation history stored as text files to provide additional context for your current prompt. This helps improve continuity between sessions or when referring to previous discussions. The default scans the current working directory, but can also be set to [False] to skip this entirely.

Example:
```bash
assistant --history ~/Desktop/history_docs --prompt "Where are they playing this week?" 
```

### Chain of Thought Tracking

This feature helps guide the model's response by breaking down the steps in complex reasoning tasks. The --thought flag enables the tool to append "chain of thought" prompts to ensure more detailed responses. It is [True] by default and automatically added to the default assistant, combio, and invest system role prompts. The chain of thought flag will prompt the model to provide a step-by-step explanation or breakdown of reasoning, which can be especially useful in educational or technical explanations. It also helps mitigate the occurence of hallucinations.

Example:
```bash
assistant --thought True --prompt "Can you write out a list of directions to change a tire?" 
```


You are also able to instead provide the key directly to the assistant if it is not specified by your system.

```bash
assistant --api_key YOUR_API_KEY_HERE --prompt "How do you make pizza dough?"
```


## Contributing

If you encounter any problems, please [file an issue](https://github.com/mjenior/cli_assistant/issues) along with a detailed description.

We welcome contributions! If you'd like to contribute to this project, please follow these steps:

- Fork the repository.
- Create a new feature branch (git checkout -b feature-name).
- Commit your changes (git commit -m 'Add new feature').
- Push the branch (git push origin feature-name).
- Create a pull request.


## License

This project is licensed under the [MIT](http://opensource.org/licenses/MIT) License. See the [LICENSE](https://raw.githubusercontent.com/mjenior/cli_assistant/refs/heads/main/LICENSE.txt) file for more details.


