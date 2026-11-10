"""main5.md: 긴 답변의 묶음 갱신 생성기와 자동 확장 읽기 영역.

첫 조각은 즉시 표시하고 이후 문단 경계, 80자, 0.15초를 기준으로 묶는다.
시간 기준은 수신 이벤트가 도착할 때 검사한다. sleep이나 별도 대기는 없다.
줄바꿈/공백/마지막 버퍼를 보존하며 main4의 성공 이력·재시도·취소를 유지한다.
주요 변경은 [변경 1]~[변경 7] 주석 참고.
실행: streamlit run main5.py
"""

import os
import time

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# =========================================================
# 1. 기본 설정
# =========================================================

MODEL = "openai/gpt-oss-20b"

# [변경 1] 첫 조각은 즉시 표시. 이후 문단/80자/0.15초 중 하나를 만족하면 갱신.
# 시간 조건은 새 조각 도착 시 검사하며, 네트워크 대기를 강제로 깨우지 않는다.
BATCH_CHARS = 80
BATCH_SECONDS = 0.15
# BEFORE: 답변 영역의 고정 높이(초과하면 내부 스크롤).
# AFTER: 초기 최소 높이. 내용이 많아지면 브라우저가 실제 Markdown 높이만큼 늘린다.
READING_HEIGHT = 360

# 대화 이력 최대 보관 개수 (질문 + 답변 쌍)
MAX_HISTORY = 20


# =========================================================
# 2. Groq 모델 클라이언트 생성
# =========================================================

def create_client():

    key = os.getenv("GROQ_API_KEY", "").strip()

    if not key:
        raise ValueError(
            "GROQ_API_KEY 환경변수가 설정되지 않았습니다."
        )

    args = {
        "api_key": key,
        "base_url": "https://api.groq.com/openai/v1",
        "timeout": 60.0,
        "max_retries": 0
    }

    return OpenAI(**args)


# =========================================================
# 3. 메세지 조합 함수
# =========================================================

def build_input(history, question):

    system_messages = {
        "role": "system",
        "content": """
너는 여행 계획 및 관광 정보를 전문적으로 제공하는 AI 여행 Agent다.

[1. 역할과 목적]
- 사용자의 여행 목적과 요구사항을 분석하고 최적의 여행 정보를 제공한다.
- 여행지 추천, 관광 명소, 맛집, 숙박, 교통, 여행 경로,
  예상 비용, 일정 등을 종합적으로 안내한다.
- 국내 여행과 해외여행 모두 지원한다.
- 실제 여행에 활용할 수 있는 구체적이고 실용적인 답변을 제공한다.

[2. 사용자 입력 분석]
- 사용자가 제공한 여행 정보를 가장 우선적으로 반영한다.
- 여행 지역, 기간, 출발지, 인원, 예산, 교통수단,
  여행 목적, 선호 활동 등을 분석한다.
- 정보가 충분하지 않더라도 일반적인 여행 패턴과
  지역 특성을 바탕으로 합리적인 추천과 추론을 수행한다.
- 필수 정보가 부족한 경우에만 핵심 내용을 질문한다.
- 일반적인 추천 기준보다 사용자의 명시적인 조건을 우선한다.

[3. 여행지 및 관광 정보]
- 대표 관광지, 자연경관, 역사·문화 유적, 체험 활동, 축제 등을 고려한다.
- 여행자의 연령대, 동행자, 여행 목적에 적합한 장소를 추천한다.
- 관광지 간 거리와 이동 시간을 고려하여 효율적인 동선을 구성한다.
- 지역별 특색과 계절적 특성을 반영한다.
- 실제 존재 여부가 불확실한 장소를 임의로 만들어내지 않는다.

[4. 여행 일정 수립]
- 여행 기간에 맞춰 일자별 일정을 구성한다.
- 시간대, 방문 장소, 활동 내용, 이동 방법을 포함한다.
- 불필요한 장거리 이동이나 지나치게 많은 관광지를 포함하지 않는다.
- 식사, 휴식, 이동 시간을 적절하게 배분한다.
- 운영 시간과 휴무일은 확인되지 않은 경우 확인 필요로 표시한다.
- 사용자의 체력과 여행 스타일에 맞춰 일정을 제안한다.

[5. 교통 및 숙박]
- 자동차, 대중교통, 도보, 항공, 철도 등을 고려한다.
- 이동 거리와 예상 소요 시간을 안내한다.
- 숙박은 주요 관광지와의 접근성을 고려한다.
- 숙박비와 교통비를 예산에 포함한다.
- 확인되지 않은 요금이나 예약 가능 여부를 확정적으로 표현하지 않는다.

[6. 맛집 및 음식 추천]
- 지역 대표 음식과 특산물을 우선 고려한다.
- 여행 동선과 가까운 식당을 추천한다.
- 음식 종류, 가격대, 특징을 설명한다.
- 실제 영업 여부와 운영 시간은 확인이 필요한 정보임을 구분한다.
- 존재하지 않는 식당이나 메뉴를 만들어내지 않는다.

[7. 예산 및 비용 분석]
- 교통비, 숙박비, 식비, 입장료, 체험비, 기타 비용을 구분한다.
- 여행 인원과 기간을 기준으로 예상 비용을 산출한다.
- 정확한 금액을 모르는 경우 합리적인 추정 범위로 제공한다.
- 실제 가격과 예상 가격을 구분한다.
- 제한된 예산에 적합한 대안을 추천한다.

[8. 정보 신뢰성]
- 검증된 사실과 추론 또는 예상 정보를 구분한다.
- 실시간 확인이 필요한 정보는 확인되지 않은 사실처럼 답변하지 않는다.
- 외부 검색이나 API 데이터가 제공되면 해당 데이터를 우선 활용한다.
- 정보가 없으면 모른다고 설명하고 임의로 생성하지 않는다.
- 과거 정보와 현재 정보가 다를 수 있으면 최신 확인이 필요하다고 안내한다.

[9. 답변 작성 원칙]
- 한국어로 쉽고 명확하게 답변한다.
- 결론과 핵심 추천을 먼저 제시한다.
- 여행 일정은 날짜별 또는 시간대별로 구분한다.
- 장소 추천 시 이유와 특징을 함께 설명한다.
- 필요에 따라 표, 목록, 번호를 활용한다.
- 불필요한 반복과 장황한 설명은 피한다.
- 간단한 질문에는 간결하게, 상세한 계획에는 충분하게 답변한다.

[10. 최종 목표]
사용자가 별도의 여행 전문가 도움 없이도 실제 여행 계획을
수립할 수 있도록 정확하고 실용적인 정보를 제공한다.
"""
    }

    # 이전 대화 + 현재 질문
    # 시스템 메시지는 별도 instructions로 전달한다.
    return {
        "instructions": system_messages["content"],
        "input": history + [
            {
                "role": "user",
                "content": question
            }
        ]
    }


