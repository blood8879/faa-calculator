import { NextResponse } from 'next/server';

/**
 * POST /api/validate_ticker
 * Validates ticker symbol format
 *
 * This is a simplified validation for better UX.
 * Real ticker existence is verified during score calculation.
 */
export async function POST(request: Request) {
  try {
    const body = await request.json();
    const ticker = body.ticker?.trim().toUpperCase();

    if (!ticker) {
      return NextResponse.json(
        { error: 'Missing ticker field', valid: false },
        { status: 400 }
      );
    }

    // Basic ticker format validation
    // Most US stock tickers are 1-5 uppercase letters
    // Can also include dots (e.g., BRK.B)
    const tickerPattern = /^[A-Z]{1,5}(\.[A-Z])?$/;

    if (!tickerPattern.test(ticker)) {
      return NextResponse.json({ valid: false });
    }

    // Format is valid
    return NextResponse.json({
      valid: true,
      name: `${ticker} (Format Valid)`,
      exchange: 'To be verified',
    });
  } catch (error) {
    console.error('Ticker validation error:', error);
    return NextResponse.json(
      { error: 'Internal server error', valid: false },
      { status: 500 }
    );
  }
}

// Handle OPTIONS for CORS
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}
