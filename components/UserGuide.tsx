'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { HelpCircle, X, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function UserGuide() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Help Button */}
      <Button
        onClick={() => setIsOpen(true)}
        variant="outline"
        size="sm"
        className="fixed bottom-6 right-6 shadow-lg z-50"
      >
        <HelpCircle className="mr-2 h-4 w-4" />
        사용방법
      </Button>

      {/* Guide Modal */}
      {isOpen && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-background border rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="sticky top-0 bg-background border-b p-6 flex items-center justify-between">
              <h2 className="text-2xl font-bold">FAA 계산기 사용방법</h2>
              <Button
                onClick={() => setIsOpen(false)}
                variant="ghost"
                size="sm"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>

            {/* Content */}
            <div className="p-6 space-y-8">
              {/* 소개 */}
              <section>
                <h3 className="text-xl font-semibold mb-3">FAA (Flexible Asset Allocation)란?</h3>
                <p className="text-muted-foreground leading-relaxed">
                  FAA는 모멘텀, 변동성, 상관관계를 종합적으로 고려하여 최적의 포트폴리오를 구성하는
                  자산 배분 전략입니다. 시장 상황에 따라 유연하게 자산을 재배분하여 위험을 관리하고
                  수익을 극대화합니다.
                </p>
              </section>

              {/* 사용 단계 */}
              <section>
                <h3 className="text-xl font-semibold mb-4">사용 단계</h3>
                <div className="space-y-6">
                  {/* Step 1 */}
                  <div className="flex gap-4">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-semibold">
                      1
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold mb-2">티커 입력</h4>
                      <p className="text-sm text-muted-foreground mb-3">
                        분석하고 싶은 7개의 ETF 또는 주식 티커를 입력하세요.
                      </p>
                      <div className="bg-muted p-3 rounded-md">
                        <p className="text-xs text-muted-foreground mb-2">
                          <strong>기본 티커 예시:</strong>
                        </p>
                        <ul className="text-xs text-muted-foreground space-y-1">
                          <li><ChevronRight className="inline h-3 w-3 mr-1" />VTI (미국 전체 주식)</li>
                          <li><ChevronRight className="inline h-3 w-3 mr-1" />VEA (선진국 주식)</li>
                          <li><ChevronRight className="inline h-3 w-3 mr-1" />VWO (신흥국 주식)</li>
                          <li><ChevronRight className="inline h-3 w-3 mr-1" />SHY (단기 미국 국채)</li>
                          <li><ChevronRight className="inline h-3 w-3 mr-1" />BND (미국 채권)</li>
                          <li><ChevronRight className="inline h-3 w-3 mr-1" />GSG (원자재)</li>
                          <li><ChevronRight className="inline h-3 w-3 mr-1" />VNQ (부동산)</li>
                        </ul>
                      </div>
                      <p className="text-xs text-muted-foreground mt-2">
                        💡 &quot;기본값 채우기&quot; 버튼을 클릭하면 위 티커들이 자동으로 입력됩니다.
                      </p>
                    </div>
                  </div>

                  {/* Step 2 */}
                  <div className="flex gap-4">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-semibold">
                      2
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold mb-2">스코어 계산</h4>
                      <p className="text-sm text-muted-foreground mb-3">
                        모든 티커가 검증되면 &quot;FAA 스코어 계산&quot; 버튼을 클릭하세요.
                      </p>
                      <div className="bg-muted p-3 rounded-md">
                        <p className="text-xs text-muted-foreground">
                          ⏱️ 계산에는 <strong>30초~1분</strong> 정도 소요됩니다.
                          Yahoo Finance에서 실시간 데이터를 가져오기 때문입니다.
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Step 3 */}
                  <div className="flex gap-4">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-semibold">
                      3
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold mb-2">결과 확인</h4>
                      <p className="text-sm text-muted-foreground mb-3">
                        각 티커의 모멘텀, 변동성, 상관관계 점수와 종합 점수를 확인하세요.
                      </p>
                      <ul className="text-sm text-muted-foreground space-y-2">
                        <li className="flex items-start">
                          <ChevronRight className="h-4 w-4 mr-2 mt-0.5 flex-shrink-0" />
                          <span><strong>모멘텀:</strong> 최근 4개월간 수익률</span>
                        </li>
                        <li className="flex items-start">
                          <ChevronRight className="h-4 w-4 mr-2 mt-0.5 flex-shrink-0" />
                          <span><strong>변동성:</strong> 80일 기준 가격 변동폭</span>
                        </li>
                        <li className="flex items-start">
                          <ChevronRight className="h-4 w-4 mr-2 mt-0.5 flex-shrink-0" />
                          <span><strong>상관관계:</strong> 다른 자산과의 연관성</span>
                        </li>
                        <li className="flex items-start">
                          <ChevronRight className="h-4 w-4 mr-2 mt-0.5 flex-shrink-0" />
                          <span><strong>종합점수:</strong> 모멘텀 × 1.0 + 변동성 × 0.5 + 상관관계 × 0.5</span>
                        </li>
                      </ul>
                      <div className="bg-primary/5 border border-primary/20 p-3 rounded-md mt-3">
                        <p className="text-xs text-muted-foreground">
                          📊 <strong>종합점수가 낮을수록 좋습니다.</strong> 상위 3개 티커가 자동으로 선택됩니다.
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Step 4 */}
                  <div className="flex gap-4">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-semibold">
                      4
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold mb-2">투자 금액 입력</h4>
                      <p className="text-sm text-muted-foreground mb-3">
                        투자할 총 금액을 USD로 입력하면 자산 배분을 확인할 수 있습니다.
                      </p>
                      <div className="bg-muted p-3 rounded-md">
                        <p className="text-xs text-muted-foreground">
                          💰 선택된 티커에 <strong>균등 배분</strong>됩니다.
                          예: $10,000 투자 시 3개 티커 선택되었다면 각각 약 $3,333씩 배분
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              {/* 주의사항 */}
              <section>
                <h3 className="text-xl font-semibold mb-3">주의사항</h3>
                <div className="bg-destructive/5 border border-destructive/20 p-4 rounded-md">
                  <ul className="text-sm text-muted-foreground space-y-2">
                    <li className="flex items-start">
                      <span className="text-destructive mr-2">⚠️</span>
                      <span>이 도구는 투자 조언이 아닙니다. 실제 투자 결정은 본인의 책임입니다.</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-destructive mr-2">⚠️</span>
                      <span>과거 성과가 미래 수익을 보장하지 않습니다.</span>
                    </li>
                    <li className="flex items-start">
                      <span className="text-destructive mr-2">⚠️</span>
                      <span>투자 전 전문가와 상담하시기 바랍니다.</span>
                    </li>
                  </ul>
                </div>
              </section>

              {/* FAQ */}
              <section>
                <h3 className="text-xl font-semibold mb-3">자주 묻는 질문</h3>
                <div className="space-y-4">
                  <div className="border rounded-md p-4">
                    <h4 className="font-semibold mb-2">Q. 계산이 너무 오래 걸려요</h4>
                    <p className="text-sm text-muted-foreground">
                      A. Yahoo Finance에서 실시간 데이터를 가져오기 때문에 30초~1분 정도 소요됩니다.
                      이는 정상적인 동작입니다.
                    </p>
                  </div>
                  <div className="border rounded-md p-4">
                    <h4 className="font-semibold mb-2">Q. 어떤 티커를 입력해야 하나요?</h4>
                    <p className="text-sm text-muted-foreground">
                      A. 주식, ETF, 인덱스 펀드 등 Yahoo Finance에서 거래되는 모든 티커를 사용할 수 있습니다.
                      &quot;기본값 채우기&quot; 버튼으로 추천 티커를 확인해보세요.
                    </p>
                  </div>
                  <div className="border rounded-md p-4">
                    <h4 className="font-semibold mb-2">Q. 왜 상위 3개만 선택되나요?</h4>
                    <p className="text-sm text-muted-foreground">
                      A. FAA 전략의 기본 원칙으로, 종합점수가 가장 낮은 (가장 좋은) 3개 자산에 집중 투자합니다.
                      이는 위험 분산과 수익 극대화의 균형을 맞춘 전략입니다.
                    </p>
                  </div>
                </div>
              </section>
            </div>

            {/* Footer */}
            <div className="border-t p-6 bg-muted/30">
              <Button
                onClick={() => setIsOpen(false)}
                className="w-full"
              >
                시작하기
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
