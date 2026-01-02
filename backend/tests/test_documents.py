"""
Unit tests for Document Service (S3 and Textract).

Tests presigned URL generation, S3 downloads, and Textract text extraction.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from botocore.exceptions import ClientError
from src.services.documents import (
    generate_upload_url,
    download_from_s3,
    extract_text_from_document,
)


@pytest.mark.asyncio
async def test_generate_upload_url_success():
    """Test successful presigned URL generation."""
    mock_response = {
        "url": "https://s3.amazonaws.com/test-bucket",
        "fields": {
            "key": "uploads/test.pdf",
            "Content-Type": "application/pdf",
        },
    }
    
    mock_s3 = Mock()
    mock_s3.generate_presigned_post = Mock(return_value=mock_response)
    
    with patch("src.services.documents.settings.AWS_S3_BUCKET", "test-bucket"):
        with patch("src.services.documents.boto3.client", return_value=mock_s3):
            result = await generate_upload_url("test.pdf", "application/pdf")
            
            assert result["url"] == "https://s3.amazonaws.com/test-bucket"
            assert "fields" in result
            assert "s3_key" in result
            assert "uploads/" in result["s3_key"]
            assert "test.pdf" in result["s3_key"]
            
            # Verify the API was called correctly
            mock_s3.generate_presigned_post.assert_called_once()
            call_args = mock_s3.generate_presigned_post.call_args[1]
            assert call_args["Fields"]["Content-Type"] == "application/pdf"
            assert call_args["ExpiresIn"] == 900  # 15 minutes


@pytest.mark.asyncio
async def test_generate_upload_url_empty_filename():
    """Test that empty filename raises ValueError."""
    with pytest.raises(ValueError, match="Filename cannot be empty"):
        await generate_upload_url("")
    
    with pytest.raises(ValueError, match="Filename cannot be empty"):
        await generate_upload_url("   ")


@pytest.mark.asyncio
async def test_generate_upload_url_no_bucket():
    """Test that missing bucket configuration raises ValueError."""
    with patch("src.services.documents.settings.AWS_S3_BUCKET", ""):
        with pytest.raises(ValueError, match="AWS_S3_BUCKET not configured"):
            await generate_upload_url("test.pdf")


@pytest.mark.asyncio
async def test_generate_upload_url_api_error():
    """Test error handling when S3 API fails."""
    mock_s3 = Mock()
    error_response = {
        "Error": {
            "Code": "AccessDenied",
            "Message": "Access denied",
        }
    }
    mock_s3.generate_presigned_post = Mock(
        side_effect=ClientError(error_response, "GeneratePresignedPost")
    )
    
    with patch("src.services.documents.settings.AWS_S3_BUCKET", "test-bucket"):
        with patch("src.services.documents.boto3.client", return_value=mock_s3):
            with pytest.raises(RuntimeError, match="Failed to generate upload URL"):
                await generate_upload_url("test.pdf")


@pytest.mark.asyncio
async def test_download_from_s3_success():
    """Test successful S3 download."""
    test_content = b"Test file content"
    
    mock_response = {
        "Body": Mock(read=Mock(return_value=test_content))
    }
    
    mock_s3 = Mock()
    mock_s3.get_object = Mock(return_value=mock_response)
    
    with patch("src.services.documents.settings.AWS_S3_BUCKET", "test-bucket"):
        with patch("src.services.documents.boto3.client", return_value=mock_s3):
            result = await download_from_s3("uploads/test.pdf")
            
            assert result == test_content
            
            # Verify the API was called correctly
            mock_s3.get_object.assert_called_once()
            call_args = mock_s3.get_object.call_args[1]
            assert call_args["Key"] == "uploads/test.pdf"


@pytest.mark.asyncio
async def test_download_from_s3_empty_key():
    """Test that empty S3 key raises ValueError."""
    with pytest.raises(ValueError, match="S3 key cannot be empty"):
        await download_from_s3("")
    
    with pytest.raises(ValueError, match="S3 key cannot be empty"):
        await download_from_s3("   ")


@pytest.mark.asyncio
async def test_download_from_s3_no_bucket():
    """Test that missing bucket configuration raises ValueError."""
    with patch("src.services.documents.settings.AWS_S3_BUCKET", ""):
        with pytest.raises(ValueError, match="AWS_S3_BUCKET not configured"):
            await download_from_s3("uploads/test.pdf")


@pytest.mark.asyncio
async def test_download_from_s3_not_found():
    """Test error handling when file not found in S3."""
    mock_s3 = Mock()
    error_response = {
        "Error": {
            "Code": "NoSuchKey",
            "Message": "The specified key does not exist",
        }
    }
    mock_s3.get_object = Mock(
        side_effect=ClientError(error_response, "GetObject")
    )
    
    with patch("src.services.documents.settings.AWS_S3_BUCKET", "test-bucket"):
        with patch("src.services.documents.boto3.client", return_value=mock_s3):
            with pytest.raises(RuntimeError, match="S3 download failed"):
                await download_from_s3("uploads/nonexistent.pdf")


@pytest.mark.asyncio
async def test_extract_text_success():
    """Test successful text extraction with Textract."""
    test_bytes = b"fake pdf content"
    
    mock_response = {
        "Blocks": [
            {"BlockType": "LINE", "Text": "First line of text"},
            {"BlockType": "LINE", "Text": "Second line of text"},
            {"BlockType": "WORD", "Text": "ignored"},  # Should be ignored
        ]
    }
    
    mock_textract = Mock()
    mock_textract.detect_document_text = Mock(return_value=mock_response)
    
    with patch("src.services.documents.boto3.client", return_value=mock_textract):
        result = await extract_text_from_document(test_bytes)
        
        assert result == "First line of text\nSecond line of text"
        
        # Verify the API was called correctly
        mock_textract.detect_document_text.assert_called_once()
        call_args = mock_textract.detect_document_text.call_args[1]
        assert call_args["Document"]["Bytes"] == test_bytes


@pytest.mark.asyncio
async def test_extract_text_empty_bytes():
    """Test that empty file bytes raises ValueError."""
    with pytest.raises(ValueError, match="File bytes cannot be empty"):
        await extract_text_from_document(b"")


@pytest.mark.asyncio
async def test_extract_text_file_too_large():
    """Test that file exceeding size limit raises ValueError."""
    large_file = b"a" * (5242881)  # Exceed 5MB limit
    
    with pytest.raises(ValueError, match="File too large"):
        await extract_text_from_document(large_file)


@pytest.mark.asyncio
async def test_extract_text_api_error():
    """Test error handling when Textract API fails."""
    test_bytes = b"fake pdf content"
    
    mock_textract = Mock()
    error_response = {
        "Error": {
            "Code": "InvalidParameterException",
            "Message": "Invalid document",
        }
    }
    mock_textract.detect_document_text = Mock(
        side_effect=ClientError(error_response, "DetectDocumentText")
    )
    
    with patch("src.services.documents.boto3.client", return_value=mock_textract):
        with pytest.raises(RuntimeError, match="Textract failed"):
            await extract_text_from_document(test_bytes)


@pytest.mark.asyncio
async def test_extract_text_no_blocks():
    """Test text extraction with no text blocks."""
    test_bytes = b"fake pdf content"
    
    mock_response = {"Blocks": []}
    
    mock_textract = Mock()
    mock_textract.detect_document_text = Mock(return_value=mock_response)
    
    with patch("src.services.documents.boto3.client", return_value=mock_textract):
        result = await extract_text_from_document(test_bytes)
        
        assert result == ""


@pytest.mark.asyncio
async def test_generate_upload_url_custom_expiration():
    """Test presigned URL generation with custom expiration."""
    mock_response = {
        "url": "https://s3.amazonaws.com/test-bucket",
        "fields": {"key": "uploads/test.pdf"},
    }
    
    mock_s3 = Mock()
    mock_s3.generate_presigned_post = Mock(return_value=mock_response)
    
    with patch("src.services.documents.settings.AWS_S3_BUCKET", "test-bucket"):
        with patch("src.services.documents.boto3.client", return_value=mock_s3):
            await generate_upload_url("test.pdf", expiration=1800)  # 30 minutes
            
            call_args = mock_s3.generate_presigned_post.call_args[1]
            assert call_args["ExpiresIn"] == 1800


@pytest.mark.asyncio
async def test_generate_upload_url_unexpected_error():
    """Test error handling for unexpected exceptions."""
    mock_s3 = Mock()
    mock_s3.generate_presigned_post = Mock(side_effect=Exception("Unexpected error"))
    
    with patch("src.services.documents.settings.AWS_S3_BUCKET", "test-bucket"):
        with patch("src.services.documents.boto3.client", return_value=mock_s3):
            with pytest.raises(RuntimeError, match="Upload URL generation error"):
                await generate_upload_url("test.pdf")
