'use client';

import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

export interface ScoreData {
  ticker: string;
  current_price: number;
  momentum: number;
  volatility: number;
  correlation: number;
  momentum_rank: number;
  volatility_rank: number;
  correlation_rank: number;
  total_score: number;
  selected: boolean;
  cash_proxy: boolean;
  hold_cash: boolean;
}

interface ScoreTableProps {
  scores: ScoreData[];
  isLoading?: boolean;
}

export default function ScoreTable({ scores, isLoading = false }: ScoreTableProps) {
  if (isLoading) {
    return (
      <div className="w-full space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-semibold tracking-tight">FAA 스코어</h2>
        </div>
        <div className="rounded-lg border p-8 flex items-center justify-center">
          <p className="text-muted-foreground">스코어 계산 중...</p>
        </div>
      </div>
    );
  }

  if (!scores || scores.length === 0) {
    return null;
  }

  // Sort by total score (descending)
  const sortedScores = [...scores].sort((a, b) => b.total_score - a.total_score);

  return (
    <div className="w-full space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">FAA 스코어</h2>
          <p className="text-sm text-muted-foreground mt-1">
            종합 스코어 기준 정렬 (모멘텀 × 1.0 + 변동성 × 0.5 + 상관관계 × 0.5)
          </p>
        </div>
      </div>

      <div className="rounded-lg border overflow-hidden">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="bg-muted/50">
                <TableHead className="w-[100px] font-semibold">티커</TableHead>
                <TableHead className="text-right font-semibold">현재가</TableHead>
                <TableHead className="text-right font-semibold">모멘텀</TableHead>
                <TableHead className="text-right font-semibold">순위</TableHead>
                <TableHead className="text-right font-semibold">변동성</TableHead>
                <TableHead className="text-right font-semibold">순위</TableHead>
                <TableHead className="text-right font-semibold">상관관계</TableHead>
                <TableHead className="text-right font-semibold">순위</TableHead>
                <TableHead className="text-right font-semibold">종합점수</TableHead>
                <TableHead className="text-center font-semibold">상태</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sortedScores.map((score, index) => (
                <TableRow
                  key={score.ticker}
                  className={cn(
                    'transition-colors',
                    score.selected && 'bg-primary/5 hover:bg-primary/10'
                  )}
                >
                  {/* Ticker */}
                  <TableCell className="font-mono font-semibold">
                    {score.ticker}
                  </TableCell>

                  {/* Current Price */}
                  <TableCell className="text-right font-mono">
                    ${score.current_price.toFixed(2)}
                  </TableCell>

                  {/* Momentum */}
                  <TableCell className="text-right font-mono">
                    {(score.momentum * 100).toFixed(2)}%
                  </TableCell>
                  <TableCell className="text-right text-muted-foreground">
                    {score.momentum_rank}
                  </TableCell>

                  {/* Volatility */}
                  <TableCell className="text-right font-mono">
                    {(score.volatility * 100).toFixed(2)}%
                  </TableCell>
                  <TableCell className="text-right text-muted-foreground">
                    {score.volatility_rank}
                  </TableCell>

                  {/* Correlation */}
                  <TableCell className="text-right font-mono">
                    {score.correlation.toFixed(4)}
                  </TableCell>
                  <TableCell className="text-right text-muted-foreground">
                    {score.correlation_rank}
                  </TableCell>

                  {/* Total Score */}
                  <TableCell className="text-right font-mono font-semibold">
                    {score.total_score.toFixed(2)}
                  </TableCell>

                  {/* Status */}
                  <TableCell className="text-center">
                    <div className="flex items-center justify-center gap-1">
                      {score.selected && (
                        <Badge variant="default" className="font-semibold">
                          선택됨
                        </Badge>
                      )}
                      {score.hold_cash && (
                        <Badge variant="destructive" className="font-medium">
                          현금보유
                        </Badge>
                      )}
                      {score.cash_proxy && !score.hold_cash && (
                        <Badge variant="secondary" className="font-medium">
                          SHY
                        </Badge>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>

      {/* Summary */}
      <div className="flex items-center gap-4 text-sm text-muted-foreground">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-sm bg-primary/20 border border-primary/30" />
          <span>포트폴리오 선택 (상위 3개)</span>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="font-medium">SHY</Badge>
          <span>마이너스 모멘텀 자산 → SHY 대체</span>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="destructive" className="font-medium">현금보유</Badge>
          <span>SHY도 마이너스 → 100% 현금</span>
        </div>
      </div>
    </div>
  );
}
