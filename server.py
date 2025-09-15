from flask import Flask, request, Response
from openrpc import RPCServer

app = Flask("TestChainRPC")
rpc = RPCServer(title="TestChainRPC", version="1.0.0")

STATE = {
    "gasPrice":   "0x09184e72a000",  # 100 gwei in wei
    "gasLimit":   "0x7a1200",        # 8,000,000
    "blockNumber":"0x1b4",           # 436
    "chainId":    "0x539",           # 1337 (local dev)
}

@rpc.method(name="eth_gasPrice")
def eth_gas_price() -> str:
    # Return the current gas price.
    return STATE["gasPrice"]

@rpc.method(name="eth_blockNumber")
def eth_block_number() -> str:
    # Return the latest block number.
    return STATE["blockNumber"]

@rpc.method(name="eth_chainId")
def eth_chain_id() -> str:
    # Return the chain id.
    return STATE["chainId"]

@rpc.method(name="eth_gasLimit")
def eth_gas_limit() -> str:
    # Return the current gas limit.
    return STATE["gasLimit"]

@app.route("/rpc", methods=["POST"])
def http_process_rpc() -> tuple[Response, int]:
    response_json = rpc.process_request(request.data)  # JSON-RPC in, JSON-RPC out
    return Response(response_json, content_type="application/json"), 200

if __name__ == "__main__":
    print("JSON-RPC server on http://127.0.0.1:5000/rpc")
    app.run(host="127.0.0.1", port=5000)