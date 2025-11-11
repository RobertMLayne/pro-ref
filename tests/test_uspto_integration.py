
import os, json, pytest, vcr
from src.clients.uspto import USPTOClient
from src.utils.schema_validator import validate_json

API_KEY = os.getenv('USPTO_ODP_API_KEY')

my_vcr = vcr.VCR(
    cassette_library_dir='tests/cassettes',
    record_mode='new_episodes' if os.getenv('RECORD_VCR') else 'none',
    filter_headers=['X-API-KEY'],
)

@pytest.mark.skipif(not API_KEY, reason='Requires USPTO_ODP_API_KEY')
@my_vcr.use_cassette('pfw_search_facets.yaml')
def test_pfw_search_with_facets():
    c = USPTOClient()
    payload = {
        'q': 'applicationMetaData.applicationTypeLabelName:Utility',
        'pagination': {'offset': 0, 'limit': 5},
        'facets': ['applicationMetaData.applicationTypeLabelName','applicationMetaData.applicationStatusCode'],
    }
    data = c.pfw_search(payload)
    validate_json(data, 'docs/schemas/patent-data-schema.json')
    assert 'facets' in data

@pytest.mark.skipif(not API_KEY, reason='Requires USPTO_ODP_API_KEY')
@my_vcr.use_cassette('pfw_lookup_14412875.yaml')
def test_pfw_lookup():
    c = USPTOClient()
    data = c.pfw_lookup('14412875')
    validate_json(data, 'docs/schemas/patent-data-schema.json')
    assert data.get('count', 0) >= 1

@pytest.mark.skipif(not API_KEY, reason='Requires USPTO_ODP_API_KEY')
@my_vcr.use_cassette('pfw_documents_list.yaml')
def test_pfw_documents():
    c = USPTOClient()
    # Use a known application number from lookup cassette when recording
    data = c.pfw_documents('14412875')
    assert 'documents' in json.dumps(data).lower()

@pytest.mark.skipif(not API_KEY, reason='Requires USPTO_ODP_API_KEY')
@my_vcr.use_cassette('bulk_ptfwprd.yaml')
def test_bulk_ptfwprd():
    c = USPTOClient()
    data = c.bulk_products('PTFWPRD', latest=True)
    validate_json(data, 'docs/schemas/bulkdata-response-schema.json')
    assert data.get('count', 0) >= 1

@pytest.mark.skipif(not API_KEY, reason='Requires USPTO_ODP_API_KEY')
@my_vcr.use_cassette('petition_search.yaml')
def test_petition_search():
    c = USPTOClient()
    payload = {'q': 'inventionTitle:Design', 'pagination': {'offset': 0, 'limit': 5}}
    data = c.petition_search(payload)
    validate_json(data, 'docs/schemas/petition-decision-schema.json')
    assert data.get('count', 0) >= 0
