"""
Text Processing Utilities
Contains utility functions for text processing, especially for handling
both English and Chinese punctuation marks in text splitting operations.
"""

import re
from typing import List, Union


def split_text_by_punctuation(text: str, remove_empty: bool = True) -> List[str]:
    """
    Split text by both English and Chinese punctuation marks.

    This function handles the following separators:
    - English: semicolon (;)
    - Chinese: semicolon (；), period (。)

    Args:
        text (str): The text to split
        remove_empty (bool): Whether to remove empty strings from the result

    Returns:
        List[str]: List of split text items

    Examples:
        >>> split_text_by_punctuation("决定A;决定B。决定C，决定D")
        ['决定A', '决定B', '决定C', '决定D']

        >>> split_text_by_punctuation("Action A; Action B. Action C, Action D")
        ['Action A', 'Action B', 'Action C', 'Action D']
    """
    if not text or not isinstance(text, str):
        return []

    # Define separators: English and Chinese punctuation marks
    separators = [
        ";",  # English semicolon
        "；",  # Chinese semicolon
        "。",  # Chinese period
    ]

    # Create a regex pattern that matches any of the separators
    # We use positive lookahead and lookbehind to keep the separators
    # This allows us to split on multiple consecutive separators
    pattern = "|".join(re.escape(sep) for sep in separators)

    # Split the text and clean up
    parts = re.split(pattern, text)

    if remove_empty:
        # Remove empty strings and strip whitespace
        parts = [part.strip() for part in parts if part.strip()]

    return parts


def normalize_text_separators(text: str, target_separator: str = ";") -> str:
    """
    Normalize text by replacing various separators with a target separator.

    This function is useful for standardizing text that may contain
    mixed punctuation marks before splitting.

    Args:
        text (str): The text to normalize
        target_separator (str): The separator to use for normalization

    Returns:
        str: Normalized text with consistent separators

    Examples:
        >>> normalize_text_separators("决定A;决定B。决定C，决定D")
        '决定A;决定B;决定C;决定D'
    """
    if not text or not isinstance(text, str):
        return text

    # Define separators to replace
    separators = [
        ";",  # English semicolon
        "；",  # Chinese semicolon
        ".",  # English period
        "。",  # Chinese period
    ]

    # Replace all separators with the target separator
    normalized = text
    for sep in separators:
        if sep != target_separator:
            normalized = normalized.replace(sep, target_separator)

    # Clean up multiple consecutive separators
    normalized = re.sub(f"{re.escape(target_separator)}+", target_separator, normalized)

    return normalized.strip()


def extract_list_from_text(
    text: Union[str, List], default_value: str = "无"
) -> List[str]:
    """
    Extract a list from text that may be a string with separators or already a list.

    This function handles the common case where data might be stored as:
    - A semicolon-separated string: "item1;item2;item3"
    - A list: ["item1", "item2", "item3"]
    - Empty or None values

    Args:
        text (Union[str, List]): The text or list to process
        default_value (str): Default value to return if text is empty or invalid

    Returns:
        List[str]: List of items

    Examples:
        >>> extract_list_from_text("决定A;决定B。决定C")
        ['决定A', '决定B', '决定C']

        >>> extract_list_from_text(["决定A", "决定B", "决定C"])
        ['决定A', '决定B', '决定C']

        >>> extract_list_from_text("")
        ['无']

        >>> extract_list_from_text(None)
        ['无']
    """
    if text is None:
        return [default_value]

    if isinstance(text, list):
        # If it's already a list, clean it up
        items = [str(item).strip() for item in text if str(item).strip()]
        return items if items else [default_value]

    if isinstance(text, str):
        text = text.strip()
        if not text or text == default_value:
            return [default_value]

        # Split by punctuation marks
        items = split_text_by_punctuation(text)
        return items if items else [default_value]

    # For other types, convert to string and process
    return extract_list_from_text(str(text), default_value)


def format_list_for_display(items: List[str], numbered: bool = True) -> str:
    """
    Format a list of items for display in markdown.

    Args:
        items (List[str]): List of items to format
        numbered (bool): Whether to use numbered (1. 2. 3.) or bullet points (• • •)

    Returns:
        str: Formatted markdown string

    Examples:
        >>> format_list_for_display(["决定A", "决定B", "决定C"])
        '1. 决定A\n2. 决定B\n3. 决定C'

        >>> format_list_for_display(["决定A", "决定B", "决定C"], numbered=False)
        '• 决定A\n• 决定B\n• 决定C'
    """
    if not items:
        return ""

    if numbered:
        return "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))
    else:
        return "\n".join(f"• {item}" for item in items)
