---
title: "llama-stack vs Ollama vs vLLM: Which Local LLM Stack Should You Use in 2026"
date: 2026-05-21T09:34:00+00:00
tags: ["llm", "local-ai", "vllm", "ollama", "llama-stack", "inference", "self-hosted"]
description: "llama-stack, Ollama, vLLM 비교: 각 도구의 역할과 2026년 최적의 로컬 LLM 스택 조합을 실제 벤치마크와 함께 설명합니다."
draft: false
cover:
  image: "/images/llama-stack-vs-ollama-vs-vllm-2026.png"
  alt: "llama-stack vs Ollama vs vLLM: Which Local LLM Stack Should You Use in 2026"
  relative: false
schema: "schema-llama-stack-vs-ollama-vs-vllm-2026"
---

대부분의 llama-stack vs Ollama vs vLLM 비교 글은 핵심을 놓칩니다. 이 세 가지 도구는 서로 경쟁하는 게 아닙니다. **llama-stack은 오케스트레이션 API 레이어이고, Ollama와 vLLM은 추론 엔진입니다.** 올바른 질문은 "무엇을 선택할까?"가 아니라 "어떻게 조합할까?"입니다. 2026년 권장 스택은 셋 모두를 사용합니다.

---

## What Is Each Tool? (Clearing Up the Confusion)

llama-stack, Ollama, vLLM은 로컬 LLM 생태계에서 각각 다른 레이어를 담당하는 도구입니다. llama-stack은 Meta가 2026년 4월 8일에 릴리스한 OpenAI 호환 API 서버로, Ollama·vLLM·Fireworks 같은 여러 추론 제공자를 플러그인 방식으로 연결하는 **오케스트레이션 레이어**입니다. Ollama는 개발자 로컬 환경에 최적화된 **추론 엔진**으로, 한 줄 명령어(`ollama run llama4`)로 모델을 실행할 수 있습니다. vLLM은 PagedAttention 알고리즘을 기반으로 한 **프로덕션 급 추론 엔진**으로, GPU 서버 배포에 최적화되어 있습니다.

| 도구 | 역할 | 주요 대상 | 특징 |
|------|------|-----------|------|
| llama-stack | 오케스트레이션 API | 앱 개발자 | 제공자 무관 표준 API |
| Ollama | 로컬 추론 엔진 | 개발자/연구자 | 설치 편의성, CPU/Metal 지원 |
| vLLM | 프로덕션 추론 엔진 | MLOps/프로덕션 팀 | 고처리량, 다중 사용자 처리 |

이 세 도구를 같은 카테고리로 묶어 비교하는 것은 데이터베이스 엔진과 ORM, 그리고 REST 프레임워크를 같은 선상에서 비교하는 것과 같습니다. 각자의 위치가 있고, 함께 쓸 때 가장 강력합니다.

---

## llama-stack: The Orchestration Layer You've Been Missing

llama-stack은 2026년 4월 8일 Meta가 릴리스한 오픈소스 오케스트레이션 프레임워크로, 로컬 LLM 앱 개발에서 가장 고통스러운 문제인 공급자 종속(vendor lock-in)을 해결합니다. 핵심 아이디어는 단순합니다: 개발 환경에서 Ollama를 쓰고 프로덕션에서 vLLM으로 전환할 때 **앱 코드를 한 줄도 바꾸지 않아도 됩니다.** llama-stack이 Inference, Agents, Safety, Vector Storage, Evaluation에 대한 표준화된 API를 제공하기 때문입니다. GitHub `meta-llama/llama-stack` 기준으로 지원 제공자는 Ollama, vLLM, OpenAI, Fireworks, Together AI를 포함하며, `providers.yaml` 파일 하나만 수정하면 제공자를 전환할 수 있습니다. 특히 Responses API는 서버사이드 에이전틱 오케스트레이션을 단일 API 호출로 처리합니다 — 툴 콜링, MCP 서버 통합, 내장 RAG까지 포함하여. Ollama나 vLLM이 네이티브로 제공하지 않는 기능입니다. Gartner는 2026년 말까지 엔터프라이즈 AI 앱의 40%가 이런 추상화 레이어를 사용할 것으로 전망합니다. llama-stack은 그 구체적인 오픈소스 구현체 중 가장 성숙한 옵션이며, 마이크로소프트·레드햇·구글 클라우드 등이 공식 제공자 파트너로 참여합니다.

