import json
import math
import pandas as pd

class InvalidQueryException(Exception):
    def __init__(self, message, query=None):
        self.message = message
        self.query = query
        if query:
            self.message += f"\nQuery: {self.query}"
        super().__init__(self.message)


def is_valid(query_spec:str, columns:str, check_runnable=True):
    "Test if a query is valid"
    try:
        check_query(query_spec, columns, check_runnable)
        return True
    except InvalidQueryException:
        return False

def check_query(query_spec:str, columns:str, check_runnable=True):
    "Raise an exception if a query is invalid."
    query_spec = query_spec.replace("'", '"')
    try:
        spec = json.loads(query_spec)
    except json.decoder.JSONDecodeError:
        raise InvalidQueryException(f"JSON parsing error:\n{query_spec}", query_spec)

    valid_calculate_ops = [
        "COUNT",
        "COUNT_DISTINCT",
        "HEATMAP",
        "CONCURRENCY",
        "SUM",
        "AVG",
        "MAX",
        "MIN",
        "P001",
        "P01",
        "P05",
        "P10",
        "P25",
        "P50",
        "P75",
        "P90",
        "P95",
        "P99",
        "P999",
        "RATE_AVG",
        "RATE_SUM",
        "RATE_MAX",
    ]

    valid_filter_ops = [
        "=",
        "!=",
        ">",
        ">=",
        "<",
        "<=",
        "starts-with",
        "does-not-start-with",
        "exists",
        "does-not-exist",
        "contains",
        "does-not-contain",
        "in",
        "not-in",
    ]

    if spec == {} or isinstance(spec, float):
        raise InvalidQueryException("Query spec cannot be empty.", query_spec)
        
    if isinstance(spec, str):
        raise InvalidQueryException("Query spec was not parsed to json.", query_spec)
        
    if "calculations" in spec:
        for calc in spec["calculations"]:
            if "op" not in calc:
                raise InvalidQueryException(f"{calc}: Calculation must have an op.", query_spec)
            
            if calc["op"] not in valid_calculate_ops:
                raise InvalidQueryException(f"Invalid calculation: {calc['op']}", query_spec)
    
            if calc["op"] == "COUNT" or calc["op"] == "CONCURRENCY":
                if "column" in calc:
                    raise InvalidQueryException(f"{calc}: {calc['op']} cannot take a column as input.", query_spec)        
            else:
                if "column" not in calc:
                    raise InvalidQueryException(f"{calc}: {calc['op']} must take a column as input.", query_spec)
       
                if check_runnable and calc["column"] not in columns:
                    raise InvalidQueryException(f"Invalid column: {calc['column']}", query_spec)
        

    if "filters" in spec:
        for filter in spec["filters"]:
            if not isinstance(filter, dict):
                raise InvalidQueryException(f"filter of type other than dict found in query.", query_spec)
            if "op" not in filter:
                raise InvalidQueryException(f"No op found in filter.", query_spec)
            if filter["op"] not in valid_filter_ops:
                raise InvalidQueryException(f"Invalid filter: {filter['op']}", query_spec)
    

            if check_runnable and filter["column"] not in columns:
                raise InvalidQueryException(f"Invalid column: {filter['column']}", query_spec)
    

            if filter["op"] == "exists" or filter["op"] == "does-not-exist":
                if "value" in filter:
                    raise InvalidQueryException(f"{filter}: {filter['op']} cannot take a value as input.", query_spec)
        
            else:
                if filter["op"] == "in" or filter["op"] == "not-in":
                    if not isinstance(filter["value"], list):
                        raise InvalidQueryException(f"{filter}: {filter['op']} must take a list as input.", query_spec)
            
                else:
                    if "value" not in filter:
                        raise InvalidQueryException(f"{filter}: {filter['op']} must take a value as input.", query_spec)
            
    if "filter_combination" in spec:
        if isinstance(spec["filter_combination"], str) and spec[
            "filter_combination"
        ].lower() not in ["and", "or"]:
            raise InvalidQueryException(f"Invalid filter combination: {spec['filter_combination']}", query_spec)


    if "breakdowns" in spec:
        for breakdown in spec["breakdowns"]:
            if check_runnable and breakdown not in columns:
                raise InvalidQueryException(f"Invalid column: {breakdown}", query_spec)
    

    if "orders" in spec:
        for order in spec["orders"]:
            if "order" not in order:
                raise InvalidQueryException(f"Invalid order without orders key: {query_spec}")
            if order["order"] != "ascending" and order["order"] != "descending":
                raise InvalidQueryException(f"Invalid order: {order['order']}", query_spec)
    
            if "op" in order:
                if order["op"] not in valid_calculate_ops:
                    raise InvalidQueryException(f"Invalid order: {order['op']}", query_spec)
        

                if not any(calc["op"] == order["op"] for calc in spec.get("calculations", [])):
                    raise InvalidQueryException(f"{order}: Order op must be present in calculations: {order['op']}", query_spec)        

                if order["op"] == "COUNT" or order["op"] == "CONCURRENCY":
                    if "column" in order:
                        raise InvalidQueryException(f"{order}: {order['op']} cannot take a column as input.", query_spec)
            
                else:
                    if "column" not in order:
                        raise InvalidQueryException(f"{order}: {order['op']} must take a column as input.", query_spec)
            
                    if check_runnable and order["column"] not in columns:
                        raise InvalidQueryException(f"{order}: Invalid column in order: {order['column']}", query_spec)
            
            else:
                if "column" not in order:
                    raise InvalidQueryException(f"{order}: Order must take a column or op as input.", query_spec)
        
                if check_runnable and order["column"] not in columns:
                    raise InvalidQueryException(f"{order}: Invalid column in order: {order['column']}", query_spec)
        

    if "havings" in spec:
        for having in spec["havings"]:
            if "calculate_op" not in having:
                raise InvalidQueryException(f"{having}: Having must have a calculate_op.", query_spec)

            if "value" not in having:
                raise InvalidQueryException(f"{having}: Having must have a value.", query_spec)

            if "op" not in having:
                raise InvalidQueryException(f"{having}: Having must have an op.", query_spec)

            if having["calculate_op"] == "HEATMAP":
                raise InvalidQueryException("HEATMAP is not supported in having.", query_spec)

            if (
                having["calculate_op"] == "COUNT"
                or having["calculate_op"] == "CONCURRENCY"
            ):
                if "column" in having:
                    raise InvalidQueryException(f"{having}: {having['calculate_op']} cannot take a column as input.", query_spec)
        
            else:
                if "column" not in having:
                    raise InvalidQueryException(f"{having}: {having['calculate_op']} must take a column as input.", query_spec)
        
                if check_runnable and having["column"] not in columns:
                    raise InvalidQueryException(f"{having}: Invalid column in having: {having['column']}", query_spec)
        

    if "time_range" in spec:
        if "start_time" in spec and "end_time" in spec:
            raise InvalidQueryException("Time range cannot be specified with start_time and end_time.", query_spec)

        if not isinstance(spec["time_range"], int):
            raise InvalidQueryException(f"time_range must be an int: {spec['time_range']}", query_spec)


    if "start_time" in spec:
        if not isinstance(spec["start_time"], int):
            raise InvalidQueryException(f"start_time must be an int: {spec['start_time']}", query_spec)


    if "end_time" in spec:
        if not isinstance(spec["end_time"], int):
            raise InvalidQueryException(f"end_time must be an int: {spec['end_time']}", query_spec)


    if "granularity" in spec:
        if not isinstance(spec["granularity"], int):
            raise InvalidQueryException(f"granularity must be an int: {spec['granularity']}", query_spec)


        time_range = (
            spec["time_range"]
            if "time_range" in spec
            else spec["end_time"] - spec["start_time"]
            if "start_time" in spec and "end_time" in spec
            else 7200
        )
        if spec["granularity"] > time_range / 10:
            raise InvalidQueryException(f"granularity must be <= time_range / 10: {spec['granularity']}", query_spec)

        if spec["granularity"] < time_range / 1000:
            raise InvalidQueryException(f"granularity must be >= time_range / 1000: {spec['granularity']}", query_spec)

    if "limit" in spec:
        if not isinstance(spec["limit"], int):
            raise InvalidQueryException(f"limit must be an int: {spec['limit']}", query_spec)


def write_response(response, dest_file=None):
    "Writes jsonl response to disk."
    for c in response.choices:
        if c.finish_reason == 'stop' and hasattr(c, 'message'):
            if hasattr(c.message, 'content'):
                try:
                    row = json.dumps(json.loads(c.message.content.strip())) # get rid of artifacts from openai
                    with open(dest_file, 'a') as file:
                        file.write(row + '\n')
                except: pass

def read_responses(jsonl_file):
    "read responses from JSONL file."
    return pd.read_json(jsonl_file, lines=True)
