"""Tests for NPI validation utility."""

import pytest
from src.utils.npi import validate_npi, _luhn_check


class TestLuhnCheck:
    """Test the Luhn algorithm implementation."""
    
    def test_valid_luhn(self):
        """Test with known valid Luhn numbers."""
        # Standard credit card test number
        assert _luhn_check("4532015112830366") is True
        
    def test_invalid_luhn(self):
        """Test with invalid Luhn number."""
        assert _luhn_check("1234567890") is False


class TestValidateNPI:
    """Test NPI validation."""
    
    def test_valid_npi(self):
        """Test with valid NPI numbers."""
        # These are synthetic valid NPIs that pass Luhn check
        # NPI 1234567893 with 80840 prefix: 808401234567893
        assert validate_npi("1234567893") is True
    
    def test_invalid_npi_checksum(self):
        """Test NPI with invalid checksum."""
        # Same digits but wrong check digit
        assert validate_npi("1234567890") is False
        assert validate_npi("1234567891") is False
        assert validate_npi("1234567892") is False
    
    def test_invalid_npi_too_short(self):
        """Test NPI with less than 10 digits."""
        assert validate_npi("123456789") is False
        assert validate_npi("12345") is False
        assert validate_npi("1") is False
    
    def test_invalid_npi_too_long(self):
        """Test NPI with more than 10 digits."""
        assert validate_npi("12345678901") is False
        assert validate_npi("123456789012345") is False
    
    def test_invalid_npi_contains_letters(self):
        """Test NPI containing non-digit characters."""
        assert validate_npi("123456789A") is False
        assert validate_npi("ABCDEFGHIJ") is False
        assert validate_npi("12-34-5678") is False
    
    def test_invalid_npi_empty(self):
        """Test empty NPI."""
        assert validate_npi("") is False
        assert validate_npi(None) is False  # type: ignore
    
    def test_invalid_npi_whitespace(self):
        """Test NPI with whitespace."""
        assert validate_npi(" 1234567893") is False
        assert validate_npi("1234567893 ") is False
        assert validate_npi("123 456 7893") is False
