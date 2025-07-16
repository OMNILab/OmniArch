from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """Agent 的状态 - 包含消息流和用户信息"""

    messages: Annotated[list, add_messages]
    current_user_id: Optional[int]
    current_username: Optional[str]
