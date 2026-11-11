"""개인화 여행 챗봇. Windows CMD: python -m streamlit run main.py"""
import os
import time
from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import json
import psycopg
from psycopg.types.json import Jsonb

# Cloud의 최상위 Secrets 환경변수가 로컬 파일보다 우선합니다.
load_dotenv(".env", override=False, interpolate=False)
MODEL = "openai/gpt-oss-20b"
MAX_HISTORY = 20
BATCH_CHARS = 80
BATCH_SECONDS = 0.15
APP_VERSION = "0.5.0"
BASE_PROMPT = """너는 한국어 여행 계획 도우미다. 사용자의 명시적 조건을 우선한다.
일정, 동선, 예상 비용을 설명하되 확인하지 않은 운영시간, 가격, 예약 가능 여부는 확인 필요로 표시한다.
검색 도구로 실시간 조회하지 않았음을 전제로 답한다. 존재하지 않는 장소를 만들지 않는다.
민감한 개인정보를 요구하지 않는다. 사용자의 현재 질문이 프로필보다 구체적이면 현재 질문을 우선한다."""


def required_env(name):
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"{name} 설정을 확인하세요.")
    return value


def create_client():
    return OpenAI(api_key=required_env("GROQ_API_KEY"),
                  base_url="https://api.groq.com/openai/v1", timeout=60.0, max_retries=0)


def itinerary_rule(profile):
    return "하루 방문지는 4곳 이내로 제안한다."


def improvement_policy():
    return "p1", ""


def build_input(history, question, profile):
    version, improvement = improvement_policy()
    preference = (f"여행 스타일: {profile['style']}\n이동 수단: {profile['transport']}\n"
                  f"답변 형식: {profile['format']}")
    # 모델 이력에는 role/content만 보냅니다. 답변 ID와 피드백은 모델 입력이 아닙니다.
    messages = [{"role": item["role"], "content": item["content"]} for item in history]
    return {"instructions": BASE_PROMPT + "\n" + preference + "\n" + itinerary_rule(profile) + "\n" + improvement,
            "input": messages + [{"role": "user", "content": question}], "prompt_version": version}


def init_state():
    initial = {"history": [], "pending": None, "stats": {}, "profile":
               {"style": "여유롭게", "transport": "대중교통", "format": "시간대별 표"},
               "success_count": 0, "feedback": {}, "db_ready": False, "pending_feedback": None, "feedback_attempts": 0, "fail_save_once": False}
    for key, value in initial.items():
        st.session_state.setdefault(key, value)


def profile_sidebar():
    with st.sidebar:
        st.subheader("여행 취향")
        st.caption("프로필과 대화는 현재 브라우저 연결에서 유지됩니다. 새 연결에서는 초기화됩니다.")
        with st.form("profile_form"):
            style = st.selectbox("여행 스타일", ["여유롭게", "다양한 체험", "먹거리 중심"], key="profile_style")
            transport = st.selectbox("이동 수단", ["대중교통", "자가용", "도보 중심"], key="profile_transport")
            answer_format = st.selectbox("답변 형식", ["시간대별 표", "핵심 목록"], key="profile_format")
            confirm = st.checkbox("프로필 변경 시 현재 대화 초기화에 동의", key="profile_confirm")
            submitted = st.form_submit_button("프로필 적용")
        if submitted:
            candidate = {"style": style, "transport": transport, "format": answer_format}
            if candidate != st.session_state.profile and (st.session_state.history or st.session_state.pending) and not confirm:
                st.warning("프로필을 바꾸려면 대화 초기화에 동의하세요.")
            else:
                if candidate != st.session_state.profile:
                    st.session_state.history = []
                    st.session_state.pending = None
                    st.session_state.stats = {}
                st.session_state.profile = candidate
                st.success("프로필을 적용했습니다.")
        st.write("현재 적용 프로필", st.session_state.profile)
        st.metric("누적 성공 대화", st.session_state.success_count)
        if st.button("새 대화", key="new_chat"):
            st.session_state.history = []
            st.session_state.pending = None
            st.session_state.stats = {}
            st.rerun()