### llama-stack의 핵심 기능

llama-stack이 단순 API 래퍼가 아닌 이유는 세 가지입니다.

**제공자 무관 추상화:** `llama_stack_client.inference.chat_completion()`을 호출하면 뒤에서 Ollama가 실행되든 vLLM이 실행되든 동일한 결과가 반환됩니다. `providers.yaml`에서 제공자만 교체하면 됩니다.

**에이전틱 API 내장:** Responses API는 단일 요청으로 멀티스텝 툴 콜링, 웹 검색, 파일 I/O, MCP 서버 호출을 처리합니다. LangChain이나 LlamaIndex 없이도 에이전트 워크플로를 구현할 수 있습니다.

**Safety 레이어:** Llama Guard 기반의 입력/출력 필터링이 API 레벨에서 내장되어 있어, 모든 추론 제공자에 일관된 안전 정책을 적용할 수 있습니다.

```yaml
# providers.yaml 예시 — 이 파일만 바꾸면 제공자 전환 완료
version: '2'
image_name: ollama
providers:
  inference:
  - provider_id: ollama
    provider_type: remote::ollama
    config:
      url: http://localhost:11434
```

---

## Ollama: The Developer's Local LLM Workhorse

Ollama는 2026년 현재 로컬 LLM 개발의 사실상 표준 도구입니다. `brew install ollama` 한 줄로 macOS에 설치하고 `ollama run llama4:scout`으로 17B 파라미터 모델을 즉시 실행할 수 있습니다. 설치부터 첫 번째 응답까지 2분이면 충분합니다. 2026년 1월 15일 공개 베타로 출시된 Ollama Cloud(`ollama serve --cloud`)는 로컬과 클라우드의 경계를 흐리며, 동일한 CLI 워크플로로 전 세계에 분산된 엔드포인트를 사용할 수 있게 되었습니다. Ollama의 핵심 강점은 네 가지입니다: Apple Silicon Metal GPU 네이티브 지원(CPU 대비 3-5배 속도), NVIDIA/AMD GPU 지원, GPU 없는 환경에서의 CPU 폴백, 그리고 `/v1/chat/completions` 엔드포인트를 통한 OpenAI 완전 호환 API. 마지막 특징이 특히 중요합니다 — OpenAI SDK를 사용하는 기존 코드의 `base_url`만 `http://localhost:11434/v1`로 바꾸면 즉시 로컬 LLM으로 전환됩니다. 2026년 5월 기준 Ollama Hub에는 500개 이상의 사전 최적화된 모델이 등록되어 있으며, Llama 4, Gemma 3, Qwen 3, Mistral Small 3.1이 가장 많이 다운로드된 모델입니다. 개발자가 하루 만에 로컬 LLM 앱 프로토타입을 만드는 이유가 여기 있습니다.

### Ollama가 적합한 경우

- **로컬 개발/프로토타이핑:** 단일 사용자 환경에서 모델을 빠르게 실험
- **Apple Silicon 환경:** Metal GPU를 활용한 CPU 대비 3-5배 빠른 추론
- **오프라인 환경:** 인터넷 없이 완전 로컬에서 실행
- **소규모 RAG 파이프라인:** 단일 사용자 또는 소규모 팀 내부 도구

### Ollama의 한계

Ollama는 단일 사용자 워크로드에 최적화되어 있습니다. 50명의 동시 사용자가 API를 호출하면 p99 레이턴시가 24.7초까지 치솟습니다(SitePoint 2026 벤치마크). 이는 vLLM의 3초 이하 p99와 비교하면 8배 이상의 차이입니다. Ollama의 순차적(sequential) 요청 처리 아키텍처가 근본 원인입니다 — KV 캐시를 정적으로 할당하기 때문에 PagedAttention 기반 vLLM처럼 동시 요청을 효율적으로 처리하지 못합니다.

---

## vLLM: The Production-Grade Inference Engine

