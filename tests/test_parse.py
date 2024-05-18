import sys, os, pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/')))
from query_ops import parse_columns, parse_spec, read_df


@pytest.fixture(scope="module")
def loaded_data():
    return read_df('data/query-assistant-results.csv')

def test_read_df(loaded_data):
    assert loaded_data.shape[0] == 82

def test_parse_columns(loaded_data):
    _prompt = loaded_data['prompt'][0]
    _cols = parse_columns(_prompt)
    assert _cols == [
        'sli.latency', 'duration_ms', 'http.method', 'net.transport', 'error', 'http.target',
        'http.route', 'rpc.method', 'http.request_content_length', 'ip', 'rpc.service', 'dc.error',
        'req_flow.checkout', 'apdex', 'name', 'message.type', 'http.host', 'service.name',
        'rpc.system', 'http.scheme', 'type', 'http.flavor', 'span.kind', 'dc.platform-time',
        'library.version', 'status_code', 'net.host.port', 'net.host.ip', 'app.request_id',
        'bucket_duration_ms', 'library.name', 'sli_product', 'message.uncompressed_size',
        'rpc.grpc.status_code', 'net.peer.port', 'log10_duration_ms', 'http.status_code',
        'status_message', 'http.user_agent', 'net.host.name', 'span.num_links', 'message.id',
        'parent_name', 'app.cart_total', 'num_products', 'product_availability', 'revenue_at_risk',
        'trace.trace_id', 'dc.success_percent', 'ingest_timestamp', 'trace.parent_id'
    ]
    

def test_parse_spec(loaded_data):
    _prompt = loaded_data['prompt'][0]
    _spec = parse_spec(_prompt)
    assert _spec == {'calculations': [{'op': 'COUNT'}, {'op': 'HEATMAP', 'column': 'name'}],
    'filters': [{'column': 'name', 'op': 'exists'},
    {'column': 'name', 'op': '=', 'value': 'something'}],
    'filter_combination': 'AND',
    'breakdowns': ['column1', 'column2'],
    'orders': [{'op': 'op_in_calculation',
    'column': 'column_in_calculation',
    'order': 'ascending'},
    {'op': 'COUNT', 'order': 'descending'},
    {'column': 'column1', 'order': 'descending'}],
    'havings': [{'calculate_op': 'op_in_calculation',
    'column': 'name',
    'op': 'OPNAME',
    'value': 100},
    {'calculate_op': 'COUNT', 'op': '>', 'value': 10}],
    'time_range': 7200,
    'start_time': 1234567890,
    'end_time': 1234567890}

if __name__ == "__main__":
    pytest.main()