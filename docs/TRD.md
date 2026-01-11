# TRD: FAA Strategy Calculator

> **Technical Requirements Document**  
> Version: 1.0 | Date: 2026-01-07 | Author: AI Consultant

---

## MVP 캡슐 (12줄)

```
1. 목표(Outcome): FAA 전략 기반 투자 스코어링 자동화로 매월 리밸런싱 의사결정 시간 절감
2. 페르소나: ETF 투자를 원하지만 종목 선정이 어려운 30대 직장인
3. 핵심 가치 제안: 7개 종목의 FAA 스코어를 1분 내에 계산하고 최적 투자 비중을 제안
4. EPIC-1: 사용자가 원하는 종목군으로 FAA 스코어를 계산하고 투자 가이드를 받는다
5. FEAT-1: 7개 티커 입력 → 스코어 계산 → 상위 3개 종목 및 투자 비중 표시
6. 노스스타 지표: DAU 100명
7. 입력 지표: (1) 스코어 계산 완료율 (2) 재방문율
8. Non-goals: 로그인, 이메일 알림, 다중 포트폴리오, 백테스트 저장, 환율 변환
9. NFR Top 2: (1) 응답시간 10초 이내 (2) 가용성 99%
10. 데이터 민감도: 없음 (PII 수집 없음, LocalStorage만 사용)
11. Top 리스크: yfinance 상업 라이선스 → MVP 후 유료 API 전환 검토
12. 다음 7일 액션: 프로젝트 세팅 + 스코어 계산 API 구현 + 기본 UI
```

---

## 1. Architecture Overview

