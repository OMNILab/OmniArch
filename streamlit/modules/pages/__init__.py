"""
Pages Package
Contains all individual page implementations for the smart meeting system
"""

from .login import LoginPage
from .booking import BookingPage
from .minutes import MinutesPage
from .tasks import TasksPage
from .dashboard import DashboardPage
from .settings import SettingsPage
from .pandasai_demo import PandasAIDemoPage

__all__ = [
    "LoginPage",
    "BookingPage", 
    "MinutesPage",
    "TasksPage",
    "DashboardPage",
    "SettingsPage",
    "PandasAIDemoPage"
]