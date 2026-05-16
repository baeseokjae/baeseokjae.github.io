---
title: "OpenAI Codex Desktop Guide 2026: Full Agentic IDE Workflows and GPT-5-Codex"
date: 2026-05-16T19:41:01+00:00
tags: ["openai-codex", "agentic-coding", "gpt-5", "ide-tools", "developer-tools"]
description: "OpenAI Codex Desktop 설치부터 병렬 에이전트, AGENTS.md 설정, GitHub PR 자동화까지 — 2026년 완전 가이드."
draft: false
cover:
  image: "/images/openai-codex-desktop-guide-2026.png"
  alt: "OpenAI Codex Desktop Guide 2026: Full Agentic IDE Workflows and GPT-5-Codex"
  relative: false
schema: "schema-openai-codex-desktop-guide-2026"
---

OpenAI Codex Desktop는 GPT-5-Codex 모델을 기반으로 코드를 자율적으로 작성·수정·테스트하고 GitHub PR까지 생성하는 에이전트형 IDE 도구다. 단순한 자동완성 도구가 아니라, 하나의 지시만으로 멀티 파일 수정 → 테스트 실행 → PR 제출을 30분 안에 완료하는 완전 자율 코딩 에이전트다.

## What Is OpenAI Codex Desktop in 2026?

OpenAI Codex Desktop은 2026년 현재 GPT-5.5 모델을 탑재한 자율 코딩 에이전트 플랫폼으로, Terminal-Bench 2.0 기준 82.7% 정확도로 모든 공개 모델 중 최고 성능을 기록하고 있다. 기존 GitHub Copilot이 줄 단위 자동완성에 집중했다면, Codex Desktop은 "이 버그 고쳐줘"라고 입력하면 저장소 전체를 분석하고, 관련 파일을 수정하고, 테스트를 통과시키고, PR까지 자동으로 열어주는 엔드투엔드 에이전트 워크플로를 실행한다. macOS(Apple Silicon M1 이상)와 Windows(2026년 3월 4일부터 공식 지원) 양쪽에서 네이티브 앱으로 동작하며, 로컬에서 실행하는 방식과 Codex Cloud에서 백그라운드로 실행하는 방식 모두 지원한다. 작업 완료 시간은 복잡도에 따라 1분에서 30분 사이이며, 팀 환경에서는 여러 에이전트를 병렬로 실행해 수일치 작업을 몇 시간으로 압축할 수 있다. AI 코딩 에이전트가 수동 코딩 시간을 30~50% 줄인다는 연구 결과처럼, Codex Desktop은 그 효과를 가장 직접적으로 실현하는 도구 중 하나다. 이 가이드는 설치부터 병렬 에이전트 운영, AGENTS.md 고급 설정까지 실무자 관점에서 단계별로 다룬다.

## The 4 Surfaces of Codex: CLI, IDE Extensions, Desktop App, and Codex Cloud

OpenAI Codex는 단일 앱이 아니라 네 가지 서페이스로 구성된 에코시스템이다. 각 서페이스는 서로 다른 워크플로에 최적화되어 있으며, 어떤 표면을 선택하느냐에 따라 생산성이 크게 달라진다. CLI는 터미널에서 직접 에이전트를 호출하고 자동화 파이프라인(CI/CD, Git hooks)에 통합하기 위한 표면이다. IDE 익스텐션(VS Code, JetBrains)은 에디터 안에서 인라인 채팅과 컨텍스트 주입을 제공해 현재 파일과 선택된 코드 블록을 자동으로 에이전트에 전달한다. 데스크탑 앱은 가장 강력한 표면으로, 병렬 에이전트 실행·git worktree 격리·GitHub 통합을 GUI로 제공하며 저장소 전체를 컨텍스트로 사용한다. Codex Cloud는 긴 작업을 OpenAI 서버에서 비동기로 실행하고 완료 시 Slack이나 이메일로 알림을 받는 방식이다. 이 네 가지 표면을 이해하고 상황에 맞게 선택하는 것이 Codex 생산성의 출발점이다. 대부분의 개발자는 빠른 수정에는 IDE 익스텐션을, 자율 에이전트 태스크에는 데스크탑 앱을, 장시간 백그라운드 작업에는 Codex Cloud를 조합해 사용한다.

