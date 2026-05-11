---
title: "LLM Structured Outputs Guide 2026: JSON Mode, Instructor & Outlines"
date: 2026-05-11T15:04:22+00:00
tags: ["LLM", "structured outputs", "JSON mode", "Instructor", "Outlines", "Pydantic", "AI engineering"]
description: "2026년 LLM 구조화 출력 완벽 가이드: JSON mode의 한계, Instructor vs Outlines 선택법, 프로덕션 신뢰성 확보 전략."
draft: false
cover:
  image: "/images/llm-structured-output-guide-2026.png"
  alt: "LLM Structured Outputs Guide 2026: JSON Mode, Instructor & Outlines"
  relative: false
schema: "schema-llm-structured-output-guide-2026"
---

LLM 구조화 출력(Structured Outputs)은 AI 모델이 임의의 텍스트 대신 정해진 스키마를 따르는 JSON을 반환하도록 강제하는 기술이다. 2026년 현재, 80% 이상의 기업이 구조화 출력 기반의 생성형 AI 앱을 배포 중이며, 프로덕션에서 안정적인 JSON을 얻는 것은 모든 AI 시스템의 핵심 과제가 되었다.

## What Are LLM Structured Outputs and Why Do They Matter in 2026?

LLM 구조화 출력(Structured Outputs)은 언어 모델이 자유 형식 텍스트가 아닌, 사전에 정의된 JSON 스키마를 완전히 준수하는 데이터를 반환하도록 보장하는 기술을 말한다. 단순히 JSON을 요청하는 것과는 다르다 — 스키마 강제(schema enforcement)는 필드 누락, 타입 불일치, 마크다운 펜스 오류 같은 파싱 실패를 원천 차단한다. 2026년 기준, 전 세계 67%의 기업이 LLM을 운영에 활용하고 있으며, 80% 이상이 구조화 출력 기반 앱을 배포할 것으로 예상된다. 이 수치는 단순한 실험이 아닌 실제 비즈니스 로직이 LLM 출력에 의존한다는 의미다. 프로덕션에서 구조화 출력 없이 나이브한 프롬프팅만으로 JSON을 추출하면 5~20%의 확률로 파싱 에러가 발생하고, 이는 조용한 버그(silent bug)로 이어져 데이터 파이프라인을 무너뜨린다. OpenAI, Anthropic, Google Gemini 모두 2026년 초 기준 네이티브 구조화 출력을 지원하며, 생태계는 제약적 디코딩(constrained decoding) 방식으로 수렴하고 있다. 추출(extraction), 분류(classification), 에이전트 도구 호출(tool calls) 등 거의 모든 LLM 워크플로가 신뢰할 수 있는 구조화 출력에 의존하므로, 이를 올바르게 구현하는 것은 2026년 AI 개발의 필수 기본기다.

### 왜 구조화 출력이 AI 에이전트의 핵심인가?

AI 에이전트는 도구 호출(tool calls), 라우팅 결정, 데이터 추출 등 모든 단계에서 파싱 가능한 출력에 의존한다. 구조화 출력 없이는 에이전트 파이프라인의 어느 한 단계에서 LLM이 예상치 못한 형식을 반환할 때 전체 워크플로가 중단된다. Langchain이나 LlamaIndex 같은 에이전트 프레임워크들이 구조화 출력을 핵심 기능으로 통합하는 이유가 여기에 있다.

## The Three Levels of Structured Output: From Prompting to Constrained Decoding

구조화 출력에는 신뢰성이 다른 세 가지 수준이 존재하며, 각 수준은 실패율과 구현 복잡도 사이의 트레이드오프를 가진다. 첫 번째는 **프롬프트 엔지니어링(Prompt Engineering)** 수준으로, "JSON 형식으로 반환하라"고 지시하는 방식이다. 성공률은 80~95%에 불과하며, 복잡한 스키마일수록 실패율이 높아진다. 두 번째는 **함수 호출(Function Calling / Tool Use)** 수준으로, 모델이 사전에 정의된 함수 시그니처에 맞는 인수를 생성한다. 성공률은 95~99%이며 대부분의 API 기반 앱에서 충분하다. 세 번째는 **네이티브 구조화 출력(Native Structured Output)** 수준으로, `type: json_schema`와 `strict: true`를 사용해 모델이 제약적 디코딩으로 스키마를 100% 준수한다. 프로덕션 데이터 파이프라인, 에이전트 아키텍처, 금융/의료 등 고신뢰도 도메인에서는 반드시 세 번째 수준을 사용해야 한다.

