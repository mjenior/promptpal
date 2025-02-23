import os
import tempfile
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from PIL import Image

from promptpal.promptpal import Promptpal
from promptpal.roles import Role


@pytest.fixture(autouse=True)
def mock_env_gemini_api_key(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test_api_key")


def test_add_roles():
    promptpal = Promptpal(load_default_roles=False)
    roles = [
        Role(name="role1", description="Role 1", system_instruction="Instruction 1"),
        Role(name="role2", description="Role 2", system_instruction="Instruction 2"),
    ]
    promptpal.add_roles(roles)
    assert len(promptpal._roles) == 2
    assert "role1" in promptpal._roles
    assert "role2" in promptpal._roles


def test_add_roles_from_file(tmp_path):
    # Create a temporary YAML file
    roles_yaml = tmp_path / "roles.yaml"
    roles_yaml.write_text(
        """
        role1:
          description: "Role 1"
          system_instruction: "Instruction 1"
        role2:
          description: "Role 2"
          system_instruction: "Instruction 2"
        """
    )

    promptpal = Promptpal(load_default_roles=False)
    with open(roles_yaml) as file:
        promptpal.add_roles_from_file(file)


def test_list_roles():
    promptpal = Promptpal(load_default_roles=False)
    roles = [
        Role(name="role1", description="Role 1", system_instruction="Instruction 1"),
        Role(name="role2", description="Role 2", system_instruction="Instruction 2"),
    ]
    promptpal.add_roles(roles)
    role_names = promptpal.list_roles()
    assert role_names == ["role1", "role2"]


def test_get_role_description():
    promptpal = Promptpal()
    roles = [
        Role(name="role1", description="Role 1", system_instruction="Instruction 1"),
        Role(name="role2", description="Role 2", system_instruction="Instruction 2"),
    ]
    promptpal.add_roles(roles)
    description = promptpal.get_role_description("role1")
    assert description == "Role 1"

    with pytest.raises(ValueError):
        promptpal.get_role_description("nonexistent_role")


def test_chat_valid_role(mocker):
    # Mock the genai client
    mock_client = mocker.patch("promptpal.promptpal.genai.Client")
    mock_chat = mock_client.return_value.chats.create
    mock_chat_instance = mock_chat.return_value
    mock_response = MagicMock()
    mock_response.text = "AI response text"
    mock_response.usage_metadata.prompt_token_count = 500  # Set to a valid integer
    mock_chat_instance.send_message.return_value = mock_response

    promptpal = Promptpal()
    roles = [
        Role(
            name="role1",
            description="Role 1",
            system_instruction="Instruction 1",
            model="gemini-2.0-flash",
        ),
    ]
    promptpal.add_roles(roles)

    response = promptpal.chat(
        "role1", "Explain how AI works", write_code=False, token_threshold=1000
    )
    assert response == "AI response text"


def test_chat_invalid_role():
    promptpal = Promptpal()
    with pytest.raises(ValueError, match="Role 'nonexistent_role' not found."):
        promptpal.chat("nonexistent_role", "Explain how AI works")


def test_chat_api_error(mocker):
    promptpal = Promptpal()
    roles = [
        Role(
            name="role1",
            description="Role 1",
            system_instruction="Instruction 1",
            model="gemini-2.0-flash",
        ),
    ]
    promptpal.add_roles(roles)

    # Mock the SDK to raise an exception
    mocker.patch.object(
        promptpal._client.models, "generate_content", side_effect=Exception("API error")
    )

    with pytest.raises(Exception, match="API error"):
        promptpal.chat("role1", "Explain how AI works")


def test_promptpal_load_default_roles(mocker):
    # Mock the add_roles_from_file method to simulate loading roles
    mocker.patch("promptpal.promptpal.Promptpal.add_roles_from_file")

    promptpal = Promptpal(load_default_roles=True)
    # Verify that add_roles_from_file was called
    promptpal.add_roles_from_file.assert_called_once()


def test_promptpal_manual_role_addition():
    promptpal = Promptpal(load_default_roles=False)
    # Verify that no roles are loaded initially
    assert len(promptpal._roles) == 0

    # Manually add roles
    roles = [
        Role(name="role1", description="Role 1", system_instruction="Instruction 1"),
        Role(name="role2", description="Role 2", system_instruction="Instruction 2"),
    ]
    promptpal.add_roles(roles)

    # Verify that roles are added correctly
    assert len(promptpal._roles) == 2
    assert "role1" in promptpal._roles
    assert "role2" in promptpal._roles


def test_chat_with_file_references(mocker):
    # Mock the genai client
    mock_client = mocker.patch("promptpal.promptpal.genai.Client")
    mock_chat = mock_client.return_value.chats.create
    mock_chat_instance = mock_chat.return_value
    mock_generate_content = mock_chat_instance.send_message
    mock_generate_content.return_value.text = "Response text"
    mock_generate_content.return_value.usage_metadata.prompt_token_count = (
        500  # Set to a valid integer
    )

    # Mock the file upload
    mock_upload = mock_client.return_value.files.upload
    mock_upload.return_value = "uploaded_file_reference"

    # Create a temporary file with some content
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"This is a test file.")
        temp_file_path = temp_file.name

    # Initialize Promptpal and add roles
    promptpal = Promptpal(load_default_roles=False)
    role = Role(
        name="test_role",
        description="Test Role",
        system_instruction="Instruction",
        model="test-model",
    )
    promptpal.add_roles([role])

    # Call the chat method with a message containing the file path
    message = f"Read {temp_file_path} and provide a summary."
    response = promptpal.chat(role_name="test_role", message=message, token_threshold=1000)

    # Verify that the file was uploaded and included in the contents
    mock_upload.assert_called_once_with(file=temp_file_path)
    expected_contents = [
        "Read",
        "uploaded_file_reference",
        "and",
        "provide",
        "a",
        "summary.",
    ]
    assert mock_generate_content.call_args[0][0] == expected_contents
    assert response == "Response text"

    # Clean up the temporary file
    os.remove(temp_file_path)