vLLM은 PagedAttention이라는 핵심 혁신 위에 세워진 프로덕션 급 LLM 추론 엔진으로, 동일한 GPU 하드웨어에서 Ollama 대비 최대 19배 높은 처리량을 달성합니다. UC Berkeley 연구팀이 2023년에 개발한 PagedAttention은 OS의 가상 메모리 기법을 KV 캐시에 적용합니다 — GPU 메모리를 고정 크기 블록으로 나눠 여러 요청이 비연속적인 메모리 공간을 공유할 수 있게 하여 GPU 메모리 낭비를 60-80%에서 10% 이하로 줄입니다. 2026년 4월 출시된 vLLM v0.19.0은 NVIDIA Blackwell GPU(H200, B100) 지원을 확장했고, vLLM V1 엔진은 FlashAttention 3와 함께 V0 대비 1.7배 처리량 향상을 달성했습니다. Clarifai 벤치마크에 따르면 2x H100 GPU 환경에서 100개의 동시 요청 처리 시 4,741 tok/s를 기록합니다. SitePoint 2026 벤치마크에서 vLLM은 단일 A100 GPU 기준으로 Ollama의 41 tok/s 대비 793 tok/s의 피크 처리량을 보였습니다. vLLM이 단순한 성능 개선이 아닌 아키텍처 혁신을 기반으로 한다는 점이, 대규모 AI 서비스를 운영하는 팀들이 vLLM을 선택하는 근본 이유입니다.

### vLLM PagedAttention의 작동 원리

전통적인 추론 엔진(Ollama 포함)은 각 요청에 대해 최대 시퀀스 길이만큼의 GPU 메모리를 미리 예약합니다. 실제로 100 토큰짜리 응답이 생성되어도 4,096 토큰 분량의 메모리가 잠겨있는 것입니다. 낭비율이 60-80%에 달합니다.

PagedAttention은 KV 캐시를 2KB짜리 페이지로 분할합니다. 요청이 실제로 소비하는 만큼만 페이지를 할당하고, 요청 완료 시 즉시 해제합니다. 여러 요청이 공통 프리픽스(시스템 프롬프트 등)의 KV 캐시를 공유하는 프리픽스 캐싱도 지원합니다. 실질적 효과: 동일한 GPU에서 2-4배 많은 동시 요청을 처리할 수 있습니다.

```bash
# vLLM 서버 시작 — 프로덕션 배포 기본 명령
vllm serve meta-llama/Llama-4-Scout-17B-16E-Instruct \
  --tensor-parallel-size 2 \
  --gpu-memory-utilization 0.90 \
  --enable-prefix-caching \
  --max-num-seqs 256
```

### vLLM이 적합한 경우

- 10명 이상의 동시 API 사용자를 처리하는 서비스
- GPU 서버(A100, H100, RTX 4090 이상) 보유 환경
- SLA가 있는 프로덕션 배포
- 배치 추론(수천 개의 문서 동시 처리)

---

## Performance Benchmarks: Ollama vs vLLM vs llama-stack

성능 비교에서 llama-stack은 제외해야 합니다. llama-stack은 추론 엔진이 아니라 API 레이어이기 때문에 자체적인 추론 성능이 없습니다 — llama-stack을 통한 성능은 뒤에서 실행되는 Ollama 또는 vLLM의 성능과 동일합니다(API 오버헤드는 무시할 수준). 따라서 실질적인 벤치마크 비교는 Ollama vs vLLM입니다. 2026년 SitePoint 벤치마크(Llama 3.1 70B, NVIDIA A100 80GB GPU, 동일 서버 환경 기준): vLLM은 피크 처리량 793 tok/s를, Ollama는 41 tok/s를 기록했습니다(19배 차이). p99 레이턴시는 vLLM 80ms 대 Ollama 673ms로 8배 차이입니다. 50명의 동시 사용자 환경에서는 격차가 더 벌어집니다 — vLLM이 6배 더 높은 총 처리량을 보이고, p99 레이턴시는 vLLM 3초 이하 vs Ollama 24.7초(morphllm.com 2026 벤치마크)입니다. 단일 사용자 시나리오에서 레이턴시 차이는 작습니다(vLLM 80ms vs Ollama 673ms). 하지만 동시 사용자가 늘어날수록 차이가 급격히 커집니다. 이 차이의 근본 원인은 아키텍처입니다: Ollama는 요청을 순차적으로 처리하지만 vLLM의 PagedAttention은 수백 개의 요청을 동시에 처리하면서 GPU 메모리를 효율적으로 공유합니다. 단순 성능 수치만 보면 vLLM이 항상 유리하지만, Ollama의 설치 편의성과 Apple Silicon 지원이 개발 환경에서는 더 실질적인 가치를 제공합니다.