| 수준 | 방법 | 신뢰성 | 사용 사례 |
|------|------|--------|-----------|
| 1 | 프롬프트 엔지니어링 | 80~95% | 프로토타입, 단순 추출 |
| 2 | 함수 호출 / Tool Use | 95~99% | 일반 API 앱, 에이전트 |
| 3 | 네이티브 구조화 출력 | ~100% | 프로덕션, 데이터 파이프라인 |

### 어떤 수준을 선택해야 하는가?

실험과 프로토타입에는 레벨 1이 빠르다. 그러나 출력이 다른 시스템의 입력이 되거나 스키마가 5개 이상의 필드를 가진다면 레벨 3으로 직접 이동하라. 레벨 2는 레벨 3을 지원하지 않는 오래된 모델을 다룰 때의 중간 선택지다.

## JSON Mode vs Structured Outputs vs Function Calling — What's the Difference?

JSON mode, 구조화 출력, 함수 호출은 혼용되는 경우가 많지만 동작 방식과 신뢰성이 근본적으로 다르다. **JSON mode**는 모델이 유효한 JSON을 반환하도록 요청하는 가장 단순한 방법이다. 구조적으로 올바른 JSON을 반환하지만, 스키마 준수는 보장하지 않는다 — 필드가 누락되거나 타입이 틀릴 수 있다. 2026년 현재 JSON mode는 레거시로 간주되며, 스키마 바인딩 사용 사례에서는 deprecated된 것으로 봐야 한다. **함수 호출(Function Calling)**은 모델이 특정 함수를 호출하기 위한 인수를 생성하는 방식이다. JSON 스키마로 함수 시그니처를 정의하고, 모델은 이를 맞춰 JSON을 생성한다. **네이티브 구조화 출력**은 `response_format: {type: "json_schema", json_schema: {...}, strict: true}`를 사용해 제약적 디코딩으로 스키마를 100% 강제한다. OpenAI gpt-4o, Anthropic Claude 3.5+, Google Gemini 1.5+ 모두 이 방식을 지원한다. 2026년 프로덕션 표준은 `strict: true`를 사용한 네이티브 구조화 출력이다.

| 방식 | 스키마 보장 | 지원 범위 | 권장 사용 |
|------|------------|----------|-----------|
| JSON mode | 없음 (유효 JSON만) | 넓음 (레거시) | 사용 지양 |
| 함수 호출 | 부분적 | 대부분의 API | 에이전트 도구 호출 |
| 구조화 출력 (strict) | 100% | OpenAI, Anthropic, Gemini | 프로덕션 기본값 |

## How Constrained Decoding Works: Finite State Machines Under the Hood

제약적 디코딩(Constrained Decoding)은 LLM이 토큰을 생성할 때 스키마를 위반하는 토큰을 생성 단계에서 마스킹(masking)하여 유효하지 않은 출력을 원천적으로 불가능하게 만드는 기술이다. 구체적으로는 JSON 스키마를 유한 상태 머신(Finite State Machine, FSM)으로 변환하고, 각 생성 스텝에서 현재 FSM 상태를 기반으로 다음에 올 수 있는 유효 토큰 집합을 계산한다. LLM의 소프트맥스 출력에서 유효하지 않은 토큰의 로짓(logit)을 음의 무한대로 설정해 선택을 불가능하게 만든다. Outlines 라이브러리의 Rust 기반 `outlines-core` 0.1.0은 이 방식을 구현하여 생성 스텝당 O(1) 유효 토큰 조회를 달성했다. vLLM, TGI(Text Generation Inference), LoRAX, xinference, SGLang 등 주요 LLM 서빙 프레임워크가 Outlines를 통해 제약적 디코딩을 지원한다. 클라우드 API(OpenAI, Anthropic)도 내부적으로 동일한 원리를 적용하지만, 구현 세부사항은 공개되지 않는다. 실질적인 의미는 이렇다 — 제약적 디코딩을 사용하면 모델이 "틀린 JSON"을 생성하는 것 자체가 물리적으로 불가능해지므로, 파싱 로직이나 재시도 루프가 필요 없어진다. 이것이 Outlines가 고처리량 자체 호스팅 환경에서 선택되는 핵심 이유다.

