This cog model has been pushed to [hamelsmu/honeycomb-3](https://replicate.com/hamelsmu/honeycomb-3)

```bash
cog login
cog push r8.im/hamelsmu/honeycomb-4-awq
```

## Debug

```bash
#download weights
HF_HUB_ENABLE_HF_TRANSFER=1 huggingface-cli download --local-dir ./parlance-labs/hc-mistral-alpaca-merged-awq --local-dir-use-symlinks=False parlance-labs/hc-mistral-alpaca-merged-awq
# run server
cog run -e CUDA_VISIBLE_DEVICES=0 -p 5000 python -m cog.server.http
```

In another process:

```bash
curl http://localhost:5000/predictions -X POST -H 'Content-Type: application/json' \
	--data @- <<-EOM | jq -r '.output'
{
	"input": {
      "nlq": "EMISSING slowest traces",
      "cols": "['sli.latency', 'duration_ms', 'net.transport', 'http.method', 'error', 'http.target', 'http.route', 'rpc.method', 'ip', 'http.request_content_length', 'rpc.service', 'apdex', 'name', 'message.type', 'http.host', 'service.name', 'rpc.system', 'http.scheme', 'sli.platform-time', 'type', 'http.flavor', 'span.kind', 'dc.platform-time', 'library.version', 'status_code', 'net.host.port', 'net.host.ip', 'app.request_id', 'bucket_duration_ms', 'library.name', 'sli_product', 'message.uncompressed_size', 'rpc.grpc.status_code', 'net.peer.port', 'log10_duration_ms', 'http.status_code', 'status_message', 'http.user_agent', 'net.host.name', 'span.num_links', 'message.id', 'parent_name', 'app.cart_total', 'num_products', 'product_availability', 'revenue_at_risk', 'trace.trace_id', 'trace.span_id', 'ingest_timestamp', 'http.server_name', 'trace.parent_id']"
	}
}
EOM
```

## Run Predictions

```bash
cog predict -e CUDA_VISIBLE_DEVICES=0 -i nlq="EMISSING slowest traces" -i cols="['sli.latency', 'duration_ms', 'net.transport', 'http.method', 'error', 'http.target', 'http.route', 'rpc.method', 'ip', 'http.request_content_length', 'rpc.service', 'apdex', 'name', 'message.type', 'http.host', 'service.name', 'rpc.system', 'http.scheme', 'sli.platform-time', 'type', 'http.flavor', 'span.kind', 'dc.platform-time', 'library.version', 'status_code', 'net.host.port', 'net.host.ip', 'app.request_id', 'bucket_duration_ms', 'library.name', 'sli_product', 'message.uncompressed_size', 'rpc.grpc.status_code', 'net.peer.port', 'log10_duration_ms', 'http.status_code', 'status_message', 'http.user_agent', 'net.host.name', 'span.num_links', 'message.id', 'parent_name', 'app.cart_total', 'num_products', 'product_availability', 'revenue_at_risk', 'trace.trace_id', 'trace.span_id', 'ingest_timestamp', 'http.server_name', 'trace.parent_id']"
```
