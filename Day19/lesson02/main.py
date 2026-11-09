"""2차시: 화면이 다시 실행되어도 대화 기록을 보관한다."""
import os

import streamlit as st
from dotenv import load_dotenv, find_dotenv
from openai import APIConnectionError, APIStatusError, OpenAI

st.title("화면에서 이어가는 멀티턴 대화")
load_dotenv(find_dotenv(), override=False, interpolate=False)
API_KEY = os.getenv("GROQ_API_KEY", None)

if API_KEY is None:
    st.error(".env의 GROQ_API_KEY를 확인하세요.")
    st.stop()

def ensure_history():
    # 시작 코드: 화면이 실행될 때마다 목록을 덮어쓴다. 이 함수만 수정한다.
    st.session_state["messages"] = []

# ensure_history()
print('코드 재실행')

st.button("화면 다시 실행")

if st.button("새 대화"):
    st.session_state["messages"] = []
    st.rerun()
if st.session_state:
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.text(message["content"])
else:
    st.session_state['messages'] = []
    
question = st.chat_input("질문을 입력하세요")
if question and question.strip():
    question = question.strip()
    # if len(question) > 1000:
    #     st.warning("질문은 1000자 이내로 입력하세요.")
    #     st.stop()
    messages = [{"role": "system", "content": "한국어로 두 문장 안에서 답하세요. 대화에 나온 정보를 사용하고 모르는 개인 정보는 모른다고 말하세요."}]
    messages += st.session_state["messages"] + [{"role": "user", "content": question}]
    st.caption(f"이번 요청에 포함한 이전 메시지: {len(messages) - 2}개")
    try:
        client = OpenAI(
            api_key=os.environ["GROQ_API_KEY"],
            base_url="https://api.groq.com/openai/v1",
        )
        response = client.responses.create(
            input=messages,
            model="openai/gpt-oss-20b",
        )
        answer = response.output_text
        if not answer or not answer.strip():
            st.error("빈 답변을 받았습니다. 질문을 다시 입력하세요.")
            st.stop()
    except (APIConnectionError, APIStatusError):
        st.error("모델 API 연결을 확인하고 질문을 다시 입력하세요.")
        st.stop()
    st.session_state["messages"].extend([
        {"role": "user", "content": question},
        {"role": "assistant", "content": answer.strip()},
    ])
    for message in st.session_state["messages"][-2:]:
        with st.chat_message(message["role"]):
            st.text(message["content"])