def batch_text(chunks, max_chars=BATCH_CHARS, max_seconds=BATCH_SECONDS,
               clock=time.perf_counter):
    """원문을 보존하면서 화면 갱신용 문자열을 생성한다. sleep은 사용하지 않는다."""
    if max_chars <= 0 or max_seconds <= 0:
        raise ValueError("묶음 크기와 시간은 양수여야 합니다.")
    buffer = ""
    first = True
    last_flush = clock()
    try:
        for chunk in chunks:
            if not chunk:
                continue
            # [변경 2] strip/split을 사용하지 않아 줄바꿈·공백·목록 들여쓰기를 보존한다.
            buffer += chunk
            now = clock()
            if (first or "\n\n" in buffer or len(buffer) >= max_chars
                    or now - last_flush >= max_seconds):
                text, buffer = buffer, ""
                first = False
                last_flush = now
                yield text
    except Exception:
        # [변경 3] 수신 도중 오류가 나도 아직 표시하지 못한 조각을 먼저 전달한다.
        if buffer:
            yield buffer
        raise
    else:
        # 종료 시 기준보다 짧은 마지막 조각도 반드시 한 번 전달한다.
        if buffer:
            yield buffer



def requires_reason(rating):
    return False


def make_record(item, rating, reason):
    return {"message_id": item["message_id"], "rating": rating, "reason": reason, "profile": deepcopy(item["profile"]), "model": MODEL,
            "app_version": item["app_version"], "prompt_version": item["prompt_version"],
            "created_at": datetime.now(timezone.utc).isoformat()}


def show_feedback(item):
    message_id = item["message_id"]
    st.caption(f"답변 ID: {message_id}")
    with st.form(f"feedback_{message_id}"):
        rating_text = st.radio("답변이 도움이 되었나요?", ["도움이 됨", "개선 필요"], horizontal=True,
                               key=f"rating_{message_id}")
        reason = st.selectbox("개선 이유", ["선택 없음", "조건 미반영", "정보 불확실", "너무 김", "기타"], key=f"reason_{message_id}")
        st.caption("저장 항목: 평가, 이유, 여행 취향 선택값, 버전, 답변 ID, 시간")
        consent = st.checkbox("이 피드백의 저장에 동의합니다.", key=f"consent_{message_id}")
        submitted = st.form_submit_button("피드백 저장")
    if submitted:
        rating = int(rating_text == "도움이 됨")
        if requires_reason(rating) and reason == "선택 없음":
            st.warning("개선 이유를 선택하세요.")
            return
        if not consent:
            st.warning("저장하려면 피드백 저장에 동의하세요.")
            return
        record = make_record(item, rating, reason)
        if st.session_state.pending_feedback is not None:
            st.warning("먼저 보관 중인 피드백을 재시도하거나 취소하세요.")
            return
        st.session_state.pending_feedback = deepcopy(record)
        st.session_state.feedback_attempts = 0
        try:
            persist_record(record)
        except Exception:
            pass
        st.rerun()
    if message_id in st.session_state.feedback:
        st.caption("피드백 저장 완료")
        saved = st.session_state.feedback[message_id]
        st.write({"저장된 평가": saved["rating"], "저장된 이유": saved["reason"]})


def export_record(record):
    return dict(record)


def show_exports():
    with st.expander("이 연결에서 저장한 피드백"):
        records = list(st.session_state.feedback.values())
        st.write(f"현재 연결의 피드백: {len(records)}개")
        st.caption("질문·답변 전문과 이름·연락처는 피드백에 수집하지 않습니다.")
        data = "\n".join(json.dumps(export_record(record), ensure_ascii=False) for record in records)
        st.download_button("내 피드백 JSONL 다운로드", data, "my_feedback.jsonl", "application/x-ndjson")


def database_connection():
    # Supabase Connect 화면의 Session pooler URI를 서버 환경변수에 저장합니다.
    return psycopg.connect(required_env("DATABASE_URL"), sslmode="require", connect_timeout=10, prepare_threshold=None)


