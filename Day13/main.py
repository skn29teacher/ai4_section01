# Supabase Auth 연결 이메일 회원가입 API
# 두개 계정으로 가입 -로그인-메모접근-갱신-로그아웃
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel,ConfigDict,EmailStr,Field, SecretStr
from supabase.client import ClientOptions

# 환경변수 load
load_dotenv(override=True)

supabase_url = os.getenv("SUPABASE_URL","").strip().rstrip("/")
supabase_key = os.getenv('SUPABASE_PUBLISHABLE_KEY',"").strip()
if not supabase_url or not supabase_key:
    raise RuntimeError('SUPABASE_URL or SUPABASE_PUBLISHABLE_KEY missing')

app = FastAPI(title="Supabase Auth - 회원가입")
# pydentic을 이용한 타입검사
class SignupRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    email : EmailStr
    password : SecretStr = Field(min_length=8, max_length=128)

class SignupResponse(BaseModel):
    message : str

@app.exception_handler(RequestValidationError)
async def handelr_validation_error(_request:Request, exc:RequestValidationError):
    errors = [
        {'loc':error['loc'], 'type' : error['type']}
        for error in exc.erros()
    ]
    return JSONResponse(status_code=422,content={'detail':errors})

import httpx
from supabase import create_client, AuthApiError,AuthRetryableError

@app.post('/auth/signup',response_model=SignupResponse)
def signup(body:SignupRequest):
    try:
        # 요청할때마다 클라이언를 만들고 통신이 끝나면 자동으로 닫는다
        with httpx.Client(timeout=10.0) as http_client:
            supabase = create_client(
                supabase_url=supabase_url,
                supabase_key=supabase_key,
                options=ClientOptions(
                    persist_session=False,
                    auto_refresh_token=False,
                    httpx_client=http_client
                )
            )
            supabase.auth.sign_up(
                {
                    'email':str(body.email),
                    'password':body.password.get_secret_value()
                }
            )
    except AuthApiError as err:
        if err.status == 429:
            raise HTTPException(429,'요청이 많습니다. 잠시 후 다시 시도하세요')
        if err.status >=500 or err.status ==401:
            raise HTTPException(503,'인증 서비스 상태 또는 연결 설정을 확인')
        raise HTTPException(400,'입력과 auth 설정을 확인하세요')
    except (AuthRetryableError, httpx.HTTPError):
        raise HTTPException(503,'인증서비스에 연결할수 없습니다. 잠시후 다시 시도하세요')
    return SignupResponse(message="가입요청을 처리했습니다. 이메일 확인 설정이 켜져있다면 받은 메일을 확인")

