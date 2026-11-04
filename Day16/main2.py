import os
from dotenv import load_dotenv

import requests
import streamlit as st

load_dotenv(override=True)
base_url = os.getenv('LLAMA_BASE_URL','').strip()
model = os.getenv('LLAMA_MODEL','').strip()
timeout_text = os.getenv('LLAMA_TIMEOUT_SECONDS',"180").strip()
timeout_seconds = int(timeout_text)

name = st.text_input('이름')
question = st.text_input('질문')

with st.chat_message('user'):
    st.text(f"{name} : {question}")

if st.button('ai 답변 받기'):
    headers={}
    with st.spinner('ai가 답변을 생성하고 있습니다.'):
        with requests.post(
            f"{base_url}/v1/chat/completions",  #채팅 api 주소
            headers=headers,
            json={
                "model":model,  # 서버의 --alias 와 일치
                "messages":[
                    {'role':'system','content':'한국어로 쉽고 간결하게 대답하는 에이전트다'},
                    {'role':'user','content':question},
                ],
                "temperature":0.7, # 0 ~ 1,
                "maxtoken":512,
                "stream":False,  # 토큰별 스트리밍대신 json 응답 수신
            } ,
            timeout=(5,timeout_seconds) 
        )as response:
            response.raise_for_status()
            data = response.json()  # 객체로 복원
        choice = data['choices'][0]
        answer = choice['message']['content']
        with st.chat_message('assistant'):
            st.text(answer.strip())
