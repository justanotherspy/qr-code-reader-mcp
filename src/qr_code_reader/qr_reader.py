"""QR Code reading functionality using OpenCV."""

import base64
import logging
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


class QRCodeError(Exception):
    """Base exception for QR code related errors."""

    pass


class QRCodeNotFoundError(QRCodeError):
    """Raised when no QR code is found in the image."""

    pass


class InvalidImageError(QRCodeError):
    """Raised when the image is invalid or cannot be processed."""

    pass


async def read_qr_code(
    image_path: str | None = None,
    image_data: str | None = None,
) -> str:
    """
    Read and decode QR code from an image.

    Args:
        image_path: Path to the image file
        image_data: Base64 encoded image data

    Returns:
        Decoded QR code string

    Raises:
        QRCodeNotFoundError: When no QR code is found
        InvalidImageError: When image cannot be processed
        ValueError: When neither image_path nor image_data is provided
    """
    if not image_path and not image_data:
        raise ValueError("Either image_path or image_data must be provided")

    try:
        # Load image
        if image_path:
            image = _load_image_from_path(image_path)
        else:
            assert image_data is not None  # Type checker hint
            image = _load_image_from_base64(image_data)

        # Decode QR code
        result = _decode_qr_code(image)

        if not result:
            raise QRCodeNotFoundError("No QR code found in the image")

        logger.info(f"Successfully decoded QR code: {result[:50]}...")
        return result

    except QRCodeNotFoundError:
        # Re-raise QR code not found errors as-is
        raise
    except (cv2.error, Exception) as e:
        logger.error(f"Error processing image: {e}")
        raise InvalidImageError(f"Failed to process image: {str(e)}") from e


def _load_image_from_path(image_path: str) -> np.ndarray:
    """
    Load image from file path.

    Args:
        image_path: Path to the image file

    Returns:
        OpenCV image array

    Raises:
        InvalidImageError: When image cannot be loaded
    """
    # Validate file path
    path = Path(image_path)
    if not path.exists():
        raise InvalidImageError(f"Image file not found: {image_path}")

    if not path.is_file():
        raise InvalidImageError(f"Path is not a file: {image_path}")

    # Check file extension
    valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
    if path.suffix.lower() not in valid_extensions:
        raise InvalidImageError(f"Unsupported image format: {path.suffix}")

    # Load image
    image = cv2.imread(str(path))
    if image is None:
        raise InvalidImageError(f"Failed to load image: {image_path}")

    return image


def _load_image_from_base64(image_data: str) -> np.ndarray:
    """
    Load image from base64 encoded data.

    Args:
        image_data: Base64 encoded image data

    Returns:
        OpenCV image array

    Raises:
        InvalidImageError: When image cannot be decoded
    """
    try:
        # Remove data URL prefix if present
        if image_data.startswith("data:"):
            image_data = image_data.split(",", 1)[1]

        # Decode base64
        image_bytes = base64.b64decode(image_data)

        # Convert to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)

        # Decode image
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            raise InvalidImageError("Failed to decode base64 image data")

        return image

    except Exception as e:
        raise InvalidImageError(f"Failed to process base64 image data: {str(e)}") from e


def _decode_qr_code(image: np.ndarray) -> str | None:
    """
    Decode QR code from OpenCV image.

    Args:
        image: OpenCV image array

    Returns:
        Decoded QR code string or None if not found
    """
    # Initialize QR code detector
    detector = cv2.QRCodeDetector()

    # Try to decode QR code
    retval, decoded_info, points, _ = detector.detectAndDecodeMulti(image)

    if retval and decoded_info:
        # Return the first valid decoded result
        for info in decoded_info:
            if info:  # Skip empty strings
                return info

    # If multi-decode fails, try single decode
    retval, decoded_info, points = detector.detectAndDecode(image)  # type: ignore

    if retval and decoded_info:
        return str(decoded_info)

    # Try with grayscale conversion
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    retval, decoded_info, _ = detector.detectAndDecode(gray)  # type: ignore

    if retval and decoded_info:
        return str(decoded_info)

    # Try with different preprocessing
    # Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    retval, decoded_info, _ = detector.detectAndDecode(blurred)  # type: ignore

    if retval and decoded_info:
        return str(decoded_info)

    # Try with thresholding
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    retval, decoded_info, _ = detector.detectAndDecode(thresh)  # type: ignore

    if retval and decoded_info:
        return str(decoded_info)

    return None


def validate_image_safety(image_path: str) -> bool:
    """
    Validate image file for basic safety checks.

    Args:
        image_path: Path to the image file

    Returns:
        True if image appears safe to process
    """
    try:
        path = Path(image_path)

        # Check file size (limit to 50MB)
        if path.stat().st_size > 50 * 1024 * 1024:
            logger.warning(f"Image file too large: {path.stat().st_size} bytes")
            return False

        # Try to open with PIL for additional validation
        with Image.open(path) as img:
            # Check image dimensions (limit to 10000x10000)
            if img.width > 10000 or img.height > 10000:
                logger.warning(f"Image dimensions too large: {img.width}x{img.height}")
                return False

        return True

    except Exception as e:
        logger.error(f"Image validation failed: {e}")
        return False
