import os
import tempfile
from unittest.mock import MagicMock

import pytest

from promptpal.promptpal import Promptpal
from promptpal.roles import Role


@pytest.fixture(autouse=True)
def mock_env_gemini_api_key(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test_api_key")


def test_add_roles():
    promptpal = Promptpal(load_default_roles=False, vertexai=False)
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

    promptpal = Promptpal(load_default_roles=False, vertexai=False)
    with open(roles_yaml) as file:
        promptpal.add_roles_from_file(file)


def test_list_roles(capsys):
    promptpal = Promptpal(load_default_roles=False, vertexai=False)
    roles = [
        Role(name="role1", description="Role 1", system_instruction="Instruction 1"),
        Role(name="role2", description="Role 2", system_instruction="Instruction 2"),
    ]
    promptpal.add_roles(roles)

    # Call the method which now prints instead of returning
    promptpal.list_roles()

    # Capture the printed output
    captured = capsys.readouterr()

    # Check that the output contains the role names and descriptions
    assert "role1" in captured.out
    assert "Role 1" in captured.out
    assert "role2" in captured.out
    assert "Role 2" in captured.out
    assert "Total: 2 roles" in captured.out


def test_chat_valid_role(mocker):
    # Mock the genai client
    mock_client = mocker.patch("promptpal.promptpal.genai.Client")
    mock_chat = mock_client.return_value.chats.create
    mock_chat_instance = mock_chat.return_value
    mock_response = MagicMock()
    mock_response.text = "AI response text"
    mock_response.usage_metadata.total_token_count = 500  # Set to a valid integer
    mock_chat_instance.send_message.return_value = mock_response

    promptpal = Promptpal(load_default_roles=False, vertexai=False)
    roles = [
        Role(
            name="role1",
            description="Role 1",
            system_instruction="Instruction 1",
            model="gemini-2.0-flash",
        ),
    ]
    promptpal.add_roles(roles)

    promptpal.chat("role1", "Explain how AI works", write_code=False, token_threshold=1000)
    assert promptpal.get_last_response() == "AI response text"


def test_chat_invalid_role():
    promptpal = Promptpal(vertexai=False)
    with pytest.raises(ValueError, match="Role 'nonexistent_role' not found."):
        promptpal.chat("nonexistent_role", "Explain how AI works")


def test_chat_api_error(mocker):
    promptpal = Promptpal(vertexai=False)
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
    mocker.patch.object(promptpal._client.models, "generate_content", side_effect=Exception("API error"))

    with pytest.raises(Exception, match="API error"):
        promptpal.chat("role1", "Explain how AI works")


def test_promptpal_load_default_roles(mocker):
    # Mock the add_roles_from_file method to simulate loading roles
    mocker.patch("promptpal.promptpal.Promptpal.add_roles_from_file")

    promptpal = Promptpal(load_default_roles=True, vertexai=False)
    # Verify that add_roles_from_file was called
    promptpal.add_roles_from_file.assert_called_once()


def test_promptpal_manual_role_addition():
    promptpal = Promptpal(load_default_roles=False, vertexai=False)
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
    mock_generate_content.return_value.usage_metadata.total_token_count = 500  # Set to a valid integer

    # Mock the file upload
    mock_upload = mock_client.return_value.files.upload
    mock_upload.return_value = "uploaded_file_reference"

    # Create a temporary file with some content
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"This is a test file.")
        temp_file_path = temp_file.name

    # Initialize Promptpal and add roles
    promptpal = Promptpal(load_default_roles=False, vertexai=False)
    role = Role(
        name="test_role",
        description="Test Role",
        system_instruction="Instruction",
        model="test-model",
    )
    promptpal.add_roles([role])

    # Call the chat method with a message containing the file path
    message = f"Read {temp_file_path} and provide a summary."
    promptpal.chat(role_name="test_role", message=message, token_threshold=1000)

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
    assert promptpal.get_last_response() == "Response text"

    # Clean up the temporary file
    os.remove(temp_file_path)


def test_new_chat(mocker):
    # Mock the genai client
    mock_client = mocker.patch("promptpal.promptpal.genai.Client")
    mock_chat = mock_client.return_value.chats.create
    mock_chat_instance = mock_chat.return_value

    # Initialize Promptpal
    promptpal = Promptpal(vertexai=False)

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
    mock_response.usage_metadata.total_token_count = 1500  # Exceed threshold
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

    promptpal = Promptpal(load_default_roles=False, vertexai=False)  # Avoid loading default roles
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
    promptpal.chat("role1", "Explain how AI works", token_threshold=1000)
    assert promptpal.get_last_response() == "AI response text"

    # Verify that the summarization was triggered
    assert mock_chat_instance.send_message.call_count == 3
    assert mock_chat_instance.send_message.call_args_list[1][0][0] == ["Summarize the previous chat."]
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
    mock_response.usage_metadata.total_token_count = 500  # Set to a valid integer
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
    promptpal.chat("role1", "Generate some code", write_code=True, token_threshold=1000)
    assert promptpal.get_last_response() == mock_response.text

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