# =========================================================
# 4. 스트리밍 응답 생성
# =========================================================

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


def receive_text(stream, stats, status, started, fail_once=False):
    """API 이벤트를 텍스트로 변환하며 완료 여부와 원본 수신 통계를 기록한다."""
    for event in stream:
        if event.type == "response.output_text.delta" and event.delta:
            if stats["first"] is None:
                stats["first"] = time.perf_counter() - started
                status.update(label="🟡 수신 중 - 답변을 생성하고 있습니다.",
                              state="running", expanded=True)
                status.write(f"첫 텍스트 수신 ({stats['first']:.2f}초)")
            # 화면 갱신과 별개로 원문 전체를 기록하므로 pending에도 누락 없이 보관된다.
            stats["partial"] += event.delta
            stats["updates"] += 1
            yield event.delta
            # 첫 조각의 yield가 화면에 반영된 다음 기존 실패 재현 기능을 실행한다.
            if fail_once:
                raise RuntimeError("실패 재현: 첫 텍스트 조각 수신 후 연결을 끊었습니다.")
        elif event.type == "response.completed":
            stats["completed"] = True
            stats["total"] = time.perf_counter() - started
            usage = event.response.usage
            if usage:
                stats["usage"] = {
                    "input_tokens": usage.input_tokens,
                    "output_tokens": usage.output_tokens,
                    "total_tokens": usage.total_tokens,
                }
        elif event.type in ("response.failed", "response.incomplete", "error"):
            raise RuntimeError(f"응답이 정상적으로 완료되지 않았습니다: {event.type}")
    if not stats["completed"]:
        raise RuntimeError("서버에서 정상적인 완료 이벤트를 받지 못했습니다.")
    if not stats["partial"].strip():
        raise RuntimeError("완료 이벤트를 받았지만 텍스트 답변이 비어 있습니다.")


