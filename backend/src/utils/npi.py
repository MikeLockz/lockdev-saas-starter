"""
NPI (National Provider Identifier) validation utilities.

The NPI is a 10-digit number that uses the Luhn algorithm for validation.
The check digit (last digit) is calculated against the prefix 80840 + first 9 digits.
"""

import re


def validate_npi(npi: str) -> bool:
    """
    Validate an NPI number using the Luhn algorithm.
    
    The NPI uses a modified Luhn-10 algorithm where:
    1. Prefix 80840 is prepended to the first 9 digits
    2. Standard Luhn check is applied
    3. The check digit (10th digit) validates the result
    
    Args:
        npi: The NPI number to validate (should be 10 digits)
        
    Returns:
        True if valid, False otherwise
    """
    # Check format: must be exactly 10 digits
    if not npi or not re.match(r"^\d{10}$", npi):
        return False
    
    # The 80840 prefix is used for Healthcare ID validation
    # It represents "80" (required prefix for US) + "840" (country code for USA)
    prefixed = "80840" + npi
    
    # Apply Luhn algorithm
    return _luhn_check(prefixed)


def _luhn_check(number_string: str) -> bool:
    """
    Standard Luhn algorithm implementation.
    
    Args:
        number_string: String of digits to validate
        
    Returns:
        True if the Luhn checksum is valid (sum % 10 == 0)
    """
    digits = [int(d) for d in number_string]
    
    # Process from right to left
    # Double every second digit (from the right)
    for i in range(len(digits) - 2, -1, -2):
        doubled = digits[i] * 2
        # If doubling results in a number > 9, subtract 9 (equivalent to sum of digits)
        if doubled > 9:
            doubled -= 9
        digits[i] = doubled
    
    # Sum all digits and check if divisible by 10
    return sum(digits) % 10 == 0


def format_npi(npi: str) -> str:
    """
    Format an NPI number for display.
    Currently just returns the NPI as-is (10 digits, no separators).
    
    Args:
        npi: The NPI number
        
    Returns:
        Formatted NPI string
    """
    # NPIs are typically displayed as a single 10-digit number
    return npi.strip() if npi else ""
