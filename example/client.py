from fastrpc import FastRpcClient
from datetime import datetime

c = FastRpcClient()

print(c.echo_int(1))
print(c.echo_float(1.0))
print(c.echo_bool(True))
print(c.echo_list([1, 2, 3]))
print(c.echo_dict({"a": 1, "b": 2}))
print(c.echo_bytes(b"123"))
print(c.echo_str("123"))
print(c.echo_datetime(datetime.now()))