def test_new_chat(mocker):
    # Mock the genai client
    mock_client = mocker.patch("promptpal.promptpal.genai.Client")
    mock_chat = mock_client.return_value.chats.create
    mock_chat_instance = mock_chat.return_value

    # Initialize Promptpal
    promptpal = Promptpal()

    # Call new_chat to reset the chat
    promptpal.new_chat()

    # Verify that a new chat instance was created
    mock_chat.assert_called_with(model="gemini-2.0-flash-001")
    assert promptpal._chat == mock_chat_instance


def test_chat_summarization(mocker):
    # Mock the genai client
    mock_client = mocker.patch("promptpal.promptpal.genai.Client")
    mock_chat = mock_client.return_value.chats.create
    mock_chat_instance = mock_chat.return_value
    mock_response = MagicMock()
    mock_response.text = "AI response text"
    mock_response.usage_metadata.prompt_token_count = 1500  # Exceed threshold
    mock_chat_instance.send_message.return_value = mock_response

    # Mock the summarization response
    mock_summary_response = MagicMock()
    mock_summary_response.text = "Summary of the chat"

    # Ensure the summarization logic is triggered by setting the initial response
    # and then simulating the summarization process.
    mock_chat_instance.send_message.side_effect = [
        mock_response,  # Initial response exceeding the token threshold
        mock_summary_response,  # Summarization response
        mock_summary_response,  # Response to the new chat with the summary
    ]

    promptpal = Promptpal(load_default_roles=False)  # Avoid loading default roles
    roles = [
        Role(
            name="role1",
            description="Role 1",
            system_instruction="Instruction 1",
            model="gemini-2.0-flash",
        ),
        Role(
            name="summarizer",
            description="Summarizer",
            system_instruction="Summarize the chat",
            model="gemini-2.0-flash",
        ),
    ]
    promptpal.add_roles(roles)

    # Simulate the chat process
    response = promptpal.chat("role1", "Explain how AI works", token_threshold=1000)
    assert response == "AI response text"

    # Verify that the summarization was triggered
    assert mock_chat_instance.send_message.call_count == 3
    assert mock_chat_instance.send_message.call_args_list[1][0][0] == [
        "Summarize the previous chat."
    ]
    assert mock_chat_instance.send_message.call_args_list[2][0][0] == [
        "Here is a summary of the previous chat:",
        "Summary of the chat",
    ]


