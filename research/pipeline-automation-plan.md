# Paperclip 파이프라인 자가 개선 시스템 구축 계획

> 작성일: 2026-04-29
> 목표: 수동 이슈 대응 → 자가 진단 + 근본 원인 분석 + 자동 수정 + 학습 시스템

---

## 1. 현재 시스템 현황 진단

### 1.1 현재 운영 중인 스크립트

| 스크립트 | 주기 | 기능 | 한계 |
|---|---|---|---|
| `paperclip-auto-reset.py` | 10분 (cron) | 에러 에이전트 리셋, 좀비 이슈 정리 | symptom 기반 대응, assigneeAgentId 버그 존재 |
| `pipeline_health_check.py` | 3시간 (cron) | stuck/zombie 체크, blocked recovery, topic queue, cover/schema | 독립 실행, 타 스크립트 결과 활용 안 함 |
| `paperclip-pipeline-monitor.py` | 6시간 (cron) | 언어 검증, 파이프라인 리포트 | 관찰만 하고 수정 안 함 |

### 1.2 핵심 문제점

1. **Symptom 기반 대응** — 에러 발생 시 "리셋"만 반복, *왜* 발생했는지 추적 안 함
2. **Zero feedback loop** — 같은 패턴(예: Writer session timeout → Publish starvation → "execution disappeared")이 반복돼도 학습 안 함
3. **알려진 root cause 미활용** — 문서화된 11개 이상의 패턴(orphan, 422 loop, disabled agent, hermes_local adapter, execution disappear 등)이 스크립트에 하드코딩 안 됨
4. **assigneeAgentId 버그** (auto-reset.py에서 `assigneeId` vs `assigneeAgentId` 혼용) 여전히 미수정
5. **3개 스크립트 간 데이터 단절** — 각자 독립 실행, 서로의 결과 참조 안 함

### 1.3 기존 파이프라인 구조 (4 에이전트)

```
ContentDirector (heartbeat, 3h)
  ↓ backlog Article 선택
Researcher (claude_local) → Research done
  ↓
Writer (claude_local) → post + schema + cover done
  ↓ (ContentDirector heartbeat 감지)
Publisher (claude_local) → hugo build + git push
  ↓
Published!
```

### 1.4 알려진 장애 패턴 (11개)

| # | 패턴 | 영향 | 현재 대응 |
|---|---|---|---|
| 1 | Orphan subtask (parent done, child 미완료) | 422 loop, 파이프라인 멈춤 | auto-reset이 취소하나 미흡 |
| 2 | Stale `in_progress` (자식 모두 완료 but 부모 미갱신) | Article 방치 | health_check가 처리 |
| 3 | Blocked Publish (parent done/cancelled) | Publish 미완료 | health_check가 처리 |
| 4 | Notif todos 누적 ([Supervisor], [Auto-Reset]) | Todo 50+개 쌓임 | 부분 처리 |
| 5 | Article title 기반 타입 식별 필요 (labels 필드 항상 empty) | 버그 유발 | 문서화만 되어 있음 |
| 6 | Cover image 누락 (게시됐지만 이미지 없음) | 사이트 퀄리티 저하 | health_check가 경고만 |
| 7 | SEO agent 100% 중복 (Writer가 이미 schema 생성) | 리소스 낭비 | Apr 27 비활성화 완료 |
| 8 | Agent ID mismatch (wakeOnDemand 체인 깨짐) | 에이전트 기동 실패 | Apr 27 수정 완료 |
| 9 | Publisher "execution disappeared" → false blocked | 40% Publish가 blocked로 | health_check가 회복하나 미흡 |
| 10 | Writer timeoutSec 부족 (300s) → Publish starvation | Publish backlog 방치 | 문서화만 |
| 11 | hermes_local adapter deprecated/broken | Analyst 반복 실패 | claude_local 전환으로 해결 |

---

## 2. 참고 아키텍처: MAPE-K 루프

