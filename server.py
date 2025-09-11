from __future__ import annotations
import json, math
from functools import reduce
from flask import Flask, request, jsonify

app = Flask(__name__)

with open("calc-openrpc.json", "r", encoding="utf-8") as f:
    OPENRPC_DOC = json.load(f)

JSONRPC = "2.0"

def make_result(id_, result):
    return {"jsonrpc": JSONRPC, "id": id_, "result": result}

def make_error(id_, code, message, data=None):
    err = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return {"jsonrpc": JSONRPC, "id": id_, "error": err}

def lcm(a, b):
    return abs(a*b) // math.gcd(a, b) if a and b else 0

@app.route("/rpc", methods=["POST"])
def rpc():
    req = request.get_json(force=True, silent=True)
    if req is None:
        return jsonify(make_error(None, -32700, "Parse error")), 200

    # Support batch or single
    batch = isinstance(req, list)
    calls = req if batch else [req]
    responses = []

    for call in calls:
        id_ = call.get("id", None)
        method = call.get("method")
        params = call.get("params", [])

        try:
            # rpc.discover
            if method == "rpc.discover":
                responses.append(make_result(id_, OPENRPC_DOC))

            elif method == "calc_add":
                numbers = params[0] if isinstance(params, list) else params.get("numbers")
                total = sum(numbers)
                responses.append(make_result(id_, total))

            elif method == "calc_subtract":
                a, b = params if isinstance(params, list) else (params["a"], params["b"])
                responses.append(make_result(id_, a - b))

            elif method == "calc_multiply":
                numbers = params[0] if isinstance(params, list) else params.get("numbers")
                prod = reduce(lambda x, y: x * y, numbers, 1)
                responses.append(make_result(id_, prod))

            elif method == "calc_divide":
                a, b = params if isinstance(params, list) else (params["a"], params["b"])
                if b == 0:
                    responses.append(make_error(id_, -32001, "Division by zero", {"b": b}))
                else:
                    responses.append(make_result(id_, a / b))

            elif method == "calc_pow":
                a, b = params if isinstance(params, list) else (params["a"], params["b"])
                responses.append(make_result(id_, math.pow(a, b)))

            elif method == "calc_sqrt":
                x = params[0] if isinstance(params, list) else params["x"]
                if x < 0:
                    responses.append(make_error(id_, -32002, "Domain error: negative input", {"x": x}))
                else:
                    responses.append(make_result(id_, math.sqrt(x)))

            elif method == "calc_mean":
                numbers = params[0] if isinstance(params, list) else params.get("numbers")
                responses.append(make_result(id_, sum(numbers) / len(numbers)))

            elif method == "calc_median":
                numbers = sorted(params[0] if isinstance(params, list) else params.get("numbers"))
                n = len(numbers)
                mid = n // 2
                if n % 2:
                    val = numbers[mid]
                else:
                    val = (numbers[mid - 1] + numbers[mid]) / 2
                responses.append(make_result(id_, val))

            elif method == "calc_factorial":
                n = params[0] if isinstance(params, list) else params["n"]
                if not (isinstance(n, int) and n >= 0):
                    responses.append(make_error(id_, -32602, "Invalid params: n must be a non-negative integer"))
                else:
                    responses.append(make_result(id_, math.factorial(n)))

            elif method == "calc_gcd":
                a, b = params if isinstance(params, list) else (params["a"], params["b"])
                responses.append(make_result(id_, math.gcd(int(a), int(b))))

            elif method == "calc_lcm":
                a, b = params if isinstance(params, list) else (params["a"], params["b"])
                responses.append(make_result(id_, lcm(int(a), int(b))))

            else:
                responses.append(make_error(id_, -32601, "Method not found"))

        except Exception as e:
            responses.append(make_error(id_, -32603, "Internal error", {"detail": str(e)}))

    return jsonify(responses if batch else responses[0]), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
