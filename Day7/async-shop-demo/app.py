import asyncio
import threading
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="Sync vs Async Shop Demo",
    description="상품 재고 조회로 동기 블로킹과 비동기 처리를 비교하는 학습 앱",
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


PRODUCTS = {
    1: {"name": "무선 키보드", "stock": 12, "warehouse": "서울 A센터"},
    2: {"name": "USB-C 허브", "stock": 7, "warehouse": "인천 B센터"},
    3: {"name": "웹캠", "stock": 21, "warehouse": "부산 C센터"},
}


def get_product(product_id: int) -> dict:
    """오래 걸리는 기존 동기 재고 시스템을 흉내 낸다."""
    time.sleep(2)
    product = PRODUCTS.get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    return {**product, "lookup_thread": threading.current_thread().name}


def response_payload(product_id: int, product: dict, mode: str) -> dict:
    return {
        "product_id": product_id,
        "mode": mode,
        **product,
    }


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
async def health():
    return {"status": "ok", "thread": threading.current_thread().name}


@app.get("/api/products/blocking/{product_id}")
async def blocking_product(product_id: int):
    # 학습을 위한 의도적인 문제: 이벤트 루프 스레드에서 동기 함수를 직접 호출한다.
    product = get_product(product_id)
    return response_payload(product_id, product, "blocking")


@app.get("/api/products/async/{product_id}")
async def async_product(product_id: int):
    # 비동기 재고 API를 기다리는 상황을 흉내 낸다.
    await asyncio.sleep(2)
    product = PRODUCTS.get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    product = {**product, "lookup_thread": threading.current_thread().name}
    return response_payload(product_id, product, "async")


@app.get("/api/products/threaded/{product_id}")
async def threaded_product(product_id: int):
    # 비동기 API가 없는 기존 동기 함수를 작업 스레드로 보낸다.
    product = await asyncio.to_thread(get_product, product_id)
    return response_payload(product_id, product, "threaded")