IBM Autonomic Computing의 표준 자율 치유 아키텍처:

```
┌───────────────────────────────────────────────────────┐
│                 Orchestrator                           │
│                                                        │
│   ┌─────────┐    ┌──────────┐    ┌───────────┐       │
│   │ Monitor  │───▶│ Analyze  │───▶│   Plan    │       │
│   │ (관찰)    │    │ (분석)    │    │ (계획)     │       │
│   └─────────┘    └──────────┘    └───────────┘       │
│        ▲                                │             │
│        │         ┌──────────┐           ▼             │
│        │         │Knowledge │    ┌───────────┐       │
│        └─────────│ (학습)    │◀───│ Execute   │       │
│                  └──────────┘    │ (실행)     │       │
│                                  └───────────┘       │
└───────────────────────────────────────────────────────┘
```

현재 시스템은 **Monitor**만 일부 있고, **Analyze / Plan / Execute / Knowledge**가 전무.

### 참고 자료

- **MAPE-K**: Kephart & Chess (2003) "The Vision of Autonomic Computing"
- **Causal Inference for RCA**: Microsoft DoWhy / Causica 라이브러리
- **tenacity**: Python 재시도/백오프 라이브러리
- **durable_rules**: Python 룰 엔진 (이벤트 기반 자동 조치)
- **StackStorm**: IFTTT for ops — 이벤트 기반 자동 복구
- **Prometheus + Alertmanager**: 메트릭 + 알림 라우팅
- **Kubernetes Operator 패턴**: desired state vs actual state 감시 + reconciliation loop

---

## 3. 단계별 개선 계획

### Phase 1: 통합 Observability 레이어 (1-2일)

**목표:** 3개 스크립트 데이터를 하나의 Knowledge Store에 통합

**변경 사항:**
1. **`pipeline_events.json`** 생성 — 모든 스크립트가 이벤트 기록:
   ```json
   {
     "ts": "2026-04-29T06:00:00Z",
     "source": "auto-reset",
     "event_type": "agent_error",
     "agent_id": "b796bb1c-a6ef-...",
     "agent_name": "Writer",
     "action": "reset+wakeup",
     "success": false,
     "context": {
       "error": "execution disappeared",
       "run_id": null
     }
   }
   ```
2. **`incident_history.json`** — root cause 분석 결과 저장 (Phase 2에서 사용)
3. **`known_patterns.json`** — 이미 발견된 11개 패턴 등록 (reference skills에서 추출)
4. 각 스크립트가 실행 종료 시 이벤트 기록하도록 수정

**파일 구조:**
```
~/blog/logs/
├── pipeline-events.json       # append-only 이벤트 로그
├── incident-history.json      # root cause 분석 결과
├── known-patterns.json        # 등록된 장애 패턴
├── supervisor-health-*.md     # 기존 (유지)
└── pipeline-report-*.md       # 기존 (유지)
```

**known_patterns.json 예시:**
```json
[
  {
    "pattern_id": "writer_session_timeout",
    "name": "Writer session timeout → Publish starvation",
    "detection": {
      "events": ["Writer error 3회/10분 이내", "Publish backlog 상태"],
      "conditions": "Writer.error_count >= 3 AND Publish.status == 'backlog'"
    },
    "root_cause": "Writer timeoutSec=300, maxTurns=30으로 Steps 1-3 소진 후 handoff 불가",
    "fix_action": "PATCH /api/agents/{writer_id} adapterConfig.timeoutSec=900",
    "severity": "high",
    "occurrences": 5
  }
]
```

---

### Phase 2: Root Cause Analysis 엔진 (2-3일)

**목표:** 단순 리셋이 아닌, 컨텍스트를 분석해서 최적의 조치 결정

