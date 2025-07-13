"""
Simple test to validate pandasai communication with DashScope models
Tests the integration between pandasai and DashScope's Qwen models using a sample dataframe
"""

import os
import pandas as pd
from pandasai import SmartDataframe
from pandasai.config import Config
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
        # Set DashScope's API base
        kwargs["api_base"] = kwargs.get("api_base", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1")
        
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
            major_version = int(version.split('.')[0])
            return major_version >= 1
        except AttributeError:
            # For older versions, assume pre-1.0
            return False
        

def setup_pandasai():
    """设置 pandasAI"""
    try:
        llm = DashScopeOpenAI(
            api_token="sk-c6d44b969a2c4a62975df77f5085d56b",
            model="qwen-plus"
        )
        return llm
    except Exception as e:
        st.warning(f"pandasAI 设置失败: {e}")
        return None
    

def test_dashscope_pandasai_integration():
    """Test pandasai integration with DashScope models"""
    print("🚀 Testing pandasai + DashScope integration")
    print("=" * 50)
    
    # Check environment variables
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ DASHSCOPE_API_KEY not set!")
        print("Please set your DashScope API key:")
        print("export DASHSCOPE_API_KEY='your-api-key-here'")
        return False
    
    try:
        # Create sample dataframe
        sample_data = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
            'age': [25, 30, 35, 28, 32],
            'department': ['HR', 'IT', 'Sales', 'Marketing', 'Finance'],
            'salary': [50000, 65000, 55000, 60000, 70000],
            'experience_years': [2, 5, 8, 3, 6]
        })
        
        print("📊 Sample dataframe created:")
        print(sample_data)
        print()
        
        # Initialize pandasai with DashScope
        llm = setup_pandasai()
        
        print("✅ LLM initialized with DashScope")
        
        # Create SmartDataframe
        config = Config(llm=llm, verbose=True)
        smart_df = SmartDataframe(sample_data, config=config)
        
        print("✅ SmartDataframe created successfully")
        
        # Test basic queries
        test_queries = [
            "What is the average age?",
            "Which department has the highest average salary?",
            "How many people are in each department?",
            "What is the total salary budget?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 Test {i}: {query}")
            try:
                response = smart_df.chat(query)
                print(f"✅ Response: {response}")
            except Exception as e:
                print(f"❌ Query failed: {e}")
        
        print("\n" + "=" * 50)
        print("✅ pandasai + DashScope integration test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


if __name__ == "__main__":
    test_dashscope_pandasai_integration() 