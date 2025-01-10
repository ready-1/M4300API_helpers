"""Login helper module.

This module provides functionality to login to an M4300 switch and obtain
an authentication token for subsequent API calls.
"""

from .login import login, LoginResponse, LoginResult

__all__ = ['login', 'LoginResponse', 'LoginResult']
