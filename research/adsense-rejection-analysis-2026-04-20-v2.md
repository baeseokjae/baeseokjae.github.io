# Google AdSense 반려 원인 정밀 분석 (수정판)
**사이트**: baeseokjae.github.io (RockB)  
**분석일**: 2026-04-20  
**참고 정책**: answer/10502938, answer/10015918, answer/9044175, answer/11035931

---

## 1. 기존 분석 오류 정정

| 이전 주장 | 실제 확인 결과 | 판정 |
|-----------|---------------|------|
| Privacy Policy 없음 | `/privacy/` 존재 (HTTP 200, 53행, AdSense/Analytics 쿠키 정책 포함) | **오류** |
| Terms of Service 없음 | `/terms/` = 404. 실제로 존재하지 않음 | **맞음** |
| Contact 페이지 없음 | `/contact/` 존재 (HTTP 200, 이메일 + GitHub + X 링크) | **오류** |
| About 페이지 너무 짦음 | 39행, 1,487바이트 (4개 섹션, 작성자 소개 포함) → 충분함 | **오류** |

**존재하는 정책 페이지**: Privacy Policy, Contact, Disclaimer, About  
**존재하지 않는 정책 페이지**: Terms of Service (404)  
**Footer 링크**: About · Contact · Privacy Policy · Disclaimer (4개 모두 연결됨, Terms 없음)

---

## 2. 반려 원인 분석 (Google 정책 기준)

### 원인 1: Terms of Service (이용약관) 누락 — CRITICAL

AdSense 정책(answer/10502938)은 사이트에 **Privacy Policy + Terms of Service** 를 명시적으로 요구합니다.

- `/privacy/` = 존재 (200)
- `/terms/` = **404 (존재하지 않음)**
- Footer에 Terms 링크 없음
- 리포지토리 내 terms/tos/service 관련 콘텐츠 파일 없음

Privacy, Contact, Disclaimer, About이 있지만 **Terms of Service만 빠져 있습니다.** Google AdSense 리뷰어가 이것을 "필수 법적 페이지 누락"으로 간주했을 가능성이 매우 높습니다.

**심각도**: 매우 높음 (AdSense 승인의 필수 조건)

---

### 원인 2: Schema.org 데이터 내 도메인 불일치 — HIGH

게시글 JSON-LD 구조화된 데이터에서 **baeseokjae.com** (미구매 도메인)과 **baeseokjae.github.io** (실제 도메인)이 혼용되고 있습니다:

```
"image": "https://baeseokjae.com/images/best-llm-for-coding-2026.png"  ← 404
"mainEntityOfPage": { "@id": "https://baeseokjae.com/posts/..." }     ← 404
"publisher": { "logo": { "url": "https://baeseokjae.com/images/logo.png" } } ← 404
```

확인 결과:
- baeseokjae.com → **미해결 (HTTP 000, DNS 없음)**
- CNAME 파일 없음
- config에 커스텀 도메인 설정 없음

Google 리뷰어가 구조화된 데이터의 URL을 따라가면 404를 만납니다. 이것은 **사이트 품질 문제** + **구조화된 데이터 스팸**의 신호로 해석될 수 있습니다.

**심각도**: 높음

---

### 원인 3: 대량 AI 생성 콘텐츠 (Content Farm 패턴) — HIGH

Google의 thin content / 사이트 인지도 악용(answer/9044175) 정책에 해당:

| 지표 | 수치 | 문제 |
|------|------|------|
| 전체 포스트 | 93개 | — |
| 동일일 생성 (Apr 18) | 83개 (89%) | 대량 자동 생성 신호 |
| 생성 기간 | ~11일 (Apr 9-20) | 하루 평균 8.5개 발행 |
| FAQ 포함 | 81/93 (87%) | 동일 템플릿 |
| 비교 테이블 포함 | 92/93 (99%) | 동일 템플릿 |
| Pros/Cons 포함 | 43/93 (46%) | 동일 템플릿 |
| 내부 교차 링크 | **0개** | AI 생성 콘텐츠 전형 패턴 |
| 외부 아웃바운드 링크 | **10개** (93개 포스트 전체) | 극도로 낮음 |
| 타이틀에 "AI" 포함 | ~68/93 (73%) | 키워드 과최적화 |

