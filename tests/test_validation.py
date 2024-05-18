import sys, os, pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/')))
from validate import check_query, InvalidQueryException

def test_check_query_valid():
    query_spec = '{"calculations":[{"column":"duration_ms","op":"MAX"}]}'
    columns = ["duration_ms"]
    assert check_query(query_spec, columns) is None

def test_check_query_invalid_json():
    query_spec = 'invalid json'
    columns = ["duration_ms"]
    with pytest.raises(InvalidQueryException) as exc_info:
        check_query(query_spec, columns)
    assert "JSON parsing error" in str(exc_info.value)

def test_check_query_invalid_calculation_op():
    query_spec = '{"calculations":[{"column":"duration_ms","op":"INVALID_OP"}]}'
    columns = ["duration_ms"]
    with pytest.raises(InvalidQueryException) as exc_info:
        check_query(query_spec, columns)
    assert "Invalid calculation" in str(exc_info.value)

def test_check_query_invalid_column():
    query_spec = '{"calculations":[{"column":"invalid_column","op":"MAX"}]}'
    columns = ["duration_ms"]
    with pytest.raises(InvalidQueryException) as exc_info:
        check_query(query_spec, columns)
    assert "Invalid column" in str(exc_info.value)

def test_check_query_invalid_filter_op():
    query_spec = '{"filters":[{"column":"duration_ms","op":"INVALID_OP"}]}'
    columns = ["duration_ms"]
    with pytest.raises(InvalidQueryException) as exc_info:
        check_query(query_spec, columns)
    assert "Invalid filter" in str(exc_info.value)

def test_check_query_invalid_filter_column():
    query_spec = '{"filters":[{"column":"invalid_column","op":"="}]}'
    columns = ["duration_ms"]
    with pytest.raises(InvalidQueryException) as exc_info:
        check_query(query_spec, columns)
    assert "Invalid column" in str(exc_info.value)

def test_check_query_invalid_order():
    query_spec = '{"orders":[{"column":"duration_ms","order":"INVALID_ORDER"}]}'
    columns = ["duration_ms"]
    with pytest.raises(InvalidQueryException) as exc_info:
        check_query(query_spec, columns)
    assert "Invalid order" in str(exc_info.value)

def test_check_query_invalid_order_column():
    query_spec = '{"orders":[{"column":"invalid_column","order":"ascending"}]}'
    columns = ["duration_ms"]
    with pytest.raises(InvalidQueryException) as exc_info:
        check_query(query_spec, columns)
    assert "Invalid column in order" in str(exc_info.value)

def test_check_query_invalid_breakdown():
    query_spec = '{"breakdowns":["invalid_column"]}'
    columns = ["duration_ms"]
    with pytest.raises(InvalidQueryException) as exc_info:
        check_query(query_spec, columns)
    assert "Invalid column" in str(exc_info.value)

def test_check_query_invalid_filter_combination():
    query_spec = '{"filter_combination":"INVALID_COMBINATION"}'
    columns = ["duration_ms"]
    with pytest.raises(InvalidQueryException) as exc_info:
        check_query(query_spec, columns)
    assert "Invalid filter combination" in str(exc_info.value)

def test_check_query_invalid_filter_value():
    query_spec = '{"filters":[{"column":"duration_ms","op":"="}]}'  # value should not be a list
    columns = ["duration_ms"]
    with pytest.raises(InvalidQueryException) as exc_info:
        check_query(query_spec, columns)
    assert "must take a value as input" in str(exc_info.value)

def test_check_query_missing_filter_value():
    query_spec = '{"filters":[{"column":"duration_ms","op":"="}]}'  # missing value
    columns = ["duration_ms"]
    with pytest.raises(InvalidQueryException) as exc_info:
        check_query(query_spec, columns)
    assert "must take a value as input" in str(exc_info.value)

def test_check_query_invalid_calculation_column():
    query_spec = '{"calculations":[{"column":"invalid_column","op":"MAX"}]}'  # invalid column
    columns = ["duration_ms"]
    with pytest.raises(InvalidQueryException) as exc_info:
        check_query(query_spec, columns)
    assert "Invalid column" in str(exc_info.value)

def test_check_query_missing_calculation_column():
    query_spec = '{"calculations":[{"op":"MAX"}]}'  # missing column
    columns = ["duration_ms"]
    with pytest.raises(InvalidQueryException) as exc_info:
        check_query(query_spec, columns)
    assert "must take a column as input" in str(exc_info.value)

def test_check_query_empty_query():
    query_spec = '{}'
    columns = ["duration_ms"]
    with pytest.raises(InvalidQueryException) as exc_info:
        check_query(query_spec, columns)
    assert "cannot be empty." in str(exc_info.value)


def test_check_query_time_range_with_start_time_and_end_time():
    query_spec = '{"breakdowns":["redis.long_poll_exception"],"calculations":[{"op":"COUNT"}],"filters":[{"column":"redis.long_poll_exception","op":"exists","join_column":""}],"time_range":86400,"start_time":1677724800,"end_time":1677811199}'
    columns = ["redis.long_poll_exception"]
    with pytest.raises(InvalidQueryException) as exc_info:
        check_query(query_spec, columns)
    assert "Time range cannot be specified with start_time and end_time." in str(exc_info.value)

def test_check_query_count_with_column():
    query_spec = '{"breakdowns":["status_code"],"calculations":[{"column":"status_code","op":"COUNT"}],"filters":[{"column":"status_code","op":"=","value":0}],"time_range":7200}'
    columns = ["status_code"]
    with pytest.raises(InvalidQueryException) as exc_info:
        check_query(query_spec, columns)
    assert "COUNT cannot take a column as input." in str(exc_info.value)

def test_check_query_order_op_not_in_calculation():
    query_spec = '{"breakdowns":["name"],"calculations":[{"column":"duration_ms","op":"HEATMAP"}],"filters":[{"column":"trace.parent_id","op":"does-not-exist","join_column":""}],"orders":[{"column":"duration_ms","op":"MAX","order":"descending"}],"time_range":7200}'
    columns = ["duration_ms", "trace.parent_id", "name"]
    with pytest.raises(InvalidQueryException) as exc_info:
        check_query(query_spec, columns)
    assert "Order op must be present in calculations: MAX" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main()