**동작 방식:**
1. 이벤트 발생 (예: Writer가 10분 내 3번 error)
2. Analyze Engine이 다음을 순차 확인:
   - 최근 Claude rate limit 이력? → rate limit이면 대기, 재시도 금지
   - Writer session timeout 패턴? → timeoutSec 증가 (900s)
   - hermes_local adapter 실패? → claude_local로 전환
   - "execution disappeared" 패턴? → 파일 확인 후 done 처리
   - billing exhaustion? → 사람 알림 (텔레그램)
3. 가장 가능성 높은 root cause 선택 → Plan 단계로 전달

**분석 로직 (Pseudo):**
```
function analyze(events[], known_patterns[]):
  recent = events.filter(last_30_min)
  
  for pattern in known_patterns:
    if matches(recent, pattern.detection):
      return {
        pattern_id: pattern.pattern_id,
        confidence: calculate_confidence(recent, pattern),
        recommended_fix: pattern.fix_action
      }
  
  // Unknown pattern → fallback: reset agent
  return {
    pattern_id: "unknown",
    confidence: 0.3,
    recommended_fix: "reset_agent"
  }
```

**Phase 2에서 커버할 패턴:**
- Orphan subtask 감지 + 자동 정리
- Article 완료 시 모든 subtask 완료 확인
- Blocked Publish → 파일 존재 시 done 처리
- Publisher "execution disappeared" → done 처리
- Agent error rate limit / billing exhaustion → 대기 후 재시도
- assigneeAgentId 버그 발견 시 자동 PATCH
- ContentDirector 422 루프 → parent 상태 사전 확인
- Writer timeoutSec 부족 → adapterConfig 자동 증가
- hermes_local adapter 감지 → claude_local 전환 권장

---

### Phase 3: Feedback Loop & Learning (3-5일)

**목표:** 반복 패턴 인식 → 예방적 조치

```
Incident 발생 → 분석 → 조치 → 성공/실패 기록
                          ↓
                    Knowledge Store
                          ↓
동일 패턴 N회 반복 → 자동 스크립트 생성
           → 또는 에이전트 instruction 자동 패치
```

**핵심 기능:**
1. **패턴 클러스터링** — "Writer 10분 간격 3번 error" 패턴이 2주간 5번 발생 → timeoutSec 부족 판정 시 `adapterConfig.timeoutSec`을 300→900으로 자동 PATCH
2. **자가 수정** — Python 스크립트가 Paperclip API를 통해 에이전트 설정 변경 (`PATCH /api/agents/{id}`)
3. **에스컬레이션** — N번 실패 시 텔레그램으로 사람 알림
4. **새 패턴 자동 등록** — 미분류 패턴이 3번 반복되면 `known_patterns.json`에 자동 추가

**Learning 메커니즘:**
```
각 incident마다:
  {pattern_id, action_taken, success: bool}
  
성공률 > 80% → 해당 패턴-액션 신뢰도 증가
성공률 < 30% → 해당 액션 재평가, 다른 액션 시도
  
자동 등록:
  동일 symptom이 3회 반복 + 미분류 → 신규 패턴 후보
```

---

### Phase 4: Proactive Prevention (지속)

**목표:** 문제 발생 전에 예방

- Writer session timeout 이력 추적 → 70% 소진 시 자동 timeoutSec 증가
- Topic queue watermark가 15 이하 → Strategist 웨이크업 (현재 10 기준)
- "execution disappeared" 패턴 40% → Publisher 작업 완료 후 즉시 done 처리
- assigneeAgentId 버그 → auto-reset 스크립트 자동 패치 (스크립트 자체 수정)
- ContentDirector heartbeat 패턴 최적화 — 불필요한 wakeup 제거

---

## 4. 권장 구현 순서

