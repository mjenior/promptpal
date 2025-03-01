import os

import pytest

from promptpal.promptpal import Promptpal, PromptRefinementType
from promptpal.roles import Role

# Check if running in CI environment
is_ci = os.getenv("CI") is not None


@pytest.mark.integration
@pytest.mark.skipif(is_ci, reason="Skipping integration tests in CI environment.")
def test_add_and_list_roles_integration():
    # Initialize Promptpal with actual API
    promptpal = Promptpal(load_default_roles=False)

    # Define roles to add
    roles = [
        Role(
            name="integration_role1",
            description="Integration Role 1",
            system_instruction="Instruction 1",
        ),
        Role(
            name="integration_role2",
            description="Integration Role 2",
            system_instruction="Instruction 2",
        ),
    ]

    # Add roles
    promptpal.add_roles(roles)

    # List roles and verify (list_roles now prints instead of returning)
    # Use capsys to capture the output
    promptpal.list_roles()
    # Just verify that the roles were added successfully
    assert "integration_role1" in promptpal._roles
    assert "integration_role2" in promptpal._roles


@pytest.mark.integration
@pytest.mark.skipif(is_ci, reason="Skipping integration tests in CI environment.")
def test_chat_integration():
    # Initialize Promptpal with actual API
    promptpal = Promptpal(load_default_roles=False)

    # Define a role for chat
    role = Role(
        name="chat_role",
        description="Chat Role",
        system_instruction="Instruction",
        model="gemini-1.5-flash",
    )
    promptpal.add_roles([role])

    # Send a message and verify response
    response = promptpal.chat("chat_role", "Explain how AI works")
    assert response is not None
    assert isinstance(response, str)


@pytest.mark.integration
@pytest.mark.skip(
    reason="Image generation model not available. TODO: Fix image generation handling."
)
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
    promptpal = Promptpal(load_default_roles=False)

    # Add a role for glyph refinement
    role = Role(
        name="glyph_prompt",
        description="Glyph Prompt",
        system_instruction="<user_prompt>",
        model="gemini-1.5-pro",
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
