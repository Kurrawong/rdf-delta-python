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
    """Perform common operations against an RDF Delta Server.

    The API interface is based on the documentation at https://afs.github.io/rdf-delta/delta-server-api.

    :param base_url: The base URL of the Delta Server. Example, http://localhost:1066/.
    """

    def __init__(self, base_url: str):
        url = base_url if base_url.endswith("/") else base_url + "/"
        self.url = url
        self.client = httpx.Client()

    def _fetch_rpc(self, payload: dict) -> dict:
        """Helper function to send requests to the Delta server via the RPC endpoint.

        :param payload: The payload to send to the Delta server.
        :return: The JSON response body from the Delta server.
        """
        logger.debug(f"Sending {payload['operation']} operation to {self.url}")
        response = self.client.post(self.url + "$/rpc", json=payload)
        if response.status_code != 200:
            raise DeltaServerError(
                f"Delta server responded with error {response.status_code}: {response.text}"
            )

        return response.json()

    def list_datasource(self) -> list[str]:
        """Get a list of datasource identifiers.

        :return: A list of datasource identifiers.
        """
        payload = {"opid": "", "operation": "list_datasource", "arg": {}}
        data = self._fetch_rpc(payload)
        return data["array"]

    def list_descriptions(self) -> list[Datasource]:
        """Get a list of datasource object descriptions.

        :return: A list of datasource objects.
        """
        payload = {"opid": "", "operation": "list_descriptions", "arg": {}}
        data = self._fetch_rpc(payload)
        datasources = [Datasource(**v) for v in data["array"]]
        return datasources

    def describe_datasource(self, id_: str) -> Datasource:
        """Get a datasource object description by identifier.

        :param id_: Datasource identifier.
        :return: Datasource object.
        """
        payload = {
            "opid": "",
            "operation": "describe_datasource",
            "arg": {"datasource": id_},
        }
        data = self._fetch_rpc(payload)
        return Datasource(**data)

    def describe_log(self, id_: str) -> DatasourceLogInfo:
        """Get a datasource log object description by identifier.

        :param id_: Datasource identifier.
        :return: Datasource log object with additional information related to patch logs.
        """
        payload = {"opid": "", "operation": "describe_log", "arg": {"datasource": id_}}
        data = self._fetch_rpc(payload)
        return DatasourceLogInfo(**data)
