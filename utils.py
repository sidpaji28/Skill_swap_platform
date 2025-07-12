"""
Utility helper functions for common operations.
"""

import re
import html
from typing import Union, List, Dict, Any
from datetime import datetime, time


def format_availability(availability_data: Union[Dict, List]) -> str:
    """
    Format availability data into a human-readable string.
    
    Args:
        availability_data: Dictionary with days/times or list of time slots
        
    Returns:
        Formatted availability string
        
    Examples:
        >>> format_availability({'monday': ['9:00-17:00'], 'tuesday': ['9:00-17:00']})
        'Monday: 9:00-17:00, Tuesday: 9:00-17:00'
        
        >>> format_availability(['9:00-12:00', '14:00-17:00'])
        '9:00-12:00, 14:00-17:00'
    """
    if isinstance(availability_data, dict):
        formatted_slots = []
        for day, times in availability_data.items():
            if times:
                day_formatted = day.capitalize()
                times_str = ', '.join(times) if isinstance(times, list) else str(times)
                formatted_slots.append(f"{day_formatted}: {times_str}")
        return ', '.join(formatted_slots)
    
    elif isinstance(availability_data, list):
        return ', '.join(str(slot) for slot in availability_data)
    
    else:
        return str(availability_data)


def validate_email(email: str) -> bool:
    """
    Validate email address format using regex.
    
    Args:
        email: Email address string to validate
        
    Returns:
        True if email format is valid, False otherwise
        
    Examples:
        >>> validate_email('user@example.com')
        True
        
        >>> validate_email('invalid-email')
        False
    """
    if not isinstance(email, str):
        return False
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Check if email matches pattern and is reasonable length
    if len(email) > 254:  # RFC 5321 limit
        return False
    
    return bool(re.match(pattern, email.strip()))


def sanitize_input(user_input: str, max_length: int = 1000) -> str:
    """
    Sanitize user input by removing/escaping potentially harmful content.
    
    Args:
        user_input: Raw user input string
        max_length: Maximum allowed length for input
        
    Returns:
        Sanitized input string
        
    Examples:
        >>> sanitize_input('<script>alert("xss")</script>Hello')
        '&lt;script&gt;alert("xss")&lt;/script&gt;Hello'
        
        >>> sanitize_input('  Normal text  ')
        'Normal text'
    """
    if not isinstance(user_input, str):
        return ""
    
    # Trim whitespace
    sanitized = user_input.strip()
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    # Escape HTML entities to prevent XSS
    sanitized = html.escape(sanitized)
    
    # Remove null bytes and other control characters
    sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\n\r\t')
    
    return sanitized


# Additional utility functions that might be useful

def format_phone_number(phone: str) -> str:
    """
    Format phone number to standard format.
    
    Args:
        phone: Raw phone number string
        
    Returns:
        Formatted phone number
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Format based on length
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    else:
        return phone  # Return original if can't format


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length with optional suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def is_business_hours(check_time: datetime = None) -> bool:
    """
    Check if given time falls within business hours (9 AM - 5 PM, Mon-Fri).
    
    Args:
        check_time: Time to check (defaults to current time)
        
    Returns:
        True if within business hours, False otherwise
    """
    if check_time is None:
        check_time = datetime.now()
    
    # Check if weekday (Monday = 0, Sunday = 6)
    if check_time.weekday() >= 5:  # Saturday or Sunday
        return False
    
    # Check if within 9 AM - 5 PM
    business_start = time(9, 0)
    business_end = time(17, 0)
    current_time = check_time.time()
    
    return business_start <= current_time <= business_end