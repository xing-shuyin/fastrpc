from fastrpc import FastRpc
from datetime import datetime

f = FastRpc()


@f.path("echo_int")
def echo_int(text: int) -> int:
    return text


@f.path("echo_float")
def echo_float(text: float) -> float:
    return text


@f.path("echo_bool")
def echo_bool(text: bool) -> bool:
    return text


@f.path("echo_list")
def echo_list(text: list) -> list:
    return text


@f.path("echo_dict")
def echo_dict(text: dict) -> dict:
    return text


@f.path("echo_bytes")
def echo_bytes(text: bytes) -> bytes:
    return text


@f.path("echo_str")
def echo_str(text: str) -> str:
    return text


@f.path("echo_datetime")
def echo_datetime(text: datetime) -> datetime:
    return text


f.run()
