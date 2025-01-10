"""Logout helper module.

This module provides functionality to logout from an M4300 switch and
invalidate the current authentication token.
"""

from .logout import logout, LogoutData, LogoutResult

__all__ = ['logout', 'LogoutData', 'LogoutResult']