def test_init_without_api_key(monkeypatch):
    # Remove GEMINI_API_KEY from environment
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(EnvironmentError, match="GEMINI_API_KEY environment variable not found!"):
        Promptpal(vertexai=False)


def test_chat_with_web_search(mocker):
    # Mock the genai client
    mock_client = mocker.patch("promptpal.promptpal.genai.Client")
    mock_chat = mock_client.return_value.chats.create
    mock_chat_instance = mock_chat.return_value
    mock_response = MagicMock()
    mock_response.text = "Search response"
    mock_response.usage_metadata.total_token_count = 500
    mock_chat_instance.send_message.return_value = mock_response

    promptpal = Promptpal(load_default_roles=False, vertexai=False)
    role = Role(
        name="searcher",
        description="Web Searcher",
        system_instruction="Search the web",
        search_web=True,
    )
    promptpal.add_roles([role])

    promptpal.chat("searcher", "Search for something")
    assert promptpal.get_last_response() == "Search response"


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
    mock_response.usage_metadata.total_token_count = 500
    mock_chat_instance.send_message.return_value = mock_response

    # Mock file upload
    mock_upload = mock_client.return_value.files.upload
    mock_upload.return_value = "uploaded_file_reference"

    promptpal = Promptpal(load_default_roles=False, vertexai=False)
    role = Role(
        name="file_handler",
        description="File Handler",
        system_instruction="Handle files",
    )
    promptpal.add_roles([role])

    message = f"Process this file: {test_file!s}"
    promptpal.chat("file_handler", message)

    assert promptpal.get_last_response() == "Response with file"
    mock_upload.assert_called_once_with(file=str(test_file))


def test_chat_with_file_not_found(mocker):
    # Mock the genai client
    mock_client = mocker.patch("promptpal.promptpal.genai.Client")
    mock_chat = mock_client.return_value.chats.create
    mock_chat_instance = mock_chat.return_value
    mock_response = MagicMock()
    mock_response.text = "Response without file"
    mock_response.usage_metadata.total_token_count = 500
    mock_chat_instance.send_message.return_value = mock_response

    promptpal = Promptpal(load_default_roles=False)
    role = Role(
        name="file_handler",
        description="File Handler",
        system_instruction="Handle files",
    )
    promptpal.add_roles([role])

    message = "Process this file: /nonexistent/file.txt"
    promptpal.chat("file_handler", message)

    assert promptpal.get_last_response() == "Response without file"
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
    mock_response.usage_metadata.total_token_count = 500
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
    mock_response.usage_metadata.total_token_count = 500
    mock_chat_instance.send_message.return_value = mock_response

    # Mock file upload with different references
    mock_upload = mock_client.return_value.files.upload
    mock_upload.side_effect = ["ref1", "ref2"]

    # Store the side effect values for later use
    file_refs = ["ref1", "ref2"]

    # Test with vertexai=False (should use file uploads)
    promptpal = Promptpal(load_default_roles=False, vertexai=False)
    role = Role(
        name="file_handler",
        description="File Handler",
        system_instruction="Handle files",
    )
    promptpal.add_roles([role])

    # Create message with multiple files and text
    message = f"Process these files: {test_file1!s} and {test_file2!s} with some text"
    promptpal.chat("file_handler", message)

    assert promptpal.get_last_response() == "Response with files"
    assert mock_upload.call_count == 2

    # Verify the message was constructed correctly with file references
    expected_contents = []
    for part in message.split():
        if part == str(test_file1):
            expected_contents.append(file_refs[0])
        elif part == str(test_file2):
            expected_contents.append(file_refs[1])
        else:
            expected_contents.append(part)

    mock_chat_instance.send_message.assert_called_with(
        expected_contents,
        config={
            "temperature": role.temperature,
            "system_instruction": role.system_instruction,
            "max_output_tokens": role.max_output_tokens,
            "tools": None,
        },
    )

    # Reset mocks for the second test
    mock_chat_instance.send_message.reset_mock()
    mock_upload.reset_mock()

    # Test with vertexai=True (should read file contents)
    promptpal_vertex = Promptpal(load_default_roles=False, vertexai=True)
    promptpal_vertex.add_roles([role])

    # Mock open to capture file reading
    mock_open = mocker.patch("builtins.open", mocker.mock_open(read_data="test content"))

    promptpal_vertex.chat("file_handler", message)

    assert promptpal_vertex.get_last_response() == "Response with files"
    # No file uploads should happen with vertexai=True
    assert mock_upload.call_count == 0

    # Verify that open was called for each file
    assert mock_open.call_count == 2

    # The message should include the file contents
    mock_chat_instance.send_message.assert_called_once()
    sent_message = mock_chat_instance.send_message.call_args[0][0]
    assert isinstance(sent_message, str)
    assert "Process these files:" in sent_message
    assert "Contents of" in sent_message
    assert "```" in sent_message
    assert "test content" in sent_message


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