### FSM vs 후처리(Post-processing) 접근법 비교

FSM 기반 사전 제약(pre-generation)은 생성 자체가 스키마를 따르므로 재시도가 필요 없다. 후처리(post-generation) 검증은 Instructor 같은 라이브러리가 사용하는 방식으로, 생성 후 Pydantic으로 검증하고 실패 시 자동 재시도한다. 클라우드 API에서는 post-generation이 실용적이며, 로컬/자체 호스팅 모델에서는 pre-generation이 성능과 신뢰성 모두에서 우위다.

## Provider Guide: OpenAI, Anthropic, Google Gemini, and Mistral Structured Outputs

2026년 현재 OpenAI, Anthropic, Google Gemini, Mistral 모두 네이티브 구조화 출력을 지원하지만 API 인터페이스와 지원 수준은 다르다. **OpenAI**는 `response_format: {type: "json_schema", json_schema: schema, strict: true}`로 가장 완성도 높은 구현을 제공한다. gpt-4o, gpt-4o-mini, o1 계열 모두 지원하며, 재귀 스키마와 복잡한 `$ref` 참조도 처리한다. **Anthropic Claude**는 `tool_choice: {type: "tool", name: "extract"}`와 함께 도구 정의를 통해 구조화 출력을 강제한다. Claude 3.5 Sonnet 이후로 JSON 스키마 바인딩의 신뢰성이 크게 향상되었다. **Google Gemini**는 `response_mime_type: "application/json"`과 `response_schema`를 통해 네이티브 지원한다. Gemini 1.5 Pro와 Flash 모두 지원하며, Google AI Studio에서 시각적으로 스키마를 테스트할 수 있다. **Mistral**은 `response_format: {type: "json_object"}`를 지원하지만 strict 모드가 없어 신뢰성은 OpenAI보다 낮다. Mistral Large 2 이상에서 함수 호출과 결합 시 신뢰성이 개선된다.

| 프로바이더 | Strict 모드 | 스키마 방식 | 복잡 스키마 |
|----------|------------|------------|------------|
| OpenAI gpt-4o | ✅ | json_schema + strict | ✅ |
| Anthropic Claude 3.5+ | ✅ (도구 강제) | tool_choice 강제 | ✅ |
| Google Gemini 1.5+ | ✅ | response_schema | ✅ |
| Mistral Large 2 | ❌ | json_object | 부분적 |

```python
# OpenAI 구조화 출력 예시
from openai import OpenAI
import json

client = OpenAI()

schema = {
    "name": "product_extract",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "price": {"type": "number"},
            "in_stock": {"type": "boolean"}
        },
        "required": ["name", "price", "in_stock"],
        "additionalProperties": False
    }
}

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Extract product info: Blue Widget $29.99, available"}],
    response_format={"type": "json_schema", "json_schema": schema}
)

product = json.loads(response.choices[0].message.content)
```

## Instructor: The Python Library for Post-Generation Structured Output

Instructor는 Pydantic 모델을 사용해 LLM 출력을 검증하고, 검증 실패 시 자동으로 재시도하는 Python 라이브러리다. 2026년 기준 월 300만 다운로드 이상, GitHub 스타 11,000+, 기여자 100명 이상으로 파이썬 LLM 생태계의 사실상 표준이 되었다. Instructor의 핵심 가치는 **프로바이더 중립성**이다 — OpenAI, Anthropic, Google Gemini, Ollama, Mistral, Cohere 등 15개 이상의 프로바이더를 동일한 코드 패턴으로 사용할 수 있다. `instructor.patch()`로 기존 OpenAI 클라이언트를 래핑하거나, Anthropic용 `instructor.from_anthropic()`을 사용하는 방식이다. Instructor는 생성 후 Pydantic ValidationError를 LLM 프롬프트로 변환해 자동 재시도(automatic retry)를 수행한다. 기본 재시도 횟수는 3회이며, `max_retries` 파라미터로 조정할 수 있다. 스트리밍, 비동기(async), 부분 응답(partial streaming) 등 고급 기능도 지원한다. 클라우드 API 기반 앱에서 프로바이더를 유연하게 전환해야 한다면 Instructor가 최적의 선택이다.

