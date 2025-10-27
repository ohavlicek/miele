"""API for Miele bound to Home Assistant OAuth."""

from __future__ import annotations

import json
from typing import Any, cast

import async_timeout
from aiohttp import ClientSession
from pymiele import CONTENT_TYPE, MIELE_API, AbstractAuth

from homeassistant.helpers import config_entry_oauth2_flow


class AsyncConfigEntryAuth(AbstractAuth):
    """Provide Miele authentication tied to an OAuth2 based config entry."""

    def __init__(
        self,
        websession: ClientSession,
        oauth_session: config_entry_oauth2_flow.OAuth2Session,
    ) -> None:
        """Initialize Miele auth."""
        super().__init__(websession, MIELE_API)
        self._oauth_session = oauth_session

    async def async_get_access_token(self) -> str:
        """Return a valid access token."""
        await self._oauth_session.async_ensure_token_valid()

        return cast(str, self._oauth_session.token["access_token"])

    async def _async_device_request(
        self, serial: str, endpoint: str, data: dict[str, Any]
    ):
        """Send a JSON payload to a device-specific endpoint."""

        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"

        async with async_timeout.timeout(10):
            response = await self.request(
                "PUT",
                f"/devices/{serial}{endpoint}",
                data=json.dumps(data),
                headers={
                    "Content-Type": CONTENT_TYPE,
                    "Accept": "application/json",
                },
            )
            response.raise_for_status()

        return response

    async def assign_room(self, serial: str, data: dict[str, Any]):
        """Assign a robot vacuum to a room on the current map."""

        return await self._async_device_request(serial, "/rooms", data)
