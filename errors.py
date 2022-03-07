class EmptyBufferError(Exception):
    """
    Raised when the buffer returns as NoneType.
    """

    default_msg = 'The buffer seems to be empty, is your device transmitting?'

    def __init__(self, message: str = default_msg):
        """

        Instantiate the exception.

        Arguments:

            message (str):
                Include additional information that may help the end-user or developers figure out why the buffer is
                empty.
        """

        if message != self.default_msg:
            msg = self.default_msg + f"\n\nSome more information from the caller: {message}"
            message = msg

        Exception.__init__(self, message)


def test_exception():
    raise EmptyBufferError(__name__)