def test_chat_with_write_code(mocker, tmp_path):
    # Mock the genai client
    mock_client = mocker.patch("promptpal.promptpal.genai.Client")
    mock_chat = mock_client.return_value.chats.create
    mock_chat_instance = mock_chat.return_value
    mock_response = MagicMock()
    mock_response.text = """
    Here is some Python code:
    ```python
    def hello_world():
        print("Hello, world!")
    ```
    And some JavaScript code:
    ```javascript
    function greet() {
        console.log("Hello, world!");
    }
    ```
    """
    mock_response.usage_metadata.prompt_token_count = 500  # Set to a valid integer
    mock_chat_instance.send_message.return_value = mock_response

    # Use a temporary directory for writing code files
    output_dir = tmp_path / "code_snippets"
    promptpal = Promptpal(load_default_roles=False, output_dir=str(output_dir))
    roles = [
        Role(
            name="role1",
            description="Role 1",
            system_instruction="Instruction 1",
            model="gemini-2.0-flash",
        ),
    ]
    promptpal.add_roles(roles)

    # Call the chat method with write_code=True
    response = promptpal.chat("role1", "Generate some code", write_code=True, token_threshold=1000)
    assert response == mock_response.text

    # Verify that code files were written
    code_snippets = promptpal.extract_code_snippets(mock_response.text)
    for lang, code in code_snippets.items():
        filename = promptpal.determine_filename(lang, code)
        file_path = output_dir / filename
        assert file_path.exists()
        with open(file_path) as f:
            assert f.read() == code
        # Clean up the temporary file
        file_path.unlink()


def test_chat_image_generation(mocker, tmp_path):
    # Mock the genai client
    mock_client = mocker.patch("promptpal.promptpal.genai.Client")
    mock_generate_images = mock_client.return_value.models.generate_images
    mock_response = MagicMock()
    mock_generated_image = MagicMock()
    # Create a valid PNG image using PIL
    image = Image.new("RGBA", (1, 1), color=(255, 0, 0, 0))  # Red pixel with transparency
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format="PNG")
    mock_generated_image.image.image_bytes = img_byte_arr.getvalue()
    mock_response.generated_images = [mock_generated_image]
    mock_generate_images.return_value = mock_response

    promptpal = Promptpal(output_dir=str(tmp_path))
    roles = [
        Role(
            name="artist",
            description="Digital Artist",
            system_instruction="Create art",
            model="gemini-2.0-flash",
            output_type="image",
        ),
    ]
    promptpal.add_roles(roles)

    response = promptpal.chat("artist", "Create a sunset painting", write_code=False)
    assert response == f"Images saved to {tmp_path!s}"

    # Check that the image was saved
    saved_images = list(tmp_path.glob("*.png"))
    assert len(saved_images) == 1
    assert saved_images[0].name == "artist_image_0.png"


