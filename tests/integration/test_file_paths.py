import os
import platform

import pytest

from promptpal.promptpal import Promptpal, find_existing_files
from promptpal.roles import Role

# Check if running in CI environment
is_ci = os.getenv("CI") is not None


@pytest.mark.integration
@pytest.mark.skipif(is_ci, reason="Skipping integration tests in CI environment.")
def test_find_existing_files_function(tmp_path):
    """Test the find_existing_files function directly with different path formats."""
    # Create test files
    test_file1 = tmp_path / "test1.txt"
    test_file2 = tmp_path / "test2.txt"
    test_file1.write_text("Test content 1")
    test_file2.write_text("Test content 2")

    # Test with absolute paths
    message = f"Process these files: {test_file1.absolute()} and {test_file2.absolute()}"
    found_files = find_existing_files(message)

    # Verify both files were found
    assert len(found_files) == 2
    assert str(test_file1.absolute()) in found_files
    assert str(test_file2.absolute()) in found_files

    # Test with relative paths
    rel_path1 = os.path.relpath(test_file1)
    rel_path2 = os.path.relpath(test_file2)
    message = f"Process these files: {rel_path1} and {rel_path2}"
    found_files = find_existing_files(message)

    # Verify both files were found
    assert len(found_files) == 2
    assert rel_path1 in found_files
    assert rel_path2 in found_files


@pytest.mark.integration
@pytest.mark.skipif(is_ci, reason="Skipping integration tests in CI environment.")
def test_chat_with_file_paths(tmp_path, mocker):
    """Test the chat method with file paths in the message."""
    # Create test files
    test_file1 = tmp_path / "test1.txt"
    test_file2 = tmp_path / "test2.txt"
    test_file1.write_text("Test content 1")
    test_file2.write_text("Test content 2")

    # Mock the genai client
    mock_client = mocker.patch("promptpal.promptpal.genai.Client")
    mock_chat = mock_client.return_value.chats.create
    mock_chat_instance = mock_chat.return_value
    mock_response = mocker.MagicMock()
    mock_response.text = "I've processed the files and found the content: Test content 1 and Test content 2"
    mock_response.usage_metadata.total_token_count = 500
    mock_chat_instance.send_message.return_value = mock_response

    # Mock file upload
    mock_upload = mock_client.return_value.files.upload
    mock_upload.side_effect = ["uploaded_file1", "uploaded_file2"]

    # Initialize Promptpal
    promptpal = Promptpal(load_default_roles=False, vertexai=False)

    # Add a test role
    role = Role(
        name="file_handler",
        description="File Handler",
        system_instruction="You are a file handler. Process the files provided.",
        model="gemini-1.5-flash",
    )
    promptpal.add_roles([role])

    # Test with absolute paths
    message = f"Process these files: {test_file1.absolute()} and {test_file2.absolute()}"
    promptpal.chat("file_handler", message)

    # Verify the files were uploaded
    assert mock_upload.call_count == 2

    # Verify the response
    assert promptpal.get_last_response() is not None
    assert isinstance(promptpal.get_last_response(), str)

    # Reset mocks
    mock_upload.reset_mock()
    mock_upload.side_effect = ["uploaded_file1", "uploaded_file2"]

    # Test with relative paths
    rel_path1 = os.path.relpath(test_file1)
    rel_path2 = os.path.relpath(test_file2)
    message = f"Process these files: {rel_path1} and {rel_path2}"
    promptpal.chat("file_handler", message)

    # Verify the files were uploaded
    assert mock_upload.call_count == 2


@pytest.mark.integration
@pytest.mark.skipif(is_ci, reason="Skipping integration tests in CI environment.")
def test_chat_with_nonexistent_file_paths(mocker):
    """Test the chat method with nonexistent file paths in the message."""
    # Mock the genai client
    mock_client = mocker.patch("promptpal.promptpal.genai.Client")
    mock_chat = mock_client.return_value.chats.create
    mock_chat_instance = mock_chat.return_value
    mock_response = mocker.MagicMock()
    mock_response.text = "I couldn't find the files you mentioned."
    mock_response.usage_metadata.total_token_count = 500
    mock_chat_instance.send_message.return_value = mock_response

    # Initialize Promptpal
    promptpal = Promptpal(load_default_roles=False, vertexai=False)

    # Add a test role
    role = Role(
        name="file_handler",
        description="File Handler",
        system_instruction="You are a file handler. Process the files provided.",
        model="gemini-1.5-flash",
    )
    promptpal.add_roles([role])

    # Test with nonexistent absolute paths
    if platform.system() == "Windows":
        nonexistent_path1 = "C:\\nonexistent\\file1.txt"
        nonexistent_path2 = "D:\\nonexistent\\file2.txt"
    else:
        nonexistent_path1 = "/nonexistent/file1.txt"
        nonexistent_path2 = "/tmp/nonexistent/file2.txt"

    message = f"Process these files: {nonexistent_path1} and {nonexistent_path2}"
    promptpal.chat("file_handler", message)

    # Verify the response
    assert promptpal.get_last_response() is not None
    assert isinstance(promptpal.get_last_response(), str)
