import os

import pytest

from promptpal.promptpal import Promptpal
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

    # List roles and verify
    role_names = promptpal.list_roles()
    assert "integration_role1" in role_names
    assert "integration_role2" in role_names


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