### 벤치마크 요약표

| 지표 | Ollama | vLLM | 차이 |
|------|--------|------|------|
| 피크 처리량 | 41 tok/s | 793 tok/s | vLLM 19x |
| p99 레이턴시 (단일 사용자) | 673ms | 80ms | vLLM 8x |
| 50 동시 사용자 처리량 | 기준 | 6x 더 높음 | vLLM 6x |
| p99 레이턴시 (50 동시) | 24.7초 | <3초 | vLLM 8x+ |
| 2x H100 (100 동시) | 미지원 | 4,741 tok/s | — |
| 설치 시간 | 2분 | 15-30분 | Ollama 유리 |
| Apple Silicon 지원 | 네이티브 | 제한적 | Ollama 유리 |
| CPU 폴백 | 지원 | 미지원 | Ollama 유리 |

### vLLM + Ollama 통합

흥미로운 사실: Ollama를 vLLM 백엔드 중 하나로 통합하면 네이티브 Ollama 대비 4.3배 높은 처리량을 달성할 수 있습니다. markaicode.com 2026 벤치마크에 따르면 vLLM+Ollama 통합 시 1,200 req/hour vs 네이티브 Ollama 280 req/hour입니다.

---

## When to Use llama-stack vs Ollama vs vLLM

세 도구의 선택 기준은 동시 사용자 규모, 하드웨어 환경, 그리고 개발 단계에 따라 결정됩니다. 단순화하면: **개발 중이면 Ollama로 시작하고, 프로덕션에 배포할 때는 vLLM으로 전환하고, 앱 코드가 두 환경 모두에서 변경 없이 동작해야 한다면 llama-stack을 API 레이어로 사용하세요.** 2026년 AI 팀이 가장 자주 겪는 문제는 개발 환경(Ollama 또는 OpenAI API)과 프로덕션 환경(vLLM)의 API 불일치로 인한 환경별 코드 분기입니다. `if ENV == "dev": use_ollama() else: use_vllm()`과 같은 코드가 쌓이면 유지보수 부채가 됩니다. llama-stack은 이 문제를 설정 파일 레벨에서 해결하여 앱 코드에서 환경 분기를 제거합니다. 실제 팀 적용 사례를 보면, 스타트업은 Ollama 단독으로 MVP를 만들고, 사용자 증가 시 llama-stack을 API 레이어로 추가한 후 vLLM을 백엔드로 전환하는 3단계 패턴이 가장 일반적입니다. 동시 사용자 5명이 기준선입니다: 그 이하라면 Ollama의 단순함이 vLLM의 성능 이점보다 실질적으로 더 가치 있습니다.

### 시나리오별 권장 구성

**스타트업 MVP / 해커톤:**
- Ollama 단독 사용
- 이유: 설치 2분, 코드 10줄로 OpenAI API 드롭인 대체
- 한계: 동시 사용자 5명 이상부터 응답 지연

**소규모 팀 내부 도구 (사용자 10-50명):**
- llama-stack + Ollama
- 이유: 표준화된 API로 팀 내 일관성 유지, 나중에 vLLM 전환 용이

**프로덕션 SaaS (사용자 100명+):**
- llama-stack + vLLM
- 이유: 고처리량, 낮은 레이턴시 SLA 충족, 제공자 전환 유연성

**엔터프라이즈 AI 플랫폼:**
- llama-stack + vLLM (프로덕션) + Ollama (개발자 로컬)
- 이유: 전체 팀이 동일한 llama-stack API를 사용하면서 환경별로 최적 추론 엔진 사용

**Apple Silicon 개발자 (M3/M4 Mac):**
- Ollama 단독 또는 llama-stack + Ollama
- 이유: vLLM의 Apple Silicon Metal 지원이 아직 제한적, Ollama가 Metal GPU 활용 최적화

---

## The Recommended 2026 Stack: Combine All Three