```python
import instructor
from anthropic import Anthropic
from pydantic import BaseModel, Field
from typing import List

class ResearchSummary(BaseModel):
    key_findings: List[str] = Field(min_length=1, max_length=5)
    confidence_score: float = Field(ge=0.0, le=1.0)
    recommended_action: str

client = instructor.from_anthropic(Anthropic())

summary = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": "Summarize the key findings from this Q1 2026 AI adoption report..."
    }],
    response_model=ResearchSummary
)

print(summary.key_findings)
print(f"Confidence: {summary.confidence_score}")
```

### Instructor의 자동 재시도 메커니즘

Pydantic 검증이 실패하면 Instructor는 검증 오류 메시지를 LLM에 다시 전달하며 "이전 출력에서 다음 오류가 발생했다, 수정해 달라"는 형식으로 재시도한다. 이는 단순 JSON 파싱보다 훨씬 강력한 오류 복구 루프를 제공한다. `Iterable[Model]`을 사용한 스트리밍 추출과 `Partial[Model]`을 통한 부분 완료 스트리밍도 지원해 대용량 문서 처리에서 UX를 개선할 수 있다.

## Outlines: Pre-Generation Constraints for Local and Self-Hosted Models

Outlines는 dottxt-ai가 개발한 오픈소스 라이브러리로, LLM 생성 단계에서 JSON 스키마, 정규식, 열거형(Enum)을 FSM으로 변환하여 유효하지 않은 토큰 생성을 원천 차단한다. Instructor와 달리 Outlines는 **사전 생성(pre-generation)** 제약 방식을 사용하므로 재시도가 전혀 필요 없다. 2026년 기준 vLLM, TGI, LoRAX, xinference, SGLang을 포함한 수백 개 조직이 Outlines를 프로덕션에서 사용 중이다. Rust로 작성된 `outlines-core` 0.1.0은 생성 스텝당 O(1) 유효 토큰 조회를 제공해 대용량 배치 처리에서 Instructor보다 현저히 빠른 성능을 낸다. Outlines는 Hugging Face Transformers, vLLM, llama.cpp와 통합되며, 로컬 모델이나 자체 호스팅 LLM 서버에 특화되어 있다. JSON 스키마 외에도 정규식 패턴, 파이썬 타입 힌트, 선택형 텍스트(choices) 등 다양한 제약 방식을 지원한다.

```python
import outlines
from pydantic import BaseModel

model = outlines.models.transformers("mistralai/Mistral-7B-v0.1")

class ProductReview(BaseModel):
    sentiment: str  # "positive", "negative", "neutral"
    score: int      # 1-5
    summary: str

generator = outlines.generate.json(model, ProductReview)
review = generator("Review: This product exceeded my expectations, would buy again.")

print(review.sentiment)  # 보장된 유효값
print(review.score)      # 보장된 정수
```

### Outlines vs Instructor: 언제 무엇을 선택하는가?

핵심 구분 기준은 모델 접근 방식이다. 클라우드 API(OpenAI, Anthropic)를 사용한다면 토큰 수준 제어가 불가능하므로 Instructor를 사용한다. 로컬 모델이나 vLLM 같은 자체 호스팅 서빙 스택을 사용한다면 Outlines가 성능과 신뢰성 모두에서 우위다. 처리량(throughput)이 중요한 고볼륨 배치 파이프라인에서는 재시도 오버헤드가 없는 Outlines가 확실히 유리하다.

## LangChain and PydanticAI: Structured Outputs in Agent Frameworks

에이전트 프레임워크들은 구조화 출력을 일급 시민으로 통합하고 있으며, 이는 복잡한 멀티 스텝 워크플로에서 LLM 출력 신뢰성을 프레임워크 수준에서 보장함을 의미한다. **LangChain**은 `with_structured_output()` 메서드를 통해 Pydantic 모델이나 TypedDict를 사용한 구조화 출력을 네이티브 지원한다. `method="json_schema"` 또는 `method="function_calling"`을 선택할 수 있으며, LCEL(LangChain Expression Language) 체인에 자연스럽게 통합된다. **PydanticAI**는 Pydantic을 개발한 팀이 만든 에이전트 프레임워크로, 구조화 출력이 아키텍처의 중심이다. `result_type` 파라미터로 Pydantic 모델을 직접 지정하며, 타입 안전성(type safety)과 IDE 자동완성을 완전히 지원한다. 2026년 기준 PydanticAI는 빠르게 성장하고 있으며, 특히 타입 안전성을 중시하는 팀에서 선호된다. LangChain의 `with_structured_output()`은 기존 LangChain 코드베이스와의 호환성이 중요할 때 최적의 선택이다. PydanticAI는 새로운 에이전트 프로젝트에서 타입 안전성과 Pydantic 생태계와의 긴밀한 통합이 필요할 때 권장된다.

