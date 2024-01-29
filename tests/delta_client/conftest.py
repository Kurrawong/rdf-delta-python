from pathlib import Path

import pytest
from testcontainers.compose import DockerCompose

from rdf_delta import DeltaClient

DELTA_PORT = 9999
FUSEKI_PORT = 9998
filepath = Path(__file__).parent.resolve()
compose = DockerCompose(str(filepath))


@pytest.fixture(scope="module", autouse=True)
def setup(request: pytest.FixtureRequest):
    compose.start()
    compose.wait_for(f"http://localhost:{FUSEKI_PORT}/ds")
    request.addfinalizer(lambda: compose.stop())


@pytest.fixture(scope="module")
def client():
    _client = DeltaClient(f"http://localhost:{DELTA_PORT}")

    yield _client

    _client.close()
