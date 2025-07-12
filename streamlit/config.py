"""
智慧会议系统配置文件
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """应用配置类"""

    # 应用基础配置
    APP_NAME = "智慧会议系统"
    APP_VERSION = "1.0.0"

    # Streamlit 配置
    STREAMLIT_SERVER_PORT = int(os.getenv("STREAMLIT_SERVER_PORT", 8501))
    STREAMLIT_SERVER_ADDRESS = os.getenv("STREAMLIT_SERVER_ADDRESS", "0.0.0.0")

    # OpenAI 配置 (用于 pandasAI)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # 安全配置
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

    # 模拟数据配置
    MOCK_USERS_COUNT = 20
    MOCK_ROOMS_COUNT = 15
    MOCK_MEETINGS_COUNT = 50
    MOCK_TASKS_COUNT = 30

    # 功能开关
    ENABLE_PANDASAI = bool(OPENAI_API_KEY)
    ENABLE_VOICE_RECOGNITION = False  # PoC 版本暂未实现
    ENABLE_REAL_TIME_TRANSCRIPTION = False  # PoC 版本暂未实现

    @classmethod
    def is_production(cls):
        """判断是否为生产环境"""
        return os.getenv("ENVIRONMENT", "development") == "production"

    @classmethod
    def get_pandasai_config(cls):
        """获取 pandasAI 配置"""
        return {"api_key": cls.OPENAI_API_KEY, "enabled": cls.ENABLE_PANDASAI}
