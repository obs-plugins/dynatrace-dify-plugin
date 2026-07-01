from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
import requests


class DynatraceProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict) -> None:
        """Validate Dynatrace credentials by calling the API."""
        environment_url = credentials.get("environment_url", "").rstrip("/")
        api_token = credentials.get("api_token", "")

        if not environment_url:
            raise ToolProviderCredentialValidationError("Environment URL is required.")
        if not api_token:
            raise ToolProviderCredentialValidationError("API Token is required.")

        # Validate by calling the Dynatrace API v2 settings endpoint
        url = f"{environment_url}/api/v2/settings/schemas"
        headers = {
            "Authorization": f"Api-Token {api_token}",
            "Accept": "application/json; charset=utf-8",
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
        except requests.exceptions.RequestException as e:
            raise ToolProviderCredentialValidationError(
                f"Failed to connect to Dynatrace environment: {e}"
            )

        if response.status_code == 401:
            raise ToolProviderCredentialValidationError(
                "Invalid API token. Please check your Dynatrace API token."
            )
        if response.status_code == 403:
            raise ToolProviderCredentialValidationError(
                "API token lacks required permissions. Ensure the token has at least read scopes."
            )
        if not response.ok:
            raise ToolProviderCredentialValidationError(
                f"Dynatrace API returned status {response.status_code}: {response.text}"
            )
