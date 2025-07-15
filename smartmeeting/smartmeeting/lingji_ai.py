# -*- coding: utf8 -*-
# 阿里灵杰AI开放服务
import time
import json
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException


def get_nls_token(ak_id, ak_secret):
    """
    Test function to request and validate Aliyun NLS token
    """
    # Create AcsClient instance
    client = AcsClient(ak_id, ak_secret, "cn-shanghai")

    # Create request and set parameters
    request = CommonRequest()
    request.set_method("POST")
    request.set_domain("nls-meta.cn-shanghai.aliyuncs.com")
    request.set_version("2019-02-28")
    request.set_action_name("CreateToken")

    try:
        response = client.do_action_with_exception(request)
        print("Token request response:", response)

        response_json = json.loads(response)
        if "Token" in response_json and "Id" in response_json["Token"]:
            token = response_json["Token"]["Id"]
            expire_time = response_json["Token"]["ExpireTime"]
            print(f"Token: {token}")
            print(f"Expire Time: {expire_time}")
            return token, expire_time
        else:
            print("Invalid token response format")
            return None, None
    except Exception as e:
        print(f"Error requesting token: {e}")
        return None, None


def transcribe_file(ak_id, ak_secret, app_key, file_link):
    """
    Perform file transcription using Aliyun NLS service

    Args:
        ak_id (str): Aliyun Access Key ID
        ak_secret (str): Aliyun Access Key Secret
        app_key (str): NLS App Key
        file_link (str): URL of the audio file to transcribe

    Returns:
        dict: Transcription result or None if failed
    """
    # Constants
    REGION_ID = "cn-shanghai"
    PRODUCT = "nls-filetrans"
    DOMAIN = "filetrans.cn-shanghai.aliyuncs.com"
    API_VERSION = "2018-08-17"
    POST_REQUEST_ACTION = "SubmitTask"
    GET_REQUEST_ACTION = "GetTaskResult"

    # Request parameters
    KEY_APP_KEY = "appkey"
    KEY_FILE_LINK = "file_link"
    KEY_VERSION = "version"
    KEY_ENABLE_WORDS = "enable_words"
    KEY_AUTO_SPLIT = "auto_split"

    # Response parameters
    KEY_TASK = "Task"
    KEY_TASK_ID = "TaskId"
    KEY_STATUS_TEXT = "StatusText"
    KEY_RESULT = "Result"

    # Status values
    STATUS_SUCCESS = "SUCCESS"
    STATUS_RUNNING = "RUNNING"
    STATUS_QUEUEING = "QUEUEING"

    # Create AcsClient instance
    client = AcsClient(ak_id, ak_secret, REGION_ID)

    # Submit transcription request
    post_request = CommonRequest()
    post_request.set_domain(DOMAIN)
    post_request.set_version(API_VERSION)
    post_request.set_product(PRODUCT)
    post_request.set_action_name(POST_REQUEST_ACTION)
    post_request.set_method("POST")

    # Configure task parameters
    # Use version 4.0 for new integrations, set enable_words to False by default
    task = {
        KEY_APP_KEY: app_key,
        KEY_FILE_LINK: file_link,
        KEY_VERSION: "4.0",
        KEY_ENABLE_WORDS: False,
    }

    # Uncomment to enable auto split for multi-speaker scenarios
    # task[KEY_AUTO_SPLIT] = True

    task_json = json.dumps(task)
    print(f"Submitting task: {task_json}")
    post_request.add_body_params(KEY_TASK, task_json)

    task_id = ""
    try:
        post_response = client.do_action_with_exception(post_request)
        post_response_json = json.loads(post_response)
        print(f"Submit response: {post_response_json}")

        status_text = post_response_json[KEY_STATUS_TEXT]
        if status_text == STATUS_SUCCESS:
            print("File transcription request submitted successfully!")
            task_id = post_response_json[KEY_TASK_ID]
        else:
            print(f"File transcription request failed: {status_text}")
            return None
    except ServerException as e:
        print(f"Server error: {e}")
        return None
    except ClientException as e:
        print(f"Client error: {e}")
        return None

    if not task_id:
        print("No task ID received")
        return None

    # Create request to get task result
    get_request = CommonRequest()
    get_request.set_domain(DOMAIN)
    get_request.set_version(API_VERSION)
    get_request.set_product(PRODUCT)
    get_request.set_action_name(GET_REQUEST_ACTION)
    get_request.set_method("GET")
    get_request.add_query_param(KEY_TASK_ID, task_id)

    # Poll for results
    print(f"Polling for results with task ID: {task_id}")
    status_text = ""
    max_attempts = 60  # Maximum 10 minutes (60 * 10 seconds)
    attempt = 0

    while attempt < max_attempts:
        try:
            get_response = client.do_action_with_exception(get_request)
            get_response_json = json.loads(get_response)
            print(f"Poll response (attempt {attempt + 1}): {get_response_json}")

            status_text = get_response_json[KEY_STATUS_TEXT]
            if status_text == STATUS_RUNNING or status_text == STATUS_QUEUEING:
                # Continue polling
                time.sleep(10)
                attempt += 1
            else:
                # Exit polling
                break
        except ServerException as e:
            print(f"Server error during polling: {e}")
            return None
        except ClientException as e:
            print(f"Client error during polling: {e}")
            return None

    if status_text == STATUS_SUCCESS:
        print("File transcription completed successfully!")
        return get_response_json.get(KEY_RESULT)
    else:
        print(f"File transcription failed with status: {status_text}")
        return None
