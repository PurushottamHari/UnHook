"""
Base exception class for the user service.
"""

class UserServiceException(Exception):
    """Base exception for all user service related errors."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message) 