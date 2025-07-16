"""
Pages Manager Module
Contains the main Pages class that coordinates all individual page implementations
"""

import streamlit as st
from .pages import (
    LoginPage,
    BookingPage,
    CalendarPage,
    MinutesPage,
    TasksPage,
    DashboardPage,
    SettingsPage,
    AnalysisPage,
)


class Pages:
    """Main Pages class that coordinates all individual page implementations"""

    def __init__(self, data_manager, auth_manager, ui_components):
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.ui = ui_components
        self._init_page_state()

        # Initialize individual page classes
        self.login_page = LoginPage(data_manager, auth_manager, ui_components)
        self.booking_page = BookingPage(data_manager, auth_manager, ui_components)
        self.calendar_page = CalendarPage(data_manager, auth_manager, ui_components)
        self.minutes_page = MinutesPage(data_manager, auth_manager, ui_components)
        self.tasks_page = TasksPage(data_manager, auth_manager, ui_components)
        self.dashboard_page = DashboardPage(data_manager, auth_manager, ui_components)
        self.settings_page = SettingsPage(data_manager, auth_manager, ui_components)
        self.analysis_page = AnalysisPage(data_manager, auth_manager, ui_components)

    def _init_page_state(self):
        """Initialize page-specific session state"""
        if "booking_form_data" not in st.session_state:
            st.session_state.booking_form_data = {}
        if "task_form_data" not in st.session_state:
            st.session_state.task_form_data = {}
        if "minute_form_data" not in st.session_state:
            st.session_state.minute_form_data = {}
        if "selected_meetings" not in st.session_state:
            st.session_state.selected_meetings = []
        if "selected_tasks" not in st.session_state:
            st.session_state.selected_tasks = []

    def show_login_page(self):
        """Show the login page"""
        return self.login_page.show()

    def show_booking_page(self):
        """Show the booking page"""
        return self.booking_page.show()

    def show_calendar_page(self):
        """Show the calendar page"""
        return self.calendar_page.show()

    def show_minutes_page(self):
        """Show the minutes page"""
        return self.minutes_page.show()

    def show_tasks_page(self):
        """Show the tasks page"""
        return self.tasks_page.show()

    def show_dashboard_page(self):
        """Show the dashboard page"""
        return self.dashboard_page.show()

    def show_settings_page(self):
        """Show the settings page"""
        return self.settings_page.show()

    def show_analysis_page(self):
        """Show the PandasAI demo page"""
        return self.analysis_page.show()