### 1.1 System Context Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                         Vercel Platform                              │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                      Monorepo Structure                         │ │
│  │                                                                 │ │
│  │  ┌─────────────────────────┐    ┌──────────────────────────┐   │ │
│  │  │     Next.js Frontend    │    │  Python Serverless API   │   │ │
│  │  │     (/app, /components) │    │  (/api/*.py)             │   │ │
│  │  │                         │    │                          │   │ │
│  │  │  • React 18+ (RSC)      │───▶│  • /api/validate-ticker  │   │ │
│  │  │  • shadcn/ui            │◀───│  • /api/score            │   │ │
│  │  │  • Tailwind CSS         │    │  • /api/backtest         │   │ │
│  │  │  • Recharts             │    │                          │   │ │
│  │  └───────────┬─────────────┘    └────────────┬─────────────┘   │ │
│  │              │                               │                  │ │
│  └──────────────┼───────────────────────────────┼──────────────────┘ │
│                 │                               │                    │
│                 ▼                               ▼                    │
│  ┌─────────────────────────┐    ┌──────────────────────────────┐    │
│  │     LocalStorage        │    │        yfinance              │    │
│  │  (Browser, per-device)  │    │    (Yahoo Finance API)       │    │
│  │                         │    │                              │    │
│  │  • 종목군 (7 tickers)    │    │  • Historical prices        │    │
│  │  • 투자 금액            │    │  • Ticker validation         │    │
│  └─────────────────────────┘    └──────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
```

### 1.2 Module Boundaries

| 모듈 | 책임 | 의존성 |
|------|------|--------|
| **Frontend (Next.js)** | UI 렌더링, 상태 관리, LocalStorage 관리 | shadcn/ui, Recharts |
| **API Layer (Python)** | 데이터 페칭, FAA 계산, 백테스트 로직 | yfinance, pandas, numpy |
| **Storage (LocalStorage)** | 사용자 설정 영속화 | 없음 |

### 1.3 Data Flow

```
[사용자 입력] → [프론트엔드] → [API 호출] → [yfinance 데이터] 
                    ↑              ↓
             [LocalStorage] ← [계산 결과] → [UI 렌더링]
```

---

## 2. Non-Functional Requirements (NFR)

### NFR-1: 성능 (Performance)

| ID | 요구사항 | 목표 | 측정 방법 |
|----|----------|------|----------|
| NFR-1.1 | 스코어 계산 API 응답 시간 | ≤ 10초 (p95) | Vercel Analytics |
| NFR-1.2 | 백테스트 API 응답 시간 (5년) | ≤ 10초 (p95) | Vercel Analytics |
| NFR-1.3 | 티커 검증 응답 시간 | ≤ 2초 | Vercel Analytics |
| NFR-1.4 | 페이지 초기 로드 (LCP) | ≤ 2.5초 | Lighthouse |
| NFR-1.5 | 동시 사용자 처리 | 10명 | 부하 테스트 |

### NFR-2: 가용성 (Availability)

| ID | 요구사항 | 목표 | 비고 |
|----|----------|------|------|
| NFR-2.1 | 월간 가용성 | 99% (≤7시간 다운타임) | Vercel 무료 티어 SLA |
| NFR-2.2 | 외부 API 장애 대응 | Graceful degradation | 에러 메시지 표시 |

### NFR-3: 보안 (Security)

| ID | 요구사항 | 구현 방법 |
|----|----------|----------|
| NFR-3.1 | HTTPS 강제 | Vercel 기본 설정 |
| NFR-3.2 | 입력 티커 검증 | 서버 사이드 yfinance 검증 |
| NFR-3.3 | XSS 방지 | React 기본 escaping |
| NFR-3.4 | CORS | Vercel 설정 (same-origin) |

> **참고**: Rate Limiting, 인증/인가, 감사 로그는 MVP 범위 외 (Non-goal)

### NFR-4: 확장성 (Scalability)

| ID | 요구사항 | 비고 |
|----|----------|------|
| NFR-4.1 | Serverless 자동 스케일링 | Vercel 기본 지원 |
| NFR-4.2 | 상태 비저장 (Stateless) API | 세션/DB 없음 |

### NFR-5: 관측성 (Observability)

| ID | 요구사항 | 도구 |
|----|----------|------|
| NFR-5.1 | 에러 로깅 | Vercel 기본 로그 |
| NFR-5.2 | API 성능 모니터링 | Vercel Analytics |
| NFR-5.3 | 사용자 행동 추적 | Google Analytics (선택) |

---

## 3. Data Lifecycle

### 3.1 데이터 수집
- **외부 데이터**: yfinance를 통해 Yahoo Finance에서 실시간 수집
- **사용자 데이터**: 브라우저 LocalStorage에만 저장 (서버 수집 없음)

### 3.2 데이터 보관
| 데이터 유형 | 보관 위치 | 보관 기간 |
|-------------|----------|-----------|
| 종목군 설정 | LocalStorage | 사용자 삭제 전까지 |
| 투자 금액 | LocalStorage | 사용자 삭제 전까지 |
| 계산 결과 | 없음 (휘발성) | 세션 종료 시 삭제 |
| 백테스트 결과 | 없음 (휘발성) | 세션 종료 시 삭제 |

### 3.3 데이터 삭제
- **LocalStorage 초기화**: 사용자가 브라우저 데이터 삭제 시 자동 삭제
- **"설정 초기화" 버튼**: UI에서 제공 (선택적)

### 3.4 PII/민감 데이터
- **수집하는 PII**: 없음
- **규정 준수 요구**: 해당 없음 (GDPR, CCPA 등 적용 대상 아님)

---

## 4. AuthN/AuthZ Model

### MVP 범위
- **인증 (AuthN)**: 없음 - 익명 사용자
- **인가 (AuthZ)**: 없음 - 모든 기능 공개

### 권한 모델
```
[모든 사용자] → 전체 기능 접근 가능
  • 종목 입력 ✓
  • 스코어 계산 ✓
  • 백테스트 ✓
  • LocalStorage 읽기/쓰기 ✓
```

> **Post-MVP 고려**: 로그인 추가 시 Next-Auth + 이메일 매직링크 권장

---

## 5. Integrations & API Contracts

### 5.1 External Integrations

| 시스템 | 용도 | 프로토콜 | 인증 |
|--------|------|----------|------|
| Yahoo Finance (via yfinance) | 주가 데이터 | HTTP/REST | 없음 (공개) |
| Google AdSense | 광고 | JavaScript SDK | 퍼블리셔 ID |
| Google Analytics | 사용자 추적 | JavaScript SDK | 측정 ID |

### 5.2 Internal API Contracts

#### `POST /api/validate-ticker`
티커 심볼 유효성 검증

**Request:**
```json
{
  "ticker": "VTI"
}
```

**Response (200 OK):**
```json
{
  "valid": true,
  "name": "Vanguard Total Stock Market ETF",
  "exchange": "NYSE"
}
```

**Response (200 OK, Invalid):**
```json
{
  "valid": false,
  "error": "Ticker not found"
}
```

---

#### `POST /api/score`
FAA 스코어 계산

**Request:**
```json
{
  "tickers": ["VTI", "VEA", "VWO", "SHY", "BND", "GSG", "VNQ"],
  "investment_amount": 10000
}
```

**Response (200 OK):**
```json
{
  "calculation_date": "2026-01-07",
  "lookback_days": 80,
  "scores": [
    {
      "ticker": "VTI",
      "momentum": 0.0823,
      "volatility": 0.0142,
      "correlation": 3.245,
      "momentum_rank": 2,
      "volatility_rank": 3,
      "correlation_rank": 4,
      "total_score": 5.5,
      "selected": true,
      "cash_replaced": false
    }
    // ... 6 more
  ],
  "selected_tickers": ["VTI", "VEA", "VNQ"],
  "allocation": [
    { "ticker": "VTI", "amount": 3333.33 },
    { "ticker": "VEA", "amount": 3333.33 },
    { "ticker": "VNQ", "amount": 3333.34 }
  ],
  "notes": []
}
```

**Response (400 Bad Request):**
```json
{
  "error": "Invalid ticker: XYZ123"
}
```

---

#### `POST /api/backtest`
백테스트 실행

**Request:**
```json
{
  "tickers": ["VTI", "VEA", "VWO", "SHY", "BND", "GSG", "VNQ"],
  "start_date": "2021-01-01",
  "initial_investment": 10000
}
```

**Response (200 OK):**
```json
{
  "start_date": "2021-01-01",
  "end_date": "2026-01-07",
  "initial_investment": 10000,
  "final_value": 14523.45,
  "total_return": 0.4523,
  "cagr": 0.0772,
  "mdd": -0.1823,
  "sharpe_ratio": 0.89,
  "benchmark": {
    "ticker": "SPY",
    "total_return": 0.5234,
    "cagr": 0.0876
  },
  "monthly_data": [
    { "date": "2021-01-31", "portfolio_value": 10123.45, "benchmark_value": 10234.56 },
    // ... more months
  ],
  "trades": [
    { "date": "2021-01-31", "action": "rebalance", "holdings": ["VTI", "VEA", "SHY"] },
    // ... more trades
  ]
}
```

---

## 6. Technology Stack Options

### 권장 스택 (Option A) ✓ 선택됨

| 레이어 | 기술 | 버전 | 선택 근거 |
|--------|------|------|----------|
| 프론트엔드 프레임워크 | Next.js | 14+ | Vercel 최적화, React RSC, API Routes 통합 |
| UI 라이브러리 | shadcn/ui + Tailwind | latest | 빠른 개발, 커스터마이징 용이 |
| 차트 | Recharts | 2.x | React 친화적, 충분한 기능 |
| 백엔드 런타임 | Python | 3.11 | yfinance 호환, Vercel 지원 |
| 데이터 라이브러리 | yfinance, pandas, numpy | latest | 금융 데이터 처리 표준 |
| 호스팅 | Vercel | - | 무료 티어, 자동 배포 |
| 저장소 | LocalStorage | - | 서버리스, 무상태 |

### 대안 스택 (Option B) — 언제 더 나은가?

| 조건 | Option B 스택 | 트리거 |
|------|---------------|--------|
| 더 복잡한 백엔드 로직 필요 시 | FastAPI + Render/Fly.io | 다중 DB, 큐 처리 등 |
| React 외 프레임워크 선호 시 | SvelteKit + Vercel | 더 가벼운 번들 |
| 유료 데이터 API 전환 시 | Alpha Vantage / Polygon.io | yfinance 차단 시 |

### 대안 스택 (Option C) — 리스크/운영 관점

| 조건 | Option C 스택 | 트리거 |
|------|---------------|--------|
| 서버리스 제한 초과 시 | Docker + VPS (Hetzner) | Vercel 10초 타임아웃 초과 |
| 비용 최소화 필요 시 | Static Export + Cloudflare Workers | Vercel 무료 한도 초과 |

### Lock-in / Cost / 운영 난이도 비교

| 항목 | Option A (Next.js+Vercel) | Option B (FastAPI+VPS) | Option C (Static+CF) |
|------|---------------------------|------------------------|---------------------|
| 락인 | 중 (Vercel) | 저 | 저 |
| 비용 | $0 (무료 티어) | $5-10/월 | $0 (무료 티어) |
| 운영 난이도 | 낮음 | 중간 | 낮음 |
| 배포 속도 | 빠름 | 중간 | 빠름 |
| 확장성 | 자동 | 수동 | 자동 |

> **결정: Option A** — 1인 개발, MVP 속도, 무료 티어 활용에 최적화

---

## 7. Threat Modeling (STRIDE)

### 7.1 위협 분석

| 위협 유형 | 시나리오 | 영향 | 완화 전략 |
|----------|----------|------|----------|
| **Spoofing** | N/A (인증 없음) | - | - |
| **Tampering** | LocalStorage 조작 | 낮음 | 계산은 서버에서 수행 |
| **Repudiation** | N/A (감사 로그 없음) | - | - |
| **Information Disclosure** | 민감 데이터 없음 | 없음 | - |
| **Denial of Service** | API 남용 | 중간 | Vercel 기본 보호 |
| **Elevation of Privilege** | N/A (권한 없음) | - | - |

### 7.2 완화 전략 요약

| 위협 | MVP 대응 | Post-MVP 고려 |
|------|----------|--------------|
| API 남용 (DoS) | Vercel 기본 보호 의존 | Rate Limiting 추가 |
| 입력 인젝션 | 티커 유효성 검증 | 입력 sanitization 강화 |
| CORS 우회 | Vercel same-origin | 명시적 CORS 정책 |

---

## 8. Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        GitHub                               │
│  ┌───────────────────────────────────────────────────────┐ │
│  │                   main branch                          │ │
│  │  (push triggers deployment)                            │ │
│  └───────────────────────────┬───────────────────────────┘ │
└──────────────────────────────┼──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                        Vercel                               │
│  ┌───────────────────────────────────────────────────────┐ │
│  │                   Build Pipeline                       │ │
│  │  1. npm install                                        │ │
│  │  2. next build                                         │ │
│  │  3. Python runtime setup                               │ │
│  └───────────────────────────┬───────────────────────────┘ │
│                               │                             │
│  ┌───────────────────────────▼───────────────────────────┐ │
│  │                   Production                           │ │
│  │  • https://<project>.vercel.app                       │ │
│  │  • CDN (Edge Network)                                 │ │
│  │  • Serverless Functions                               │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 배포 전략
- **방식**: Git Push → 자동 배포 (Vercel CI/CD)
- **환경**: Production only (staging 없음 — MVP)
- **롤백**: Vercel 대시보드에서 이전 배포로 롤백

---

## 9. Decision Log (Full)

| ID | 항목 | 선택 | 근거 | 영향 | 대안 |
|----|------|------|------|------|------|
| D-01 | 제품 | FAA 스코어링 도구 | 수동 계산 자동화 | - | - |
| D-02 | 핵심 기능 | 스코어+배분+백테스트 | MVP 필수 | - | - |
| D-03 | Non-goal | 로그인/알림 제외 | MVP 축소 | - | - |
| D-04 | 노스스타 | DAU 100명 | 정의됨 | - | - |
| D-05 | 수익모델 | 애드센스 | 정의됨 | - | - |
| D-06 | 종목 | 사용자 커스터마이징 | 유연성 | 입력 검증 필요 | 고정 유니버스 |
| D-07 | 저장 | LocalStorage | 무로그인 | 기기간 동기화 불가 | 서버 저장 |
| D-08 | 플랫폼 | 웹 only | 1인 개발 | - | PWA |
| D-09 | 데이터 | yfinance | 무료/빠름 | 라이선스 리스크 | 유료 API |
| D-10 | 알림 | 제외 | MVP 단순화 | - | 이메일 |
| D-11 | 인력/일정 | 1인/ASAP | 제약 | 스콥 제한 | - |
| D-12 | 종목군 | 1개만 | MVP | - | 다중 |
| D-13 | 백테스트 저장 | 안 함 | MVP | 매번 재실행 | 저장 |
| D-14 | 데이터 갱신 | 일 1회 | 일반적 | - | 실시간 |
| D-15 | API 호출 | Serverless | MVP | - | 직접 호출 |
| D-16 | 백테스트 범위 | 5년+ | 장기 검증 | 로딩 시간 | 1년 |
| D-17 | 티커 검증 | 실시간 | UX | API 호출 증가 | 계산시 |
| D-18 | 통화 | USD only | MVP | - | KRW 지원 |
| D-19 | 결측 데이터 | Forward fill | 자동 | 부정확 가능 | 제외 |
| D-20 | 응답시간 | 10초 | 백테스트 포함 | - | 3초 |
| D-21 | 동시 사용자 | 10명 | 초기 | - | 100명 |
| D-22 | 가용성 | 99% | 무료 티어 | - | 99.9% |
| D-23 | Rate Limit | 없음 | MVP | - | IP 제한 |
| D-24 | 보안 검증 | 없음 | MVP | - | 기본 |
| D-25 | 배포 | git push 자동 | 기본 | - | 수동 승인 |
| D-26 | 에러 추적 | Vercel 로그 | 무료 | - | Sentry |
| D-27 | 도메인 | *.vercel.app | 무료 | - | 커스텀 |
| D-28 | 프론트엔드 | Next.js | Vercel 최적화 | - | Vite |
| D-29 | UI | shadcn/ui | 빠른 개발 | - | MUI |
| D-30 | 차트 | Recharts | React 친화 | - | Chart.js |
| D-31 | Python | 3.11 | 최신 | - | 3.9 |
| D-32 | 레포 | 모노레포 | 단일 관리 | - | 분리 |
| D-33 | 브랜치 | main+feature | 기본 | - | trunk |
| D-34 | 테스트 | 핵심 로직 단위 | MVP 품질 | - | 없음 |
| D-35 | AI 협업 | 전체 생성 | 속도 | 리뷰 필수 | 부분 |

---

## 10. File Structure (Proposed)

```
faa-calculator/
├── app/                          # Next.js App Router
│   ├── layout.tsx                # 루트 레이아웃
│   ├── page.tsx                  # 메인 페이지 (스코어 계산)
│   ├── backtest/
│   │   └── page.tsx              # 백테스트 페이지
│   └── globals.css               # 글로벌 스타일
├── components/
│   ├── ui/                       # shadcn/ui 컴포넌트
│   ├── TickerInput.tsx           # 티커 입력 컴포넌트
│   ├── ScoreTable.tsx            # 점수 테이블
│   ├── AllocationResult.tsx      # 배분 결과
│   ├── BacktestChart.tsx         # 백테스트 차트
│   └── Header.tsx                # 공통 헤더
├── lib/
│   ├── localStorage.ts           # LocalStorage 유틸
│   └── api.ts                    # API 호출 함수
├── api/                          # Python Serverless Functions
│   ├── validate_ticker.py
│   ├── score.py
│   └── backtest.py
├── requirements.txt              # Python 의존성
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── vercel.json                   # Vercel 설정
```
