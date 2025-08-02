"""Tests for QR code reader functionality."""

from unittest.mock import Mock, patch

import numpy as np
import pytest

from qr_code_reader.qr_reader import (
    InvalidImageError,
    QRCodeError,
    QRCodeNotFoundError,
    _decode_qr_code,
    read_qr_code,
    validate_image_safety,
)


class TestQRCodeReader:
    """Test suite for QR code reader."""

    @pytest.mark.asyncio
    async def test_read_qr_code_no_input(self):
        """Test that ValueError is raised when no input is provided."""
        with pytest.raises(
            ValueError, match="Either image_path or image_data must be provided"
        ):
            await read_qr_code()

    @pytest.mark.asyncio
    @patch("qr_code_reader.qr_reader._load_image_from_path")
    @patch("qr_code_reader.qr_reader._decode_qr_code")
    async def test_read_qr_code_from_path_success(self, mock_decode, mock_load):
        """Test successful QR code reading from file path."""
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_load.return_value = mock_image
        mock_decode.return_value = "https://example.com"

        result = await read_qr_code(image_path="/fake/path.jpg")

        assert result == "https://example.com"
        mock_load.assert_called_once_with("/fake/path.jpg")
        mock_decode.assert_called_once_with(mock_image)

    @pytest.mark.asyncio
    @patch("qr_code_reader.qr_reader._load_image_from_base64")
    @patch("qr_code_reader.qr_reader._decode_qr_code")
    async def test_read_qr_code_from_base64_success(self, mock_decode, mock_load):
        """Test successful QR code reading from base64 data."""
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_load.return_value = mock_image
        mock_decode.return_value = "test_data"

        result = await read_qr_code(
            image_data="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        )

        assert result == "test_data"
        mock_decode.assert_called_once_with(mock_image)

    @pytest.mark.asyncio
    @patch("qr_code_reader.qr_reader._load_image_from_path")
    @patch("qr_code_reader.qr_reader._decode_qr_code")
    async def test_read_qr_code_not_found(self, mock_decode, mock_load):
        """Test QRCodeNotFoundError when no QR code is found."""
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_load.return_value = mock_image
        mock_decode.return_value = None

        with pytest.raises(QRCodeNotFoundError, match="No QR code found in the image"):
            await read_qr_code(image_path="/fake/path.jpg")

    @pytest.mark.asyncio
    @patch("qr_code_reader.qr_reader._load_image_from_path")
    async def test_read_qr_code_invalid_image(self, mock_load):
        """Test InvalidImageError when image processing fails."""
        mock_load.side_effect = Exception("Invalid image")

        with pytest.raises(InvalidImageError, match="Failed to process image"):
            await read_qr_code(image_path="/fake/path.jpg")

    def test_decode_qr_code_success(self):
        """Test successful QR code decoding."""
        # Create a mock image
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)

        with patch("cv2.QRCodeDetector") as mock_detector_class:
            mock_detector = Mock()
            mock_detector_class.return_value = mock_detector

            # Mock successful detection
            mock_detector.detectAndDecodeMulti.return_value = (
                True,
                ["https://example.com"],
                None,
                None,
            )

            result = _decode_qr_code(mock_image)
            assert result == "https://example.com"

    def test_decode_qr_code_fallback_to_single(self):
        """Test fallback to single decode when multi-decode fails."""
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)

        with patch("cv2.QRCodeDetector") as mock_detector_class:
            mock_detector = Mock()
            mock_detector_class.return_value = mock_detector

            # Mock multi-decode failure and single-decode success
            mock_detector.detectAndDecodeMulti.return_value = (False, [], None, None)
            mock_detector.detectAndDecode.return_value = (True, "test_data", None)

            result = _decode_qr_code(mock_image)
            assert result == "test_data"

    def test_decode_qr_code_not_found(self):
        """Test when no QR code is found in any attempt."""
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)

        with (
            patch("cv2.QRCodeDetector") as mock_detector_class,
            patch("cv2.cvtColor") as mock_cvt,
            patch("cv2.GaussianBlur") as mock_blur,
            patch("cv2.threshold") as mock_thresh,
        ):
            mock_detector = Mock()
            mock_detector_class.return_value = mock_detector

            # Mock all detection attempts to fail
            mock_detector.detectAndDecodeMulti.return_value = (False, [], None, None)
            mock_detector.detectAndDecode.return_value = (False, "", None)

            mock_cvt.return_value = mock_image
            mock_blur.return_value = mock_image
            mock_thresh.return_value = (None, mock_image)

            result = _decode_qr_code(mock_image)
            assert result is None

    @patch("qr_code_reader.qr_reader.Path")
    @patch("qr_code_reader.qr_reader.Image")
    def test_validate_image_safety_success(self, mock_image_class, mock_path_class):
        """Test successful image safety validation."""
        # Mock Path object
        mock_path = Mock()
        mock_path.stat.return_value.st_size = 1000000  # 1MB
        mock_path_class.return_value = mock_path

        # Mock PIL Image
        mock_img = Mock()
        mock_img.width = 1920
        mock_img.height = 1080
        mock_image_class.open.return_value.__enter__.return_value = mock_img

        result = validate_image_safety("/fake/path.jpg")
        assert result is True

    @patch("qr_code_reader.qr_reader.Path")
    def test_validate_image_safety_too_large(self, mock_path_class):
        """Test image safety validation with file too large."""
        mock_path = Mock()
        mock_path.stat.return_value.st_size = 60 * 1024 * 1024  # 60MB
        mock_path_class.return_value = mock_path

        result = validate_image_safety("/fake/path.jpg")
        assert result is False

    @patch("qr_code_reader.qr_reader.Path")
    @patch("qr_code_reader.qr_reader.Image")
    def test_validate_image_safety_dimensions_too_large(
        self, mock_image_class, mock_path_class
    ):
        """Test image safety validation with dimensions too large."""
        mock_path = Mock()
        mock_path.stat.return_value.st_size = 1000000  # 1MB
        mock_path_class.return_value = mock_path

        mock_img = Mock()
        mock_img.width = 15000
        mock_img.height = 15000
        mock_image_class.open.return_value.__enter__.return_value = mock_img

        result = validate_image_safety("/fake/path.jpg")
        assert result is False


class TestQRCodeExceptions:
    """Test QR code custom exceptions."""

    def test_qr_code_error_inheritance(self):
        """Test that QRCodeError inherits from Exception."""
        assert issubclass(QRCodeError, Exception)

    def test_qr_code_not_found_error_inheritance(self):
        """Test that QRCodeNotFoundError inherits from QRCodeError."""
        assert issubclass(QRCodeNotFoundError, QRCodeError)

    def test_invalid_image_error_inheritance(self):
        """Test that InvalidImageError inherits from QRCodeError."""
        assert issubclass(InvalidImageError, QRCodeError)
