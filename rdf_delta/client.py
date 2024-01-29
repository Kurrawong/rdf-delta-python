import httpx
from loguru import logger
from pydantic import BaseModel, field_validator


class Datasource(BaseModel):
    """Basic datasource description."""
    id: str
    name: str
    uri: str

    @field_validator("id")
    @classmethod
    def convert_id_value(cls, v: str):
        """Remove the id: prefix from the identifier value."""
        return v.split("id:")[-1]


class DatasourceLogInfo(Datasource):
    """Datasource description with additional information related to patch logs."""
    min_version: int
    max_version: int
    latest: str

    @field_validator("latest")
    @classmethod
    def convert_latest_id_value(cls, v: str):
        """Remove the id: prefix from the identifier value."""
        return v.split("id:")[-1]


class DeltaServerError(Exception):
    """Any errors returned from the Delta Server."""


class DeltaClient:
    """Perform common operations against an RDF Delta Server."""
    def __init__(self, base_url: str):
        url = base_url if base_url.endswith("/") else base_url + "/"
        self.url = url + "$/rpc"
        self.client = httpx.Client()

    def _fetch(self, payload: dict) -> dict:
        """Helper function to send requests to the Delta server."""
        logger.debug(f"Sending {payload['operation']} operation to {self.url}")
        response = self.client.post(self.url, json=payload)
        if response.status_code != 200:
            raise DeltaServerError(f"Delta server responded with error {response.status_code}: {response.text}")

        return response.json()

    def list_datasource(self) -> list[str]:
        """Get a list of datasource identifiers."""
        payload = {
            "opid": "",
            "operation": "list_datasource",
            "arg": {}
        }
        data = self._fetch(payload)
        return data["array"]

    def list_descriptions(self) -> list[Datasource]:
        """Get a list of datasource object descriptions."""
        payload = {
            "opid": "",
            "operation": "list_descriptions",
            "arg": {}
        }
        data = self._fetch(payload)
        datasources = [Datasource(**v) for v in data["array"]]
        return datasources

    def describe_datasource(self, id_: str) -> Datasource:
        """Get a datasource object description by identifier."""
        payload = {
            "opid": "",
            "operation": "describe_datasource",
            "arg": {"datasource": id_}
        }
        data = self._fetch(payload)
        return Datasource(**data)

    def describe_log(self, id_: str) -> DatasourceLogInfo:
        """Get a datasource log object description by identifier."""
        payload = {
            "opid": "",
            "operation": "describe_log",
            "arg": {"datasource": id_}
        }
        data = self._fetch(payload)
        return DatasourceLogInfo(**data)