### CLI: 자동화 파이프라인을 위한 표면

```bash
# Codex CLI 설치
npm install -g @openai/codex

# 저장소 루트에서 에이전트 실행
codex "결제 모듈의 단위 테스트 커버리지를 80% 이상으로 높여줘"
```

CLI는 CI/CD 파이프라인과 쉘 스크립트에 통합할 때 사용한다. `--no-interactive` 플래그로 완전 비대화형 모드로 실행할 수 있다.

### IDE Extensions: 에디터 내 컨텍스트 주입

VS Code 익스텐션은 현재 열려 있는 파일, 선택된 코드 블록, 에러 메시지를 자동으로 에이전트 컨텍스트에 포함시킨다. `Ctrl+Shift+C`로 Codex 패널을 열고 자연어로 지시하면 된다.

### Desktop App: 병렬 에이전트의 핵심

데스크탑 앱은 네 가지 서페이스 중 가장 많은 기능을 제공하며, 특히 여러 에이전트를 동시에 실행하는 병렬 워크플로의 핵심이다. 각 에이전트 세션은 독립적인 git worktree에서 실행되므로 메인 브랜치에 영향을 주지 않는다.

### Codex Cloud: 비동기 백그라운드 실행

Codex Cloud는 복잡한 작업을 오프로드해 로컬 머신 자원을 점유하지 않고 실행한다. 수십 분이 걸리는 마이그레이션 작업에 적합하며 완료되면 Slack이나 이메일로 알림을 받는다.

## GPT-5-Codex Models: Architecture, Benchmarks, and Capabilities

GPT-5-Codex 모델군은 OpenAI가 코딩 에이전트 작업에 특화해 훈련한 모델 시리즈로, 2026년 5월 기준 최신 버전인 GPT-5.5가 Terminal-Bench 2.0에서 82.7%를 기록하며 모든 공개 모델 중 최고 성능을 달성했다. GPT-5.3-Codex는 SWE-Bench Verified에서 80.0%를 달성해 멀티파일 리팩토링 정확도를 이전 세대 대비 크게 높였다. GPT-5.5는 SWE-Bench Pro에서 58.6%를 기록해 단일 패스에서 엔드투엔드 작업 완료 능력이 역대 최고 수준에 달했다. 장기 컨텍스트 측면에서도 GPT-5.5는 MRCR v2(1M 토큰)에서 74.0%를 기록해 GPT-5.4의 36.6% 대비 두 배 이상 향상되었으며, 이는 대형 모노레포에서도 코드베이스 전체를 참조할 수 있음을 의미한다. GPT-5.5는 Expert-SWE(인간 중앙값 완료 시간 20시간인 장기 작업)에서도 73.1%를 달성해 GPT-5.4의 68.5%를 넘어섰다. 단순 버그 수정에는 GPT-5.3-Codex, 대규모 리팩토링과 복잡한 아키텍처 변경에는 GPT-5.5를 선택하는 것이 비용 대비 효율적인 전략이다.

| 모델 | SWE-Bench Verified | Terminal-Bench 2.0 | 출시 |
|------|-------------------|-------------------|------|
| GPT-5.2-Codex | ~70% | ~65% | 2025 Q4 |
| GPT-5.3-Codex | 80.0% | 77.3% | 2026 Q1 |
| GPT-5.4 | ~75% | ~78% | 2026 Q1 |
| GPT-5.5 | 58.6% (Pro) | 82.7% | 2026 Q2 |

## Setting Up the Codex Desktop App on macOS and Windows

