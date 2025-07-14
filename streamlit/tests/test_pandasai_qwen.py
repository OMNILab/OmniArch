"""
Simple test to validate pandasai communication with DashScope models
Tests the integration between pandasai and DashScope's Qwen models using a sample dataframe
"""

import os
import sys
import pandas as pd
from pandasai import SmartDataframe
from pandasai.config import Config

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")

from modules.llm_dashscope import DashScopeOpenAI


def test_dashscope_pandasai_integration():
    """Test pandasai integration with DashScope models"""
    print("🚀 Testing pandasai + DashScope integration")
    print("=" * 50)

    try:
        # Create sample dataframe
        sample_data = pd.DataFrame(
            {
                "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
                "age": [25, 30, 35, 28, 32],
                "department": ["HR", "IT", "Sales", "Marketing", "Finance"],
                "salary": [50000, 65000, 55000, 60000, 70000],
                "experience_years": [2, 5, 8, 3, 6],
            }
        )

        print("📊 Sample dataframe created:")
        print(sample_data)
        print()

        # Initialize pandasai with DashScope
        llm = DashScopeOpenAI(
            api_token=os.getenv("DASHSCOPE_API_KEY"), model="qwen-plus"
        )

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
            "What is the total salary budget?",
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
