# -*- coding: utf-8 -*-
"""
손PB 통합 정리 코드
- 가계부 분석 및 평가 결과를 글 형태로 정리
- 재무목표 선정 결과와 투자 자산 배분 표 생성
"""

import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

class FinancialAnalysisReport:
    def __init__(self, client_profile, goal_list, asset_names, yearly_weights):
        """
        재무 분석 보고서 클래스 초기화
        
        Args:
            client_profile: 고객 프로필 데이터
            goal_list: 재무목표 리스트
            asset_names: 자산군 이름 리스트
            yearly_weights: 연도별 자산 배분 가중치
        """
        self.client_profile = client_profile
        self.goal_list = goal_list
        self.asset_names = asset_names
        self.yearly_weights = yearly_weights
        
    def generate_household_analysis_report(self):
        """가계부 분석 및 평가 보고서 생성"""
        
        # 기본 정보 추출
        customer_info = self.client_profile.get('고객정보', {})
        financial_status = self.client_profile.get('수입/지출/투자 현황', {})
        asset_liability = self.client_profile.get('자산/부채 현황', {})
        monthly_cash_flow = self.client_profile.get('월별 현금흐름 요약', {})
        
        # 핵심 지표 계산
        avg_income = self._extract_amount(financial_status.get('최근 3개월 평균 수입', '0'))
        avg_expense = self._extract_amount(financial_status.get('최근 3개월 평균 지출', '0'))
        avg_investment = self._extract_amount(financial_status.get('최근 3개월 평균 저축/투자', '0'))
        avg_surplus = self._extract_amount(financial_status.get('최근 3개월 평균 현금(여윳돈)', '0'))
        
        total_assets = asset_liability.get('총자산', 0)
        total_liability = asset_liability.get('총부채', 0)
        net_assets = asset_liability.get('순자산', 0)
        
        # 재무건전성 지표 계산
        savings_rate = ((avg_investment + avg_surplus) / avg_income * 100) if avg_income > 0 else 0
        expense_ratio = (avg_expense / avg_income * 100) if avg_income > 0 else 0
        debt_ratio = (total_liability / total_assets * 100) if total_assets > 0 else 0
        
        # 비상자금 계산
        liquid_assets = self._calculate_liquid_assets(asset_liability)
        emergency_months = (liquid_assets / avg_expense) if avg_expense > 0 else 0
        
        report = f"""
# 📊 가계부 분석 및 재무상태 평가 보고서

## 1. 고객 기본 정보
- **고객명**: {customer_info.get('고객명', 'N/A')}
- **나이**: {customer_info.get('나이', 'N/A')}세
- **직업**: {customer_info.get('직업', 'N/A')}
- **성별**: {customer_info.get('성별', 'N/A')}
- **신용점수**: {customer_info.get('신용점수', 'N/A')}

## 2. 자산/부채 현황
- **총자산**: {self._format_currency(total_assets)}
- **총부채**: {self._format_currency(total_liability)}
- **순자산**: {self._format_currency(net_assets)}
- **부채비율**: {debt_ratio:.1f}%

## 3. 현금흐름 분석 (최근 3개월 평균)
- **월평균 수입**: {self._format_currency(avg_income)}
- **월평균 지출**: {self._format_currency(avg_expense)}
- **월평균 저축/투자**: {self._format_currency(avg_investment)}
- **월평균 여윳돈**: {self._format_currency(avg_surplus)}

## 4. 재무건전성 지표 평가

### 4.1 수지비율
- **현재 수지비율**: {expense_ratio:.1f}%
- **평가**: {self._evaluate_expense_ratio(expense_ratio)}

### 4.2 저축성향
- **현재 저축률**: {savings_rate:.1f}%
- **평가**: {self._evaluate_savings_rate(savings_rate)}

### 4.3 비상자금
- **유동성 자산**: {self._format_currency(liquid_assets)}
- **비상자금 개월수**: {emergency_months:.1f}개월
- **평가**: {self._evaluate_emergency_fund(emergency_months)}

## 5. 지출 구조 분석

### 5.1 최근 월별 지출 패턴
"""
        
        # 최근 3개월 지출 패턴 분석
        recent_months = list(monthly_cash_flow.keys())[-3:] if len(monthly_cash_flow) >= 3 else list(monthly_cash_flow.keys())
        
        for month in recent_months:
            month_data = monthly_cash_flow.get(month, {})
            expense_data = month_data.get('총지출(이체포함)', {})
            total_expense = expense_data.get('총합', 0)
            
            report += f"\n**{month}월 지출**: {self._format_currency(total_expense)}\n"
            
            # 상위 5개 지출 항목
            details = expense_data.get('상세내역', {})
            if isinstance(details, dict):
                sorted_expenses = sorted(details.items(), key=lambda x: x[1], reverse=True)[:5]
                for category, amount in sorted_expenses:
                    report += f"  - {category}: {self._format_currency(amount)}\n"
        
        report += f"""
## 6. 종합 평가 및 개선 방향

### 6.1 재무상태 강점
- {self._identify_strengths(avg_income, avg_expense, savings_rate, debt_ratio)}

### 6.2 개선 필요 영역
- {self._identify_improvements(expense_ratio, savings_rate, emergency_months, debt_ratio)}

### 6.3 권장 개선 방안
- {self._recommend_improvements(avg_income, avg_expense, savings_rate, emergency_months)}

## 7. 결론

> **{customer_info.get('고객명', '고객')}님의 재무상태는 전반적으로 {self._overall_assessment(expense_ratio, savings_rate, emergency_months, debt_ratio)} 수준입니다. 
> {self._conclusion_summary(avg_income, avg_expense, savings_rate, emergency_months)}**

---
*분석 기준일: {datetime.now().strftime('%Y년 %m월 %d일')}*
"""
        
        return report
    
    def generate_financial_goals_summary(self):
        """재무목표 선정 결과 및 투자 자산 배분 표 생성"""
        
        if not self.goal_list:
            return "재무목표가 설정되지 않았습니다."
        
        # 목표별 요약 테이블 생성
        goals_summary = []
        for goal in self.goal_list:
            goals_summary.append({
                '목표명': goal.get('name', 'N/A'),
                '목표기간(년)': goal.get('years', 0),
                '목표금액(원)': goal.get('target', 0),
                '우선순위': goal.get('priority', 0),
                '필수성': goal.get('necessity', '선택')
            })
        
        goals_df = pd.DataFrame(goals_summary)
        
        # 자산 배분 표 생성
        asset_allocation = self._create_asset_allocation_table()
        
        report = f"""
# 🎯 재무목표 선정 및 투자 자산 배분 계획

## 1. 선정된 재무목표 요약

### 1.1 목표별 상세 정보
"""
        
        # 목표별 상세 정보
        for i, goal in enumerate(self.goal_list, 1):
            report += f"""
**목표 {i}: {goal.get('name', 'N/A')}**
- 목표기간: {goal.get('years', 0)}년
- 목표금액: {self._format_currency(goal.get('target', 0))}
- 우선순위: {goal.get('priority', 0)}위
- 필수성: {goal.get('necessity', '선택')}
"""
        
        report += f"""
### 1.2 목표 요약 표
{goals_df.to_string(index=False)}

## 2. 투자 자산 배분 계획

### 2.1 자산군별 투자 비중
{asset_allocation.to_string(index=False)}

### 2.2 투자 전략 특징
- **TDF(Target Date Fund) 전략 적용**: 목표 시점에 가까워질수록 안정자산 비중 증가
- **리스크 관리**: 변동성 제한을 통한 포트폴리오 안정성 확보
- **다각화**: 국내외 주식, 채권, 원자재 등 다양한 자산군 분산 투자

## 3. 목표별 투자 실행 계획

### 3.1 단기 목표 (1-5년)
- **투자 성향**: 보수적
- **주요 자산**: 국내채권, 현금성 자산
- **예상 수익률**: 연 3-5%

### 3.2 중장기 목표 (5-15년)
- **투자 성향**: 중립적
- **주요 자산**: 국내주식, 해외주식, 채권 혼합
- **예상 수익률**: 연 5-8%

### 3.3 장기 목표 (15년 이상)
- **투자 성향**: 적극적
- **주요 자산**: 해외주식, 신흥시장, 원자재
- **예상 수익률**: 연 7-10%

## 4. 월 투자 계획

### 4.1 목표별 월 투자금액
"""
        
        # 목표별 월 투자금액 계산 (간단한 예시)
        total_monthly_investment = 0
        for goal in self.goal_list:
            target_amount = goal.get('target', 0)
            years = goal.get('years', 1)
            # 간단한 월 투자금액 계산 (복리 효과 고려하지 않은 단순 계산)
            monthly_investment = target_amount / (years * 12)
            total_monthly_investment += monthly_investment
            
            report += f"""
**{goal.get('name', 'N/A')}**
- 월 투자금액: {self._format_currency(monthly_investment)}
- 연간 투자금액: {self._format_currency(monthly_investment * 12)}
"""
        
        report += f"""
### 4.2 총 월 투자 계획
- **총 월 투자금액**: {self._format_currency(total_monthly_investment)}
- **총 연간 투자금액**: {self._format_currency(total_monthly_investment * 12)}

## 5. 리스크 관리 및 모니터링

### 5.1 정기 리밸런싱
- **빈도**: 분기별 또는 반기별
- **목적**: 목표 자산 배분 비중 유지
- **방법**: 수익률이 높은 자산 일부 매도, 낮은 자산 매수

### 5.2 성과 모니터링
- **지표**: 목표 대비 달성률, 포트폴리오 수익률, 변동성
- **기간**: 월별 점검, 분기별 종합 평가
- **조정**: 시장 상황 및 개인 상황 변화 시 투자 전략 조정

---
*계획 수립일: {datetime.now().strftime('%Y년 %m월 %d일')}*
"""
        
        return report
    
    def _extract_amount(self, amount_str):
        """금액 문자열에서 숫자 추출"""
        if isinstance(amount_str, (int, float)):
            return amount_str
        if isinstance(amount_str, str):
            # 쉼표와 '원' 제거
            cleaned = amount_str.replace(',', '').replace('원', '').strip()
            try:
                return int(cleaned)
            except:
                return 0
        return 0
    
    def _format_currency(self, amount):
        """금액을 한국 통화 형식으로 포맷"""
        if amount == 0:
            return "0원"
        if amount >= 100000000:  # 1억 이상
            return f"{amount/100000000:.1f}억원"
        elif amount >= 10000:  # 1만 이상
            return f"{amount/10000:.0f}만원"
        else:
            return f"{amount:,}원"
    
    def _calculate_liquid_assets(self, asset_liability):
        """유동성 자산 계산"""
        assets_detail = asset_liability.get('자산 상세', {})
        liquid_categories = ['자유입출금 자산', '현금성 자산']
        total_liquid = 0
        
        for category in liquid_categories:
            if category in assets_detail:
                category_assets = assets_detail[category]
                if isinstance(category_assets, dict):
                    total_liquid += sum(self._extract_amount(v) for v in category_assets.values())
        
        return total_liquid
    
    def _evaluate_expense_ratio(self, ratio):
        """수지비율 평가"""
        if ratio <= 70:
            return "매우 우수"
        elif ratio <= 80:
            return "우수"
        elif ratio <= 90:
            return "양호"
        elif ratio <= 100:
            return "보완 필요"
        else:
            return "미흡"
    
    def _evaluate_savings_rate(self, rate):
        """저축률 평가"""
        if rate >= 30:
            return "매우 우수"
        elif rate >= 20:
            return "우수"
        elif rate >= 10:
            return "양호"
        elif rate >= 5:
            return "보완 필요"
        else:
            return "미흡"
    
    def _evaluate_emergency_fund(self, months):
        """비상자금 평가"""
        if months >= 6:
            return "매우 우수"
        elif months >= 3:
            return "우수"
        elif months >= 1:
            return "양호"
        else:
            return "보완 필요"
    
    def _identify_strengths(self, income, expense, savings_rate, debt_ratio):
        """재무상태 강점 식별"""
        strengths = []
        if income > 4000000:  # 400만원 이상
            strengths.append("안정적인 소득 수준")
        if savings_rate >= 20:
            strengths.append("높은 저축률")
        if debt_ratio <= 20:
            strengths.append("낮은 부채비율")
        if expense / income <= 0.8:
            strengths.append("건전한 수지관리")
        
        return ", ".join(strengths) if strengths else "특별한 강점이 식별되지 않음"
    
    def _identify_improvements(self, expense_ratio, savings_rate, emergency_months, debt_ratio):
        """개선 필요 영역 식별"""
        improvements = []
        if expense_ratio > 80:
            improvements.append("지출 비율 감소 필요")
        if savings_rate < 20:
            improvements.append("저축률 향상 필요")
        if emergency_months < 3:
            improvements.append("비상자금 확충 필요")
        if debt_ratio > 40:
            improvements.append("부채 관리 필요")
        
        return ", ".join(improvements) if improvements else "현재 상태 유지 권장"
    
    def _recommend_improvements(self, income, expense, savings_rate, emergency_months):
        """개선 방안 권장"""
        recommendations = []
        
        if savings_rate < 20:
            target_savings = income * 0.2
            recommendations.append(f"저축률을 20%({self._format_currency(target_savings)})로 향상")
        
        if emergency_months < 3:
            target_emergency = expense * 3
            recommendations.append(f"비상자금을 {self._format_currency(target_emergency)}로 확충")
        
        if expense / income > 0.8:
            target_expense = income * 0.8
            recommendations.append(f"지출을 {self._format_currency(target_expense)} 이하로 관리")
        
        return "; ".join(recommendations) if recommendations else "현재 상태 유지"
    
    def _overall_assessment(self, expense_ratio, savings_rate, emergency_months, debt_ratio):
        """전체 재무상태 평가"""
        scores = []
        if expense_ratio <= 80: scores.append(1)
        if savings_rate >= 20: scores.append(1)
        if emergency_months >= 3: scores.append(1)
        if debt_ratio <= 40: scores.append(1)
        
        avg_score = sum(scores) / 4
        if avg_score >= 0.8:
            return "매우 우수"
        elif avg_score >= 0.6:
            return "우수"
        elif avg_score >= 0.4:
            return "양호"
        else:
            return "보완 필요"
    
    def _conclusion_summary(self, income, expense, savings_rate, emergency_months):
        """결론 요약"""
        if savings_rate >= 20 and emergency_months >= 3:
            return "안정적인 재무기반을 바탕으로 목표 달성에 집중할 수 있는 상태입니다."
        elif savings_rate >= 10:
            return "기본적인 재무건전성을 갖추고 있으나, 저축률 향상과 비상자금 확충이 권장됩니다."
        else:
            return "재무기반 강화를 위한 지출 관리와 저축 습관 형성이 우선적으로 필요합니다."
    
    def _create_asset_allocation_table(self):
        """자산 배분 표 생성"""
        if not self.yearly_weights or not self.asset_names:
            return pd.DataFrame()
        
        # 첫 해 자산 배분을 기준으로 표 생성
        first_year_weights = self.yearly_weights[0] if self.yearly_weights else []
        
        allocation_data = []
        for i, asset_name in enumerate(self.asset_names):
            weight = first_year_weights[i] if i < len(first_year_weights) else 0
            if weight > 0.01:  # 1% 이상만 표시
                allocation_data.append({
                    '자산군': asset_name,
                    '투자비중(%)': f"{weight*100:.1f}%",
                    '자산특성': self._classify_asset(asset_name),
                    '예상수익률(%)': self._estimate_return(asset_name)
                })
        
        return pd.DataFrame(allocation_data)
    
    def _classify_asset(self, asset_name):
        """자산 분류"""
        if '채권' in asset_name:
            return "안정자산"
        elif 'KOSPI' in asset_name or 'KOSDAQ' in asset_name:
            return "국내주식"
        elif 'S&P' in asset_name or '나스닥' in asset_name or '니케이' in asset_name:
            return "해외주식"
        elif 'GLD' in asset_name:
            return "원자재"
        else:
            return "기타"
    
    def _estimate_return(self, asset_name):
        """예상 수익률 추정"""
        if '채권' in asset_name:
            return "3-5%"
        elif 'KOSPI' in asset_name or 'KOSDAQ' in asset_name:
            return "6-8%"
        elif 'S&P' in asset_name or '나스닥' in asset_name:
            return "7-9%"
        elif 'GLD' in asset_name:
            return "4-6%"
        else:
            return "5-7%"