Codex Desktop 설치는 macOS와 Windows 양쪽에서 10분 이내에 완료된다. macOS는 Apple Silicon(M1 이상)이 필수이며 Intel Mac은 지원하지 않는다. Windows는 2026년 3월 4일부터 공식 지원이 시작됐으며, WSL2 환경에서 최적의 성능을 제공한다. 설치 전 ChatGPT Plus($20/월) 이상의 구독이 필요하며, Codex 기능은 Plus, Pro, Team, Enterprise 플랜 모두에서 사용 가능하다. 단, 사용량 한도가 플랜마다 다르므로 팀 도입 전에 반드시 플랜을 확인해야 한다. 설치 후 처음 실행하면 OpenAI 계정으로 로그인하고 저장소 접근 권한을 설정하는 온보딩 플로를 거친다. 이 단계에서 GitHub 계정도 연결해두면 이후 PR 자동화가 원활하게 동작한다. 로컬 저장소 경로와 기본 셸(bash/zsh/fish)도 이 단계에서 설정하며, 여러 저장소를 등록해두면 나중에 에이전트 세션에서 빠르게 전환할 수 있다. 기업 환경에서는 SSO(Single Sign-On) 연동과 프록시 설정을 추가로 구성해야 할 수 있으며, Codex Desktop은 HTTP_PROXY 환경 변수를 자동으로 인식한다.

### macOS 설치

```bash
# Homebrew 사용 (권장)
brew install --cask openai-codex

# 또는 공식 사이트에서 .dmg 다운로드
```

설치 후 첫 실행 시 "Allow Codex to access your repositories" 권한 팝업이 표시된다. "Allow" 클릭 후 GitHub 계정을 연결한다.

### Windows 설치

Windows에서는 winget 또는 `.exe` 설치 파일을 사용한다:

```powershell
winget install OpenAI.Codex
```

WSL2가 설치되어 있으면 Codex가 자동으로 이를 감지해 Linux 환경에서 에이전트를 실행한다.

### 초기 설정 체크리스트

- OpenAI 계정 로그인 완료
- GitHub 계정 연결 (Settings → Integrations → GitHub)
- 기본 셸 설정 (bash/zsh/fish)
- 로컬 저장소 경로 등록

## Connecting GitHub Repositories and Enabling PR Automation

GitHub 통합은 Codex Desktop의 핵심 기능 중 하나로, 에이전트가 자동으로 브랜치를 생성하고, 코드를 수정하고, PR을 열고, 리뷰 코멘트에 응답하는 전체 개발 사이클을 자동화한다. 연결 방법은 두 가지다: OAuth를 통한 개인 저장소 연결과, GitHub App을 통한 조직 저장소 연결이다. 개인 저장소에서는 OAuth 방식이 간단하지만, 조직 저장소에서는 GitHub App 방식이 권장된다. GitHub App 방식은 세밀한 권한 제어(읽기/쓰기 분리, 특정 저장소만 허용)를 지원하며, 조직의 보안 정책과 충돌하지 않는다. PR 자동화를 활성화하면 에이전트가 작업을 완료한 후 자동으로 PR 제목, 설명, 체인지로그를 작성한다. PR 설명에는 변경 이유, 영향받는 파일 목록, 테스트 통과 여부가 포함된다. 자동 생성된 PR에는 `codex-agent` 레이블이 붙어 팀의 리뷰 큐에서 쉽게 식별할 수 있다. 에이전트의 PR 생성 결과물은 반드시 사람이 리뷰해야 하며, 머지 전 SAST 보안 스캔을 CI 파이프라인에 추가해 자동으로 검증하는 구조를 만드는 것이 좋다. GitHub Actions 워크플로에 Semgrep을 연동하면 Codex PR에 대한 자동 보안 검토가 가능하다.

### GitHub App 설치

1. Codex Desktop → Settings → GitHub → "Install GitHub App"
2. GitHub에서 설치할 조직/계정 선택
3. 접근 허용할 저장소 선택 (전체 또는 특정 저장소)
4. 권한 검토 후 "Install" 클릭

### PR 자동화 워크플로

에이전트가 작업을 완료하면 다음 순서로 PR이 생성된다:

```
사용자 지시 → 에이전트 작업(isolated worktree) → 
테스트 실행 → 통과 확인 → 브랜치 push → PR 생성
```

리뷰어가 코멘트를 남기면 "Codex야, 이 코멘트 반영해줘"라고 지시해 수정 커밋을 추가할 수 있다.

