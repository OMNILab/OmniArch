"""
Speech Transcription Tool
Contains functions for extracting transcription text from speech recognition results
"""

import streamlit as st


def extract_transcription_text(result):
    """
    Extract transcription text from the lingji_ai result.

    Args:
        result: The result from transcribe_file function

    Returns:
        str: Extracted transcription text or None if extraction fails
    """
    try:
        # The result structure from lingji_ai contains sentences with text
        if isinstance(result, dict) and "Sentences" in result:
            sentences = result["Sentences"]
            if isinstance(sentences, list):
                # Extract text from each sentence, avoiding duplicates
                # Since there are duplicate entries with different ChannelId,
                # we'll use a set to store unique texts
                unique_texts = set()
                for sentence in sentences:
                    if isinstance(sentence, dict) and "Text" in sentence:
                        text = sentence["Text"].strip()
                        if text:  # Only add non-empty text
                            unique_texts.add(text)

                # Convert set back to list and join
                if unique_texts:
                    transcription_parts = sorted(list(unique_texts))
                    return " ".join(transcription_parts)

        # If the structure is different, try to find text in the result
        if isinstance(result, dict):
            # Look for common transcription result keys
            for key in ["text", "transcription", "content", "result"]:
                if key in result:
                    return str(result[key])

            # If no direct text found, try to extract from nested structure
            import json

            result_str = json.dumps(result, ensure_ascii=False)
            # This is a fallback - return the full result as string
            return result_str

        # If result is already a string, return it
        if isinstance(result, str):
            return result

    except Exception as e:
        st.error(f"提取转写文本时出错: {str(e)}")
        return None

    return None
