import re
import httpx
from agentbridge.models.endpoint import Endpoint, HttpMethod
from agentbridge.models.project import Project


_GET_LIKE = {HttpMethod.get, HttpMethod.delete, HttpMethod.head, HttpMethod.options}


class GeneratedClient:
    def __init__(self, project: Project):
        self.base_url = project.base_url or ""
        self.api_key = project.api_key
        self.auth_header = project.auth_header
        self.auth_scheme = project.auth_scheme
        self._client = httpx.AsyncClient()

    def _build_headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers[self.auth_header] = f"{self.auth_scheme} {self.api_key}"
        return headers

    async def call_endpoint(self, ep: Endpoint, **kwargs) -> dict:
        url = f"{self.base_url.rstrip('/')}{ep.path}"

        path_params = {}
        query_params = {}
        for p in ep.parameters:
            value = kwargs.get(p.name)
            if value is not None:
                if p.location == "path":
                    path_params[p.name] = value
                else:
                    query_params[p.name] = value

        if path_params:
            url = re.sub(r"\{(\w+)\}", lambda m: str(path_params.get(m.group(1), m.group(0))), url)

        headers = self._build_headers()
        is_get_like = ep.method in _GET_LIKE
        response = await self._client.request(
            method=ep.method.value,
            url=url,
            headers=headers,
            params=query_params if is_get_like else None,
            json=query_params if not is_get_like else None,
        )
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self._client.aclose()