2026년 가장 견고한 로컬 LLM 스택은 세 도구를 각자의 역할에 맞게 조합하는 것입니다. llama-stack을 API 게이트웨이로 두고, 개발 환경에서는 Ollama를, 스테이징·프로덕션 환경에서는 vLLM을 추론 엔진으로 사용합니다. 이 구성의 핵심 장점은 **앱 코드의 변경 없이 환경 전환이 가능하다**는 점입니다. llama-stack의 `providers.yaml`을 수정하는 것만으로 Ollama에서 vLLM으로, 또는 외부 클라우드 API(Fireworks, Together AI)로 전환할 수 있습니다. Netflix가 환경별로 다른 CDN을 사용하지만 내부 API는 동일한 것과 같은 원리입니다. 이 패턴을 따르면 팀 내 모든 개발자는 로컬 Ollama 환경에서 개발하면서 프로덕션의 vLLM과 동일한 API 인터페이스를 사용합니다. 2026년 기준으로 이 조합이 현실적인 이유는 llama-stack이 안정화 단계에 접어들어 프로덕션 사용 사례가 충분히 검증되었고, Ollama Cloud와 vLLM v0.19.0 모두 llama-stack 제공자로 공식 지원되기 때문입니다. 에이전틱 AI 앱을 구축하는 팀이라면 llama-stack의 Responses API가 LangChain/LlamaIndex 없이도 멀티스텝 툴 콜링과 RAG를 처리하므로, 의존성을 크게 줄일 수 있습니다.

### 권장 스택 아키텍처

```
앱 코드 (Python/JS)
    ↓
llama-stack Responses API (표준화된 인터페이스)
    ↓
providers.yaml
    ├── 개발: Ollama (localhost:11434)
    ├── 스테이징: vLLM (gpu-server:8000)
    └── 프로덕션: vLLM 클러스터 또는 Fireworks/Together AI
```

### llama-stack providers.yaml 환경별 설정

```yaml
# dev.yaml — 개발 환경
providers:
  inference:
  - provider_id: ollama
    provider_type: remote::ollama
    config:
      url: http://localhost:11434

# prod.yaml — 프로덕션 환경  
providers:
  inference:
  - provider_id: vllm
    provider_type: remote::vllm
    config:
      url: http://gpu-cluster:8000
      max_tokens: 4096
```

앱 코드는 두 환경 모두에서 동일합니다:

```python
from llama_stack_client import LlamaStackClient

client = LlamaStackClient(base_url="http://localhost:5001")

response = client.inference.chat_completion(
    model_id="llama4-scout",
    messages=[{"role": "user", "content": "Explain PagedAttention in 3 sentences"}],
)
print(response.completion_message.content.text)
```

---

## Setup Guide: Getting Started with Each Tool

각 도구의 설치와 기본 설정 방법을 환경별로 정리합니다. Ollama는 설치에 2분, vLLM은 CUDA 환경 포함 15-30분, llama-stack은 Ollama 또는 vLLM이 이미 실행 중인 상태에서 5분이면 설정할 수 있습니다. 로컬 LLM 스택 구축에서 가장 흔한 실수는 GPU 서버를 확보하기 전에 vLLM과 llama-stack을 동시에 구성하려다 복잡성에 압도되는 것입니다. **Ollama로 시작해서 작동하는 프로토타입을 만든 후, 실제 동시 사용자 부하가 발생할 때 vLLM으로 전환하는 점진적 접근을 권장합니다.** llama-stack은 Ollama 단계부터 추가하면 나중에 환경 전환 비용을 제거할 수 있습니다. 아래 가이드는 macOS(Apple Silicon) 및 Linux 환경을 모두 다루며, 각 단계에서 검증할 수 있는 curl 테스트 명령을 포함합니다. Hugging Face에서 모델을 다운로드하려면 `huggingface-cli login`으로 인증이 필요하고, Llama 4 모델은 Meta의 사용 약관 동의가 선행되어야 합니다. Python 3.10 이상, CUDA 12.1 이상(vLLM의 경우), 그리고 모델 크기에 따라 최소 16GB(7B), 40GB(70B) GPU 메모리가 필요합니다.

### Ollama 설치 (macOS/Linux)

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# 서버 시작 및 모델 실행
ollama serve &
ollama pull llama4:scout
ollama run llama4:scout "Hello, World!"

# OpenAI 호환 API 테스트
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"llama4:scout","messages":[{"role":"user","content":"Hi"}]}'
```

### vLLM 설치 (Linux + CUDA GPU)

```bash
# Python 3.10+ 및 CUDA 12.1+ 필요
pip install vllm