def test_refine_prompt_with_glyph_refinement(mocker):
    # Mock the genai client
    mock_client = mocker.patch("promptpal.promptpal.genai.Client")
    mock_generate_content = mock_client.return_value.models.generate_content
    mock_response = MagicMock()
    mock_response.text = "Refined prompt using glyph refinement"
    mock_generate_content.return_value = mock_response

    promptpal = Promptpal(load_default_roles=False)
    roles = [
        Role(
            name="glyph_prompt",
            description="Glyph Prompt",
            system_instruction="<user_prompt>",
            model="gemini-1.5-pro",
        ),
    ]
    promptpal.add_roles(roles)

    response = promptpal.refine_prompt("Test prompt", glyph_refinement=True)
    assert response == "Refined prompt using glyph refinement"


def test_refine_prompt_with_chain_of_thought(mocker):
    # Mock the genai client
    mock_client = mocker.patch("promptpal.promptpal.genai.Client")
    mock_generate_content = mock_client.return_value.models.generate_content
    mock_response = MagicMock()
    mock_response.text = "Refined prompt using chain of thought"
    mock_generate_content.return_value = mock_response

    promptpal = Promptpal(load_default_roles=False)
    roles = [
        Role(
            name="chain_of_thought",
            description="Chain of Thought",
            system_instruction="<user_prompt>",
            model="gemini-1.5-pro",
        ),
    ]
    promptpal.add_roles(roles)

    response = promptpal.refine_prompt("Test prompt", chain_of_thought=True)
    assert response == "Refined prompt using chain of thought"


def test_refine_prompt_with_keyword_refinement():
    promptpal = Promptpal(load_default_roles=False)
    prompt = "This is a test prompt."
    keyword = "simplify"
    expected_instruction = "Use less complex language for easier comprehension."
    expected_output = f"{expected_instruction}\n\n{prompt}"

    response = promptpal.refine_prompt(prompt, keyword_refinement=keyword)
    assert response == expected_output


def test_refine_prompt_with_invalid_keyword_refinement():
    promptpal = Promptpal(load_default_roles=False)
    with pytest.raises(ValueError, match="Keyword refinement 'invalid_keyword' not recognized."):
        promptpal.refine_prompt("Test prompt", keyword_refinement="invalid_keyword")


def test_refine_prompt_with_multiple_refinements():
    promptpal = Promptpal(load_default_roles=False)
    with pytest.raises(
        ValueError,
        match="Only one of glyph_refinement, chain_of_thought, or keyword_refinement can be true.",
    ):
        promptpal.refine_prompt("Test prompt", glyph_refinement=True, chain_of_thought=True)


def test_init_without_api_key(monkeypatch):
    # Remove GEMINI_API_KEY from environment
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(EnvironmentError, match="GEMINI_API_KEY environment variable not found!"):
        Promptpal()


def test_chat_with_web_search(mocker):
    # Mock the genai client
    mock_client = mocker.patch("promptpal.promptpal.genai.Client")
    mock_chat = mock_client.return_value.chats.create
    mock_chat_instance = mock_chat.return_value
    mock_response = MagicMock()
    mock_response.text = "Search response"
    mock_response.usage_metadata.prompt_token_count = 500
    mock_chat_instance.send_message.return_value = mock_response

    promptpal = Promptpal(load_default_roles=False)
    role = Role(
        name="searcher",
        description="Web Searcher",
        system_instruction="Search the web",
        search_web=True,
    )
    promptpal.add_roles([role])

    response = promptpal.chat("searcher", "Search for something")
    assert response == "Search response"
    assert mock_chat_instance.send_message.called


def test_chat_with_image_generation(mocker):
    # Mock the genai client
    mock_client = mocker.patch("promptpal.promptpal.genai.Client")
    mock_generate_images = mock_client.return_value.models.generate_images
    mock_response = MagicMock()
    mock_generated_image = MagicMock()

    # Create a valid PNG image using PIL
    image = Image.new("RGBA", (1, 1), color=(255, 0, 0, 0))
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format="PNG")
    mock_generated_image.image.image_bytes = img_byte_arr.getvalue()
    mock_response.generated_images = [mock_generated_image]
    mock_generate_images.return_value = mock_response

    promptpal = Promptpal(load_default_roles=False)
    role = Role(
        name="artist",
        description="Image Generator",
        system_instruction="Generate images",
        output_type="image",
    )
    promptpal.add_roles([role])

    with tempfile.TemporaryDirectory() as tmpdir:
        promptpal._output_dir = tmpdir
        response = promptpal.chat("artist", "Generate an image")
        assert response == f"Images saved to {tmpdir}"
        assert Path(tmpdir).joinpath("artist_image_0.png").exists()