Google의 관점에서 이 사이트는:
- 11일 만에 93개 글이 대량 생산됨 → **AI content farm**
- 모든 글이 동일 구조(FAQ + 테이블 + 장단점) → **템플릿 기반 자동 생성**
- 외부 소스 링크 거의 없음 → **부가 가치 없는 콘텐츠**
- 글 간 교차 참조 없음 → **독립적으로 생성된 AI 출력**
- GSC: 1 impression, 0 clicks → **실제 사용자 가치 미검증**

**심각도**: 높음

---

### 원인 4: 무료 호스팅 스팸 카테고리 — MEDIUM

사이트가 `github.io` (GitHub Pages 무료 호스팅)에서 운영됩니다. Google의 무료 호스팅 스팸(answer/9044175) 정책에서:

> "무료 호스팅 서비스의 대규모 스팸 사이트" 카테고리에 해당할 수 있음

이것만으로 반려 사유는 아니지만, 위 원인 3과 결합하면 **매우 부정적인 시그널**입니다. GitHub Pages 자체가 문제가 아니라, 무료 호스팅 + 대량 AI 콘텐츠 조합이 스팸 패턴에 부합합니다.

**심각도**: 중간 (단독으로는 반려 사유가 아닐 수 있으나 가중 요인)

---

### 원인 5: 누락된 이미지 (1건) — LOW

```
claude-opus-4-vs-gpt-5-coding-2026.png → static/images/ 에 존재하지 않음
```

SEO 크롤링 시 이미지 404 발생. 구조화된 데이터의 이미지 URL도 일부 baeseokjae.com 도메인이어서 실제 접근 불가.

**심각도**: 낮음 (1건이지만 품질 신호에 가산)

---

## 3. 제외된 원인 (이전 분석에서 오진단한 것들)

| 항목 | 상태 |
|------|------|
| Privacy Policy 누락 | **정상 존재** — 반려 사유 아님 |
| Contact 페이지 누락 | **정상 존재** — 반려 사유 아님 |
| About 페이지 부족 | **충분한 내용** — 반려 사유 아님 |
| 클로킹 | **없음** — Googlebot과 일반 사용자에게 동일 콘텐츠 제공 |
| 숨겨진 텍스트/키워드 스터핑 | **없음** — HTML/CSS에 hidden text 없음 |
| 사이트 인지도 악용 | **해당 없음** — 타사 스팸 흔적 없음 |

---

## 4. 해결 방안 (우선순위순)

### P0: Terms of Service 페이지 생성
- content/terms.md 작성
- 이용 약관, 콘텐츠 저작권, AI 도구 검토 공시, 면책 조항 포함
- Footer에 `/terms/` 링크 추가
- Privacy Policy에도 Terms 링크 추가

### P0: Schema.org 도메인 불일치 수정
- layouts/partials/schema-*.html 에서 `baeseokjae.com` → `baeseokjae.github.io` 일괄 변경
- 또는 커스텀 도메인 구매 후 CNAME 설정
- 누락된 이미지 파일 보완

### P1: 콘텐츠 품질 개선 (장기)
- 각 글에 3-5개 외부 소스 링크 추가 (공식 문서, 연구 논문, 원본 보고서)
- 글 간 내부 교차 링크 추가 (관련 글 서로 참조)
- 발행 주기를 자연스럽게 분산 (일 1-2개)
- AI 템플릿 구조 탈피 — FAQ/비교표/장단점이 아닌 독창적 구조 도입
- 실제 사용 경험, 스크린샷, 개인 의견 추가

### P2: GSC 트래픽 확보 후 재신청
- 현재 1 impression / 0 clicks = Google이 아직 이 사이트를 신뢰하지 않음
- 최소 100-1000 impressions/월, 유기적 클릭 존재 확인 후 재신청
- AdSense 승인은 보통 3-6개월 유기적 트래픽 후 가능

---

## 5. 요약

**핵심 반려 원인**:

1. **Terms of Service 누락** (AdSense 필수 요건) — 즉시 수정 가능
2. **Schema.org 내 baeseokjae.com → 404 도메인 혼용** — 즉시 수정 가능  
3. **대량 AI 생성 콘텐츠 패턴** (89% 동일일 생성, 템플릿 구조, 외부 링크 10개/93글) — 장기 개선 필요
4. **무료 호스팅 + AI 콘텐츠 스팸 시그널** — 가중 요인

**오진단 정정**: Privacy Policy, Contact, Disclaimer, About은 모두 정상 존재함. 이전 분석의 "법적 페이지 누락" 주장은 Terms of Service 1개를 제외하면 사실이 아님.