# 서버 시작
vllm serve meta-llama/Llama-4-Scout-17B-16E-Instruct \
  --port 8000 \
  --tensor-parallel-size 1 \
  --gpu-memory-utilization 0.85

# 멀티 GPU (2x H100)
vllm serve meta-llama/Llama-4-Maverick-17B-128E-Instruct \
  --tensor-parallel-size 2 \
  --enable-prefix-caching \
  --max-num-seqs 512
```

### llama-stack 설치 및 설정

```bash
# llama-stack 서버 설치
pip install llama-stack

# Ollama 백엔드로 초기화
llama stack build --template ollama --image-type venv
llama stack run ollama

# 또는 Docker로 실행
docker run -it \
  -p 5001:5001 \
  -v ~/.llama:/root/.llama \
  llamastack/distribution-ollama \
  --port 5001 \
  --env INFERENCE_MODEL=llama4:scout

# API 테스트
curl http://localhost:5001/v1/inference/chat-completion \
  -H "Content-Type: application/json" \
  -d '{"model_id":"llama4:scout","messages":[{"role":"user","content":"Test"}]}'
```

---

## Frequently Asked Questions

**Q: llama-stack과 Ollama/vLLM을 동시에 사용해야 하나요, 아니면 하나만 선택해야 하나요?**

동시에 사용하는 것이 권장 구성입니다. llama-stack은 추론 엔진이 아니라 API 레이어이므로, Ollama 또는 vLLM이 실제 모델 실행을 담당합니다. llama-stack 없이 Ollama나 vLLM만 사용해도 무방하지만, llama-stack을 추가하면 환경 전환 시 코드 변경 없이 제공자를 교체할 수 있는 유연성을 얻게 됩니다.

**Q: 개인 프로젝트에서 vLLM을 쓸 이유가 있나요?**

GPU가 있고 여러 명이 동시에 API를 사용한다면 vLLM이 유리합니다. 단독 사용자라면 Ollama가 더 편리합니다. vLLM은 설치와 설정이 복잡하고 CUDA GPU가 필수입니다. RTX 4090 이상의 GPU를 보유한 개발자라면 vLLM으로도 로컬 개발이 가능하고 더 빠른 응답을 얻을 수 있습니다.

**Q: Apple Silicon Mac(M3/M4)에서 가장 좋은 선택은 무엇인가요?**

2026년 현재 Apple Silicon에서는 Ollama가 최선의 선택입니다. Ollama는 Metal GPU를 네이티브로 지원하여 CPU 대비 3-5배 빠른 추론이 가능합니다. vLLM의 Apple Silicon 지원(`vllm-mlx` 패키지)은 아직 실험적 단계입니다. MLX 기반 접근이 필요하다면 MLX-LM을 직접 사용하거나 Ollama를 통해 간접적으로 사용하는 것이 안정적입니다.

**Q: llama-stack의 에이전틱 API가 LangChain이나 LlamaIndex와 어떻게 다른가요?**

llama-stack의 Responses API는 서버사이드에서 에이전틱 오케스트레이션을 처리합니다. 클라이언트는 단일 API 호출을 보내고 서버가 멀티스텝 툴 콜링, MCP 서버 통합, RAG를 처리합니다. LangChain/LlamaIndex는 클라이언트사이드 오케스트레이션 프레임워크로, 앱 코드 내에서 멀티스텝 로직을 구현합니다. llama-stack은 더 단순한 클라이언트 코드를 가능하게 하지만, 커스터마이징 유연성은 LangChain 쪽이 높습니다.

**Q: vLLM과 Ollama 중 하나만 선택해야 한다면 2026년에는 어떤 기준으로 결정하나요?**

판단 기준은 하나입니다: **동시 사용자 수.** 5명 이하라면 Ollama, 10명 이상이라면 vLLM입니다. 그 사이(5-10명)는 워크로드 성격에 따라 다릅니다. 응답 레이턴시보다 설치 편의성이 중요하면 Ollama, SLA가 있거나 배치 처리가 필요하면 vLLM을 선택하세요. 어떤 선택이든 llama-stack을 API 레이어로 사용하면 나중에 전환 비용 없이 결정을 바꿀 수 있습니다.