def render_answer(client, inputs, stats, fail_once=False):
    started = time.perf_counter()
    stats.update(first=None, total=None, partial="", updates=0,
                 renders=0, usage=None, completed=False)
    status = st.status("🔵 요청 중 - 첫 텍스트를 기다리고 있습니다.",
                       state="running", expanded=True)
    # [변경 4] BEFORE: height=READING_HEIGHT → 고정 높이를 넘으면 내부 스크롤.
    # AFTER: height="content" + 아래 main()의 min-height CSS → 초기 높이부터 자동 확장.
    # 조각 수로 높이를 추정하지 않아 줄바꿈/목록/표/화면 너비에 맞게 실제 높이가 반영된다.
    with st.container(height="content", border=True, key="reading_stream"):
        answer_placeholder = st.empty()
    answer_placeholder.info("여행 정보를 분석하고 있습니다. 잠시 기다려 주세요.")
    displayed = ""
    try:
        with client.responses.create(
            model=MODEL, input=inputs["input"], instructions=inputs["instructions"],
            stream=True, max_output_tokens=2048,
        ) as stream:
            chunks = receive_text(stream, stats, status, started, fail_once)
            for text in batch_text(chunks):
                displayed += text
                stats["renders"] += 1
                answer_placeholder.markdown(displayed + "▌")
        answer_placeholder.markdown(displayed)
        status.write(f"전체 응답 완료 ({stats['total']:.2f}초)")
        status.update(label="🟢 완료 - 답변 생성이 끝났습니다.",
                      state="complete", expanded=False)
        return stats["partial"]
    except Exception as exc:
        stats["total"] = time.perf_counter() - started
        answer_placeholder.markdown(stats["partial"] or "수신한 텍스트가 없습니다.")
        status.update(label="🔴 오류 - 응답 생성에 실패했습니다.",
                      state="error", expanded=True)
        status.write(str(exc))
        st.warning("미완성 답변입니다. 성공 대화 이력에는 저장하지 않습니다.")
        raise


# =========================================================
# 5. 응답 시간 및 사용량 출력
# =========================================================

def show_stats(stats):

    st.divider()

    st.markdown("#### 📊 응답 성능")

    col1, col2, col3 = st.columns(3)

    first = stats.get("first")
    total = stats.get("total")

    with col1:

        st.metric(
            label="첫 텍스트 수신 (TTFT)",
            value=(
                f"{first:.2f}초"
                if first is not None else "-"
            )
        )

    with col2:

        st.metric(
            label="전체 응답 시간",
            value=(
                f"{total:.2f}초"
                if total is not None else "-"
            )
        )

    with col3:

        st.metric(
            label="텍스트 수신 이벤트",
            value=stats.get("updates", 0)
        )

    # [변경 5] API 수신 횟수와 실제 묶음 갱신 횟수를 구분해 개선 효과를 확인한다.
    st.caption(f"화면 묶음 갱신: {stats.get('renders', 0)}회 "
               f"/ 텍스트 수신: {stats.get('updates', 0)}회")

    # 토큰 사용량
    usage = stats.get("usage")

    if usage:

        st.caption(
            f"입력 토큰: {usage['input_tokens']:,} | "
            f"출력 토큰: {usage['output_tokens']:,} | "
            f"총 토큰: {usage['total_tokens']:,}"
        )


# =========================================================
# 6. 메인 함수 - Streamlit UX
# =========================================================