### 브랜치 네이밍 규칙 설정

AGENTS.md에서 브랜치 네이밍 패턴을 지정할 수 있다:

```
codex/{task-type}/{short-description}
예: codex/fix/payment-null-check, codex/feat/user-auth-refresh
```

## Configuring AGENTS.md for Custom Agentic Workflows

AGENTS.md는 저장소 루트에 위치하는 마크다운 파일로, Codex 에이전트가 해당 저장소에서 작업할 때 따라야 할 규칙, 컨텍스트, 명령어를 정의한다. 이 파일은 에이전트의 "헌법"과 같은 역할을 하며, 잘 작성된 AGENTS.md는 에이전트의 정확도와 코드 품질을 크게 높인다. AGENTS.md가 없으면 에이전트는 저장소 구조를 추론해서 작업하므로 오류 가능성이 높아지고, 기존 코드베이스 스타일과 불일치하는 코드를 생성할 확률이 높다. 핵심 섹션은 세 가지다: 첫째, 프로젝트 컨텍스트(기술 스택, 아키텍처 결정, 외부 의존성). 둘째, 실행 명령어(테스트, 빌드, 린트 명령어를 정확히 명시). 셋째, 코딩 규칙(네이밍 컨벤션, 금지된 패턴, 에러 처리 방식). 병렬 에이전트를 실행할 때는 AGENTS.md의 일관된 규칙이 각 에이전트의 코드 스타일을 통일시켜 병합 충돌을 줄이는 데 중요한 역할을 한다. 실무 경험상 테스트 명령어와 금지 패턴을 명확하게 작성하는 것이 가장 큰 효과를 낸다. 5분 투자로 AGENTS.md를 작성하면 에이전트 첫 시도 성공률이 눈에 띄게 향상되며, 팀 전체가 동일한 에이전트 동작을 기대할 수 있게 된다.

### 기본 AGENTS.md 구조 예시

```markdown
# Project Context
Next.js 15 앱, PostgreSQL 데이터베이스, Drizzle ORM 사용.
인증: NextAuth.js v5. API 라우트는 REST 컨벤션 준수.

# Tech Stack
Frontend: Next.js 15, TypeScript, Tailwind CSS
Backend: Next.js API routes, Drizzle ORM
Database: PostgreSQL 16
Testing: Vitest, Playwright

# Commands
Build: npm run build
Test: npm run test
E2E: npm run test:e2e
Lint: npm run lint
Type check: npm run typecheck

# Coding Conventions
- TypeScript strict mode 사용
- const 우선, let 최소화, var 금지
- 에러 처리: Result 타입 사용, 서비스 레이어에서 raw throw 금지
- DB: 항상 Drizzle 쿼리 빌더 사용, raw SQL 금지
- 프로덕션 코드에 console.log 금지; logger 유틸리티 사용

# Forbidden Patterns
- any 타입 사용 금지
- 데이터베이스 RLS(Row Level Security) 우회 금지
- 소스 코드에 시크릿 하드코딩 금지
```

### 작업별 고급 지시 설정

```markdown
# Task-Specific Instructions

When writing tests:
- 테스트 파일 위치: src/__tests__/{module}.test.ts
- 외부 API 목킹: MSW(Mock Service Worker) 사용
- 최소 커버리지: 신규 파일 80% 이상

When fixing bugs:
1. 먼저 실패하는 테스트로 버그 재현
2. 코드 수정
3. 테스트 통과 확인
4. 동일 패턴이 코드베이스에 있는지 검색 후 일괄 수정
```

## Running Parallel Agents with Built-in Worktrees

