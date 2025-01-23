# llm_api
Python based tool for improved conversation using ChatGPT API package


[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Overview

**ChatGPT-API Tool** is a Python-based LLM API tool that allows users to interact with OpenAI's ChatGPT API efficiently. This tool provides several powerful features, including automated system role selection, code identification, and the ability to save identified code snippets as separate scripts. Additionally, the tool can scan previous conversation history for context and includes basic chain of thought tracking in prompts. Whether you're looking for insightful conversations, code suggestions, or a simple chat interface, this CLI tool streamlines your interactions with the ChatGPT API.

## Requirements
- openai >= 1.59.0
- black >= 24.10.0

## Key Features

- **Automated System Role Selection**: Automatically assign system roles for your ChatGPT interaction, optimizing the model's responses based on your desired use case 
- **Code Detection**: The tool automatically identifies code snippets in the responses from the ChatGPT model and formats them properly.
- **Save Code as Separate Scripts**: Detected code snippets can be saved as separate script files in your working directory for future use or execution.
- **Flexible Command-Line Interface**: Simple, yet powerful, CLI commands allow easy interaction with the OpenAI ChatGPT API.
- **Iterative Response Iterpretation**: Collects multiple responses to each query for model reflection, and condenses the best components into a single, higher quality response
- **Chain of Thought Tracking**: Adds prompts that track reasoning and thought process, improving responses in scenarios requiring step-by-step reasoning.


## Table of Contents

1. [Installation and Setup](#installation)
2. [Usage](#usage)
   - [System Role Selection](#system-role-selection)
   - [Chain of Thought Tracking](#chain-of-thought-tracking)
   - [Query Prompt Refinement](#query-prompt-refinement)
   - [Response Iterations](#response-iterations)
   - [Identify and Save Code Snippets](#identify-code-snippets)
   - [Associative Glyph Prompting](#associative-glyph-prompting)
4. [Advanced Usage](#advanced-usage)
5. [Contributing](#contributing)
6. [License](#license)


## Installation and Setup

First, ensure you have Python 3.10+ installed on your system. You can install the ChatGPT-CLI tool directly from the repository.

Clone the repository and install:

```bash
git clone https://github.com/mjenior/llm_api.git
cd llm_api
pip install .
```

Now you are able to initialize a <assistant.OpenAIQueryHandler> class instance in a python environment to set up a customized API client with any of the built-in settings. After that, use the method <.request("your prompt here")> to submit queries.

Example:
```python
from llm_api.core import OpenAIQueryHandler

assistant = OpenAIQueryHandler()
assistant.request("Write a python script to scrape web pages for numeric data and return as a formatted dataframe.")
````

### Command Line Execution

Optionally: [alias.py] begins a series of prompts to add a a customized bash alias to you profile to access the assistant with a chosen command which can be run from any relative path. Results will be quickly returned to StdOut for quicker reference for certain tasks. Once [alias.py] is run, you can invoke the ChatGPT CLI tool directly from the terminal.

Example:
```bash
llmapi "Write a python script to scrape web pages for numeric data and return as a formatted dataframe."
```

### API Keys

Before using the tool, a final helpful step is to also set up your API keys. Otherwise you'll need to provide to the app directly (described below).

Set the environment variable(s):
```bash
export OPENAI_API_KEY="your_openai_api_key"
```
Also will parse <DEEPSEEK_API_KEY> if <deepseek-chat> is the requested model. Can also be provided directly, identical to OpenAI key.


## Usage

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
    LLM to use in queiries.
    Default is gpt-4o-mini
chain_of_thought : bool
    Include chain of thought enforcement in user prompt.
    Default is False
refine_prompt : bool
    Automatically improve user prompt to improve query specificity.
    Default is False
glyph_prompt : bool 
    Restructures queries into associative glyph formatting (NEEDS TESTING)
    Default is False
iterations : int
    Number of responses to generate and parse for model reflection
    Default is 1
save_code: bool
    Extracts and saves code snippets from the response.
    Default is False
scan_files: bool
    Scans prompt for existing files, extracts contents, and adds to prompt.
    Default is False
seed : str or int
    Set moded seed for more deterministic reponses
    Converts strings into binary-like equivalent, constrained by max system bit size
    Default is based on the pinnacle code from Freakazoid
dimensions : str
    Dimensions for Dall-e image generation
    Default is 1024x1024
quality : str
    Image quality for Dall-e images
    Default is standard
unit_testing : bool
    rite comprehesive unit tests for any generated code.
    Default is False
api_key : str
    User-specific OpenAI API key. 
    Default looks for pre-set OPENAI_API_KEY environmental variable.
verbose : bool
    Print all additional information to StdOut.
    Default is False
```

### System Role Selection

The --role option allows you to specify a system role for ChatGPT, which will optimize its responses based on the role you choose. Any text that does not match one of the existing role shortcuts will be submitted as a new custom role. The default is an improved personal assistant.

Available role shortcuts:
- assistant (default): Standard personal assistant with improved ability to help with tasks
- compbio: Expertise in bioinformatics and systems biology. Knowledgeable in commonly used computational biology platforms.
- developer: Generates complete, functional application code based on user requirements, ensuring clarity and structure.
- refactor: Senior full stack developer with emphases in correct syntax, documentation, and unit testing.
- writer: Writing assistant to help with generating science & technology related content
- editor: Text editing assistant to help with clarity and brevity.
- artist: Creates an images described by the prompt, default style leans toward illustrations.
- photographer: Generates more photo-realistic images
- investor: Provides advice in technology stock investment and wealth management.

Built-in roles:
```python
agent = OpenAIQueryHandler(role="compbio")
````

```bash
cli.py --role compbio --prompt "Generate a Python script to align DNA sequences and analyze the data. Add code to generate at least 2 figures summarizing the results."
```

Alternatively, the user can describe their own custom role easily by simply adding s description string to the role arguement instead of a keyword.

User-defined role:
```python
agent = OpenAIQueryHandler(role="You are a Senior game developer.")
````

```bash
cli.py --role "You are a Senior game developer." --prompt "Recreate the game Chip's Challenge in python."
```

### Identify Code Snippets

The tool can automatically detects code snippets within an LLM's responses and saves them to individual scripts with the --save_code flag.

Example:
```python
agent = OpenAIQueryHandler(save_code=True)
````

```bash
cli.py --save_code True --prompt "Show me a Python function to find the maximum element in a list."
```

Example output snippet:
```python
def find_max(lst):
    return max(lst)
```

It will then automatically save the generated code into find_max.time_stamp.py in the current working directory. Set to [True] by default.

### Chain of Thought Tracking

This feature helps guide the model's response by breaking down the steps in complex reasoning tasks. The --chain_of_thought flag enables the tool to append "chain of thought" prompts to ensure more detailed responses. It is [True] by default and automatically added to the default assistant, combio, developer, and invest system role prompts. The chain of thought flag will prompt the model to provide a step-by-step explanation or breakdown of reasoning, which can be especially useful in educational or technical explanations. It also helps mitigate the occurence of hallucinations.

Example:
```python
agent = OpenAIQueryHandler(chain_of_thought=True)
````

```bash
cli.py --chain_of_thought True --prompt "Can you write out a list of directions to change a tire?"
```

### Query Prompt Refinement

Attempts to improve the clarity, focus, and specificity of a prompt to align with the desired outcomes or objectives with the --refine_prompt flag. It involves adjusting language, structure, and scope to ensure the prompt effectively guides responses and generates accurate, relevant, and actionable results. Results are automatically submitted as a new query to the requested LLM.

Example:
```python
agent = OpenAIQueryHandler(refine_prompt=True)
````

```bash
cli.py --refine_prompt True --prompt "Can you write out a list of directions to change a tire?" 
```

Result:
```
Can you provide detailed, step-by-step instructions for changing a tire, emphasizing key safety precautions and necessary tools? 
You should include comprehensive details like how to safely park the car, the importance of using a wheel chock, and the correct way to position the jack. 
Also, expand on how to properly remove the lug nuts, replace the tire, and ensure everything is secure before driving again.
```

### Associative Glyph Prompting

During prompt refinement, the addition --glyph_prompt flag will restructure the revised prompt utilizing concepts from [Symbolic Representations Framework](https://github.com/severian42/Computational-Model-for-Symbolic-Representations) to create user-defined symbolic representations (glyphs) guide AI interactions. Glyphs serve as conceptual tags, steering AI focus within specific domains like storytelling or thematic development without altering the model's architecture. Instead, they leverage existing AI mechanisms—contextual priming, attention, and latent space activation—repurposing them to create a shared symbolic framework for dynamic and intuitive collaboration. This feature *requires* the --refine_prompt flag, and still requires additional testing.

Example:
```python
agent = OpenAIQueryHandler(glyph_prompt=True)
````

```bash
cli.py --refine_prompt True --glyph_prompt True --prompt "Write a plan to improve efficiency of a computational pipeline." 
```

Resulting altered user prompt:
```
<human_instructions>
- Treat each glyph as a direct instruction to be followed sequentially, driving the process to completion.
- Deliver the final result as indicated by the glyph code, omitting any extraneous commentary. Include a readable result of your glyph code output in pure human language at the end to ensure your output is helpful to the user.
- Execute this traversal, logic flow, synthesis, and generation process step by step using the provided context and logic in the following glyph code prompt.
</human_instructions>

{
  Φ(Define the Problem/Goal) -> Clearly articulate the primary objective of enhancing the computational pipeline's efficiency. This should include specific metrics for success and desired outcomes to ensure clarity in the problem statement.
  
  Θ(Provide Contextual Parameters, Constraints) -> Detail any existing limitations that affect the pipeline's performance, such as hardware specifications, software dependencies, data processing limits, and time constraints. This information is crucial for understanding the environment in which the pipeline operates.
  
  ↹(Specify Initial Focus Areas, if any) -> Identify key areas within the pipeline that are currently bottlenecks or could be optimized for better performance. This may include data input/output processes, algorithmic efficiencies, or resource allocation strategies.

  Ω[
    ↹(Sub-Focus 1) -> Generate Spectrum of Possibilities (e.g., approaches, perspectives, solutions) -> Explore various optimization techniques, such as parallel processing, code refactoring, or algorithmic changes that could enhance efficiency.
    
    ↹(Sub-Focus 2) -> Generate Spectrum of Possibilities -> Investigate hardware upgrades or cloud computing solutions that could alleviate resource limitations and improve processing speeds.
    
    ↹(Sub-Focus n) -> Generate Spectrum of Possibilities -> Consider workflow management tools or containerization options (like Docker) that could streamline the pipeline and improve reproducibility.
  ] -> α[
     ↹(Sub-Focus 1) -> Analyze & Evaluate Spectrum Elements (Pros/Cons, Risks/Benefits) -> Assess the feasibility of each optimization technique, weighing potential gains against implementation challenges.
     
     ↹(Sub-Focus 2) -> Analyze & Evaluate Spectrum Elements -> Evaluate the cost-effectiveness and technical requirements of hardware upgrades or cloud solutions.
     
     ↹(Sub-Focus n) -> Analyze & Evaluate Spectrum Elements -> Review the impact of adopting workflow management tools on team collaboration and project scalability.
  ] -> Σ(Synthesize Insights, Formulate Solution/Understanding) -> Combine findings from the analysis to propose a comprehensive strategy for improving pipeline efficiency, ensuring that all aspects are aligned with the defined goals.
  
  -> ∇(Self-Assess, Critique, Suggest Improvements) -> Reflect on the proposed solutions to identify any overlooked elements or potential for further enhancement, ensuring a robust approach to the problem.
  
  -> ∞(Iterate/Refine if further input is given) -> Be prepared to adjust the strategy based on additional feedback or emerging data that could influence the pipeline's efficiency.
  
  @Output(Final Solution/Understanding, Justification, Reflection on Process) -> Present a clear, actionable plan that outlines the steps to be taken, providing justification for each recommendation and reflecting on the overall process to ensure thoroughness and clarity.
}
````


### Response Iterations

This feature helps to increase the creative ability of a model thorugh multiple distinct reponse generation followed by critical evaluation for the most optimal response. The --iterations flag accepts an integer value representing the number of separate reponse iterations the model will create for the given prompt. Increasing this value past the 1 will prompt the model to also provide a summary of it's evaluation including why the returned response was selected over others. Tip: Best results might be seen increasing this number relative to the complexity of the input prompt, but diminishing returns do seem to occur at a certain point. WANRING: More testing required for reliability, so use with caution.

Example:
```python
agent = OpenAIQueryHandler(iterations=3)
````

```bash
cli.py --iterations 3 --prompt "Create a python script to download DNA sequence data and preprocess the data."
```

This will generate 3 distinct versions of the reponse, each likely with a varied solution, and the work to synthesize them into a single higher quality response.

### Image Generation Parameters

You are able to set specific parameters of the output image created by Dall-e. Flags for dimenions (--dimenions) in pixels, as well as definition quality (--quality) have been implemented. The agent will try to recognize multiple iterations of quality reponses to differentiate preference in standard versus HD correctly.

Example:
```python
agent = OpenAIQueryHandler(dimensions="1024x1024", quality="high")
````

```bash
cli.py --dimensions 1024x1024 --quality high --prompt "Please create an image of a cell dissolving into code in the style of the impressionists." 
```

### User-specific API Keys

You are also able to instead provide the key directly to the assistant if it is not specified by your system. The default settings attempt to pull from system-wide environmental variables ().

Example:
```python
agent = OpenAIQueryHandler(api_key=YOUR_API_KEY_HERE)
````

```bash
cli.py --api_key YOUR_API_KEY_HERE --prompt "How do you make pizza dough?"
```

## Advanced Usage

Multiple agents with distinct roles may be called to cooperate in generating the most complete reponses needed by the user. This is most easily accomplised by using with the imported package version. The following example is also implemented in the accompanying jupyter notebook [multiagent_testing.ipynb](https://github.com/mjenior/llm_api/blob/main/multiagent_example.ipynb)

Example:

First, create a team of distinct agents with differing expertise.

```python
from llm_api.core import OpenAIQueryHandler

# Initialize agents
comp_bio = OpenAIQueryHandler(role="compbio", save_code=True, refine_prompt=True, chain_of_thought=True, glyph_prompt=True) # Computational biologist
recode = OpenAIQueryHandler(role="refactor", save_code=True, unit_testing=True, scan_files=True) # Code refactoring and formatting expert
write = OpenAIQueryHandler(role="writer", iterations=5, chain_of_thought=True, glyph_prompt=True) # Creative science writer
edit = OpenAIQueryHandler(role="editor", refine_prompt=True, logging=True) # Expert copy editor
````

Use inital agent to start the project:

```python
# Make initial request to first agent for computational biology project
query = """
Write an analysis pipeline in python to assemble long nanopore reads into contigs and then align them to an annotated reference genome.
Then identify all of the sequence variation present in the new genome that is not present in the reference.
Additionally generate a figure from data generated during the alignment based on quality scores, and 2 more figures to help interpret the results at the end.
"""
comp_bio.request(query)
````

```python
# Optimize and document any new code, add unit testing.
query = """
Refactor and format the following scripts for optimal efficiency, useability, and generalization:
"""
if len(comp_bio.scripts) > 0:
    query += " ".join(comp_bio.scripts)
    recode.request(query)
````

Then use the next agents to read through the new pipeline and generate a high-quality blog post describing it's utility.

```python
# Utilize the writer agent to generate an informed post on the background and utility of the newly created pipeline
query = """
Write a biotechnology blog post about the pipeline described below. 
Include relevant background that would necessitate this type of analysis, and add at least one example use case for the workflow. 
Extrapolate how the pipeline may be useful in cell engineering efforts, and what future improvements could lead to with continued work. 
The resulting post should be at least 3 paragraphs long with 4-5 sentences in each.
Speak in a conversational tone and cite all sources with biological relevance to you discussion.
"""
query = f"{query}\n{comp_bio.message}"

write.request(query)

# Pass the rough draft text to the editor agent to recieve a more finalize version
edit.request(write.message)
````

This is one example of how multiple LLM agents may be leveraged in concert to accelerate the rate that user workloads may be accomplished.


## Contributing

If you encounter any problems, please [file an issue](https://github.com/mjenior/llm_api/issues) along with a detailed description.

We welcome contributions! If you'd like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new feature branch (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push the branch (`git push origin feature-name`).
5. Create a [pull request](https://github.com/mjenior/llm_api/pulls).


## License

This project is licensed under the [MIT](http://opensource.org/licenses/MIT) License. See the [LICENSE](https://raw.githubusercontent.com/mjenior/llm_api/refs/heads/main/LICENSE.txt) file for more details.
