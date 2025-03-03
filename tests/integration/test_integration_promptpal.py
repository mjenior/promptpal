import os

import pytest

from promptpal.promptpal import Promptpal, PromptRefinementType
from promptpal.roles import Role

# Check if running in CI environment
is_ci = os.getenv("CI") is not None


@pytest.mark.integration
@pytest.mark.skipif(is_ci, reason="Skipping integration tests in CI environment.")
def test_message_integration():
    # Initialize Promptpal with actual API
    promptpal = Promptpal(load_default_roles=False, vertexai=False)

    # Define a role for message
    role = Role(
        model="gemini-2.0-flash",
        name="message_role",
        description="Message Role",
        system_instruction="Instruction",
    )
    promptpal.add_roles([role])

    # Send a message and verify response
    response = promptpal.message("message_role", "Hello, world!")
    assert response is not None
    assert isinstance(response, str)


@pytest.mark.integration
@pytest.mark.skipif(is_ci, reason="Skipping integration tests in CI environment.")
def test_chat_integration():
    # Initialize Promptpal with actual API
    promptpal = Promptpal(load_default_roles=False, vertexai=False)

    # Define a role for chat
    role = Role(
        name="chat_role",
        description="Chat Role",
        system_instruction="Instruction",
        model="gemini-2.0-flash",
    )
    promptpal.add_roles([role])

    # Send a message and verify response
    promptpal.chat("chat_role", "Explain how AI works")
    assert promptpal.get_last_response() is not None
    assert isinstance(promptpal.get_last_response(), str)


@pytest.mark.integration
@pytest.mark.skip(reason="Image generation model not available. TODO: Fix image generation handling.")
def test_image_generation_integration(tmp_path):
    # Initialize Promptpal with actual API
    promptpal = Promptpal(output_dir=str(tmp_path))

    # Define a role for image generation
    role = Role(
        name="artist",
        description="Digital Artist",
        system_instruction="Create art",
        model="imagen-3.0-generate-002",
        output_type="image",
    )
    promptpal.add_roles([role])

    # Generate an image and verify
    response = promptpal.chat("artist", "Create a sunset painting")
    assert response == f"Images saved to {tmp_path!s}"

    # Check that the image was saved
    saved_images = list(tmp_path.glob("*.png"))
    assert len(saved_images) == 1
    assert saved_images[0].name == "artist_image_0.png"


@pytest.mark.integration
@pytest.mark.skipif(is_ci, reason="Skipping integration tests in CI environment.")
def test_refine_prompt_integration():
    # Initialize Promptpal with actual API
    promptpal = Promptpal(load_default_roles=False, vertexai=False)

    # Add a role for glyph refinement
    role = Role(
        name="glyph_prompt",
        description="Glyph Prompt",
        system_instruction="<user_prompt>",
        model="gemini-2.0-flash",
    )
    promptpal.add_roles([role])

    # Define a prompt to refine
    prompt = """
    **System Role: Virology Lab Logistics & Procurement Agent**

    *   **Human Oversight:**  While the agent can automate many aspects of the procurement process,
        human oversight is still essential to review purchase orders, address unexpected issues,
        and ensure compliance with all relevant policies and regulations.
    """

    # Attempt to refine the prompt using the new enum-based approach
    try:
        updated_prompt = promptpal.refine_prompt(prompt, refinement_type=PromptRefinementType.GLYPH)
        print(updated_prompt)
    except Exception as e:
        pytest.fail(f"Refine prompt failed with exception: {e}")
