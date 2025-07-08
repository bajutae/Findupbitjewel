"""
AI 기반 분석 모듈 (Gemini AI 활용)
기존 기술적 분석 결과를 AI가 해석하고 더 지능적인 조언 제공
"""

import logging
from typing import Dict, List, Optional, Union, Any
import json
import os
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  google-generativeai 라이브러리가 설치되지 않았습니다.")
    print("설치 방법: pip install google-generativeai")

logger = logging.getLogger(__name__)

class GeminiAnalyzer:
    """Gemini AI 기반 암호화폐 분석기"""
    
    def __init__(self, api_key: Optional[str] = None):
        """초기화"""
        if not GEMINI_AVAILABLE:
            logger.warning("Gemini AI not available. Install google-generativeai library.")
            self.model = None
            return
            
        # API 키 설정
        api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
            self.model = None
            return
            
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-pro')
            logger.info("Gemini AI initialized successfully with gemini-2.5-pro model")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {e}")
            self.model = None
    
    def analyze_market_data(self, 
                          symbol: str,
                          technical_analysis: Dict,
                          market_summary: Dict,
                          user_profile: Optional[Dict] = None) -> Dict[str, Any]:
        """시장 데이터 종합 분석 - 모듈화된 접근 방식"""
        if not self.model:
            return {"error": "Gemini AI not available"}
            
        try:
            # 시스템 컨텍스트 설정
            system_context = self._create_system_context(user_profile)
            
            # 단계별 분석 수행
            analysis_results = {}
            
            # 1. 시장 개요 분석
            market_overview = self._analyze_market_overview(symbol, technical_analysis, market_summary, system_context)
            analysis_results['market_overview'] = market_overview
            
            # 2. 기술적 분석 해석
            technical_interpretation = self._analyze_technical_signals(symbol, technical_analysis, system_context)
            analysis_results['technical_analysis'] = technical_interpretation
            
            # 3. 거래 전략 제안
            trading_strategy = self._generate_trading_strategy(symbol, technical_analysis, market_summary, system_context)
            analysis_results['trading_strategy'] = trading_strategy
            
            # 4. 리스크 평가
            risk_assessment = self._assess_risks(symbol, technical_analysis, market_summary, system_context)
            analysis_results['risk_assessment'] = risk_assessment
            
            return {
                'timestamp': datetime.now(),
                'symbol': symbol,
                'ai_analysis': analysis_results,
                'confidence_score': self._calculate_overall_confidence(analysis_results),
                'risk_level': self._assess_risk_level(analysis_results),
                'recommendations': self._extract_key_recommendations(analysis_results)
            }
            
        except Exception as e:
            logger.error(f"Error in Gemini analysis: {e}")
            return {"error": f"Analysis failed: {str(e)}"}
    
    def _create_system_context(self, user_profile: Optional[Dict] = None) -> str:
        """시스템 컨텍스트 생성"""
        
        # 사용자 프로필 정보
        risk_tolerance = user_profile.get('risk_tolerance', 'medium') if user_profile else 'medium'
        experience_level = user_profile.get('experience_level', 'intermediate') if user_profile else 'intermediate'
        
        system_context = f"""
당신은 전문적인 암호화폐 분석가입니다.

## 🎯 당신의 역할:
- 기술적 분석 데이터를 해석하고 실용적인 조언 제공
- 복잡한 시장 정보를 이해하기 쉽게 설명
- 구체적이고 실행 가능한 거래 전략 제안
- 리스크를 명확히 식별하고 관리 방안 제시

## 👤 투자자 정보:
- 리스크 성향: {risk_tolerance}
- 경험 수준: {experience_level}

## 📋 응답 원칙:
1. 간결하고 명확한 설명
2. 구체적인 수치와 가격대 제시
3. 실행 가능한 조언 제공
4. 리스크를 솔직하게 언급
5. 한국어로 작성, 이모지 적절히 활용

## ⚠️ 중요사항:
- 투자 조언이 아닌 분석 정보임을 명시
- 높은 변동성 시장의 리스크 강조
- 개인 판단과 추가 조사 필요성 언급
"""
        return system_context
    
    def _analyze_market_overview(self, symbol: str, technical_analysis: Dict, market_summary: Dict, system_context: str) -> str:
        """시장 개요 분석"""
        
        current_price = technical_analysis.get('current_price', 'N/A')
        trend = technical_analysis.get('trend_analysis', {}).get('overall', 'N/A')
        btc_dominance = market_summary.get('btc_dominance', 'N/A')
        fear_greed = market_summary.get('fear_greed_index', 'N/A')
        
        prompt = f"""
{system_context}

## 📊 시장 개요 분석 요청

**종목**: {symbol}
**현재가**: {current_price}
**전체 트렌드**: {trend}
**BTC 도미넌스**: {btc_dominance}%
**공포탐욕지수**: {fear_greed}

**분석 요청사항**:
1. 현재 시장 상황을 한 문장으로 요약
2. 이 종목의 단기 전망 (1-3일)
3. 주의해야 할 시장 요인들
4. 투자자들이 지금 알아야 할 핵심 포인트 3가지

간결하고 실용적으로 답변해주세요.
"""
        
        try:
            if not self.model:
                return "AI 분석을 사용할 수 없습니다."
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error in market overview analysis: {e}")
            return f"시장 개요 분석 중 오류가 발생했습니다: {str(e)}"
    
    def _analyze_technical_signals(self, symbol: str, technical_analysis: Dict, system_context: str) -> str:
        """기술적 신호 분석"""
        
        rsi = technical_analysis.get('RSI', 'N/A')
        macd_signal = technical_analysis.get('MACD_signal', 'N/A')
        bb_signal = technical_analysis.get('BB_signal', 'N/A')
        signals = technical_analysis.get('trading_signals', {})
        key_levels = technical_analysis.get('key_levels', {})
        
        prompt = f"""
{system_context}

## 🔍 기술적 분석 해석 요청

**RSI**: {rsi}
**MACD 신호**: {macd_signal}
**볼린저 밴드**: {bb_signal}
**매매 신호**: {signals}
**주요 레벨**: {key_levels}

**분석 요청사항**:
1. 현재 기술적 지표들이 말하는 것
2. 가장 중요한 신호 1개와 그 이유
3. 지지선과 저항선의 중요성
4. 현재 모멘텀 상태 평가

기술적 용어는 쉽게 설명해주세요.
"""
        
        try:
            if not self.model:
                return "AI 분석을 사용할 수 없습니다."
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error in technical analysis: {e}")
            return f"기술적 분석 중 오류가 발생했습니다: {str(e)}"
    
    def _generate_trading_strategy(self, symbol: str, technical_analysis: Dict, market_summary: Dict, system_context: str) -> str:
        """거래 전략 생성"""
        
        current_price = technical_analysis.get('current_price', 'N/A')
        key_levels = technical_analysis.get('key_levels', {})
        signals = technical_analysis.get('trading_signals', {})
        
        prompt = f"""
{system_context}

## 📋 거래 전략 수립 요청

**현재가**: {current_price}
**주요 레벨**: {key_levels}
**매매 신호**: {signals}

**전략 요청사항**:
1. 단타 거래 전략 (당일 또는 1-2일)
   - 진입 시점과 가격대
   - 손절선 설정 (구체적 가격과 %)
   - 목표가 설정 (구체적 가격과 %)
   - 손익비 계산

2. 포지션 관리
   - 적절한 포지션 크기 (%)
   - 분할 매수/매도 전략

3. 실행 주의사항
   - 언제 들어가면 안 되는지
   - 손절 규칙 준수의 중요성

구체적인 숫자와 가격을 제시해주세요.
"""
        
        try:
            if not self.model:
                return "AI 분석을 사용할 수 없습니다."
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error in trading strategy: {e}")
            return f"거래 전략 생성 중 오류가 발생했습니다: {str(e)}"
    
    def _assess_risks(self, symbol: str, technical_analysis: Dict, market_summary: Dict, system_context: str) -> str:
        """리스크 평가"""
        
        trend = technical_analysis.get('trend_analysis', {}).get('overall', 'N/A')
        volatility = technical_analysis.get('volatility', 'N/A')
        fear_greed = market_summary.get('fear_greed_index', 'N/A')
        
        prompt = f"""
{system_context}

## 🚨 리스크 평가 요청

**트렌드**: {trend}
**변동성**: {volatility}
**공포탐욕지수**: {fear_greed}

**리스크 평가 요청사항**:
1. 현재 가장 큰 리스크 요인 3가지
2. 급락 가능성과 주요 트리거
3. 리스크 관리 방법
4. 투자 금액 조절 가이드
5. 언제 시장에서 나와야 하는지

솔직하고 현실적인 리스크 평가를 해주세요.
"""
        
        try:
            if not self.model:
                return "AI 분석을 사용할 수 없습니다."
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error in risk assessment: {e}")
            return f"리스크 평가 중 오류가 발생했습니다: {str(e)}"
    
    def _calculate_overall_confidence(self, analysis_results: Dict) -> float:
        """전체 신뢰도 계산"""
        try:
            # 각 분석 결과의 길이와 품질을 기반으로 신뢰도 계산
            total_length = 0
            successful_analyses = 0
            
            for key, value in analysis_results.items():
                if isinstance(value, str) and len(value) > 50:
                    total_length += len(value)
                    successful_analyses += 1
            
            if successful_analyses == 0:
                return 0.3
            
            # 기본 신뢰도 계산 (분석 완성도 기반)
            base_confidence = min(0.9, 0.5 + (successful_analyses / 4) * 0.4)
            
            # 응답 품질 보정
            avg_length = total_length / successful_analyses
            quality_factor = min(1.0, avg_length / 200)
            
            return base_confidence * quality_factor
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def _assess_risk_level(self, analysis_results: Dict) -> str:
        """리스크 레벨 평가"""
        try:
            risk_assessment = analysis_results.get('risk_assessment', '')
            
            # 리스크 키워드 분석
            high_risk_keywords = ['급락', '위험', '조심', '주의', '높은 변동성', '불안정']
            low_risk_keywords = ['안정', '저위험', '낮은 변동성', '안전']
            
            risk_assessment_lower = risk_assessment.lower()
            
            high_risk_count = sum(1 for keyword in high_risk_keywords if keyword in risk_assessment_lower)
            low_risk_count = sum(1 for keyword in low_risk_keywords if keyword in risk_assessment_lower)
            
            if high_risk_count > low_risk_count:
                return 'high'
            elif low_risk_count > high_risk_count:
                return 'low'
            else:
                return 'medium'
                
        except Exception as e:
            logger.error(f"Error assessing risk level: {e}")
            return 'medium'
    
    def _extract_key_recommendations(self, analysis_results: Dict) -> List[str]:
        """핵심 추천사항 추출"""
        try:
            recommendations = []
            
            # 거래 전략에서 추천사항 추출
            strategy = analysis_results.get('trading_strategy', '')
            if '진입' in strategy:
                recommendations.append("거래 전략 검토 필요")
            
            # 리스크 평가에서 추천사항 추출
            risk_assessment = analysis_results.get('risk_assessment', '')
            if '손절' in risk_assessment:
                recommendations.append("리스크 관리 철저히 준수")
            
            # 시장 개요에서 추천사항 추출
            market_overview = analysis_results.get('market_overview', '')
            if '주의' in market_overview:
                recommendations.append("시장 동향 면밀히 관찰")
            
            return recommendations[:3]  # 최대 3개
            
        except Exception as e:
            logger.error(f"Error extracting recommendations: {e}")
            return ["분석 결과를 참고하여 신중한 판단 필요"]

    def quick_analysis(self, symbol: str, price: float, trend: str) -> str:
        """빠른 분석 (간단한 조언)"""
        if not self.model:
            return "AI 분석을 사용할 수 없습니다."
            
        try:
            if not self.model:
                return "AI 분석을 사용할 수 없습니다."
                
            prompt = f"""
당신은 암호화폐 분석 전문가입니다.

{symbol}의 현재 상황:
- 현재가: {price}
- 트렌드: {trend}

이 정보를 바탕으로 30초 안에 읽을 수 있는 간단한 조언을 해주세요:
1. 현재 상황 한 줄 요약
2. 단기 전망 (1-2일)
3. 주의사항 하나

간결하고 실용적으로 답변해주세요.
"""
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error in quick analysis: {e}")
            return f"빠른 분석 중 오류가 발생했습니다: {str(e)}"
    
    def explain_technical_indicator(self, indicator_name: str, value: float, signal: str) -> str:
        """기술적 지표 설명"""
        if not self.model:
            return f"{indicator_name}: {value} ({signal})"
            
        try:
            if not self.model:
                return f"{indicator_name}: {value} ({signal})"
                
            prompt = f"""
기술적 지표 설명 요청:
- 지표명: {indicator_name}
- 현재값: {value}
- 신호: {signal}

이 지표가 현재 무엇을 의미하는지 초보자도 이해할 수 있게 2-3 문장으로 설명해주세요.
"""
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error explaining indicator: {e}")
            return f"{indicator_name} 설명 중 오류가 발생했습니다."
    
    def is_available(self) -> bool:
        """AI 사용 가능 여부"""
        return self.model is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """모델 정보 반환"""
        return {
            'available': self.is_available(),
            'model_name': 'gemini-2.5-pro' if self.is_available() else None,
            'features': ['market_analysis', 'trading_strategy', 'risk_assessment', 'quick_analysis']
        } 