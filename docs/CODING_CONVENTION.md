# Coding Convention & AI Collaboration Guide

> FAA Strategy Calculator  
> Version: 1.0 | Date: 2026-01-07

---

## 핵심 원칙

> **"Don't trust, verify"**  
> AI가 생성한 모든 코드는 검증 후 커밋한다.

---

## 1. 레포지토리 구조

```
faa-calculator/
├── app/                    # Next.js App Router
│   ├── layout.tsx
│   ├── page.tsx
│   ├── backtest/
│   │   └── page.tsx
│   └── globals.css
├── components/
│   ├── ui/                 # shadcn/ui 컴포넌트
│   ├── TickerInput.tsx
│   ├── ScoreTable.tsx
│   ├── AllocationResult.tsx
│   ├── BacktestChart.tsx
│   └── Header.tsx
├── lib/
│   ├── localStorage.ts
│   ├── api.ts
│   └── utils.ts
├── api/                    # Python Serverless
│   ├── validate_ticker.py
│   ├── score.py
│   ├── backtest.py
│   └── faa_calculator.py
├── __tests__/
│   ├── faa_calculator.test.py
│   └── localStorage.test.ts
├── requirements.txt
├── package.json
├── vercel.json
└── README.md
```

---

## 2. 네이밍 컨벤션

### 파일명

| 유형 | 규칙 | 예시 |
|------|------|------|
| React 컴포넌트 | PascalCase | `TickerInput.tsx` |
| 유틸리티 | camelCase | `localStorage.ts` |
| Python 모듈 | snake_case | `faa_calculator.py` |
| 테스트 | *.test.ts/py | `localStorage.test.ts` |

### 코드 내 네이밍

| 유형 | TypeScript | Python |
|------|------------|--------|
| 변수/함수 | camelCase | snake_case |
| 상수 | UPPER_SNAKE | UPPER_SNAKE |
| 클래스/타입 | PascalCase | PascalCase |
| 컴포넌트 | PascalCase | - |

---

## 3. TypeScript 스타일

### 타입 정의

```typescript
// ✅ 인터페이스 사용 (확장 가능)
interface ScoreResult {
  ticker: string;
  momentum: number;
  volatility: number;
  correlation: number;
  totalScore: number;
  selected: boolean;
}

// ✅ 유니온 타입
type TickerState = 'empty' | 'validating' | 'valid' | 'invalid';
```

### 컴포넌트 패턴

```typescript
// ✅ 함수 컴포넌트 + Props 타입
interface TickerInputProps {
  value: string;
  onChange: (value: string) => void;
  state: TickerState;
}

export function TickerInput({ value, onChange, state }: TickerInputProps) {
  return (/* ... */);
}
```

### 금지 사항

```typescript
// ❌ any 사용 금지
const data: any = response;

// ❌ 타입 단언 남용 금지
const result = data as ScoreResult;

// ✅ 타입 가드 사용
function isScoreResult(data: unknown): data is ScoreResult {
  return typeof data === 'object' && data !== null && 'ticker' in data;
}
```

---

## 4. Python 스타일

### 타입 힌트

```python
# ✅ 타입 힌트 필수
def calculate_momentum(prices: pd.Series) -> float:
    return (prices.iloc[-1] / prices.iloc[0]) - 1

# ✅ 반환 타입 명시
def get_scores(tickers: list[str]) -> dict[str, ScoreResult]:
    pass
```

### Docstring

```python
def calculate_faa_score(tickers: list[str], lookback_days: int = 80) -> dict:
    """
    FAA 전략 스코어를 계산합니다.
    
    Args:
        tickers: 7개 티커 심볼 리스트
        lookback_days: 관측 기간 (기본 80일)
    
    Returns:
        각 티커별 스코어 및 순위 정보
    
    Raises:
        ValueError: 티커가 7개가 아닌 경우
    """
    pass
```

---

## 5. Git 워크플로우

### 브랜치 전략

```
main              ← 프로덕션 (자동 배포)
  └── feature/*   ← 기능 개발
```

### 브랜치 네이밍

```
feature/TASK-001-project-setup
feature/TASK-005-faa-calculator
fix/score-calculation-bug
```

### 커밋 메시지

```
<type>(<scope>): <subject>

[optional body]
```

**Type**:
- `feat`: 새 기능
- `fix`: 버그 수정
- `refactor`: 리팩토링
- `test`: 테스트
- `docs`: 문서
- `chore`: 빌드/설정

**예시**:
```
feat(api): implement FAA score calculation

- Add momentum calculation
- Add volatility calculation
- Add correlation calculation
- TASK-005
```

### PR 규칙

1. feature → main PR 필수
2. Self-review 체크리스트 완료
3. 테스트 통과 확인
4. 1인 개발이므로 자체 승인 후 머지

---

## 6. 코드 품질

### Linting

```json
// .eslintrc.json
{
  "extends": ["next/core-web-vitals"],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/no-explicit-any": "error"
  }
}
```

### Formatting

```json
// .prettierrc
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5"
}
```

### Python

```
# requirements.txt에 추가
black
flake8
mypy
```

---

## 7. 보안 가이드

### 비밀 관리

```bash
# ❌ 코드에 직접 포함 금지
API_KEY = "sk-1234..."

# ✅ 환경 변수 사용
import os
API_KEY = os.environ.get("API_KEY")
```

### 입력 검증

```python
# ✅ 티커 검증
import re

def validate_ticker(ticker: str) -> bool:
    # 1-5자 대문자 영문만 허용
    return bool(re.match(r'^[A-Z]{1,5}$', ticker.upper()))
```

