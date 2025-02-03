# PromptPal
Python based tool for improved LLM interactions using the OpenAI API package.

#### VERSION = 1.3.0

## Overview

This package is a Python-based prompt enhancing tool that allows users to automate significant portions of interactions with the OpenAI API. It provides several powerful features, including automated system role selection, prompt refinement, iterative response parsing, and the ability to save identified code snippets as separate scripts. Additionally, it includes basic chain of thought enforcement in prompts and associative glyph representation in prompts. Whether you're looking for insightful project planning, code suggestions, writing help, or a completely custom experience, this package can streamline any interaction with the ChatGPT API.

## Requirement(s)
- openai >= 1.59.0

## Key Features

- **Automated System Role Selection**: Automatically assign system roles for your LLM interaction, optimizing the model's responses based on your desired use case 
- **Chain of Thought Enforcement**: Adds prompts that track reasoning and thought process, improving responses in scenarios requiring step-by-step reasoning.
- **Automated Prompt Refinement and Glyph Representation**: Will automatically refactor prompts to be more descriptive and structured for improved LLM interpretability. The tool is also able to translate prompts into an associative glyph format, based on [recent findings](https://github.com/severian42/Computational-Model-for-Symbolic-Representations), to further improve potential results.
- **Flexible Parameterization**: Simple, yet powerful, argumenets during agent initialization allow easy interaction with the OpenAI's API.
- **Iterative Response Iterpretation**: Collects multiple responses to each query for model reflection, and condenses the best components into a single, higher quality response
- **Code Detection**: The tool automatically identifies code snippets in the responses from the model, formats them properly, saves as separate script files for future use or execution.
- **File and Directory Structure Comprehension**: Understands and reads in content of files listed directly in the prompt, and is also able to recursively read in entire subdirectories.


## Table of Contents

1. [Installation and Setup](#installation)
2. [Usage](#usage)
   - [System Role Selection](#system-role-selection)
   - [Identify and Save Code Snippets](#identify-code-snippets)
   - [Chain of Thought Enforcement](#chain-of-thought-enforcement)
   - [Query Prompt Refinement](#query-prompt-refinement)
   - [Response Iterations](#response-iterations)
   - [Recursive Directory Scanning](#recursive-directory-scanning)
   - [Associative Glyph Prompting](#associative-glyph-prompting)
   - [Image Generation Parameters](#image-generation-parameters)
4. [Advanced Usage](#advanced-usage)
5. [Contributing](#contributing)
6. [License](#license)


## Installation and Setup

Clone the repository and install using pip:

```bash
pip install promptpal
```

That's it! Now you are able to initialize a **core.CreateAgent** class instance in a python environment. After that, use the method **agent.request("your prompt here")** to submit queries.

Example:
```python
from promptpal.core import CreateAgent

assistant = CreateAgent()
assistant.request("Write a python script to scrape web pages for numeric data and return as a formatted dataframe.")
```

### API Keys

IMPORTANT: Before using the tool, another important step is to also set up your OpenAI API key. The package natively attempts to pull from system-wide environmental variables.

Set the environment variable(s):
```bash
export OPENAI_API_KEY="your_openai_api_key"
```

## Usage

Current [CreateAgent()] adjustable attributes:
- model (str): The model to use for the query (e.g., 'gpt-4o-mini', 'dall-e-3').
- client (OpenAI): The OpenAI client instance for API requests.
- refine (bool): If True, refines the prompt before submission.
- glyph (bool): If True, restructures queries with representative/associative glyphs and logic flow
- chain_of_thought (bool): If True, enables chain-of-thought reasoning.
- save_code (bool): If True, extracts and saves code snippets from the response.
- scan_dirs (bool): If True, recursively scans directories found in prompt for existing files, extracts contents, and adds to prompt.
- logging (bool): If True, logs the session to a file.
- seed (int or str): Seed for reproducibility. Can be an integer or a string converted to binary.
- iterations (int): Number of response iterations for refining or condensing outputs.
- dimensions (str): Dimensions for image generation (e.g., '1024x1024').
- quality (str): Quality setting for image generation (e.g., 'hd').
- role (str): The role or persona for the query (e.g., 'assistant', 'artist').
- temperature (float): Range from 0.0 to 2.0, lower values increase randomness, and higher values increase randomness.
- top_p (float): Range from 0.0 to 2.0, lower values increase determinism, and higher values increase determinism.
- verbose (bool): If True, prints detailed logs and status messages.
- silent (bool): If True, silences all StdOut messages.
- tokens (dict): Tracks token usage for prompt and completion.
- summary (bool): If True, summarizes the current conversation context to reference later.

For simplicity, after initializing with the desired parameters the only user-executable method is **CreateAgent.request()** to submit prompts to the API. After which the **CreateAgent.message** attribute is then available containing the system response text.


### System Role Selection

The --role option allows you to specify an agent role for ChatGPT, which will optimize its responses based on the role you choose. Any text that does not match one of the existing role shortcuts will be submitted as a new custom role. The default is an improved personal assistant.

Available role shortcuts:
- assistant (default): Standard personal assistant with improved ability to help with tasks
- developer: Generates complete, functional application code based on user requirements, ensuring clarity and structure.
- refactor: Senior full stack developer with emphases in correct syntax and documentation.
- tester: Quality assurance tester with experience in software testing and debugging, generates high-quality unit tests.
- analyst: Create clear, insightful data visualizations and provide analysis, focusing solely on visualization requests and recommendations.
- writer: Writing assistant to help with generating science & technology related content.
- editor: Text editing assistant to help with clarity and brevity.
- artist: Creates an images described by the prompt, default style leans toward illustrations.
- photographer: Generates more photo-realistic images

Built-in roles:
```python
agent = CreateAgent(role="refactor")
print(agent.role)
```

```
System Role: Code Refactoring Specialist
Primary Function: You are a code refactoring specialist focused on both technical and architectural improvements. Your goal is to enhance code quality, maintainability, and performance while preserving the original functionality.

Input Requirements:
1. Must receive valid code to proceed
2. Must specify programming language if not evident

Output Format (strictly follow this order):
1. Original Code Analysis:
   - Outline the intended functionality of the original code
   - Identify potential bugs and shortcomings

2. Refactored Code:

   ```[language]
   [Refactored code here with inline comments]
   \```
   
2. Improvements Made:
   - Technical improvements (performance, type hints, error handling)
   - Architectural improvements (design patterns, structure)
   - Interpretability improvements (consolidate or eliminate any redundancies)
   - Documentation enhancements

3. Performance Analysis:
   - Time complexity changes
   - Memory usage implications
   - Potential bottlenecks addressed

4. Future Considerations:
   - Scalability recommendations
   - Maintenance considerations
   - Modern alternatives (if applicable)

Refactoring Constraints:
1. Preserve original output data structures exactly
2. Balance readability with performance
3. Implement type hints where applicable
4. Follow language-specific best practices
5. Do not make assumptions about unclear code

Boundaries:
1. Only add new features or dependencies which significantly improve performance or brevity
2. Do not exclude ANY code for brevity
3. Balance readability with performance
4. Implement type hints where applicable
5. Follow language-specific best practices

For each significant change, explain the reasoning, and thoroughly document it.
```

Alternatively, the user can describe their own custom role easily by simply adding s description string to the role arguement instead of a keyword.

User-defined role:
```python

new_role = '''
**System Role: Expert Game Developer**

You are an expert game developer with extensive knowledge and experience in game design, development, and production. Your expertise spans various platforms, including PC, consoles, and mobile devices. You possess a deep understanding of programming languages such as C++, C#, and Python, as well as proficiency in development tools and engines like Unity, Unreal Engine, and Godot. Your comprehensive knowledge of game mechanics, physics, and AI allows you to create engaging and immersive experiences. 

You are well-versed in the entire lifecycle of game development, from concept and prototyping to testing and deployment. You can advise on best practices for project management and team collaboration, utilizing methodologies like Agile and Scrum. Your experience extends to optimizing performance, ensuring cross-platform compatibility, and integrating cutting-edge technologies such as virtual reality (VR) and augmented reality (AR). 

Additionally, you have a keen eye for aesthetics and user experience, enabling you to work effectively with artists and designers to achieve a cohesive vision. You stay up to date with industry trends and innovations, and you understand the importance of community engagement, monetization strategies, and post-launch support. 

As an expert, you are equipped to provide insights, solve complex challenges, and offer guidance on building successful games that resonate with players and stand out in the competitive gaming market.
'''

game_dev = CreateAgent(role=new_role)
```

### Identify Code Snippets

The tool can automatically detects code snippets within an LLM's responses and saves them to individual scripts with the --save_code flag.

Example:
```python
agent = CreateAgent(save_code=True)
```

Example output snippet:
```python
def find_max(lst):
    return max(lst)
```

It will then automatically save the generated code into find_max.[time_stamp].py in the current working directory. Set to [True] by default.

### Chain of Thought Enforcement

This feature helps guide the model's response by breaking down the steps in complex reasoning tasks. The --chain_of_thought flag enables the tool to append "chain of thought" prompts to ensure more detailed responses. It is [False] by default but automatically added to the default assistant, analyst, and developer system role prompts. The chain of thought flag will require the model to provide a step-by-step explanation or breakdown of reasoning, which can be especially useful in educational or technical explanations. It also helps mitigate the occurence of hallucinations.

Example:
```python
agent = CreateAgent(chain_of_thought=True)
```

### Query Prompt Refinement

Attempts to improve the clarity, focus, and specificity of a prompt to align with the desired outcomes or objectives with the --refine flag. It involves adjusting language, structure, and scope to ensure the prompt effectively guides responses and generates accurate, relevant, and actionable results. Results are automatically submitted as a new query to the requested LLM.

Example:
```python
agent = CreateAgent(refine=True)
```

Result:
```
Can you provide detailed, step-by-step instructions for changing a tire, emphasizing key safety precautions and necessary tools? 
You should include comprehensive details like how to safely park the car, the importance of using a wheel chock, and the correct way to position the jack. 
Also, expand on how to properly remove the lug nuts, replace the tire, and ensure everything is secure before driving again.
```

### Response Iterations

This feature helps to increase the creative ability of a model thorugh multiple distinct reponse generation followed by critical evaluation for the most optimal response. The --iterations flag accepts an integer value representing the number of separate reponse iterations the model will create for the given prompt. Increasing this value past the 1 will prompt the model to also provide a summary of it's evaluation including why the returned response was selected over others. Tip: Best results might be seen increasing this number relative to the complexity of the input prompt, but diminishing returns do seem to occur at a certain point. Recommended to use in combination with changing temperatature OR top_p for more creativity across responses (NOTE: OpenAI recommendeds NOT to change both of these parameters at once, could increase hallucinations).

Example:
```python
agent = CreateAgent(iterations=3, temperatature=0.9)
```

This will generate 3 distinct versions of the reponse, and then synthesize them into a single higher quality response.

### Recursive Directory Scanning

This feature allows the tool to traverse all subdirectories within a specified root directory to systematically read and collect files throughout an entire codebase. This automation efficiently gathers and processes files regardless of their nesting level, ensuring comprehensive codebase analysis and management.

Example:
```python
agent = CreateAgent(scan_dirs=True)
```

### Associative Glyph Prompting

During prompt refinement, the addition --glyph flag will restructure the revised prompt utilizing concepts from [Symbolic Representations Framework](https://github.com/severian42/Computational-Model-for-Symbolic-Representations) to create user-defined symbolic representations (glyphs) guide AI interactions. Glyphs serve as conceptual tags, steering AI focus within specific domains like storytelling or thematic development without altering the model's architecture. Instead, they leverage existing AI mechanisms—contextual priming, attention, and latent space activation—repurposing them to create a shared symbolic framework for dynamic and intuitive collaboration. These methods have been shown to not only dramatically improve the quality of responses, but also reduce costs for both token generation and compute times.

Example:
```python
agent = CreateAgent(glyph=True)
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
```

### Image Generation Parameters

You are able to set specific parameters of the output image created by Dall-e. Flags for dimenions (--dimenions) in pixels, as well as definition quality (--quality) have been implemented. The agent will try to recognize multiple iterations of quality reponses to differentiate preference in standard versus HD correctly. Optionally as list above, built-in roles are included for artist and photographer.

Example:
```python
artist = CreateAgent(role="artist", dimensions="1024x1024", quality="high")

artist.request('Generate an image of a bacterial cell dissolving into matix code in the style of the Impressionists.')
```

Result:

![image](./extras/dalle3.20240927_083555.image.png)


## Advanced Usage

Multiple agents with distinct roles may be called to cooperate in generating the most complete reponses needed by the user. This is most easily accomplised by using with the imported package version. The following example is also implemented in the accompanying jupyter notebook [multi-agent_example.ipynb](https://github.com/mjenior/promptpal/blob/main/extras/multi-agent_example.ipynb)

Example:

First, create a team of distinct agents with differing expertise.

```python
from promptpal.core import CreateAgent

# Initialize agents
comp_bio = CreateAgent(role="analyst", refine=True, chain_of_thought=True, glyph=True) # Computational biologist
recode = CreateAgent(role="refactor") # Code refactoring and formatting expert
tests = CreateAgent(role="tester") # Unit test generator
write = CreateAgent(role="writer", iterations=5, chain_of_thought=True, glyph=True) # Creative science writer
edit = CreateAgent(role="editor", refine=True) # Expert copy editor
```

Use inital agent to start the project:

```python
# Make initial request to first agent for computational biology project
query = """
Write an analysis pipeline in python to assemble long nanopore reads into contigs and then align them to an annotated reference genome.
Then identify all of the sequence variation present in the new genome that is not present in the reference.
Additionally generate a figure from data generated during the alignment based on quality scores, and 2 more figures to help interpret the results at the end.
"""
developer.request(query)
```

Optimize and document any new code, add unit testing.

```python
query = """
Refactor and format the previous for optimal efficiency, useability, and generalization:
"""
recode.request(query)

query = """
Create unit tests for the newly refactored code.
"""
tests.request(query)
```

Then use the next agents to read through the new pipeline and generate a high-quality blog post describing it's utility.

```python
# Utilize the writer agent to generate an informed post on the background and utility of the newly created pipeline
query = """
Write a biotechnology blog post about the pipeline described you have just outlined. 
Include relevant background that would necessitate this type of analysis, and add at least one example use case for the workflow. 
Extrapolate how the pipeline may be useful in cell engineering efforts, and what future improvements could lead to with continued work. 
The resulting post should be at least 3 paragraphs long with 4-5 sentences in each.
Speak in a conversational tone and cite all sources with biological relevance to you discussion.
"""
write.request(query)

# Pass the rough draft text to the editor agent to recieve a more finalize version
query ="""
Edit the previous post to be much more polished and ready for release.
"""
edit.request(query)
```

This is one just example of how multiple LLM agents may be leveraged in concert to accelerate the rate that user workloads may be accomplished.


## Contributing

If you encounter any problems, please [file an issue](https://github.com/mjenior/promptpal/issues) along with a detailed description.

We welcome contributions! If you'd like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new feature branch (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push the branch (`git push origin feature-name`).
5. Create a [pull request](https://github.com/mjenior/promptpal/pulls).


## License

This project is licensed under the [MIT](http://opensource.org/licenses/MIT) License. See the [LICENSE](https://raw.githubusercontent.com/mjenior/promptpal/refs/heads/main/LICENSE.txt) file for more details.
