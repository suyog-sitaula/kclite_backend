#  exceptions.py
class DidwwAPIError(Exception):
    """
    Exception raised for errors returned by the DIDWW API.
    Attributes:
        status_code -- HTTP status code returned by the API
        error_body -- JSON body of the error response
    """

    def __init__(self, status_code, error_body):
        super().__init__(f"DIDWW API returned status {status_code}: {error_body}")
        self.status_code = status_code
        self.error_body = error_body
