from fastrpc import FastRpcClient
from datetime import datetime
import time

c = FastRpcClient()

print(c.echo_int(1))
print(c.echo_float(1.0))
print(c.echo_bool(True))
print(c.echo_list([1, 2, 3]))
print(c.echo_dict({"a": 1, "b": 2}))
start = time.time()
file = "/home/c/project/vam/back/media/videos/2025/9/4/1a892844-1ce4-4561-b016-48950c675e33.mp4"
with open("output.mp4", "wb") as f:
    f.write(c.echo_bytes(file))
end = time.time()
print(f"[方式1] 传路径，耗时：{end - start:.2f} 秒")


start = time.time()
with open(file, "rb") as f:
    r = c.echo_bytes(f.read())
    with open("output2.mp4", "wb") as f2:
        f2.write(r)
end = time.time()
print(f"[方式2] 传内容，耗时：{end - start:.2f} 秒")


print(c.echo_str("123"))
print(c.echo_datetime(datetime.now()))