병렬 에이전트 실행은 Codex Desktop의 가장 강력한 기능으로, 각 에이전트 세션이 독립적인 git worktree에서 실행되어 서로 충돌 없이 동시에 여러 작업을 처리할 수 있다. 예를 들어 "결제 모듈 리팩토링", "사용자 인증 버그 수정", "API 문서 업데이트"를 세 에이전트에 동시에 할당하면, 순차적으로 처리할 때 3시간 걸리는 작업을 45분 안에 완료할 수 있다. 각 에이전트는 별도의 브랜치(`codex/fix/auth-bug`, `codex/refactor/payment`, `codex/docs/api`)에서 작업하므로 메인 브랜치는 완전히 보호된다. 병렬 에이전트가 효과적으로 작동하려면 작업을 명확히 분리하고 각 에이전트에 독립적인 파일 범위를 할당해야 한다. 같은 파일을 여러 에이전트가 동시에 수정하도록 지시하면 병합 충돌이 발생하므로, 작업 분할 단계에서 파일 소유권을 명확히 정해야 한다. Pro 플랜에서는 최대 10개의 에이전트 세션을 동시에 실행할 수 있으며, AGENTS.md의 공통 규칙이 모든 세션에 일관되게 적용되어 병렬로 생성된 코드의 스타일이 통일된다. git worktree 기반 격리는 에이전트 작업이 실패하거나 잘못된 방향으로 진행되더라도 메인 브랜치와 다른 에이전트 작업에 영향을 주지 않아 안전하다.

### 병렬 에이전트 시작하기

Codex Desktop에서 "New Session" 버튼을 클릭하면 새 에이전트 세션이 추가된다. 각 세션은 독립적인 탭으로 표시된다:

```
Session 1: [결제 모듈] 리팩토링 진행 중... (worktree: codex/refactor/payment)
Session 2: [인증] 세션 만료 버그 수정 중... (worktree: codex/fix/auth-timeout)
Session 3: [테스트] 결제 API 커버리지 확장 중... (worktree: codex/test/payment-coverage)
```

### 효과적인 작업 분할 원칙

1. **파일 범위 분리**: 각 에이전트에게 서로 겹치지 않는 파일 집합을 할당
2. **독립적인 완료 조건**: 각 작업이 다른 작업 완료에 의존하지 않도록 설계
3. **명확한 테스트 기준**: "모든 단위 테스트 통과" 같은 검증 가능한 완료 조건 명시
4. **AGENTS.md 일관성 확보**: 공통 규칙 파일로 코드 스타일 통일

### CSV 기반 팬아웃 워크플로

동일한 작업을 여러 항목에 반복 적용할 때는 `spawn_agents_on_csv` 패턴이 유용하다:

```python
codex.spawn_agents_on_csv(
    template="'{endpoint}' 엔드포인트에 입력 유효성 검사 추가",
    csv_file="endpoints.csv",
    max_parallel=5
)
```

## Codex Cloud vs. Local App: When to Use Each

Codex Cloud와 로컬 데스크탑 앱은 서로 보완적인 도구로, 작업 특성에 따라 선택해야 한다. Codex Cloud는 OpenAI 서버에서 에이전트를 실행하므로 로컬 머신 자원을 사용하지 않으며, 작업 중에 노트북을 닫아도 계속 실행된다. 반면 로컬 앱은 로컬 파일 시스템, 내부 네트워크, 로컬 서비스(데이터베이스, 개발 서버)에 직접 접근할 수 있어서 개발 서버 연동이나 로컬 DB 마이그레이션 테스트가 필요한 작업에 적합하다. 기업 환경에서는 두 방식 중 어느 것이 보안 정책에 부합하는지도 반드시 고려해야 한다. 코드가 로컬 머신 외부로 전송되지 않아야 하는 보안 요구사항이 있다면 로컬 앱만 사용해야 한다. 인터넷이 연결된 환경에서 장시간 작업을 실행해야 한다면 Codex Cloud가 적합하며, 실무에서는 두 방식을 조합하는 것이 가장 효율적이다. 로컬에서 빠른 버그 수정은 데스크탑 앱으로 처리하고, 대규모 리팩토링은 Codex Cloud에 넘겨 밤 사이에 실행한 후 아침에 PR을 검토한다.

| 기준 | 로컬 데스크탑 앱 | Codex Cloud |
|------|----------------|-------------|
| 로컬 파일 접근 | 직접 접근 가능 | 불가 |
| 로컬 서비스 접근 | 가능 | 불가 |
| 실행 중 노트북 닫기 | 작업 중단 | 계속 실행 |
| 자원 사용 | 로컬 CPU/메모리 | 서버 실행 |
| 보안 | 코드 로컬 유지 | OpenAI 서버 처리 |
| 적합한 작업 | 개발 서버 연동, DB 마이그레이션 | 장시간 리팩토링, 문서화 |

