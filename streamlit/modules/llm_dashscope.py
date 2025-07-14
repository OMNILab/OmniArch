from pandasai.llm.openai import OpenAI
import openai


class DashScopeOpenAI(OpenAI):
    """Custom OpenAI class for DashScope's Qwen models"""

    _supported_chat_models = [
        "qwen-plus",
        "qwen-turbo",
        "qwen-max",
        # Add other Qwen models as needed from DashScope documentation
    ]

    def __init__(self, api_token: str, model: str = "qwen-plus", **kwargs):
        """
        Initialize the DashScopeOpenAI class with DashScope's API base and Qwen model.

        Args:
            api_token (str): DashScope API key.
            model (str): Qwen model name (e.g., 'qwen-plus').
            **kwargs: Additional parameters for the OpenAI client.
        """
        # Set DashScope's API base - using the correct endpoint
        kwargs["api_base"] = kwargs.get(
            "api_base", "https://dashscope.aliyuncs.com/compatible-mode/v1"
        )

        # Initialize the parent OpenAI class
        super().__init__(api_token=api_token, model=model, **kwargs)

        # Force chat model client for Qwen models
        self._is_chat_model = True
        self.client = (
            openai.OpenAI(**self._client_params).chat.completions
            if self.is_openai_v1()
            else openai.ChatCompletion
        )

    def is_openai_v1(self) -> bool:
        """
        Check if the openai library version is >= 1.0.

        Returns:
            bool: True if openai version is >= 1.0, False otherwise.
        """
        import openai

        try:
            # For openai >= 1.0, the version is stored in openai.__version__
            version = openai.__version__
            major_version = int(version.split(".")[0])
            return major_version >= 1
        except AttributeError:
            # For older versions, assume pre-1.0
            return False