def main():
    """메인 실행 함수"""
    print("손PB 통합 정리 코드 실행 중...")
    
    # 예시 데이터 (실제로는 파일에서 로드)
    try:
        # client_profile 로드 시도
        if 'client_profile' in globals():
            client_profile = globals()['client_profile']
        else:
            print("client_profile을 찾을 수 없습니다. 예시 데이터를 사용합니다.")
            client_profile = {
                "고객정보": {
                    "고객명": "넉넉한 윤리쌤",
                    "나이": 30,
                    "직업": "공무원",
                    "성별": "남",
                    "신용점수": 934
                },
                "수입/지출/투자 현황": {
                    "분석 기준월": "2025-05",
                    "최근 3개월 평균 수입": "4,751,009원",
                    "최근 3개월 평균 지출": "3,138,115원",
                    "최근 3개월 평균 저축/투자": "800,000원",
                    "최근 3개월 평균 현금(여윳돈)": "812,893원"
                },
                "자산/부채 현황": {
                    "총자산": 37189716,
                    "총부채": 0,
                    "순자산": 37189716,
                    "자산 상세": {
                        "자유입출금 자산": {
                            "입출금통장": 1550152
                        }
                    }
                }
            }
        
        # goal_list 로드 시도
        if 'goal_list' in globals():
            goal_list = globals()['goal_list']
        else:
            print("goal_list를 찾을 수 없습니다. 예시 데이터를 사용합니다.")
            goal_list = [
                {
                    "name": "단기 저축 목표",
                    "years": 5,
                    "target": 63155583,
                    "priority": 2,
                    "necessity": "필수"
                },
                {
                    "name": "은퇴 자금 마련",
                    "years": 35,
                    "target": 496529103,
                    "priority": 1,
                    "necessity": "필수"
                }
            ]
        
        # 자산군 이름 (예시)
        asset_names = [
            "KOSPI", "KOSDAQ", "S&P 500", "나스닥 100", 
            "KRX 채권지수 국채 3Y~5Y", "KRX 채권지수 국채 5Y~10Y"
        ]
        
        # 연도별 자산 배분 가중치 (예시)
        yearly_weights = [
            [0.3, 0.2, 0.2, 0.1, 0.1, 0.1],  # 첫 해
            [0.25, 0.15, 0.2, 0.15, 0.15, 0.1]  # 둘째 해
        ]
        
        # 보고서 생성
        report_generator = FinancialAnalysisReport(
            client_profile, goal_list, asset_names, yearly_weights
        )
        
        # 1. 가계부 분석 보고서 생성
        print("\n" + "="*80)
        print("1. 가계부 분석 및 평가 보고서")
        print("="*80)
        household_report = report_generator.generate_household_analysis_report()
        print(household_report)
        
        # 파일로 저장
        with open("가계부_분석_보고서.md", "w", encoding="utf-8") as f:
            f.write(household_report)
        print("\n✅ 가계부 분석 보고서가 '가계부_분석_보고서.md' 파일로 저장되었습니다.")
        
        # 2. 재무목표 선정 결과 생성
        print("\n" + "="*80)
        print("2. 재무목표 선정 및 투자 자산 배분 계획")
        print("="*80)
        goals_report = report_generator.generate_financial_goals_summary()
        print(goals_report)
        
        # 파일로 저장
        with open("재무목표_투자계획.md", "w", encoding="utf-8") as f:
            f.write(goals_report)
        print("\n✅ 재무목표 투자계획이 '재무목표_투자계획.md' 파일로 저장되었습니다.")
        
        # 3. 통합 요약 생성
        print("\n" + "="*80)
        print("3. 통합 요약")
        print("="*80)
        
        summary = f"""
# 📋 손PB 통합 정리 요약

## 📊 가계부 분석 결과
- **고객명**: {client_profile.get('고객정보', {}).get('고객명', 'N/A')}
- **나이**: {client_profile.get('고객정보', {}).get('나이', 'N/A')}세
- **직업**: {client_profile.get('고객정보', {}).get('직업', 'N/A')}
- **총자산**: {report_generator._format_currency(client_profile.get('자산/부채 현황', {}).get('총자산', 0))}
- **순자산**: {report_generator._format_currency(client_profile.get('자산/부채 현황', {}).get('순자산', 0))}

## 🎯 선정된 재무목표
"""
        
        for i, goal in enumerate(goal_list, 1):
            summary += f"""
**목표 {i}**: {goal.get('name', 'N/A')}
- 기간: {goal.get('years', 0)}년
- 금액: {report_generator._format_currency(goal.get('target', 0))}
- 우선순위: {goal.get('priority', 0)}위
"""
        
        summary += f"""
## 📈 투자 자산 배분
- **주요 자산군**: {', '.join(asset_names[:3])} 등
- **투자 전략**: TDF(목표시점별 자산배분) 전략 적용
- **리스크 관리**: 변동성 제한을 통한 포트폴리오 안정성 확보

---
*생성일: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}*
"""
        
        print(summary)
        
        # 통합 요약 파일로 저장
        with open("손PB_통합요약.md", "w", encoding="utf-8") as f:
            f.write(summary)
        print("\n✅ 통합 요약이 '손PB_통합요약.md' 파일로 저장되었습니다.")
        
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
        print("필요한 데이터가 올바르게 로드되었는지 확인해주세요.")

if __name__ == "__main__":
    main()

