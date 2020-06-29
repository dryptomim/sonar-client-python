from sonarclient import SonarClient
import pytest
import asyncio
import tempfile2
import subprocess
import os
from async_generator import yield_, async_generator


@pytest.mark.asyncio
async def test_put_and_del_record(start_sonar_server, event_loop):
    client = SonarClient()
    collection = await client.create_collection('testndcollection')
    print("COLLECTION: ", collection)
    record = {
        'schema': 'doc',
        'id': 'foo',
        'value': {'title': 'hello world'}}
    res = await collection.put(record)
    print(res)
    id = res.get('id')
    results = await collection.query(
        'records', {'id': id}, {'waitForSync': 'true'})
    assert len(results) == 1
    assert results[0].get('id') == id
    assert results[0].get('value').get('title') == 'hello world'
    await client.close()

@pytest.mark.asyncio
async def test_get_and_delete_record(event_loop):
    client = SonarClient()
    collection = await client.create_collection('foocollection')
    record = {
        'schema': 'doc',
        'id': 'foo',
        'value': {'title': 'hello world'}}
    res = await collection.put(record)
    id = res['id']
    records = await collection.get({'id': id}, {'waitForSync': 'true'})
    assert len(records) == 1
    await collection.delete(record)
    nu_records = await collection.get({'id': id}, {'waitForSync': 'true'})
    assert len(nu_records) == 0

@pytest.fixture
async def start_sonar_server(scope='session'):
    sonar_location = '../../../sonar'
    with tempfile2.TemporaryDirectory() as tmpdir:
        try:
            wd = os.getcwd()
            os.chdir(sonar_location)
            process = await asyncio.create_subprocess_shell(
                "./sonar start -s" + tmpdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            out, err = process.communicate(timeout=30)
            print(process)
            os.chdir(wd)
            print(out)
            return await yield_(process)

        except Exception:
            print('error')
            process.kill()
