# cli_assistant
Python based command line interface for prompted conversation using ChatGPT API


[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Overview

**ChatGPT-CLI Tool** is a Python-based command-line interface (CLI) tool that allows users to interact with OpenAI's ChatGPT API efficiently. This tool provides several powerful features, including automated system role selection, code identification, and the ability to save identified code snippets as separate scripts. Additionally, the tool can scan previous conversation history for context and includes basic chain of thought tracking in prompts. Whether you're looking for insightful conversations, code suggestions, or a simple chat interface, this CLI tool streamlines your interactions with the ChatGPT API.

## Requirements
- openai


## Key Features

- **Automated System Role Selection**: Automatically assign system roles for your ChatGPT interaction, optimizing the model's responses based on your desired use case 
- **Code Detection**: The tool automatically identifies code snippets in the responses from the ChatGPT model and formats them properly.
- **Save Code as Separate Scripts**: Detected code snippets can be saved as separate script files in your working directory for future use or execution.
- **Flexible Command-Line Interface**: Simple, yet powerful, CLI commands allow easy interaction with the OpenAI ChatGPT API.
- **Iterative Response Iterpretation**: Collects multiple responses to each query and condenses the best components into a single, higher quality response
- **Contextual History Integration**: The tool can scan and incorporate previous conversation history from text files for added context in current requests.
- **Chain of Thought Tracking**: Adds prompts that track reasoning and thought process, improving responses in scenarios requiring step-by-step reasoning.


## Table of Contents

1. [Installation and Setup](#installation)
2. [Usage](#usage)
   - [System Role Selection](#system-role-selection)
   - [Identify and Save Code Snippets](#identify-code-snippets)
   - [Scanning Conversation History for Context](#scanning-conversation-history-for-context)
   - [Chain of Thought Tracking](#chain-of-thought-tracking)
4. [Contributing](#contributing)
5. [License](#license)


## Installation and Setup

First, ensure you have Python 3.10+ installed on your system. You can install the ChatGPT-CLI tool directly from the repository.

Clone the repository:

```bash
git clone https://github.com/mjenior/cli_assistant.git
cd cli_assistant
python setup.py
```

[setup.py] also adds a bash alias <assistant.py --prompt> to you profile to access the assistant with the command <gpt>, this command can be run from any relative path.


Before using the tool, a final helpful step is to also set up your OpenAI API key. Otherwise you'll need to provide to the app directly (described below).

Set the OPENAI_API_KEY as an environment variable:
```bash
export OPENAI_API_KEY="your_openai_api_key"
```

That's it! The assistant API is ready to use in the termal, below are some example uses and additional arguments that further tailor responses.


## Usage

Once installed, you can invoke the ChatGPT CLI tool directly from the terminal.

Example:
```bash
gpt "Help me compose an agenda for a week-long trip to Tokyo."
```

All arguments:
```
REQUIRED
prompt : str
    User prompt text, request that is sent to ChatGPT

OPTIONAL
role : str
    System role text, predefines system behaviours or type of expertise
    Several built-in options are available, refer to README for details
    Default is assistant
model : str
    ChatGPT model to interact with
    Default is gpt-4o-mini
chain_of_thought : bool
    Include chain of thought enforcement in user prompt.
    Default is False
code : bool
    Save detected code in responses as individual scripts.
    Default is True
context : bool
    Search for previous chat transcripts for reflection prompting.
    Default is False
dim : str
    Dimensions for Dall-e image generation
    Default is 1024x1024
qual : str
    Image quality for Dall-e output
    Default is standard
iters : int
    Number of responses to generate and parse for highest quality
    Default is 1
refine : bool
    Automatically refine user prompt to improve query specificity.
    Default is False
key : str
    User-specific OpenAI API key. 
    Default looks for pre-set OPENAI_API_KEY environmental variable.
verbose : bool
    Print all additional information to StdOut
    Default is False
silent : bool
    Silences all StdOut
    Default is False
log : bool
    Save response to current query as a separate text file
    Default is False
```

### System Role Selection

The --role option allows you to specify a system role for ChatGPT, which will optimize its responses based on the role you choose. Any text that does not match one of the existing role shortcuts will be submitted as a new custom role. The default is an improved personal assistant.

Available role shortcuts:

- assist (default): Standard personal assistant with improved ability to help with tasks
- compbio: Expertise in bioinformatics and systems biology. Knowledgeable in commonly used computational biology platforms.
- invest: Experience in technology stock investment and wealth management. Provides analyses for new stocks to invest in.
- art: Creates an images described by the prompt, default style leans toward illustrations
- photo: Gnereates more photo-realistic images
- refine: Designed to assist with iterative prompt engineering and refinement
- story: Retells plot of popular books and movies to appropriate for ~3 year olds with fun changes to characters
- write: Writing assistant to help with clarity and brevity

Example 1:
```bash
assistant.py --role compbio --prompt "Generate a Python script to align DNA sequences and analyze the data. Add code to generate at least 2 figures summarizing the results."
```

Example 2:
```bash
assistant.py --role "You are a Sr. game developer." --prompt "Recreate the game Chip's Challenge in python."
```

### Identify Code Snippets

The CLI tool automatically detects code snippets within ChatGPT's responses and formats them properly.

Example:
```bash
assistant.py --code True --prompt "Show me a Python function to find the maximum element in a list."
```

Output:
```python
def find_max(lst):
    return max(lst)
```

This assistant will then automatically save the generated code into find_max.time_stamp.py in the current working directory. Set to [True] by default.

### Scanning Conversation History for Improved Context (Reflection)

You can scan previous chat conversation history stored as text files to provide additional context for your current prompt. This helps improve continuity between sessions or when referring to previous discussions. The default scans the current working directory, but can also be set to [False] to skip this entirely.

Example:
```bash
assistant.py --context True --prompt "Where are they playing this week?" 
```

### Chain of Thought Tracking

This feature helps guide the model's response by breaking down the steps in complex reasoning tasks. The --thought flag enables the tool to append "chain of thought" prompts to ensure more detailed responses. It is [True] by default and automatically added to the default assistant, combio, developer, and invest system role prompts. The chain of thought flag will prompt the model to provide a step-by-step explanation or breakdown of reasoning, which can be especially useful in educational or technical explanations. It also helps mitigate the occurence of hallucinations.

Example:
```bash
assistant.py --chain_of_thought True --prompt "Can you write out a list of directions to change a tire?" 
```

### Response Evaluation

This feature helps to increase the creative ability of a model thorugh multiple distinct reponse generation followed by critical evaluation for the most optimal response. The --iterations flag accepts an integer value representing the number of separate reponse iterations the model will create for the given prompt. Increasing this value past the 1 will prompt the model to also provide a summary of it's evaluation including why the returned response was selected over others. Tip: Best results might be seen increasing this number relative to the complexity of the input prompt, but diminishing returns do seem to occur at a certain point. 

Example:
```bash
assistant.py --iters 3 --prompt "Create a python script to download DNA sequence data from the SRA, preprocess the data for maximum comparibility, and idenify putative gene sequences." 
```

### Image Generation Parameters

You are able to set specific parameters of the output image created by Dall-e. Flags for length (--dim_l) and width (--dim_w) dimenions in pixels, as well as definition quality (--qual) have been implemented.

Example:
```bash
assistant.py --dim_l 800 --dim_w 600 --qual high --prompt "Please create an image of a cell dissolving into code in the style of the impressionists." 
```

### User-specific API Keys

You are also able to instead provide the key directly to the assistant if it is not specified by your system. The default settings attempt to pull from system-wide environmental variables ().

Example:
```bash
assistant.py --key YOUR_API_KEY_HERE --prompt "How do you make pizza dough?"
```


## Contributing

If you encounter any problems, please [file an issue](https://github.com/mjenior/cli_assistant/issues) along with a detailed description.

We welcome contributions! If you'd like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new feature branch (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push the branch (`git push origin feature-name`).
5. Create a [pull request](https://github.com/mjenior/cli_assistant/pulls).


## License

This project is licensed under the [MIT](http://opensource.org/licenses/MIT) License. See the [LICENSE](https://raw.githubusercontent.com/mjenior/cli_assistant/refs/heads/main/LICENSE.txt) file for more details.