### XSS 방지

```typescript
// ✅ React 기본 escaping 사용
<div>{userInput}</div>

// ❌ dangerouslySetInnerHTML 금지
<div dangerouslySetInnerHTML={{ __html: userInput }} />
```

---

## 8. AI 협업 규칙

### 8.1 작업 단위

```
1 Task = 1 PR = 1 기능 단위
```

- TASK 단위로 AI에게 요청
- 너무 큰 범위 한 번에 요청 금지
- 완료 후 검증 → 다음 TASK

### 8.2 컨텍스트 공유

AI에게 제공할 정보:
1. 현재 TASK ID 및 설명
2. 관련 PRD/TRD 섹션 링크
3. 기존 코드 구조 (필요시)
4. 예상 입출력 예시

```markdown
## 요청
TASK-005: FAA 스코어 계산 로직 구현

## 컨텍스트
- PRD 섹션 9의 공식 참조
- 입력: 7개 티커
- 출력: 각 티커별 모멘텀, 변동성, 상관성, 순위

## 제약
- yfinance 사용
- 응답시간 10초 이내
```

### 8.3 코드 리뷰 체크리스트

AI 생성 코드 검증 시 확인:

**기능**:
- [ ] 요구사항 충족
- [ ] 엣지 케이스 처리
- [ ] 에러 핸들링

**품질**:
- [ ] 타입 안전성
- [ ] 네이밍 컨벤션 준수
- [ ] 중복 코드 없음

**보안**:
- [ ] 입력 검증
- [ ] 비밀 하드코딩 없음

**성능**:
- [ ] 불필요한 API 호출 없음
- [ ] 메모리 누수 없음

### 8.4 오류 처리 프로토콜

AI 코드에서 오류 발생 시:

1. **에러 로그 전체 공유**
2. **재현 단계 설명**
3. **기대 동작 vs 실제 동작**
4. **시도한 해결책**

```markdown
## 에러 발생
TASK-006 /api/score 엔드포인트

## 에러 로그
```
TypeError: Cannot read property 'iloc' of undefined
  at calculate_momentum (faa_calculator.py:23)
```

## 재현 단계
1. POST /api/score with tickers=["VTI", ...]
2. 에러 발생

## 기대 동작
스코어 계산 결과 반환

## 시도한 해결책
- 데이터 로딩 확인 → 정상
```

### 8.5 회귀 방지

```
변경 전 → 테스트 실행 → 변경 후 → 테스트 실행 → 커밋
```

---

## 9. 디버깅 워크플로우

### 프론트엔드

```typescript
// 1. console.log 디버깅
console.log('[ScoreTable] scores:', scores);

// 2. React DevTools 활용

// 3. Network 탭 확인
```

### 백엔드 (Python)

```python
# 1. print 디버깅
print(f"[score.py] tickers: {tickers}")

# 2. Vercel 로그 확인
# vercel logs --follow
```

### 공통

1. 에러 메시지 정확히 읽기
2. 최소 재현 케이스 만들기
3. 이분 탐색으로 원인 좁히기
4. 수정 후 테스트

---

## 10. 테스트 가이드

### 단위 테스트 (Python)

```python
# __tests__/test_faa_calculator.py
import pytest
from api.faa_calculator import calculate_momentum

def test_momentum_positive():
    prices = pd.Series([100, 105, 110, 115, 120])
    result = calculate_momentum(prices)
    assert result == pytest.approx(0.2, rel=1e-2)

def test_momentum_negative():
    prices = pd.Series([100, 95, 90, 85, 80])
    result = calculate_momentum(prices)
    assert result == pytest.approx(-0.2, rel=1e-2)
```

### 단위 테스트 (TypeScript)

```typescript
// __tests__/localStorage.test.ts
import { getPortfolio, savePortfolio } from '@/lib/localStorage';

describe('localStorage', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  test('returns default tickers when empty', () => {
    const result = getPortfolio();
    expect(result).toHaveLength(7);
    expect(result[0]).toBe('VTI');
  });
});
```

---

## 11. 문서 참조 링크

| 문서 | 용도 |
|------|------|
| [PRD.md](file:///Users/yunjihwan/.gemini/antigravity/brain/9d420c35-8a71-4e40-8d28-3bc9f52216cb/PRD.md) | 요구사항 확인 |
| [TRD.md](file:///Users/yunjihwan/.gemini/antigravity/brain/9d420c35-8a71-4e40-8d28-3bc9f52216cb/TRD.md) | 기술 스펙 확인 |
| [USER_FLOW.md](file:///Users/yunjihwan/.gemini/antigravity/brain/9d420c35-8a71-4e40-8d28-3bc9f52216cb/USER_FLOW.md) | 사용자 흐름 |
| [DATABASE_DESIGN.md](file:///Users/yunjihwan/.gemini/antigravity/brain/9d420c35-8a71-4e40-8d28-3bc9f52216cb/DATABASE_DESIGN.md) | 데이터 구조 |
| [DESIGN_SYSTEM.md](file:///Users/yunjihwan/.gemini/antigravity/brain/9d420c35-8a71-4e40-8d28-3bc9f52216cb/DESIGN_SYSTEM.md) | UI 스타일 |
| [TASKS.md](file:///Users/yunjihwan/.gemini/antigravity/brain/9d420c35-8a71-4e40-8d28-3bc9f52216cb/TASKS.md) | 개발 태스크 |
