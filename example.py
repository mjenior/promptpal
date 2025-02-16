# main.py

from promptpal.promptpal import Promptpal
import os

# Set up a directory for code snippets and images
output_dir = "./example_output"
os.makedirs(output_dir, exist_ok=True)

# Initialize Promptpal and load default roles
promptpal = Promptpal(load_default_roles=True, output_dir=output_dir)

# List available roles with names
print("Available Roles:")
for role_name in promptpal.list_roles():
    print(f"- {role_name}")

# Interact with different roles
try:
    # Use a role to generate content
    print("\nUsing 'analyst' role to generate content:")
    response = promptpal.chat(
        "analyst", "Analyze the gene expression data for patterns."
    )
    print(response)

    # Use a role to refine a prompt with keyword refinement
    print("\nRefining a prompt with keyword refinement:")
    refined_prompt = promptpal.refine_prompt(
        "Explain the process of DNA replication.", keyword_refinement="simplify"
    )
    print("Refined Prompt:", refined_prompt)

    # Demonstrate chat reset
    print("\nResetting chat and starting a new session:")
    promptpal.new_chat()
    response = promptpal.chat(
        "analyst", "Describe the impact of a specific mutation on protein function."
    )
    print(response)

    # Demonstrate writing code snippets to files
    print("\nUsing 'developer' role to generate code and write to files:")
    response = promptpal.chat(
        "developer",
        "Write a Python function to calculate the GC content of a DNA sequence.",
        write_code=True,
    )
    print(response)
    print(f"Code snippets written to {output_dir}")

    # Demonstrate image generation with a clear example
    print("\nUsing 'artist' role to generate an image:")
    response = promptpal.chat(
        "artist",
        "Create a detailed and artistic representation of a DNA double helix.",
    )
    print(response)
    print(f"Images saved to {output_dir}")

except ValueError as e:
    print(f"Error: {e}")
