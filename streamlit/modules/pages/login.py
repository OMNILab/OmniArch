"""
Login Page Module
Contains the login page implementation for the smart meeting system
"""

import streamlit as st


class LoginPage:
    """Login page implementation"""

    def __init__(self, data_manager, auth_manager, ui_components):
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.ui = ui_components

    def show(self):
        """Login page implementation"""
        st.markdown('<h1 class="main-header">智慧会议系统</h1>', unsafe_allow_html=True)

        # Center the login form
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown("### 用户登录")

            # Show login attempts if any
            if st.session_state.get("login_attempts", 0) > 0:
                st.info(f"登录尝试次数: {st.session_state.login_attempts}")

            with st.form("login_form"):
                username = st.text_input("用户名", placeholder="请输入用户名")
                password = st.text_input(
                    "密码", type="password", placeholder="请输入密码"
                )

                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("登录", type="primary")
                with col2:
                    if st.form_submit_button("重置"):
                        st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

            # Demo users help
            st.markdown(
                """
            **演示用户提示：**
            - 输入任意用户名和密码即可登录
            - 系统会自动创建演示用户
            - 数据仅在当前会话中保存
            """
            )

            # Handle login outside form
            if submitted:
                if username and password:
                    if self.auth_manager.login(username, password):
                        st.success("登录成功！")
                        st.rerun()
                    else:
                        st.error("登录失败，请检查用户名和密码")
                else:
                    st.warning("请输入用户名和密码")
