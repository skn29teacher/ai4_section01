
from openai import OpenAI

# 1. LM Studio 로컬 서버 연결
client = OpenAI(
    base_url="http://localhost:1235/v1",
    api_key="lm-studio"
)

# 2. 사용 가능한 모델 확인
models = client.models.list()

if not models.data:
    raise RuntimeError("사용 가능한 모델이 없습니다.")

model_id = models.data[0].id
print(f"사용 모델: {model_id}")
print("AI 챗봇을 시작합니다. 종료하려면 'exit'를 입력하세요.")

# 3. 대화 기록 초기화
messages = [
    {
        "role": "system",
        "content": "당신은 친절하고 정확하게 답변하는 한국어 AI 도우미입니다."
    }
]

# 4. 사용자와 대화
while True:
    user_input = input("\n사용자: ").strip()

    if user_input.lower() in ["exit", "quit", "종료"]:
        print("챗봇을 종료합니다.")
        break

    if not user_input:
        continue

    # 사용자 메시지 추가
    messages.append({
        "role": "user",
        "content": user_input
    })

    try:
        # 5. LM Studio 모델에 답변 요청
        response = client.chat.completions.create(
            model=model_id,
            messages=messages,
            temperature=0.7
        )

        # 6. AI 응답 출력
        answer = response.choices[0].message.content
        print(f"\nAI: {answer}")

        # 7. 대화 기록에 AI 응답 추가
        messages.append({
            "role": "assistant",
            "content": answer
        })

    except Exception as e:
        print(f"오류 발생: {e}")
        # 실패한 사용자 메시지는 대화 기록에서 제거
        messages.pop()