```
Week 1: Phase 1
  - pipeline-events.json 포맷 정의
  - auto-reset.py → 이벤트 기록 추가
  - health_check.py → 이벤트 기록 추가
  - known-patterns.json 작성 (11개 패턴)
  - assigneeAgentId 버그 수정

Week 2: Phase 2
  - pipeline_analyzer.py (RCA 엔진) 개발
  - 패턴 매칭 로직 구현 (패턴 1-6 우선)
  - 자동 조치 실행 (Paperclip API PATCH)
  - 조치 결과 이벤트 기록

Week 3: Phase 3
  - Knowledge Store에 학습 메커니즘 추가
  - 성공/실패 추적
  - 패턴 자동 등록
  - 텔레그램 알림 연동

Week 4: Phase 4
  - 예방적 조치 로직
  - 메트릭 기반 timeout 조정
  - ContentDirector 최적화
  - 전체 안정화 및 모니터링
```

---

## 5. 핵심 기술적 결정사항

### 5.1 구현 언어 및 런타임
- **Python 3** (기존 스크립트와 일관성)
- System Python (`/usr/bin/python3`) — Pillow 의존성 있음
- 외부 라이브러리 최소화 (requests, json, datetime만으로 충분)

### 5.2 API 엔드포인트 정리
| 작업 | 메소드 | URL | 비고 |
|---|---|---|---|
| 에이전트 목록 | GET | `/api/companies/{companyId}/agents` | Company-scoped |
| 에이전트 상태 변경 | PATCH | `/api/agents/{agentId}` | **Unscoped**, company-scoped는 404 |
| 에이전트 웨이크업 | POST | `/api/agents/{agentId}/wakeup` | `{}` body 필수 |
| 이슈 목록 | GET | `/api/companies/{companyId}/issues` | limit=500 사용, pagination 금지 |
| 이슈 상태 변경 | PATCH | `/api/issues/{issueId}` | Unscoped 권장 |
| 이슈 생성 | POST | `/api/companies/{companyId}/issues` | Company-scoped |
| Heartbeat run 조회 | GET | `/api/companies/{companyId}/heartbeat-runs?limit=30` | 에러 진단용 |

**공통 헤더:** `X-Paperclip-Local-Board: true`, `Content-Type: application/json`

### 5.3 데이터 저장소
- 로컬 JSON 파일 (SQLite 도입은 Phase 3 이후)
- 이벤트 로그: append-only (파일 크기 관리 위해 주기적 rotate)
- Knowledge Store: JSON 객체 (읽기/쓰기 빈도 낮음)

### 5.4 에스컬레이션
- 3회 연속 자동 복구 실패 → 텔레그램 알림
- billing exhaustion → 즉시 텔레그램 알림 (복구 불가)
- 신규 미분류 패턴 3회 반복 → 텔레그램 알림 + 패턴 등록 제안

---

## 6. 향후 확장 가능성

- **텔레그램 봇 연동**: `send_message`를 통한 실시간 알림
- **메트릭 대시보드**: prometheus_client로 에이전트 상태 메트릭 노출
- **Webhook 기반 이벤트**: Paperclip webhook 구독 (실시간 이벤트 처리)
- **ML 기반 이상 탐지**: Isolation Forest / Prophet으로 패턴 자동 발견
- **다중 파이프라인 지원**: 다른 Paperclip 회사/보드로 확장

---

## 7. 파일 위치 요약

| 파일 | 설명 |
|---|---|
| `~/blog/agents/pipeline_orchestrator.py` | (신규) 통합 오케스트레이터 |
| `~/blog/agents/paperclip-auto-reset.py` | (수정) 이벤트 기록 추가 |
| `~/blog/agents/supervisor/pipeline_health_check.py` | (수정) 이벤트 기록 추가 |
| `~/blog/agents/paperclip-pipeline-monitor.py` | (유지 또는 통합) |
| `~/blog/logs/pipeline-events.json` | (신규) 이벤트 로그 |
| `~/blog/logs/incident-history.json` | (신규) 인시던트 히스토리 |
| `~/blog/logs/known-patterns.json` | (신규) 장애 패턴 저장소 |
| `~/blog/agents/pipeline_analyzer.py` | (신규, Phase 2) RCA 엔진 |
