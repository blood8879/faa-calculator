# lib/ - Utility Functions

This directory contains reusable utility functions for the FAA Calculator application.

## localStorage.ts

Type-safe localStorage wrapper for persisting user data.

### Features

- SSR-safe (checks for window object)
- Full TypeScript type safety
- Runtime data validation
- Automatic data normalization
- Error handling with console logging

### Usage

```typescript
import { getPortfolio, savePortfolio, getAmount, saveAmount, clearAll } from '@/lib/localStorage';

// Save user's portfolio
const tickers = ['VTI', 'VEA', 'VWO', 'SHY', 'BND', 'GSG', 'VNQ'];
savePortfolio(tickers); // Returns true on success

// Retrieve portfolio (returns null if not found)
const savedTickers = getPortfolio();
if (savedTickers) {
  console.log('Saved tickers:', savedTickers);
}

// Save investment amount
saveAmount(10000); // Returns true on success

// Retrieve amount (returns null if not found)
const savedAmount = getAmount();
if (savedAmount !== null) {
  console.log('Saved amount:', savedAmount);
}

// Clear all saved data
clearAll(); // Returns true on success
```

### Data Validation

#### Portfolio (Tickers)
- Must be an array of strings
- Automatically trimmed and uppercased
- Empty strings are filtered out
- Invalid inputs return `false` and log error

```typescript
savePortfolio(['  vti  ', 'vea', 'VWO ']);
// Saves as: ['VTI', 'VEA', 'VWO']

savePortfolio('VTI'); // Returns false (not an array)
savePortfolio(['VTI', 123]); // Returns false (contains non-string)
```

#### Amount
- Must be a positive number
- Rejects NaN, Infinity, and negative values
- Supports decimal values
- Zero is allowed

```typescript
saveAmount(10000);    // OK
saveAmount(10000.50); // OK
saveAmount(0);        // OK
saveAmount(-1000);    // Returns false
saveAmount(NaN);      // Returns false
saveAmount(Infinity); // Returns false
```

### SSR Compatibility

All functions check for `window` object availability before accessing localStorage. This prevents errors during server-side rendering in Next.js.

```typescript
// During SSR
getPortfolio();    // Returns null (instead of crashing)
savePortfolio([]); // Returns false (instead of crashing)
```

### Error Handling

All functions include try-catch blocks and log errors to console:

```typescript
// If localStorage is corrupted or unavailable
getPortfolio(); // Returns null, logs error to console
savePortfolio(['VTI']); // Returns false, logs error to console
```

### Storage Keys

The utility uses namespaced keys to avoid conflicts:
- `faa_portfolio` - Stores ticker array
- `faa_investment_amount` - Stores investment amount

### Testing

See `__tests__/localStorage.test.ts` for comprehensive test coverage including:
- SSR safety
- CRUD operations
- Validation scenarios
- Error recovery
- Integration workflows
- Edge cases

Run tests with:
```bash
npm test localStorage
```

## utils.ts

Standard shadcn/ui utility for className merging.

### Usage

```typescript
import { cn } from '@/lib/utils';

// Merge Tailwind classes with conflict resolution
const className = cn('px-4 py-2', isActive && 'bg-blue-500', 'px-6');
// Result: 'py-2 bg-blue-500 px-6' (px-6 overrides px-4)
```