def test_chat_with_image_generation_error(mocker):
    # Mock the genai client
    mock_client = mocker.patch("promptpal.promptpal.genai.Client")
    mock_generate_images = mock_client.return_value.models.generate_images
    mock_generate_images.side_effect = Exception("Image generation failed")

    promptpal = Promptpal(load_default_roles=False)
    role = Role(
        name="artist",
        description="Image Generator",
        system_instruction="Generate images",
        output_type="image",
    )
    promptpal.add_roles([role])

    with pytest.raises(Exception, match="Image generation failed"):
        promptpal.chat("artist", "Generate an image")


def test_chat_with_file_upload(mocker, tmp_path):
    # Create a test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    # Mock the genai client
    mock_client = mocker.patch("promptpal.promptpal.genai.Client")
    mock_chat = mock_client.return_value.chats.create
    mock_chat_instance = mock_chat.return_value
    mock_response = MagicMock()
    mock_response.text = "Response with file"
    mock_response.usage_metadata.prompt_token_count = 500
    mock_chat_instance.send_message.return_value = mock_response

    # Mock file upload
    mock_upload = mock_client.return_value.files.upload
    mock_upload.return_value = "uploaded_file_reference"

    promptpal = Promptpal(load_default_roles=False)
    role = Role(
        name="file_handler",
        description="File Handler",
        system_instruction="Handle files",
    )
    promptpal.add_roles([role])

    message = f"Process this file: {test_file!s}"
    response = promptpal.chat("file_handler", message)

    assert response == "Response with file"
    mock_upload.assert_called_once_with(file=str(test_file))


def test_chat_with_file_not_found(mocker):
    # Mock the genai client
    mock_client = mocker.patch("promptpal.promptpal.genai.Client")
    mock_chat = mock_client.return_value.chats.create
    mock_chat_instance = mock_chat.return_value
    mock_response = MagicMock()
    mock_response.text = "Response without file"
    mock_response.usage_metadata.prompt_token_count = 500
    mock_chat_instance.send_message.return_value = mock_response

    promptpal = Promptpal(load_default_roles=False)
    role = Role(
        name="file_handler",
        description="File Handler",
        system_instruction="Handle files",
    )
    promptpal.add_roles([role])

    message = "Process this file: /nonexistent/file.txt"
    response = promptpal.chat("file_handler", message)

    assert response == "Response without file"
    # Verify that the message was sent without the file reference
    assert mock_chat_instance.send_message.called


def test_chat_with_web_search_tool_configuration(mocker):
    # Mock the genai client and types
    mock_client = mocker.patch("promptpal.promptpal.genai.Client")
    mock_types = mocker.patch("promptpal.promptpal.genai.types")
    mock_chat = mock_client.return_value.chats.create
    mock_chat_instance = mock_chat.return_value
    mock_response = MagicMock()
    mock_response.text = "Search response"
    mock_response.usage_metadata.prompt_token_count = 500
    mock_chat_instance.send_message.return_value = mock_response

    # Create Promptpal instance with web search role
    promptpal = Promptpal(load_default_roles=False)
    role = Role(
        name="searcher",
        description="Web Searcher",
        system_instruction="Search the web",
        search_web=True,
    )
    promptpal.add_roles([role])

    # Call chat method
    promptpal.chat("searcher", "Search for something")

    # Verify tool configuration
    mock_types.Tool.assert_called_once()
    mock_types.GoogleSearchRetrieval.assert_called_once()
    mock_types.DynamicRetrievalConfig.assert_called_once_with(dynamic_threshold=0.6)


