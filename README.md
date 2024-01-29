# RDF Delta Python

## Client

A Python client to interact with a Delta Server.

Example usage:

```python
from rdf_delta import DeltaClient

client = DeltaClient("http://localhost:1066/")
ids = client.list_datasource()
for id_ in ids:
    print(client.describe_log(id_))

```

See the [DeltaClient](rdf_delta/client.py) class for all the possible methods.

## RDF Patch Lark Parser

A Lark parser of the [RDF Patch](https://afs.github.io/rdf-delta/rdf-patch.html) format will be implemented soon.

This will allow for [Lark transformer and visitor](https://lark-parser.readthedocs.io/en/latest/visitors.html) implementations to process and transform the abstract syntax tree as needed.