```python
# LangChain 구조화 출력
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

class TicketClassification(BaseModel):
    category: str
    priority: int  # 1-5
    requires_human: bool

llm = ChatOpenAI(model="gpt-4o")
structured_llm = llm.with_structured_output(TicketClassification, method="json_schema")

result = structured_llm.invoke("User can't log in after password reset, production system")
print(result.category, result.priority, result.requires_human)
```

## Production Best Practices: Validation, Retries, and Fallback Chains

프로덕션 LLM 앱에서 구조화 출력의 신뢰성을 극대화하려면 단순한 스키마 강제 이상의 전략이 필요하다. 검증(validation), 재시도(retry), 폴백 체인(fallback chain)을 체계적으로 구성해야 한다. 첫째, **입력 스키마 설계**: `additionalProperties: false`를 항상 설정하고, 선택 필드는 `default` 값을 지정하라. 중첩이 깊은 스키마는 성능 저하와 실패율 증가를 유발한다 — 3단계 이하로 유지하라. 둘째, **Pydantic 검증 레이어**: 스키마 통과 후에도 Pydantic `@field_validator`로 비즈니스 로직 검증을 추가하라. 예를 들어 `price`가 양수인지, `email`이 올바른 형식인지 LLM 레이어에만 의존하지 말라. 셋째, **재시도 전략**: Instructor의 자동 재시도를 사용하되, 최대 3회로 제한하고 재시도 간 지수 백오프를 적용하라. 프롬프트에 구체적인 오류 메시지를 포함하면 재시도 성공률이 크게 높아진다. 넷째, **폴백 체인**: 메인 모델 실패 시 더 저렴한 모델이나 단순화된 스키마로 폴백하는 체인을 구성하라. 마지막으로, **옵저버빌리티**: 구조화 출력 실패율, 재시도 횟수, 폴백 발생률을 메트릭으로 추적하라 — 이 지표들이 5%를 넘으면 프롬프트나 스키마를 재검토해야 한다.

```python
import instructor
from openai import OpenAI
from pydantic import BaseModel, field_validator
from tenacity import retry, stop_after_attempt, wait_exponential

class OrderExtract(BaseModel):
    product_id: str
    quantity: int
    unit_price: float

    @field_validator("quantity")
    @classmethod
    def quantity_positive(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be positive")
        return v

    @field_validator("unit_price")
    @classmethod
    def price_positive(cls, v):
        if v <= 0:
            raise ValueError("Price must be positive")
        return v

client = instructor.patch(OpenAI())

order = client.chat.completions.create(
    model="gpt-4o",
    max_retries=3,
    response_model=OrderExtract,
    messages=[{"role": "user", "content": "Extract: 5 units of SKU-429 at $12.50 each"}]
)
```

## Choosing the Right Tool: Decision Matrix for Structured Output Libraries

어떤 구조화 출력 도구를 선택할지는 모델 접근 방식, 팀의 기술 스택, 처리량 요구사항, 그리고 프로바이더 유연성 필요 여부에 따라 결정된다. 2026년 기준 생태계는 세 가지 명확한 패턴으로 정착했다. 첫 번째 패턴은 **클라우드 API + Instructor**: OpenAI, Anthropic, Gemini API를 사용하며 여러 프로바이더를 전환하거나 빠른 개발이 필요한 팀에 최적이다. Instructor는 프로바이더 중립적이며 Pydantic 생태계와 완벽히 통합된다. 두 번째 패턴은 **로컬/자체 호스팅 + Outlines**: 데이터 보안, 비용 절감, 또는 특화된 파인튜닝 모델 사용이 필요한 경우다. vLLM + Outlines 조합은 고처리량 배치 추론에서 업계 표준이 되고 있다. 세 번째 패턴은 **에이전트 프레임워크 + 빌트인 지원**: LangChain이나 PydanticAI 위에 구축 중이라면 각 프레임워크의 네이티브 구조화 출력 지원을 사용하라 — 별도 라이브러리 없이도 충분하다.

