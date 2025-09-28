import io
import json
from typing import Union
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import Response
from starlette.datastructures import UploadFile
from fastapi.exceptions import HTTPException
import inspect
import requests
import os
from datetime import datetime
import tempfile

localhosts = ("127.0.0.1", "localhost", "0.0.0.0")


class FastRpc:
    def __init__(self):
        self.app = FastAPI()
        self.funcs: dict[str, callable] = {}
        self.init()

    def init(self):
        @self.app.post("/run/{path}")
        async def wrapper(path, request: Request):
            form = await request.form()
            if path in self.funcs:
                func = self.funcs[path]
                sig = inspect.signature(func)
                params = {}
                for k, v in sig.parameters.items():  # 参数类型还原
                    if v.annotation is bytes:
                        file_obj = form[k]  # 直接使用索引访问，而不是 get 方法
                        # 检查是否是 UploadFile 对象
                        if isinstance(file_obj, UploadFile):
                            print(
                                f"获取到文件: {file_obj.filename}, 类型: {file_obj.content_type}"
                            )
                            params[k] = await file_obj.read()
                        else:
                            if self.host in localhosts:
                                if os.path.exists(file_obj):
                                    with open(file_obj, "rb") as f:
                                        params[k] = f.read()
                                else:
                                    raise HTTPException(
                                        status_code=400,
                                        detail=f"参数 {k} 指定的文件路径不存在: {file_obj}",
                                    )
                            else:
                                # 如果获取到的不是 UploadFile，可能是字符串或其他类型
                                print(
                                    f"参数 {k} 的类型: {type(file_obj)}, 值: {str(file_obj)[:100]}..."
                                )
                                raise HTTPException(
                                    status_code=400,
                                    detail=f"参数 {k} 需要文件但获取到的是 {type(file_obj)}",
                                )
                    elif v.annotation is str:
                        params[k] = form[k]
                    elif v.annotation is int:
                        params[k] = int(form[k])
                    elif v.annotation is float:
                        params[k] = float(form[k])
                    elif v.annotation is datetime:
                        params[k] = datetime.fromisoformat(form[k])
                    elif v.annotation is dict:
                        params[k] = json.loads(form[k])
                    elif v.annotation is list:
                        params[k] = json.loads(form[k])
                    elif v.annotation is bool:
                        params[k] = bool(form[k])
                    else:
                        params[k] = form[k]
                r = self.funcs[path](**params)  # 返回类型转换
                if type(r) is bytes:
                    if self.host in localhosts:
                        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                            tmp_file.write(r)
                            temp_path = tmp_file.name  # 文件不会自动删除
                        return Response(
                            content=temp_path,
                            media_type="text/plain",
                        )
                    else:
                        return Response(
                            content=r,
                            media_type="application/octet-stream",  # 通用二进制类型
                            headers={
                                f"Content-Disposition": "attachment; filename={path}"
                            },
                        )
                if type(r) is bool:
                    return 1 if r else 0
                return r

        @self.app.get("/funcs")
        def wrapper():
            r = {}
            for name, f in self.funcs.items():
                sig = inspect.signature(f)

                r[name] = {
                    "params": {
                        k: v.annotation.__name__ for k, v in sig.parameters.items()
                    },
                    "return": sig.return_annotation.__name__,
                }
            return r

    def path(self, path):
        def decorator(func):

            # 验证函数签名
            sig = inspect.signature(func)
            if sig.return_annotation not in (
                bytes,
                str,
                int,
                float,
                datetime,
                dict,
                list,
                bool,
            ):
                raise ValueError(
                    f"Return type {sig.return_annotation.__name__} must be bytes, str, int, float, datetime, dict, list"
                )
            for param_name, param in sig.parameters.items():
                if param.annotation not in (
                    bytes,
                    str,
                    int,
                    float,
                    datetime,
                    dict,
                    list,
                    bool,
                ):
                    raise ValueError(
                        f"Parameter {param_name} must be bytes, UploadFile, str, int, float, datetime, dict, list"
                    )

                if (
                    param.annotation is bytes
                    and param.default is not inspect.Parameter.empty
                ):
                    raise ValueError(
                        f"File parameter {param_name} cannot have default value"
                    )

            self.funcs[path] = func

            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    def run(self, host="0.0.0.0", port=8000):
        self.host = host
        self.port = port
        uvicorn.run(self.app, host=host, port=port)


class FastRpcClient:
    def __init__(self, host="127.0.0.1", port=8000):
        self.host = host
        self.port = port
        self.url = f"http://{host}:{port}"
        self.session = requests.Session()
        self.funs = self.get_funs()

    def __getattr__(self, funcname, *args, **kwargs):
        def wrapper(*args, **kwargs):
            params = {}
            files = {}
            params_list = list(self.funs[funcname]["params"].keys())
            params_dict = self.funs[funcname]["params"]
            for i, v in enumerate(args):
                if type(v) is str:
                    if os.path.exists(v) and params_list[i] == "bytes":
                        if self.host in localhosts:
                            params[params_list[i]] = v
                        else:
                            with open(v, "rb") as f:
                                files[params_list[i]] = (os.path.basename(v), f)
                    else:
                        params[params_list[i]] = v
                elif type(v) is bytes:
                    files[params_list[i]] = (params_list[i], io.BytesIO(v))
                elif type(v) is int:
                    params[params_list[i]] = str(v)
                elif type(v) is float:
                    params[params_list[i]] = str(v)
                elif type(v) is datetime:
                    params[params_list[i]] = v.isoformat()
                elif type(v) is dict:
                    params[params_list[i]] = json.dumps(v)
                elif type(v) is list:
                    params[params_list[i]] = json.dumps(v)
                elif type(v) is bool:
                    params[params_list[i]] = 1 if v else 0
                else:
                    params[params_list[i]] = v
            for k, v in kwargs.items():  # 参数类型转换
                if type(v) is str:
                    if os.path.exists(v) and params_dict[k] == "bytes":
                        if self.host in localhosts:
                            params[k] = v
                        else:
                            with open(v, "rb") as f:
                                files[k] = (os.path.basename(v), f)
                    else:
                        params[k] = v
                elif type(v) is bytes:
                    files[k] = (k, io.BytesIO(v))
                elif type(v) is int:
                    params[k] = str(v)
                elif type(v) is float:
                    params[k] = str(v)
                elif type(v) is datetime:
                    params[k] = v.isoformat()
                elif type(v) is dict:
                    params[k] = json.dumps(v)
                elif type(v) is list:
                    params[k] = json.dumps(v)
                elif type(v) is bool:
                    params[k] = 1 if v else 0
                else:
                    params[k] = v
            r = self.session.post(
                self.url + f"/run/{funcname}", data=params, files=files
            )
            r_type = self.funs[funcname]["return"]  # 返回类型还原
            if r_type == "bytes":
                if self.host in localhosts:
                    print(f"Received local file: {r.text}")
                    with open(r.text, "rb") as f:
                        content = f.read()
                    os.remove(r.text)  # 删除临时文件
                    return content
                return r.content
            elif r_type == "str":
                return r.text
            elif r_type == "int":
                return int(r.text)
            elif r_type == "float":
                return float(r.text)
            elif r_type == "datetime":
                return datetime.fromisoformat(json.loads(r.text))
            elif r_type == "dict":
                return json.loads(r.text)
            elif r_type == "list":
                return json.loads(r.text)
            elif r_type == "bool":
                return r.text == "1"
            else:
                return r.text

        return wrapper

    def get_funs(self):
        return self.session.get(self.url + "/funcs").json()
