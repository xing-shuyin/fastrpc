# FastRPC
GITHUB 仓库：[xing-shuyin/fastrpc](https://github.com/xing-shuyin/fastrpc)

一个基于 FastAPI 的轻量级、高性能 RPC（远程过程调用）框架，支持多种数据类型的高效传输。

## 特性

- 🚀 **基于 FastAPI**：享受 FastAPI 的高性能和异步支持
- 📦 **多数据类型支持**：支持字符串、整数、浮点数、布尔值、列表、字典、字节流、日期时间等多种数据类型
- 📁 **文件传输**：支持二进制文件上传和下载
- 🔍 **自动类型转换**：客户端和服务器端自动进行类型序列化和反序列化
- 📋 **服务发现**：自动生成可用的函数列表和参数信息
- 🐍 **Pythonic API**：使用装饰器和魔术方法提供简洁的接口

## 安装

```bash
pip install fastrpc-py
```

## 快速开始

### 服务器端

```python
from fastrpc import FastRpc
from datetime import datetime

# 创建 FastRPC 实例
app = FastRpc()

# 注册 RPC 函数
@app.path("echo_int")
def echo_int(number: int) -> int:
    """返回传入的整数"""
    return number

@app.path("echo_float")
def echo_float(number: float) -> float:
    """返回传入的浮点数"""
    return number

@app.path("echo_bool")
def echo_bool(flag: bool) -> bool:
    """返回传入的布尔值"""
    return flag

@app.path("echo_list")
def echo_list(items: list) -> list:
    """返回传入的列表"""
    return items

@app.path("echo_dict")
def echo_dict(data: dict) -> dict:
    """返回传入的字典"""
    return data

@app.path("echo_bytes")
def echo_bytes(data: bytes) -> bytes:
    """返回传入的字节数据"""
    return data

@app.path("echo_str")
def echo_str(text: str) -> str:
    """返回传入的字符串"""
    return f"Echo: {text}"

@app.path("echo_datetime")
def echo_datetime(dt: datetime) -> datetime:
    """返回传入的日期时间"""
    return dt

@app.path("process_file")
def process_file(file_data: bytes) -> dict:
    """处理上传的文件"""
    return {
        "file_size": len(file_data),
        "processed": True,
        "message": "File processed successfully"
    }

# 启动服务器
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```

### 客户端

```python
from fastrpc import FastRpcClient
from datetime import datetime

# 创建客户端实例
client = FastRpcClient(host="127.0.0.1", port=8000)

# 调用远程函数
print("整数:", client.echo_int(42))
print("浮点数:", client.echo_float(3.14159))
print("布尔值:", client.echo_bool(True))
print("列表:", client.echo_list([1, 2, 3, 4]))
print("字典:", client.echo_dict({"name": "Alice", "age": 30}))
print("字符串:", client.echo_str("Hello FastRPC!"))
print("日期时间:", client.echo_datetime(datetime.now()))

# 文件处理
with open("example.txt", "rb") as f:
    file_content = f.read()
result = client.process_file(file_content)
print("文件处理结果:", result)

# 或者直接传递文件路径
result = client.process_file("example.txt")
print("文件处理结果:", result)
```

## API 参考

### FastRpc 类

#### `FastRpc()`
创建 FastRPC 服务器实例。

#### `@app.path(path: str)`
装饰器，用于注册 RPC 函数。
- `path`: 函数的访问路径

#### `app.run(host: str = "0.0.0.0", port: int = 8000)`
启动 RPC 服务器。
- `host`: 监听地址
- `port`: 监听端口

### FastRpcClient 类

#### `FastRpcClient(host: str = "127.0.0.1", port: int = 8000)`
创建 RPC 客户端实例。
- `host`: 服务器地址
- `port`: 服务器端口

#### 动态方法调用
客户端支持动态方法调用，方法名对应服务器端注册的函数路径：
```python
client.function_name(param1=value1, param2=value2)
```

## 支持的数据类型

### 参数类型
- `str`: 字符串
- `int`: 整数
- `float`: 浮点数
- `bool`: 布尔值
- `list`: 列表
- `dict`: 字典
- `bytes`: 字节数据（支持文件上传）
- `datetime`: 日期时间对象

### 返回类型
- `str`: 字符串
- `int`: 整数
- `float`: 浮点数
- `bool`: 布尔值
- `list`: 列表
- `dict`: 字典
- `bytes`: 字节数据（支持文件下载）
- `datetime`: 日期时间对象

## 文件传输

### 上传文件
```python
# 方式1：直接传递字节数据
with open("file.txt", "rb") as f:
    data = f.read()
client.process_file(data)

# 方式2：传递文件路径（自动读取）
client.process_file("file.txt")
```

### 下载文件
```python
# 服务器端返回 bytes 类型会自动作为文件下载
@app.path("get_file")
def get_file() -> bytes:
    with open("large_file.zip", "rb") as f:
        return f.read()
```

## 服务发现

FastRPC 提供了自动的服务发现功能：

```python
# 获取所有可用的函数
client = FastRpcClient()
print("可用函数:", client.get_funs())

# 输出示例：
# {
#   "echo_int": {
#     "params": {"text": "int"},
#     "return": "int"
#   },
#   "echo_str": {
#     "params": {"text": "str"},
#     "return": "str"
#   }
# }
```

## 错误处理

服务器端会自动验证参数类型，如果类型不匹配会返回详细的错误信息：

```python
# 如果传递错误类型的参数
try:
    client.echo_int("not_a_number")
except Exception as e:
    print("错误:", e)
```

## 高级用法

### 自定义错误处理

```python
from fastapi import HTTPException

@app.path("secure_operation")
def secure_operation(token: str, data: dict) -> dict:
    if token != "secret":
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"processed": True, "data": data}
```

### 组合多个 RPC 调用

```python
# 客户端可以链式调用多个函数
result1 = client.get_user_data(user_id=123)
result2 = client.process_data(result1)
final_result = client.save_result(result2)
```

## 性能建议

1. **重用客户端连接**：创建一次客户端实例并重复使用
2. **批量处理**：对于大量数据，考虑使用批量处理函数
3. **文件压缩**：传输大文件时考虑压缩
4. **连接池**：客户端默认使用 requests.Session 保持连接

## 开发指南

### 安装开发版本

```bash
git clone https://github.com/yourusername/fastrpc.git
cd fastrpc
pip install -e .
```

### 运行测试

```bash
# 启动测试服务器
python examples/server.py

# 运行客户端测试
python examples/client.py
```

## 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 LICENSE 文件了解详情。

## 更新日志
### v0.1.2
- 加速本地文件传输

### v0.1.0
- 初始版本发布
- 支持基本数据类型传输
- 文件上传下载功能
- 自动服务发现

## 技术支持

如果您遇到问题或有建议：
- 提交 https://github.com/yourusername/fastrpc/issues
- 发送邮件至: your.email@example.com

## 相关项目

- https://fastapi.tiangolo.com/ - 现代、快速的 Web 框架
- https://docs.python-requests.org/ - 优雅的 HTTP 客户端
- https://www.uvicorn.org/ - 快速的 ASGI 服务器

---

享受使用 FastRPC！ 🚀