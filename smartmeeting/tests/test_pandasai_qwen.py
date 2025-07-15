"""
Simple test to validate pandasai communication with DashScope models
Tests the integration between pandasai and DashScope's Qwen models using a sample dataframe
"""

import pandas as pd
import pandasai as pai
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from smartmeeting.tools import setup_pandasai_llm, create_pandasai_agent


def test_dashscope_pandasai_integration():
    """Test pandasai integration with DashScope models"""
    print("🚀 Testing pandasai + DashScope integration")
    print("=" * 50)

    try:
        # Create sample dataframe
        sample_data = pai.DataFrame(
            pd.DataFrame(
                {
                    "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
                    "age": [25, 30, 35, 28, 32],
                    "department": ["HR", "IT", "Sales", "Marketing", "Finance"],
                    "salary": [50000, 65000, 55000, 60000, 70000],
                    "experience_years": [2, 5, 8, 3, 6],
                }
            )
        )

        print("📊 Sample dataframe created:")
        print(sample_data)
        print()

        # Initialize pandasai with DashScope
        llm = setup_pandasai_llm()

        print("✅ LLM initialized with DashScope")

        agent = create_pandasai_agent(sample_data, llm)

        print("✅ pandasAI Agent created successfully")

        # Test basic queries
        test_queries = [
            "What is the average age?",
        ]

        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 Test {i}: {query}")
            try:
                response = agent.chat(query)
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
