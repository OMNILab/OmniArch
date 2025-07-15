#! /usr/bin/env python
# coding=utf-8
import os
from smartmeeting.lingji_ai import get_nls_token, transcribe_file


def test_token_request():
    """
    Test function to request and validate Aliyun NLS token
    """
    access_key_id = os.getenv("ALIYUN_AK_ID")
    access_key_secret = os.getenv("ALIYUN_AK_SECRET")

    if not access_key_id or not access_key_secret:
        print("Missing required environment variables for token test")
        return None, None

    print("Testing token request...")
    token, expire_time = get_nls_token(access_key_id, access_key_secret)

    if token:
        print(f"✓ Token request successful: {token[:20]}...")
        print(f"  Expires at: {expire_time}")
    else:
        print("✗ Token request failed")

    return token, expire_time


def test_file_transcription():
    """
    Test function to transcribe an audio file
    """
    access_key_id = os.getenv("ALIYUN_AK_ID")
    access_key_secret = os.getenv("ALIYUN_AK_SECRET")
    app_key = os.getenv("NLS_APP_KEY")

    if not all([access_key_id, access_key_secret, app_key]):
        print("Missing required environment variables for transcription test")
        return None

    # Test file link (you can replace this with your own audio file)
    # file_link = "https://gw.alipayobjects.com/os/bmw-prod/0574ee2e-f494-45a5-820f-63aee583045a.wav"
    file_link = "http://116.62.193.164:9380/public/omniarch/sample1_8k_15min.mp4"

    print("Testing file transcription...")
    result = transcribe_file(access_key_id, access_key_secret, app_key, file_link)

    if result:
        print("✓ File transcription successful")
        print(f"  Result: {result}")
    else:
        print("✗ File transcription failed")

    return result


def main():
    """
    Main function to run the tests
    """
    print("=== Testing Aliyun NLS Integration ===")

    # Check environment variables
    required_vars = ["ALIYUN_AK_ID", "ALIYUN_AK_SECRET", "NLS_APP_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print("✗ Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these environment variables before running the test.")
        return

    print("✓ All required environment variables are set")

    # Test token request
    print("\n=== Testing Token Request ===")
    token, expire_time = test_token_request()

    if not token:
        print("Skipping transcription test due to token failure")
        return

    # Test file transcription
    print("\n=== Testing File Transcription ===")
    result = test_file_transcription()

    # Summary
    print("\n=== Test Summary ===")
    if token and result:
        print("✓ All tests passed!")
    elif token:
        print("⚠ Token test passed, but transcription failed")
    else:
        print("✗ Tests failed")


if __name__ == "__main__":
    main()
