class user_exception(Exception):
    """Raised when a user is not found in the user service."""

    def __init__(self, user_id: str):
        super().__init__(f"User with ID '{user_id}' not found.")
        self.user_id = user_id
