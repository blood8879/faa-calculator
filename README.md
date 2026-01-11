# FAA Strategy Calculator

Financial Asset Allocation (FAA) 전략을 활용한 포트폴리오 최적화 계산기입니다.

## 🚀 Features

- **티커 검증**: 실시간 티커 심볼 유효성 검증
- **FAA 스코어 계산**: 모멘텀, 변동성, 상관성 기반 자산 점수 산출
- **투자 배분**: 선정된 자산에 대한 균등 배분 계산
- **백테스트**: 과거 데이터를 활용한 전략 성과 분석
- **벤치마크 비교**: SPY 대비 성과 비교

## 📋 Requirements

- Node.js 18+
- Python 3.8+
- npm or yarn

## 🛠️ Installation

```bash
# Clone the repository
git clone <repository-url>
cd faa-calculator

# Install Node.js dependencies
npm install

# Install Python dependencies
pip install -r requirements.txt
```

## 🏃 Running the Application

### Development Mode

```bash
# Start the development server
npm run dev
```

애플리케이션이 http://localhost:3000에서 실행됩니다.

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## 📁 Project Structure

```
faa-calculator/
├── app/                    # Next.js app router pages
│   ├── page.tsx           # 메인 계산기 페이지
│   ├── backtest/          # 백테스트 페이지
│   └── layout.tsx         # 앱 레이아웃
├── components/            # React 컴포넌트
│   ├── TickerInput.tsx    # 티커 입력 컴포넌트
│   ├── ScoreTable.tsx     # 스코어 테이블
│   ├── AllocationResult.tsx # 배분 결과
│   ├── BacktestChart.tsx  # 백테스트 차트
│   ├── MetricCard.tsx     # 성과 지표 카드
│   └── ui/                # shadcn/ui 컴포넌트
├── api/                   # Python API endpoints
│   ├── validate_ticker.py # 티커 검증 API
│   ├── score.py          # FAA 스코어 계산 API
│   ├── backtest.py       # 백테스트 API
│   └── faa_calculator.py # FAA 계산 로직
├── lib/                   # 유틸리티 함수
│   ├── localStorage.ts   # LocalStorage 관리
│   ├── types.ts          # TypeScript 타입 정의
│   └── utils.ts          # 공통 유틸리티
└── __tests__/            # 테스트 파일

```

## 🔧 API Endpoints

### 1. Ticker Validation

```http
POST /api/validate-ticker
Content-Type: application/json

{
  "ticker": "VTI"
}
```

**Response:**
```json
{
  "valid": true,
  "name": "Vanguard Total Stock Market ETF",
  "exchange": "PCX"
}
```

### 2. FAA Score Calculation

```http
POST /api/score
Content-Type: application/json

{
  "tickers": ["VTI", "VEA", "VWO", "SHY", "BND", "GSG", "VNQ"],
  "amount": 10000
}
```

**Response:**
```json
{
  "success": true,
  "scores": {
    "VTI": {
      "momentum": 0.15,
      "momentum_rank": 1,
      "volatility": 0.12,
      "volatility_rank": 2,
      "correlation": 0.85,
      "correlation_rank": 3,
      "integrated_score": 2.0,
      "selected": true,
      "cash_replacement": false
    }
  },
  "allocation": {
    "VTI": 3333.33,
    "VEA": 3333.33,
    "VWO": 3333.34
  }
}
```

### 3. Backtest

```http
POST /api/backtest
Content-Type: application/json

{
  "tickers": ["VTI", "VEA", "VWO", "SHY", "BND", "GSG", "VNQ"],
  "start_date": "2019-01-01"
}
```

**Response:**
```json
{
  "success": true,
  "equity_curve": [
    {"date": "2019-01-01", "value": 10000, "return": 0},
    {"date": "2019-02-01", "value": 10500, "return": 0.05}
  ],
  "metrics": {
    "cagr": 0.12,
    "mdd": -0.15,
    "sharpe": 1.5
  },
  "spy_benchmark": [...]
}
```

## 🧪 Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run Python tests
python -m pytest api/
```

## 📊 FAA Strategy

FAA (Financial Asset Allocation) 전략은 다음 3가지 지표를 기반으로 자산을 평가합니다:

1. **모멘텀 (Momentum)**: 최근 4개월 수익률
2. **변동성 (Volatility)**: 80일 일별 수익률 표준편차
3. **상관성 (Correlation)**: 다른 자산과의 상관계수 합

**통합 점수 계산:**
```
Score = Momentum_Rank × 1.0 + Volatility_Rank × 0.5 + Correlation_Rank × 0.5
```

**자산 선정:**
- 상위 3개 자산 선정
- 절대 모멘텀 < 0인 경우 현금(SHY) 대체

## 🌐 Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Environment Variables

필요한 환경 변수가 있다면 `.env.local`에 설정:

```env
# Add any required environment variables here
```

## 📝 License

MIT License

## 👥 Contributors

- Built with Claude Code + Sisyphus Multi-Agent System

## 🙏 Acknowledgments

- [Next.js](https://nextjs.org/)
- [shadcn/ui](https://ui.shadcn.com/)
- [Recharts](https://recharts.org/)
- [yfinance](https://github.com/ranaroussi/yfinance)

---

**Note**: 이 프로젝트는 교육 및 연구 목적으로 제작되었습니다. 실제 투자 결정에 사용하기 전에 충분한 검증이 필요합니다.
