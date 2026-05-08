class RescheduleMessageException(Exception):
    """
    Exception thrown to explicitly request a command to be rescheduled.
    """

    def __init__(
        self, delay_ms: int, max_retries: int = 3, message: str = "Rescheduling command"
    ):
        self.delay_ms = delay_ms
        self.max_retries = max_retries
        super().__init__(message)