## OpenAI Codex vs. Cursor vs. Claude Code vs. GitHub Copilot

네 가지 AI 코딩 도구는 모두 강력하지만 최적화된 사용 시나리오가 다르다. Codex Desktop은 완전 자율 에이전트 작업(PR 생성까지 자동화)에 특화되어 있고, Cursor는 에디터 내 인라인 편집과 실시간 코드 탐색에 강하다. Claude Code는 터미널 기반 에이전트로 복잡한 멀티스텝 태스크와 코드베이스 심층 분석에 탁월하며, GitHub Copilot은 에디터 통합이 가장 넓고 기업 규정 준수 지원이 강하다. 시장 규모를 보면 Cursor가 $1.2B ARR, Claude가 $2.5B 연환산 매출을 달성한 상황에서, Codex Desktop은 OpenAI의 GPT-5.5 모델 벤치마크 우위를 바탕으로 자율 에이전트 작업 정확도로 경쟁하고 있다. 선택 기준은 명확하다: 결과물을 PR로 받고 싶다면 Codex, 에디터 안에서 실시간 수정을 원한다면 Cursor, 복잡한 코드베이스 분석이 필요하다면 Claude Code, 기업 규정 준수가 최우선이라면 Copilot이다. 많은 팀이 이 도구들을 조합해서 사용하며, 하나만 선택해야 할 이유는 없다.

| 기능 | Codex Desktop | Cursor | Claude Code | GitHub Copilot |
|------|--------------|--------|-------------|----------------|
| 자율 PR 생성 | 최강 | 가능 | 가능 | 제한적 |
| 인라인 편집 | 보통 | 최강 | CLI 기반 | 최강 |
| 병렬 에이전트 | 내장 | 미지원 | 수동 설정 | 미지원 |
| 로컬 모델 지원 | 미지원 | 지원 | 미지원 | 미지원 |
| 가격 시작점 | $20/월 | $20/월 | API 기반 | $10/월 |
| 최강 시나리오 | 에이전트 자동화 | 에디터 통합 | 복잡한 분석 | 기업 규정 준수 |

## Codex Pricing and Plan Comparison for 2026

Codex 가격은 ChatGPT 구독 플랜에 포함되어 있으며 플랜별로 사용량 한도가 크게 다르다. ChatGPT Plus($20/월)는 기본 Codex 사용량을 포함하며, 하루 10개 미만의 가벼운 에이전트 태스크를 실행하는 개인 개발자에게 적합하다. Pro 플랜($100/월)은 Plus 대비 5배 더 많은 Codex 사용량을 제공하고, $200/월 프리미엄 Pro 플랜은 20배 높은 한도를 제공한다. 팀 환경에서 병렬 에이전트를 자주 실행하고 Codex Cloud 장시간 태스크를 활용한다면 Pro 또는 Team 플랜이 필요하다. Codex 사용량은 ChatGPT 앱 → Usage → Codex 탭에서 실시간으로 확인할 수 있으며 한도 임박 시 이메일 알림을 설정할 수 있다. 비용 최적화를 위해서는 여러 작은 수정을 하나의 에이전트 세션으로 묶어 사용량을 절약하고, 복잡한 작업에만 GPT-5.5를 사용하며 단순 작업에는 GPT-5.3-Codex를 선택하는 전략이 효과적이다. Enterprise 플랜은 사용량 무제한 옵션을 제공하며 SSO, 감사 로그, 데이터 잔류 보장 기능을 포함한다.

| 플랜 | 월 가격 | Codex 한도 | 최적 대상 |
|------|--------|-----------|---------|
| ChatGPT Plus | $20 | 기본 | 개인 개발자 (가벼운 사용) |
| ChatGPT Pro | $100 | 5x | 헤비 유저, 프리랜서 |
| ChatGPT Pro Premium | $200 | 20x | 팀 리드, 대용량 자동화 |
| ChatGPT Team | $30/인 | 팀 공유 풀 | 소규모 개발팀 |
| ChatGPT Enterprise | 협의 | 무제한 | 대기업 |