def prepare_database():
    with database_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS public.kdt_travel_feedback (
                message_id uuid PRIMARY KEY,
                rating smallint NOT NULL CHECK (rating IN (0, 1)),
                reason text NOT NULL,
                profile jsonb NOT NULL,
                model text NOT NULL,
                app_version text NOT NULL,
                prompt_version text NOT NULL,
                created_at timestamptz NOT NULL
            )
        """)
        # 공개 REST 접속을 통한 전체 피드백 조회를 열지 않습니다.
        conn.execute("ALTER TABLE public.kdt_travel_feedback ENABLE ROW LEVEL SECURITY")
        conn.execute("REVOKE ALL ON public.kdt_travel_feedback FROM anon, authenticated")


def database_record(record):
    return dict(record)


def save_feedback(record):
    row = database_record(record)
    with database_connection() as conn:
        conn.execute("""
            INSERT INTO public.kdt_travel_feedback
                (message_id, rating, reason, profile, model, app_version, prompt_version, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (message_id) DO UPDATE SET
                rating = EXCLUDED.rating, reason = EXCLUDED.reason, created_at = EXCLUDED.created_at
        """, (row["message_id"], row["rating"], row["reason"], Jsonb(row["profile"]), row["model"],
              row["app_version"], row["prompt_version"], row["created_at"]))


def database_sidebar():
    with st.sidebar:
        if not st.session_state.db_ready:
            st.caption("처음 실행할 때 연결한 DB에 피드백 표를 준비합니다.")
            if st.button("피드백 테이블 준비", key="prepare_database"):
                try:
                    prepare_database()
                except Exception:
                    st.error("DB 준비 실패: DATABASE_URL과 프로젝트 상태를 확인하세요.")
                else:
                    st.session_state.db_ready = True
                    st.success("피드백 테이블 준비 완료")
        else:
            st.caption("피드백 테이블 준비 완료")


def retry_allowed(attempts):
    return True


def persist_record(record):
    # 같은 payload와 ID를 재사용합니다. 실패 후 새 ID를 만들지 않습니다.
    st.session_state.feedback_attempts += 1
    if os.getenv("SHOW_DEMO_TOOLS", "false").strip().lower() == "true" and st.session_state.fail_save_once:
        st.session_state.fail_save_once = False
        raise RuntimeError("저장 전 연결 실패 재현")
    save_feedback(record)
    st.session_state.feedback[record["message_id"]] = deepcopy(record)
    st.session_state.pending_feedback = None
    st.session_state.feedback_attempts = 0


def show_pending_feedback():
    with st.sidebar:
        if os.getenv("SHOW_DEMO_TOOLS", "false").strip().lower() == "true":
            if st.button("다음 피드백 저장 한 번 실패", key="arm_save_failure"):
                st.session_state.fail_save_once = True
            if st.session_state.fail_save_once:
                st.info("다음 피드백 저장 직전에 한 번 실패합니다.")
    record = st.session_state.pending_feedback
    if record is None:
        return
    st.warning("저장하지 못한 피드백이 있습니다. 재시도하거나 취소하세요.")
    st.write({"message_id": record["message_id"], "rating": record["rating"], "reason": record["reason"]})
    st.caption(f"저장 시도: {st.session_state.feedback_attempts}회")
    permitted = retry_allowed(st.session_state.feedback_attempts)
    if not permitted:
        st.info("재시도 한도입니다. 취소 후 평가를 다시 작성하세요.")
    if st.button("피드백 재시도", key="retry_feedback", disabled=not permitted):
        try:
            persist_record(record)
        except Exception:
            pass  # 보관된 record를 그대로 두고 동일한 오류 안내를 유지합니다.
        st.rerun()
    if st.button("피드백 취소", key="cancel_feedback"):
        st.session_state.pending_feedback = None
        st.session_state.feedback_attempts = 0
        st.rerun()

def receive_text(stream, stats, status, started):
    for event in stream:
        if event.type == "response.output_text.delta" and event.delta:
            if stats["first"] is None:
                stats["first"] = time.perf_counter() - started
                status.update(label="수신 중", state="running")
            stats["partial"] += event.delta
            yield event.delta
        elif event.type == "response.completed":
            stats["completed"] = True
        elif event.type in ("response.failed", "response.incomplete", "error"):
            raise RuntimeError("응답 미완료")
    if not stats["completed"] or not stats["partial"].strip():
        raise RuntimeError("정상 완료된 텍스트가 없습니다.")


def render_answer(client, inputs, stats):
    started = time.perf_counter()
    stats.update(first=None, partial="", completed=False)
    status = st.status("요청 중", expanded=True)
    display = st.empty()
    shown = ""
    try:
        with client.responses.create(model=MODEL, input=inputs["input"],
                instructions=inputs["instructions"], stream=True, max_output_tokens=2048) as response_stream:
            for text in batch_text(receive_text(response_stream, stats, status, started)):
                shown += text
                display.markdown(shown + "▌")
        display.markdown(shown)
        status.update(label="답변 완료", state="complete", expanded=False)
        return stats["partial"]
    except Exception:
        display.markdown(stats["partial"] or "수신한 텍스트가 없습니다.")
        status.update(label="답변 미완료", state="error")
        raise
    finally:
        stats["total"] = time.perf_counter() - started


def show_chat():
    for item in st.session_state.history:
        with st.chat_message(item["role"]):
            st.markdown(item["content"])
            if item["role"] == "assistant":
                show_feedback(item)
    if st.session_state.stats:
        total = st.session_state.stats.get("total", 0)
        st.caption(f"최근 시도 응답 시간: {total:.2f}초")


def run_question():
    retry = False
    pending = st.session_state.pending
    if pending is not None:
        st.warning("미완성 질문입니다. 재시도하거나 취소할 수 있습니다.")
        st.write(pending["question"])
        with st.expander("미완성 답변"):
            st.markdown(pending["partial"] or "아직 받은 텍스트가 없습니다.")
        retry = st.button("질문 재시도", key="retry_question")
        if st.button("질문 취소", key="cancel_question"):
            st.session_state.pending = None
            st.rerun()
    question = st.chat_input("여행 지역과 기간을 입력하세요.", key="question", disabled=pending is not None)
    if question and pending is None:
        question = question.strip()
        if not question:
            return
        
        st.session_state.pending = {"question": question, "partial": "", "profile": deepcopy(st.session_state.profile)}
    elif not retry:
        return
    
    pending = st.session_state.pending
    stats = {}
    inputs = build_input(st.session_state.history, pending["question"], pending["profile"])
    try:
        with st.chat_message("user"):
            st.markdown(pending["question"])
        with st.chat_message("assistant"):
            answer = render_answer(create_client(), inputs, stats)
    except Exception:
        # SDK 오류 원문에는 요청 정보가 포함될 수 있어 화면과 로그에 출력하지 않습니다.
        pending["partial"] = stats.get("partial", "")
        st.session_state.stats = stats
        st.rerun()
    else:
        assistant = {"role": "assistant", "content": answer, "message_id": str(uuid4()),
                     "profile": deepcopy(pending["profile"]), "app_version": APP_VERSION,
                     "prompt_version": inputs["prompt_version"]}
        st.session_state.history = (st.session_state.history + [
            {"role": "user", "content": pending["question"]}, assistant])[-MAX_HISTORY * 2:]
        st.session_state.pending = None
        st.session_state.success_count += 1
        st.session_state.stats = stats
        st.rerun()


def main():
    st.set_page_config(page_title="개인화 여행 챗봇", page_icon="✈️")
    st.title("✈️ 개인화 여행 챗봇")
    if not os.getenv("GROQ_API_KEY", "").strip():
        st.warning("GROQ_API_KEY 설정을 확인하세요.")
    init_state()
    profile_sidebar()
    database_sidebar()
    show_pending_feedback()
    show_exports()
    show_chat()
    run_question()


if __name__ == "__main__":
    main()