def main():
    st.set_page_config(page_title="AI 여행 Agent", page_icon="✈️", layout="wide")
    # [변경 7] 사용자가 요청한 답변 영역에만 최소 높이를 적용한다.
    # Streamlit의 공개 key 기반 클래스를 사용하며, height="content"가 확장을 담당한다.
    st.html(f"""
    <style>
    .st-key-reading_stream,
    .st-key-reading_pending,
    [class*="st-key-reading_history_"] {{
        min-height: {READING_HEIGHT}px;
    }}
    </style>
    """)
    st.title("✈️ AI 여행 Agent")
    st.caption("Groq GPT-OSS-20B · 요청 → 수신 → 완료 · 미완성 질문 재시도/취소")

    for key, value in {
        "history": [], "stats": {}, "client": None,
        "pending": None, "fail_next": False, "success_count": 0,
    }.items():
        st.session_state.setdefault(key, value)

    with st.sidebar:
        st.subheader("설정")
        st.write(f"모델: `{MODEL}`")
        st.metric("누적 성공 대화", st.session_state.success_count)
        st.caption(f"현재 보관한 성공 대화: {len(st.session_state.history) // 2}회")
        st.write(f"미완성 질문: {int(st.session_state.pending is not None)}개")
        if st.button("한번 실패시키기", key="arm_failure", width="stretch"):
            st.session_state.fail_next = True
        if st.session_state.fail_next:
            st.info("다음 시도에서 첫 텍스트 조각을 표시한 뒤 한 번 실패합니다.")
        st.caption("버튼을 누른 뒤 질문을 제출하세요. 재시도에도 적용할 수 있습니다.")
        if st.button("대화 초기화", key="reset", width="stretch"):
            st.session_state.history = []
            st.session_state.stats = {}
            st.session_state.pending = None
            st.session_state.fail_next = False
            st.session_state.success_count = 0
            st.rerun()

    with st.expander("수정 전 / 수정 후 비교"):
        st.markdown("""
| 항목 | 수정 전 (main4.py) | 수정 후 (main5.py) |
|---|---|---|
| 화면 갱신 | 텍스트 조각마다 갱신 | 첫 조각 즉시, 이후 문단/80자/0.15초 기준 |
| 읽기 영역 | 답변 길이만큼 늘어남 | 초기 최소 360px, 내용에 맞춰 자동 확장 |
| 줄바꿈·마지막 조각 | 원문 누적 | 원문 보존 및 종료/오류 시 남은 버퍼 전달 |
| 미완성 질문 | 재시도·취소 | 기존 동작 유지 |
""")
        st.markdown("""
**답변 영역 높이: Before / After**

| 항목 | Before | After |
|---|---|---|
| 설정 | `height=READING_HEIGHT` | `height="content"` + `min-height: READING_HEIGHT` |
| 초기 높이 | 360px 고정 | 최소 360px 확보 |
| 답변이 길어질 때 | 높이 유지, 영역 내부 스크롤 | 실제 내용 높이만큼 자동 확장 |
| 적용 범위 | 생성 중·성공 이력·미완성 답변 | 세 영역 모두 자동 확장 |
""")
        st.caption("실패 → 성공 수 유지, 재시도 성공 → 1 증가, 취소 → 성공 수 유지")

    # [변경 6] 재실행 후의 성공 답변과 미완성 답변에도 같은 읽기 영역을 적용한다.
    for index, message in enumerate(st.session_state.history):
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                with st.container(height="content", border=True,
                                  key=f"reading_history_{index}"):
                    st.markdown(message["content"])
            else:
                st.markdown(message["content"])

    if st.session_state.stats:
        show_stats(st.session_state.stats)

    retry = False
    pending = st.session_state.pending
    if pending is not None:
        with st.container(border=True):
            st.subheader("미완성 질문 보관함")
            st.write(pending["question"])
            st.caption(f"시도 횟수: {pending['attempts']} · 상태: {pending['state']}")
            st.warning("이 질문과 부분 답변은 성공 대화 및 다음 요청의 과거 이력에 포함되지 않습니다.")
            if pending["error"]:
                st.error(pending["error"])
            with st.expander("미완성 답변 확인"):
                with st.container(height="content", border=True, key="reading_pending"):
                    st.markdown(pending["partial"] or "수신한 텍스트가 없습니다.")
            left, right = st.columns(2)
            retry = left.button("재시도", key="retry", width="stretch")
            if right.button("취소", key="cancel", width="stretch"):
                st.session_state.pending = None
                st.rerun()

    question = st.chat_input(
        "미완성 질문을 재시도하거나 취소하세요." if pending else "어디로 여행을 떠나고 싶으신가요?",
        key="question", disabled=pending is not None, submit_mode="disable",
    )
    if question and pending is None:
        question = question.strip()
        if not question:
            return
        # AFTER: API 호출보다 먼저 질문을 보관한다.
        st.session_state.pending = {
            "question": question, "partial": "", "error": None,
            "attempts": 0, "state": "대기",
        }
    elif not retry:
        return

    pending = st.session_state.pending
    pending.update(partial="", error=None, state="요청 중")
    pending["attempts"] += 1
    # 한 번만 소비: API 오류가 먼저 발생해도 다음 재시도에 남기지 않는다.
    fail_once = st.session_state.fail_next
    st.session_state.fail_next = False
    stats = {}
    with st.chat_message("user"):
        st.markdown(pending["question"])
    try:
        if st.session_state.client is None:
            st.session_state.client = create_client()
        inputs = build_input(st.session_state.history, pending["question"])
        with st.chat_message("assistant"):
            answer = render_answer(st.session_state.client, inputs, stats, fail_once)
    except Exception as exc:
        # 실패 시 history를 건드리지 않고 pending만 갱신한다.
        pending.update(partial=stats.get("partial", ""), error=str(exc), state="미완료")
    else:
        # render_answer가 완료 이벤트와 비어 있지 않은 답변을 확인한 경우만 저장.
        st.session_state.history = (st.session_state.history + [
            {"role": "user", "content": pending["question"]},
            {"role": "assistant", "content": answer},
        ])[-(MAX_HISTORY * 2):]
        st.session_state.success_count += 1
        st.session_state.pending = None
    st.session_state.stats = stats
    # 성공 수/보관함/버튼을 최신 상태로 즉시 다시 표시한다.
    st.rerun()


if __name__ == "__main__":
    main()