---

## FAQ

OpenAI Codex Desktop에 대해 개발자들이 가장 자주 묻는 다섯 가지 질문과 실무 기반 답변을 정리한다. 이 FAQ는 설치 요구사항(GitHub 필수 여부, 지원 OS), AGENTS.md 필수 여부와 작성 효과, 병렬 에이전트 동시 실행 한도, 에이전트 생성 코드의 보안 검토 방법, 그리고 데스크탑 앱과 VS Code 익스텐션의 실질적 차이점에 대한 핵심 내용을 다룬다. Codex Desktop을 처음 도입하는 팀뿐만 아니라 이미 사용 중이지만 고급 기능(병렬 에이전트, Codex Cloud, GitHub App 통합)을 탐색하는 시니어 개발자 모두에게 유용한 내용이다. 각 답변은 OpenAI 공식 문서와 실제 팀 도입 경험을 바탕으로 작성했으며, 2026년 5월 현재 기준의 최신 정보를 반영하고 있다. Codex는 빠르게 발전하는 플랫폼이므로 플랜 한도와 지원 플랫폼은 OpenAI 공식 페이지에서 최신 정보를 확인하는 것을 권장한다. GitLab 지원처럼 아직 미지원이지만 출시 예정인 기능과 현재 한계도 솔직하게 포함했다. 현재 기준으로 Codex Desktop이 지원하는 플랫폼은 macOS Apple Silicon과 Windows이며, Intel Mac과 Linux 네이티브 앱은 미지원 상태다.

### Q. Codex Desktop을 사용하려면 GitHub 계정이 필수인가요?

GitHub 계정 없이도 로컬 저장소에서 Codex Desktop을 사용할 수 있습니다. 단, PR 자동 생성, 리뷰 코멘트 반영, Codex Cloud와의 저장소 동기화 등 고급 기능은 GitHub 연결이 필요합니다. GitLab 지원은 2026년 하반기 출시 예정입니다.

### Q. AGENTS.md가 없어도 Codex가 동작하나요?

동작합니다. 단, AGENTS.md가 없으면 에이전트가 저장소 구조를 직접 추론해서 작업하므로 오류율이 높아지고, 코딩 스타일이 기존 코드베이스와 불일치할 수 있습니다. 5분 투자로 AGENTS.md를 작성하면 에이전트 성공률이 크게 향상됩니다.

### Q. 병렬 에이전트를 몇 개까지 동시에 실행할 수 있나요?

데스크탑 앱에서는 기술적으로 제한이 없지만, ChatGPT 플랜의 동시 세션 한도가 적용됩니다. Plus 플랜은 최대 3개, Pro 플랜은 최대 10개의 동시 Codex 세션을 지원합니다. 병렬 실행 수가 늘어날수록 로컬 메모리와 CPU도 비례해서 사용됩니다.

### Q. Codex가 생성한 코드의 보안은 어떻게 검토하나요?

Codex가 생성한 PR을 머지하기 전에 반드시 코드 리뷰를 수행해야 합니다. AGENTS.md에 보안 규칙(SQL 인젝션 방지, 시크릿 하드코딩 금지, RLS 우회 금지 등)을 명시하고, GitHub Actions에 Semgrep이나 SonarQube 같은 SAST 도구를 추가해 자동 보안 스캔을 통과한 PR만 리뷰 대상이 되도록 설정하세요.

### Q. Codex Desktop과 VS Code Codex 익스텐션의 차이는 무엇인가요?

VS Code 익스텐션은 에디터 컨텍스트(현재 파일, 선택된 코드, 에러 메시지)를 자동으로 포함해 빠른 인라인 수정에 적합합니다. 데스크탑 앱은 저장소 전체를 에이전트 컨텍스트로 사용하며 병렬 실행, PR 자동화, 멀티파일 리팩토링에 특화되어 있습니다. 대부분의 팀은 두 도구를 함께 사용합니다.
