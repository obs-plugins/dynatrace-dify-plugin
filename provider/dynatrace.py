# TODO: Implement provider credential validation
# This module validates the Dynatrace provider credentials.

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
import requests


class DynatraceProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict) -> None:
        """Validate Dynatrace credentials by calling the API."""
        # TODO: implement validation
        pass