| 상황 | 권장 도구 | 이유 |
|------|----------|------|
| 클라우드 API, 다중 프로바이더 | Instructor | 프로바이더 중립, Pydantic 통합 |
| 로컬 모델 (vLLM, TGI) | Outlines | FSM 사전 제약, 재시도 없음, O(1) 성능 |
| LangChain 기반 앱 | LangChain with_structured_output | 네이티브 통합 |
| PydanticAI 에이전트 | PydanticAI result_type | 타입 안전성 최우선 |
| 단일 프로바이더 (OpenAI) | 네이티브 API (strict mode) | 추가 의존성 없음 |
| 고볼륨 배치 추론 | Outlines + vLLM | 처리량 최적화 |

### 마이그레이션 경로: JSON mode에서 벗어나기

기존 코드베이스에서 `response_format: {type: "json_object"}`를 사용 중이라면 단계적 마이그레이션을 권장한다. 먼저 현재 JSON 출력의 실제 구조를 분석해 Pydantic 모델을 정의하고, `strict: true`와 `json_schema` 방식으로 전환한다. Instructor를 도입해 기존 파싱 코드를 제거하면 코드베이스가 단순해지고 신뢰성이 높아진다.

---

## FAQ

**Q: JSON mode와 구조화 출력(Structured Outputs)의 차이는 무엇인가요?**

JSON mode는 유효한 JSON 형식을 반환하도록 요청하지만 스키마 준수를 보장하지 않습니다. 구조화 출력(특히 `strict: true`와 함께)은 사전에 정의한 JSON 스키마를 100% 준수하는 출력을 제약적 디코딩으로 강제합니다. 2026년 프로덕션에서는 JSON mode 사용을 피하고 네이티브 구조화 출력을 사용하세요.

**Q: Instructor와 Outlines 중 어떤 것을 선택해야 하나요?**

클라우드 API(OpenAI, Anthropic, Gemini)를 사용한다면 Instructor를 선택하세요. 로컬 모델이나 vLLM 같은 자체 호스팅 스택을 사용한다면 Outlines를 선택하세요. Instructor는 사후 검증 + 자동 재시도 방식이고, Outlines는 생성 단계에서 유효하지 않은 토큰을 차단하는 사전 제약 방식입니다.

**Q: LLM 구조화 출력 실패율이 얼마나 되나요?**

프롬프트 엔지니어링만 사용하는 경우 프로덕션에서 5~20%의 파싱 실패율이 보고됩니다. 함수 호출을 사용하면 1~5%로, 네이티브 구조화 출력(strict mode)을 사용하면 사실상 0%에 가깝게 줄어듭니다. 파싱 실패는 조용한 버그(silent bug)로 이어지기 때문에 프로덕션에서는 반드시 스키마 강제를 사용해야 합니다.

**Q: 재귀적이거나 매우 복잡한 JSON 스키마도 지원되나요?**

OpenAI와 Google Gemini는 복잡한 중첩 스키마와 `$ref` 참조를 지원하지만, 스키마가 복잡해질수록 성능이 떨어질 수 있습니다. 실무에서는 스키마를 3단계 이하의 중첩으로 유지하고, 재귀 스키마는 반드시 프로덕션에서 철저히 테스트하세요. Outlines는 FSM 변환 단계에서 복잡도가 높은 스키마의 컴파일 시간이 길어질 수 있습니다.

**Q: LLM 구조화 출력을 TypeScript/JavaScript에서 사용할 수 있나요?**

네. OpenAI JavaScript SDK는 `zodResponseFormat()`을 통해 Zod 스키마와 결합한 구조화 출력을 지원합니다. Instructor JS(`@instructor-ai/instructor`)도 Zod 기반 검증과 자동 재시도를 지원합니다. TypeScript 사용자는 Zod + OpenAI SDK 또는 Instructor JS를 파이썬의 Pydantic + Instructor와 동일한 패턴으로 사용할 수 있습니다.
