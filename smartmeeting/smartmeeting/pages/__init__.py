"""
Pages Package
Contains all individual page implementations for the smart meeting system
"""

from .login import LoginPage
from .booking import BookingPage
from .calendar import CalendarPage
from .minutes import MinutesPage
from .tasks import TasksPage
from .dashboard import DashboardPage
from .settings import SettingsPage

# from .analysis import AnalysisPage

__all__ = [
    "LoginPage",
    "BookingPage",
    "CalendarPage",
    "MinutesPage",
    "TasksPage",
    "DashboardPage",
    "SettingsPage",
    # "AnalysisPage",
]
