"""07장 실습 시작용 FastAPI: 아래 TODO 세 군데를 구현하세요."""
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title='Chapter 07 - Student Practice')


class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=80)
    done: bool = False


class TaskOut(TaskIn):
    id: int


_db: dict[int, TaskOut] = {}
_next_id = 1


@app.get('/tasks', response_model=list[TaskOut])
def list_tasks():
    return list(_db.values())


@app.post('/tasks', status_code=status.HTTP_201_CREATED, response_model=TaskOut)
def add_task(payload: TaskIn):
    # TODO 1: 다음 ID로 TaskOut 생성, _db에 저장, 반환
    raise HTTPException(status_code=501, detail='TODO 1')


@app.get('/tasks/{task_id}', response_model=TaskOut)
def get_task(task_id: int):
    # TODO 2: 있으면 반환, 없으면 HTTPException(404)
    raise HTTPException(status_code=501, detail='TODO 2')


@app.patch('/tasks/{task_id}', response_model=TaskOut)
def patch_task(task_id: int, payload: dict):
    # TODO 3: dict 대신 별도의 Pydantic Patch 모델을 만들고 exclude_unset=True 적용
    raise HTTPException(status_code=501, detail='TODO 3')
