import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ScoreTable, { ScoreData } from '@/components/ScoreTable';

describe('ScoreTable Component', () => {
  const mockScores: ScoreData[] = [
    {
      ticker: 'VTI',
      momentum: 0.15,
      volatility: 0.12,
      correlation: 0.85,
      momentum_rank: 1,
      volatility_rank: 2,
      correlation_rank: 3,
      total_score: 2.0,
      selected: true,
      cash_proxy: false,
    },
    {
      ticker: 'VEA',
      momentum: 0.10,
      volatility: 0.15,
      correlation: 0.90,
      momentum_rank: 2,
      volatility_rank: 3,
      correlation_rank: 4,
      total_score: 3.5,
      selected: true,
      cash_proxy: false,
    },
    {
      ticker: 'SHY',
      momentum: -0.05,
      volatility: 0.05,
      correlation: 0.20,
      momentum_rank: 7,
      volatility_rank: 1,
      correlation_rank: 1,
      total_score: 8.5,
      selected: true,
      cash_proxy: true,
    },
  ];

  it('renders score table with data', () => {
    render(<ScoreTable scores={mockScores} />);

    expect(screen.getByText('FAA Scores')).toBeInTheDocument();
    expect(screen.getByText('VTI')).toBeInTheDocument();
    expect(screen.getByText('VEA')).toBeInTheDocument();
    expect(screen.getByText('SHY')).toBeInTheDocument();
  });

  it('displays loading state', () => {
    render(<ScoreTable scores={[]} isLoading={true} />);

    expect(screen.getByText('Calculating scores...')).toBeInTheDocument();
  });

  it('renders nothing when no scores provided', () => {
    const { container } = render(<ScoreTable scores={[]} />);

    expect(container.firstChild).toBeNull();
  });

  it('formats momentum as percentage', () => {
    render(<ScoreTable scores={mockScores} />);

    // 15% momentum for VTI
    expect(screen.getByText('15.00%')).toBeInTheDocument();
  });

  it('shows selected badge for selected assets', () => {
    render(<ScoreTable scores={mockScores} />);

    const selectedBadges = screen.getAllByText('Selected');
    expect(selectedBadges).toHaveLength(3);
  });

  it('shows cash badge for cash proxy assets', () => {
    render(<ScoreTable scores={mockScores} />);

    expect(screen.getByText('Cash')).toBeInTheDocument();
  });

  it('sorts scores by total_score in descending order', () => {
    render(<ScoreTable scores={mockScores} />);

    const rows = screen.getAllByRole('row');
    // First row is header, second should be VTI (lowest score 2.0)
    expect(rows[1]).toHaveTextContent('VTI');
  });
});