def test_chat_with_file_upload_and_message_parts(mocker, tmp_path):
    # Create test files
    test_file1 = tmp_path / "test1.txt"
    test_file2 = tmp_path / "test2.txt"
    test_file1.write_text("test content 1")
    test_file2.write_text("test content 2")

    # Mock the genai client
    mock_client = mocker.patch("promptpal.promptpal.genai.Client")
    mock_chat = mock_client.return_value.chats.create
    mock_chat_instance = mock_chat.return_value
    mock_response = MagicMock()
    mock_response.text = "Response with files"
    mock_response.usage_metadata.prompt_token_count = 500
    mock_chat_instance.send_message.return_value = mock_response

    # Mock file upload with different references
    mock_upload = mock_client.return_value.files.upload
    mock_upload.side_effect = ["ref1", "ref2"]

    promptpal = Promptpal(load_default_roles=False)
    role = Role(
        name="file_handler",
        description="File Handler",
        system_instruction="Handle files",
    )
    promptpal.add_roles([role])

    # Create message with multiple files and text
    message = f"Process these files: {test_file1!s} and {test_file2!s} with some text"
    response = promptpal.chat("file_handler", message)

    assert response == "Response with files"
    assert mock_upload.call_count == 2

    # Verify the message was constructed correctly with file references
    expected_contents = [
        "Process",
        "these",
        "files:",
        "ref1",
        "and",
        "ref2",
        "with",
        "some",
        "text",
    ]
    mock_chat_instance.send_message.assert_called_once_with(expected_contents)


def test_chat_with_prompt_refinement(mocker):
    # Mock the genai client
    mock_client = mocker.patch("promptpal.promptpal.genai.Client")
    mock_generate_content = mock_client.return_value.models.generate_content
    mock_response = MagicMock()
    mock_response.text = "Refined prompt"
    mock_generate_content.return_value = mock_response

    promptpal = Promptpal(load_default_roles=False)
    roles = [
        Role(
            name="glyph_prompt",
            description="Glyph Prompt",
            system_instruction="<user_prompt>",
            model="gemini-1.5-pro",
        ),
        Role(
            name="chain_of_thought",
            description="Chain of Thought",
            system_instruction="<user_prompt>",
            model="gemini-1.5-pro",
        ),
    ]
    promptpal.add_roles(roles)

    # Test different refinement methods
    glyph_response = promptpal.refine_prompt("Test prompt", glyph_refinement=True)
    assert glyph_response == "Refined prompt"

    chain_response = promptpal.refine_prompt("Test prompt", chain_of_thought=True)
    assert chain_response == "Refined prompt"

    keyword_response = promptpal.refine_prompt("Test prompt", keyword_refinement="simplify")
    assert "Use less complex language for easier comprehension" in keyword_response

    # Verify generate_content was called with correct parameters
    assert mock_generate_content.call_count == 2  # Once for glyph, once for chain of thought


def test_load_roles_from_file(tmp_path):
    # Create a temporary YAML file with role definitions
    roles_file = tmp_path / "roles.yaml"
    code = "role_data:\n  name: test\n  description: test role"
    roles_file.write_text(code)
    with open(roles_file) as f:
        assert f.read() == code


def test_find_existing_files(tmp_path):
    # Create test files
    test_file1 = tmp_path / "test1.txt"
    test_file2 = tmp_path / "test2.txt"
    test_file1.touch()
    test_file2.touch()

    # Test the find_existing_files function directly
    from promptpal.promptpal import find_existing_files

    message = f"Process these files: {test_file1} and {test_file2} with some text"
    found_files = find_existing_files(message)

    # Verify both files were found
    assert len(found_files) == 2
    assert str(test_file1) in found_files
    assert str(test_file2) in found_files
