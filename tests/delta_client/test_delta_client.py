import pytest

from rdf_delta import DeltaClient


def test_delta_client(client: DeltaClient):
    # Initial state.
    datasources = client.list_descriptions()
    assert len(datasources) == 1
    assert datasources[0].name == "ds"

    # Create new datasource.
    # Note: currently not supported with the rdf-delta container image we're using.
    with pytest.raises(NotImplementedError):
        datasource = client.create_datasource("ds2")
        assert datasource.name == "ds2"
        assert len(client.list_datasource()) == 2

    # Get datasource ds description.
    ds = client.describe_datasource("ds")
    assert ds.name == "ds"
    assert ds.uri == "delta:ds"

    # Get datasource log information.
    ds_log = client.describe_log(ds.id)
    assert ds_log.id == ds.id
    assert ds_log.name == "ds"
    assert ds_log.uri == "delta:ds"
    assert ds_log.min_version == 0
    assert ds_log.max_version == 0
    assert ds_log.latest == ""

    # Add patch log to the ds log.
    patch_log_1 = """H id <uuid:7b0f0324-e0b5-4a76-badd-4f0680c10bbf> .
TX .
A <https://example.com/A> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2004/02/skos/core#ConceptScheme> .
TC .
"""
    log_created_metadata = client.create_log(patch_log_1, ds.name)

    ds_log = client.describe_log(ds.id)
    assert ds_log.min_version == 1
    assert ds_log.max_version == 1
    assert ds_log.latest != ""
    assert client.get_log(log_created_metadata.version, ds.name) == patch_log_1

    # Add another patch log
    patch_log_2 = """H id <uuid:785a4d97-fdfd-44fa-a23f-633567663438> .
H prev <uuid:7b0f0324-e0b5-4a76-badd-4f0680c10bbf> .
TX .
A <https://example.com/A> <http://www.w3.org/2004/02/skos/core#prefLabel> "Example A"@en .
TC .
"""
    log_created_metadata = client.create_log(patch_log_2, ds.name)

    ds_log = client.describe_log(ds.id)
    assert ds_log.min_version == 1
    assert ds_log.max_version == 2
    assert ds_log.latest != ""
    assert client.get_log(log_created_metadata.version, ds.name) == patch_log_2
