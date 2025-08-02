"""Basic tests for the qr_code_reader package."""

import qr_code_reader


def test_version():
    """Test that version is defined."""
    assert hasattr(qr_code_reader, "__version__")
    assert isinstance(qr_code_reader.__version__, str)
    assert qr_code_reader.__version__ == "0.1.0"


def test_package_import():
    """Test that the package can be imported."""
    assert qr_code_reader is not None
