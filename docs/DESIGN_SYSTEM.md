# Design System: FAA Strategy Calculator

> Version: 1.0 | Date: 2026-01-07

---

## 1. 디자인 원칙

1. **명확함**: 투자 데이터는 한눈에 이해 가능해야 함
2. **신뢰감**: 금융 서비스답게 전문적이고 안정적인 느낌
3. **효율성**: 최소 클릭으로 원하는 결과 도달
4. **반응성**: 데스크톱/태블릿/모바일 모두 지원
5. **접근성**: WCAG 2.1 AA 준수

---

## 2. 디자인 토큰

### 2.1 색상 (Colors)

```css
:root {
  /* Primary - 신뢰/금융 (Blue) */
  --primary: 221.2 83.2% 53.3%;
  --primary-foreground: 210 40% 98%;
  
  /* Secondary - 보조 */
  --secondary: 210 40% 96%;
  --secondary-foreground: 222.2 47.4% 11.2%;
  
  /* 상태 색상 */
  --success: 142.1 76.2% 36.3%;      /* 상승/긍정 */
  --destructive: 0 84.2% 60.2%;      /* 하락/에러 */
  --warning: 38 92% 50%;             /* 경고 */
  
  /* 중립 */
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --muted: 210 40% 96%;
  --muted-foreground: 215.4 16.3% 46.9%;
  
  /* 테두리/구분선 */
  --border: 214.3 31.8% 91.4%;
  --ring: 221.2 83.2% 53.3%;
}

/* Dark Mode */
.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  --primary: 217.2 91.2% 59.8%;
  --muted: 217.2 32.6% 17.5%;
}
```

### 2.2 타이포그래피 (Typography)

```css
:root {
  /* Font Family */
  --font-sans: 'Inter', -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
  
  /* Font Size */
  --text-xs: 0.75rem;    /* 12px */
  --text-sm: 0.875rem;   /* 14px */
  --text-base: 1rem;     /* 16px */
  --text-lg: 1.125rem;   /* 18px */
  --text-xl: 1.25rem;    /* 20px */
  --text-2xl: 1.5rem;    /* 24px */
  --text-3xl: 1.875rem;  /* 30px */
  
  /* Font Weight */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
  
  /* Line Height */
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;
}
```

### 2.3 간격 (Spacing)

```css
:root {
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.25rem;   /* 20px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
  --space-10: 2.5rem;   /* 40px */
  --space-12: 3rem;     /* 48px */
}
```

### 2.4 그림자 (Shadows)

```css
:root {
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
}
```

### 2.5 애니메이션 (Animations)

```css
:root {
  --duration-fast: 150ms;
  --duration-normal: 300ms;
  --duration-slow: 500ms;
  --ease-default: cubic-bezier(0.4, 0, 0.2, 1);
}
```

---

## 3. 컴포넌트 목록

### 3.1 shadcn/ui 사용 컴포넌트

| 컴포넌트 | 용도 | 상태 |
|----------|------|------|
| Button | 계산하기, 백테스트 실행 | default, loading, disabled |
| Input | 티커 입력, 금액 입력 | default, error, success |
| Card | 결과 카드, 지표 카드 | default |
| Table | 스코어 테이블 | default, loading |
| Tabs | 메인/백테스트 전환 | default |
| Badge | 선정 종목, 상태 표시 | default, success, warning |
| Skeleton | 로딩 상태 | - |
| Alert | 에러/경고 메시지 | error, warning, info |

### 3.2 커스텀 컴포넌트

| 컴포넌트 | 설명 | 상태 |
|----------|------|------|
| TickerInput | 티커 입력 + 검증 | empty, validating, valid, invalid |
| ScoreTable | FAA 점수 테이블 | loading, loaded |
| AllocationCard | 배분 결과 카드 | hidden, visible |
| BacktestChart | 수익률 차트 | loading, loaded, error |
| MetricCard | 성과 지표 카드 | default |

---

## 4. 컴포넌트 상태

### TickerInput

```
┌─────────────────────────────────────────┐
│ [Empty]     │ 빈 입력      │ 회색 테두리  │
│ [Validating]│ 검증 중      │ Spinner     │
│ [Valid]     │ 유효         │ ✓ 녹색      │
│ [Invalid]   │ 무효         │ ✗ 빨강      │
└─────────────────────────────────────────┘
```

### Button

```
┌─────────────────────────────────────────┐
│ [Default]   │ 클릭 가능    │ Primary 색상 │
│ [Loading]   │ 처리 중      │ Spinner     │
│ [Disabled]  │ 비활성       │ 회색, 투명도 │
└─────────────────────────────────────────┘
```

---

## 5. 접근성 (Accessibility)

### WCAG 2.1 AA 체크리스트

| 항목 | 요구사항 | 구현 방법 |
|------|----------|----------|
| 색상 대비 | 4.5:1 이상 | shadcn 기본 준수 |
| 포커스 표시 | 시각적 포커스 링 | ring 클래스 사용 |
| 키보드 네비게이션 | Tab 순서 | tabIndex 관리 |
| 스크린 리더 | aria 레이블 | aria-label 적용 |
| 에러 안내 | 명확한 에러 메시지 | Alert 컴포넌트 |

### 키보드 단축키

| 키 | 동작 |
|----|------|
| Tab | 다음 입력 필드 |
| Enter | 폼 제출 (계산 실행) |
| Escape | 모달 닫기 |

---

## 6. 반응형 브레이크포인트

```css
/* Tailwind 기본값 사용 */
sm: 640px   /* 모바일 → 태블릿 */
md: 768px   /* 태블릿 → 작은 데스크톱 */
lg: 1024px  /* 데스크톱 */
xl: 1280px  /* 큰 데스크톱 */
```

### 레이아웃 변화

| 화면 | 종목 입력 | 결과 테이블 |
|------|----------|-------------|
| Mobile | 세로 1열 | 가로 스크롤 |
| Tablet | 세로 1열 | 전체 표시 |
| Desktop | 가로 그리드 | 전체 표시 |
