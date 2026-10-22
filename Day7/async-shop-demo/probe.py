import asyncio
from time import perf_counter

import httpx


BASE_URL = "http://127.0.0.1:8010"


async def request_product(
    client: httpx.AsyncClient,
    mode: str,
    product_id: int,
    batch_started_at: float,
):
    started_at = perf_counter()
    print(f"  상품 {product_id} 시작: +{started_at - batch_started_at:.4f}초")
    response = await client.get(f"/api/products/{mode}/{product_id}")
    response.raise_for_status()
    elapsed = perf_counter() - started_at
    print(f"  상품 {product_id} 완료: {elapsed:.2f}초")


async def compare(client: httpx.AsyncClient, mode: str):
    print(f"\n[{mode}] 요청 3개를 동시에 시작합니다.")
    started_at = perf_counter()
    await asyncio.gather(
        request_product(client, mode, 1, started_at),
        request_product(client, mode, 2, started_at),
        request_product(client, mode, 3, started_at),
    )
    print(f"  전체 완료: {perf_counter() - started_at:.2f}초")


async def main():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=20, trust_env=False) as client:
        for mode in ("blocking", "async", "threaded"):
            await compare(client, mode)


if __name__ == "__main__":
    asyncio.run(main())

