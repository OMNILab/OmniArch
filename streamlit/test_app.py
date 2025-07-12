"""
Test script to verify the enhanced smart meeting system functionality
"""

import streamlit as st
import sys
import os

# Add the streamlit directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.data_manager import DataManager
from modules.auth_manager import AuthManager
from modules.ui_components import UIComponents
from modules.pages import Pages


def test_data_manager():
    """Test DataManager functionality"""
    st.header("DataManager Test")

    dm = DataManager()

    # Test data generation
    data = dm.get_data()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Users", len(data["users"]))

    with col2:
        st.metric("Meetings", len(data["meetings"]))

    with col3:
        st.metric("Tasks", len(data["tasks"]))

    with col4:
        st.metric("Rooms", len(data["rooms"]))

    # Test adding new data
    if st.button("Add Test Meeting"):
        new_meeting = {
            "title": "Test Meeting",
            "room_id": 1,
            "organizer_id": 1,
            "participants": 5,
            "type": "测试会议",
            "status": "已确认",
            "description": "This is a test meeting",
        }
        dm.add_meeting(new_meeting)
        st.success("Test meeting added!")
        st.rerun()

    # Test data export
    if st.button("Test Data Export"):
        meetings_df = dm.get_dataframe("meetings")
        if len(meetings_df) > 0:
            csv_data = meetings_df.to_csv(index=False)
            st.download_button(
                label="Download Test Data",
                data=csv_data,
                file_name="test_meetings.csv",
                mime="text/csv",
            )
        else:
            st.info("No meetings to export")

    # Test data reset
    if st.button("Reset Data"):
        dm.reset_to_default()
        st.success("Data reset completed!")
        st.rerun()


def test_auth_manager():
    """Test AuthManager functionality"""
    st.header("AuthManager Test")

    dm = DataManager()
    am = AuthManager(dm)

    if not am.is_authenticated():
        st.info("Not authenticated. Please login.")

        username = st.text_input("Test Username")
        password = st.text_input("Test Password", type="password")

        if st.button("Test Login"):
            if am.login(username, password):
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Login failed")
    else:
        st.success("Already authenticated!")

        current_user = am.get_current_user()
        st.write(f"**Current User:** {current_user['name']}")
        st.write(f"**Role:** {current_user['role']}")
        st.write(f"**Department:** {current_user['department']}")

        if st.button("Test Logout"):
            am.logout()
            st.success("Logout successful!")
            st.rerun()


def test_session_state():
    """Test session state functionality"""
    st.header("Session State Test")

    # Initialize test counters
    if "test_counter" not in st.session_state:
        st.session_state.test_counter = 0

    if "test_data" not in st.session_state:
        st.session_state.test_data = []

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Counter", st.session_state.test_counter)

        if st.button("Increment Counter"):
            st.session_state.test_counter += 1
            st.rerun()

    with col2:
        st.metric("Data Items", len(st.session_state.test_data))

        if st.button("Add Data Item"):
            st.session_state.test_data.append(
                f"Item {len(st.session_state.test_data) + 1}"
            )
            st.rerun()

    # Display session data
    if st.session_state.test_data:
        st.write("**Session Data:**")
        for item in st.session_state.test_data:
            st.write(f"- {item}")

    # Test session reset
    if st.button("Reset Session"):
        st.session_state.test_counter = 0
        st.session_state.test_data = []
        st.success("Session reset!")
        st.rerun()


def main():
    """Main test function"""
    st.set_page_config(
        page_title="Smart Meeting System - Test", page_icon="🧪", layout="wide"
    )

    st.title("Smart Meeting System - Test Suite")

    # Test selection
    test_option = st.sidebar.selectbox(
        "Select Test",
        [
            "DataManager Test",
            "AuthManager Test",
            "Session State Test",
            "Integration Test",
        ],
    )

    if test_option == "DataManager Test":
        test_data_manager()
    elif test_option == "AuthManager Test":
        test_auth_manager()
    elif test_option == "Session State Test":
        test_session_state()
    elif test_option == "Integration Test":
        st.header("Integration Test")

        try:
            # Test full integration
            dm = DataManager()
            am = AuthManager(dm)
            ui = UIComponents()
            pages = Pages(dm, am, ui)

            st.success("✅ All modules loaded successfully!")

            # Test data availability
            data = dm.get_data()
            st.info(f"📊 Data loaded: {len(data)} data types")

            # Test dashboard data
            dashboard_data = dm.get_dashboard_data()
            st.info(f"📈 Dashboard data: {len(dashboard_data)} metrics")

            # Display some stats
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Meetings", dashboard_data["total_meetings"])

            with col2:
                st.metric("Total Tasks", dashboard_data["total_tasks"])

            with col3:
                st.metric("Total Users", dashboard_data["total_users"])

            with col4:
                st.metric("Total Rooms", dashboard_data["total_rooms"])

            st.success("🎉 Integration test completed successfully!")

        except Exception as e:
            st.error(f"❌ Integration test failed: {str(e)}")
            st.exception(e)

    # Show session state info
    with st.sidebar:
        st.markdown("---")
        st.markdown("### Session Info")

        if hasattr(st.session_state, "mock_data"):
            st.write(f"Mock data loaded: ✅")
        else:
            st.write(f"Mock data loaded: ❌")

        if hasattr(st.session_state, "authenticated"):
            st.write(f"Auth status: {'✅' if st.session_state.authenticated else '❌'}")
        else:
            st.write(f"Auth status: ❌")

        st.write(f"Session keys: {len(st.session_state.keys())}")


if __name__ == "__main__":
    main()
