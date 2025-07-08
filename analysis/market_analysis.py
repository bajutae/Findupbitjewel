"""
비트코인 & 이더리움 종합 시황 분석 모듈
매크로 환경, 기술적 분석, 시장 심리 등을 종합하여 AI와 함께 분석
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

# 내부 모듈
from data.collector import CryptoDataCollector, MarketDataCollector
from analysis.technical import TechnicalAnalyzer
from analysis.ai_analyzer import GeminiAnalyzer

logger = logging.getLogger(__name__)

class ComprehensiveMarketAnalysis:
    """종합 시장 분석기 - 비트코인과 이더리움 시황 분석"""
    
    def __init__(self):
        """초기화"""
        self.crypto_collector = CryptoDataCollector()
        self.market_collector = MarketDataCollector()
        self.technical_analyzer = TechnicalAnalyzer()
        self.ai_analyzer = GeminiAnalyzer()
        
        logger.info("Comprehensive Market Analysis initialized")
    
    def generate_daily_market_report(self) -> Dict[str, any]:
        """일일 종합 시장 리포트 생성"""
        try:
            logger.info("Starting daily market report generation...")
            
            # 1. 전일 뉴욕증시 & 매크로 지표
            macro_data = self.market_collector.get_comprehensive_market_data()
            
            # 2. 비트코인 & 이더리움 기본 데이터
            btc_data = self._get_crypto_analysis('BTC/USDT')
            eth_data = self._get_crypto_analysis('ETH/USDT')
            
            # 3. 시장 도미넌스 분석
            dominance_analysis = self.crypto_collector.get_enhanced_dominance_analysis()
            
            # 4. 시장 심리 지표
            sentiment_data = self._get_market_sentiment()
            
            # 5. 종합 AI 분석
            ai_analysis = self._get_ai_market_analysis({
                'macro_data': macro_data,
                'btc_data': btc_data,
                'eth_data': eth_data,
                'dominance': dominance_analysis,
                'sentiment': sentiment_data
            })
            
            # 6. 최종 리포트 구성
            daily_report = {
                'timestamp': datetime.now().isoformat(),
                'macro_environment': {
                    'nyse_data': macro_data.get('nyse_data', {}),
                    'macro_indicators': macro_data.get('macro_indicators', {}),
                    'economic_calendar': macro_data.get('economic_calendar', []),
                    'analysis': self._analyze_macro_environment(macro_data)
                },
                'crypto_market': {
                    'btc_analysis': btc_data,
                    'eth_analysis': eth_data,
                    'dominance_analysis': dominance_analysis,
                    'tether_dominance': macro_data.get('tether_dominance', {}),
                    'trending_coins': macro_data.get('trending_coins', [])
                },
                'market_sentiment': sentiment_data,
                'derivatives_data': {
                    'btc_funding': btc_data.get('funding_rate', {}),
                    'eth_funding': eth_data.get('funding_rate', {}),
                    'open_interest': {
                        'btc': macro_data.get('btc_open_interest', {}),
                        'eth': macro_data.get('eth_open_interest', {})
                    },
                    'cvd_analysis': {
                        'btc': macro_data.get('btc_cvd', {}),
                        'eth': macro_data.get('eth_cvd', {})
                    }
                },
                'ai_analysis': ai_analysis,
                'comprehensive_outlook': self._generate_comprehensive_outlook(btc_data, eth_data, macro_data, ai_analysis),
                'trading_recommendations': self._generate_trading_recommendations(btc_data, eth_data, macro_data, ai_analysis)
            }
            
            logger.info("Daily market report generated successfully")
            return daily_report
            
        except Exception as e:
            logger.error(f"Error generating daily market report: {e}")
            return {}
    
    def _get_crypto_analysis(self, symbol: str) -> Dict[str, any]:
        """개별 암호화폐 분석"""
        try:
            # 기본 가격 정보
            current_prices = self.crypto_collector.get_current_prices([symbol])
            current_price = current_prices.get(symbol, 0)
            
            # 기술적 분석
            historical_data = self.crypto_collector.get_historical_data(symbol, 100)
            technical_analysis = self.technical_analyzer.full_analysis(historical_data)
            
            # 다중 시간봉 분석
            multi_timeframe = self.crypto_collector.get_multi_timeframe_data(symbol)
            
            # 펀딩비 분석 (BTC만)
            funding_rate = {}
            if symbol == 'BTC/USDT':
                funding_rate = self.crypto_collector.get_funding_rate(symbol)
            
            # 성과 분석
            performance_data = {
                '24h': self._calculate_performance(historical_data, 1),
                '7d': self._calculate_performance(historical_data, 7),
                '30d': self._calculate_performance(historical_data, 30),
                '90d': self._calculate_performance(historical_data, 90)
            }
            
            crypto_analysis = {
                'symbol': symbol,
                'current_price': current_price,
                'technical_analysis': technical_analysis,
                'multi_timeframe': self._analyze_multi_timeframe(multi_timeframe),
                'funding_rate': funding_rate,
                'performance': performance_data,
                'key_levels': self._identify_key_levels(historical_data),
                'trend_strength': self._calculate_trend_strength(historical_data),
                'volatility_analysis': self._analyze_volatility(historical_data)
            }
            
            return crypto_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return {}
    
    def _calculate_performance(self, historical_data: pd.DataFrame, days: int) -> Dict[str, any]:
        """성과 계산"""
        try:
            if historical_data.empty or len(historical_data) < days:
                return {}
            
            current_price = historical_data['close'].iloc[-1]
            past_price = historical_data['close'].iloc[-days]
            
            performance = ((current_price - past_price) / past_price) * 100
            
            return {
                'change_percent': performance,
                'start_price': past_price,
                'end_price': current_price,
                'days': days
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance: {e}")
            return {}
    
    def _analyze_multi_timeframe(self, multi_timeframe: Dict[str, pd.DataFrame]) -> Dict[str, any]:
        """다중 시간봉 분석"""
        try:
            timeframe_analysis = {}
            
            for timeframe, df in multi_timeframe.items():
                if df.empty:
                    continue
                
                # 각 시간봉별 트렌드 분석
                trend = self._determine_trend(df)
                momentum = self._calculate_momentum(df)
                
                timeframe_analysis[timeframe] = {
                    'trend': trend,
                    'momentum': momentum,
                    'current_price': df['close'].iloc[-1],
                    'volume_trend': self._analyze_volume_trend(df)
                }
            
            return timeframe_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing multi-timeframe: {e}")
            return {}
    
    def _determine_trend(self, df: pd.DataFrame) -> str:
        """트렌드 방향 결정"""
        try:
            if len(df) < 20:
                return 'neutral'
            
            # 단순 이동평균 기반 트렌드 판단
            ma20 = df['close'].rolling(window=20).mean()
            current_price = df['close'].iloc[-1]
            ma20_current = ma20.iloc[-1]
            ma20_prev = ma20.iloc[-5]
            
            if current_price > ma20_current and ma20_current > ma20_prev:
                return 'bullish'
            elif current_price < ma20_current and ma20_current < ma20_prev:
                return 'bearish'
            else:
                return 'neutral'
                
        except Exception as e:
            logger.error(f"Error determining trend: {e}")
            return 'neutral'
    
    def _calculate_momentum(self, df: pd.DataFrame) -> Dict[str, any]:
        """모멘텀 계산"""
        try:
            if len(df) < 14:
                return {}
            
            # RSI 계산
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            current_rsi = rsi.iloc[-1]
            
            # 모멘텀 해석
            if current_rsi > 70:
                momentum_signal = 'overbought'
            elif current_rsi < 30:
                momentum_signal = 'oversold'
            else:
                momentum_signal = 'neutral'
            
            return {
                'rsi': current_rsi,
                'signal': momentum_signal,
                'strength': abs(current_rsi - 50) / 50  # 0-1 범위
            }
            
        except Exception as e:
            logger.error(f"Error calculating momentum: {e}")
            return {}
    
    def _analyze_volume_trend(self, df: pd.DataFrame) -> str:
        """거래량 트렌드 분석"""
        try:
            if len(df) < 10:
                return 'neutral'
            
            recent_volume = df['volume'].iloc[-5:].mean()
            past_volume = df['volume'].iloc[-15:-5].mean()
            
            if recent_volume > past_volume * 1.2:
                return 'increasing'
            elif recent_volume < past_volume * 0.8:
                return 'decreasing'
            else:
                return 'stable'
                
        except Exception as e:
            logger.error(f"Error analyzing volume trend: {e}")
            return 'neutral'
    
    def _identify_key_levels(self, df: pd.DataFrame) -> Dict[str, any]:
        """주요 레벨 식별"""
        try:
            if df.empty:
                return {}
            
            # 최근 20일 기준 지지/저항 레벨
            recent_data = df.tail(20)
            
            support_level = recent_data['low'].min()
            resistance_level = recent_data['high'].max()
            current_price = df['close'].iloc[-1]
            
            # 피벗 포인트 계산
            high = recent_data['high'].iloc[-1]
            low = recent_data['low'].iloc[-1]
            close = recent_data['close'].iloc[-1]
            
            pivot = (high + low + close) / 3
            r1 = (2 * pivot) - low
            s1 = (2 * pivot) - high
            
            return {
                'support': support_level,
                'resistance': resistance_level,
                'pivot_point': pivot,
                'r1': r1,
                's1': s1,
                'distance_to_support': ((current_price - support_level) / current_price) * 100,
                'distance_to_resistance': ((resistance_level - current_price) / current_price) * 100
            }
            
        except Exception as e:
            logger.error(f"Error identifying key levels: {e}")
            return {}
    
    def _calculate_trend_strength(self, df: pd.DataFrame) -> Dict[str, any]:
        """트렌드 강도 계산"""
        try:
            if len(df) < 20:
                return {}
            
            # ADX 계산 (간단한 버전)
            high = df['high']
            low = df['low']
            close = df['close']
            
            plus_dm = high.diff()
            minus_dm = low.diff()
            
            plus_dm[plus_dm < 0] = 0
            minus_dm[minus_dm > 0] = 0
            minus_dm = minus_dm.abs()
            
            tr = pd.concat([high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
            
            atr = tr.rolling(window=14).mean()
            plus_di = 100 * (plus_dm.rolling(window=14).mean() / atr)
            minus_di = 100 * (minus_dm.rolling(window=14).mean() / atr)
            
            dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
            adx = dx.rolling(window=14).mean()
            
            current_adx = adx.iloc[-1]
            
            # 트렌드 강도 해석
            if current_adx > 50:
                strength = 'very_strong'
            elif current_adx > 25:
                strength = 'strong'
            elif current_adx > 20:
                strength = 'moderate'
            else:
                strength = 'weak'
            
            return {
                'adx': current_adx,
                'strength': strength,
                'plus_di': plus_di.iloc[-1],
                'minus_di': minus_di.iloc[-1]
            }
            
        except Exception as e:
            logger.error(f"Error calculating trend strength: {e}")
            return {}
    
    def _analyze_volatility(self, df: pd.DataFrame) -> Dict[str, any]:
        """변동성 분석"""
        try:
            if len(df) < 20:
                return {}
            
            # 일별 수익률 계산
            returns = df['close'].pct_change().dropna()
            
            # 변동성 지표들
            volatility_20d = returns.rolling(window=20).std() * np.sqrt(252) * 100  # 연환산
            current_volatility = volatility_20d.iloc[-1]
            
            # 변동성 해석
            if current_volatility > 80:
                volatility_level = 'very_high'
            elif current_volatility > 60:
                volatility_level = 'high'
            elif current_volatility > 40:
                volatility_level = 'normal'
            elif current_volatility > 20:
                volatility_level = 'low'
            else:
                volatility_level = 'very_low'
            
            return {
                'volatility_20d': current_volatility,
                'level': volatility_level,
                'recent_range': (df['close'].iloc[-5:].max() - df['close'].iloc[-5:].min()) / df['close'].iloc[-1] * 100
            }
            
        except Exception as e:
            logger.error(f"Error analyzing volatility: {e}")
            return {}
    
    def _get_market_sentiment(self) -> Dict[str, any]:
        """시장 심리 지표 수집"""
        try:
            # 공포탐욕 지수
            fear_greed = self.crypto_collector.get_fear_greed_index()
            
            # 알트시즌 지수
            altseason_index = self.crypto_collector.get_altseason_index()
            
            # 종합 심리 분석
            sentiment_score = self._calculate_sentiment_score(fear_greed, altseason_index)
            
            return {
                'fear_greed': fear_greed,
                'altseason_index': altseason_index,
                'sentiment_score': sentiment_score,
                'interpretation': self._interpret_sentiment(sentiment_score)
            }
            
        except Exception as e:
            logger.error(f"Error getting market sentiment: {e}")
            return {}
    
    def _calculate_sentiment_score(self, fear_greed: Dict, altseason_index: float) -> float:
        """종합 심리 점수 계산"""
        try:
            fg_value = fear_greed.get('value', 50)
            
            # 0-100 범위로 정규화
            normalized_fg = fg_value / 100
            normalized_alt = altseason_index / 100
            
            # 가중 평균 (공포탐욕 지수 70%, 알트시즌 30%)
            sentiment_score = (normalized_fg * 0.7 + normalized_alt * 0.3) * 100
            
            return sentiment_score
            
        except Exception as e:
            logger.error(f"Error calculating sentiment score: {e}")
            return 50
    
    def _interpret_sentiment(self, sentiment_score: float) -> str:
        """심리 점수 해석"""
        if sentiment_score > 80:
            return "Extreme Greed"
        elif sentiment_score > 60:
            return "Greed"
        elif sentiment_score > 40:
            return "Neutral"
        elif sentiment_score > 20:
            return "Fear"
        else:
            return "Extreme Fear"
    
    def _analyze_macro_environment(self, macro_data: Dict) -> Dict[str, any]:
        """매크로 환경 분석"""
        try:
            nyse_data = macro_data.get('nyse_data', {})
            macro_indicators = macro_data.get('macro_indicators', {})
            
            # 주식 시장 분석
            stock_sentiment = self._analyze_stock_market(nyse_data)
            
            # 매크로 지표 분석
            macro_sentiment = self._analyze_macro_indicators(macro_indicators)
            
            # 종합 매크로 환경 점수
            macro_score = (stock_sentiment + macro_sentiment) / 2
            
            return {
                'stock_market_sentiment': stock_sentiment,
                'macro_indicators_sentiment': macro_sentiment,
                'overall_macro_score': macro_score,
                'interpretation': self._interpret_macro_score(macro_score),
                'key_concerns': self._identify_macro_concerns(nyse_data, macro_indicators)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing macro environment: {e}")
            return {}
    
    def _analyze_stock_market(self, nyse_data: Dict) -> float:
        """주식 시장 분석"""
        try:
            if not nyse_data:
                return 50
            
            positive_count = 0
            total_count = 0
            
            for symbol, data in nyse_data.items():
                if 'change_percent' in data:
                    change_pct = float(data['change_percent'])
                    if change_pct > 0:
                        positive_count += 1
                    total_count += 1
            
            if total_count > 0:
                return (positive_count / total_count) * 100
            else:
                return 50
                
        except Exception as e:
            logger.error(f"Error analyzing stock market: {e}")
            return 50
    
    def _analyze_macro_indicators(self, macro_indicators: Dict) -> float:
        """매크로 지표 분석"""
        try:
            if not macro_indicators:
                return 50
            
            sentiment_scores = []
            
            # VIX 분석
            vix_data = macro_indicators.get('VIX', {})
            if vix_data:
                vix_value = vix_data.get('value', 20)
                vix_score = max(0, min(100, 100 - (vix_value - 10) * 2))  # VIX 역방향
                sentiment_scores.append(vix_score)
            
            # 금 가격 분석
            gold_data = macro_indicators.get('GOLD', {})
            if gold_data:
                gold_change = gold_data.get('change', 0)
                gold_score = 50 - (gold_change * 5)  # 금 가격 상승 시 위험 회피
                sentiment_scores.append(max(0, min(100, gold_score)))
            
            # DXY 분석
            dxy_data = macro_indicators.get('DXY', {})
            if dxy_data:
                dxy_change = dxy_data.get('change', 0)
                dxy_score = 50 - (dxy_change * 10)  # 달러 강세 시 위험 자산에 부정적
                sentiment_scores.append(max(0, min(100, dxy_score)))
            
            if sentiment_scores:
                return sum(sentiment_scores) / len(sentiment_scores)
            else:
                return 50
                
        except Exception as e:
            logger.error(f"Error analyzing macro indicators: {e}")
            return 50
    
    def _interpret_macro_score(self, score: float) -> str:
        """매크로 점수 해석"""
        if score > 75:
            return "Very Bullish Macro Environment"
        elif score > 60:
            return "Bullish Macro Environment"
        elif score > 40:
            return "Neutral Macro Environment"
        elif score > 25:
            return "Bearish Macro Environment"
        else:
            return "Very Bearish Macro Environment"
    
    def _identify_macro_concerns(self, nyse_data: Dict, macro_indicators: Dict) -> List[str]:
        """매크로 우려사항 식별"""
        concerns = []
        
        try:
            # VIX 체크
            vix_data = macro_indicators.get('VIX', {})
            if vix_data.get('value', 0) > 30:
                concerns.append("High volatility (VIX > 30)")
            
            # 주식 시장 체크
            negative_indices = []
            for symbol, data in nyse_data.items():
                if float(data.get('change_percent', 0)) < -2:
                    negative_indices.append(data.get('name', symbol))
            
            if negative_indices:
                concerns.append(f"Major indices declining: {', '.join(negative_indices)}")
            
            # 달러 강세 체크
            dxy_data = macro_indicators.get('DXY', {})
            if dxy_data.get('change', 0) > 1:
                concerns.append("Strong dollar rally (negative for crypto)")
            
            # 금 가격 급등 체크
            gold_data = macro_indicators.get('GOLD', {})
            if gold_data.get('change', 0) > 2:
                concerns.append("Gold rally (flight to safety)")
            
        except Exception as e:
            logger.error(f"Error identifying macro concerns: {e}")
        
        return concerns
    
    def _get_ai_market_analysis(self, market_data: Dict) -> Dict[str, any]:
        """AI 기반 시장 분석"""
        try:
            # BTC 및 ETH 데이터 추출
            btc_data = market_data.get('btc_data', {})
            eth_data = market_data.get('eth_data', {})
            
            # AI 분석 실행 - BTC
            btc_ai_result = self.ai_analyzer.analyze_market_data(
                symbol='BTC/USDT',
                technical_analysis=btc_data.get('technical_analysis', {}),
                market_summary=market_data.get('market_sentiment', {}),
                user_profile=None
            )
            
            # AI 분석 실행 - ETH
            eth_ai_result = self.ai_analyzer.analyze_market_data(
                symbol='ETH/USDT',
                technical_analysis=eth_data.get('technical_analysis', {}),
                market_summary=market_data.get('market_sentiment', {}),
                user_profile=None
            )
            
            return {
                'btc_ai_analysis': btc_ai_result,
                'eth_ai_analysis': eth_ai_result,
                'confidence_score': self._calculate_ai_confidence({'btc': btc_ai_result, 'eth': eth_ai_result}),
                'key_insights': self._extract_ai_insights({'btc': btc_ai_result, 'eth': eth_ai_result})
            }
            
        except Exception as e:
            logger.error(f"Error getting AI market analysis: {e}")
            return {}
    
    def _prepare_ai_analysis_prompt(self, market_data: Dict) -> str:
        """AI 분석용 프롬프트 준비"""
        try:
            macro_data = market_data.get('macro_data', {})
            btc_data = market_data.get('btc_data', {})
            eth_data = market_data.get('eth_data', {})
            
            prompt = f"""
            다음 시장 데이터를 바탕으로 비트코인과 이더리움의 종합적인 시장 분석을 제공해주세요:
            
            **매크로 환경:**
            - 뉴욕증시: {macro_data.get('nyse_data', {})}
            - 매크로 지표: {macro_data.get('macro_indicators', {})}
            - 테더 도미넌스: {macro_data.get('tether_dominance', {})}
            
            **비트코인 분석:**
            - 현재가: {btc_data.get('current_price', 0)}
            - 기술적 분석: {btc_data.get('technical_analysis', {})}
            - 펀딩비: {btc_data.get('funding_rate', {})}
            
            **이더리움 분석:**
            - 현재가: {eth_data.get('current_price', 0)}
            - 기술적 분석: {eth_data.get('technical_analysis', {})}
            
            **도미넌스 분석:**
            {market_data.get('dominance', {})}
            
            다음 관점에서 분석해주세요:
            1. 매크로 환경이 암호화폐 시장에 미치는 영향
            2. 비트코인과 이더리움의 상대적 강세
            3. 주요 리스크 요소들
            4. 단기/중기 전망
            5. 투자 전략 권장사항
            """
            
            return prompt
            
        except Exception as e:
            logger.error(f"Error preparing AI analysis prompt: {e}")
            return ""
    
    def _calculate_ai_confidence(self, ai_result: Dict) -> float:
        """AI 분석 신뢰도 계산"""
        try:
            # 간단한 신뢰도 계산 (실제로는 더 복잡한 로직 필요)
            if ai_result and 'analysis' in ai_result:
                return 0.8  # 기본 신뢰도
            else:
                return 0.3
                
        except Exception as e:
            logger.error(f"Error calculating AI confidence: {e}")
            return 0.5
    
    def _extract_ai_insights(self, ai_result: Dict) -> List[str]:
        """AI 분석에서 핵심 인사이트 추출"""
        try:
            insights = []
            
            if ai_result and 'analysis' in ai_result:
                # 여기에 AI 결과 파싱 로직 추가
                insights.append("AI 분석이 완료되었습니다.")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error extracting AI insights: {e}")
            return []
    
    def _generate_comprehensive_outlook(self, btc_data: Dict, eth_data: Dict, macro_data: Dict, ai_analysis: Dict) -> Dict[str, any]:
        """종합 전망 생성"""
        try:
            # 각 섹터별 점수 계산
            macro_score = self._calculate_macro_score(macro_data)
            btc_score = self._calculate_crypto_score(btc_data)
            eth_score = self._calculate_crypto_score(eth_data)
            
            # 종합 점수 계산
            overall_score = (macro_score * 0.3 + btc_score * 0.4 + eth_score * 0.3)
            
            # 전망 생성
            outlook = {
                'overall_score': overall_score,
                'macro_score': macro_score,
                'btc_score': btc_score,
                'eth_score': eth_score,
                'overall_sentiment': self._interpret_overall_score(overall_score),
                'key_drivers': self._identify_key_drivers(macro_data, btc_data, eth_data),
                'risk_factors': self._identify_risk_factors(macro_data, btc_data, eth_data),
                'opportunities': self._identify_opportunities(macro_data, btc_data, eth_data)
            }
            
            return outlook
            
        except Exception as e:
            logger.error(f"Error generating comprehensive outlook: {e}")
            return {}
    
    def _calculate_macro_score(self, macro_data: Dict) -> float:
        """매크로 점수 계산"""
        try:
            macro_analysis = macro_data.get('macro_environment', {})
            return macro_analysis.get('overall_macro_score', 50)
        except:
            return 50
    
    def _calculate_crypto_score(self, crypto_data: Dict) -> float:
        """암호화폐 점수 계산"""
        try:
            # 기술적 분석 점수
            technical = crypto_data.get('technical_analysis', {})
            
            # 간단한 점수 계산 (실제로는 더 복잡한 로직)
            if technical.get('trend', 'neutral') == 'bullish':
                return 70
            elif technical.get('trend', 'neutral') == 'bearish':
                return 30
            else:
                return 50
                
        except Exception as e:
            logger.error(f"Error calculating crypto score: {e}")
            return 50
    
    def _interpret_overall_score(self, score: float) -> str:
        """종합 점수 해석"""
        if score > 75:
            return "Very Bullish"
        elif score > 60:
            return "Bullish"
        elif score > 40:
            return "Neutral"
        elif score > 25:
            return "Bearish"
        else:
            return "Very Bearish"
    
    def _identify_key_drivers(self, macro_data: Dict, btc_data: Dict, eth_data: Dict) -> List[str]:
        """주요 동력 요소 식별"""
        drivers = []
        
        try:
            # 매크로 동력
            macro_analysis = macro_data.get('macro_environment', {})
            if macro_analysis.get('overall_macro_score', 50) > 60:
                drivers.append("Supportive macro environment")
            
            # BTC 동력
            btc_trend = btc_data.get('technical_analysis', {}).get('trend', 'neutral')
            if btc_trend == 'bullish':
                drivers.append("Bitcoin bullish momentum")
            
            # ETH 동력
            eth_trend = eth_data.get('technical_analysis', {}).get('trend', 'neutral')
            if eth_trend == 'bullish':
                drivers.append("Ethereum bullish momentum")
            
        except Exception as e:
            logger.error(f"Error identifying key drivers: {e}")
        
        return drivers
    
    def _identify_risk_factors(self, macro_data: Dict, btc_data: Dict, eth_data: Dict) -> List[str]:
        """리스크 요소 식별"""
        risks = []
        
        try:
            # 매크로 리스크
            macro_concerns = macro_data.get('macro_environment', {}).get('key_concerns', [])
            risks.extend(macro_concerns)
            
            # 기술적 리스크
            btc_volatility = btc_data.get('volatility_analysis', {}).get('level', 'normal')
            if btc_volatility in ['high', 'very_high']:
                risks.append("High Bitcoin volatility")
            
            eth_volatility = eth_data.get('volatility_analysis', {}).get('level', 'normal')
            if eth_volatility in ['high', 'very_high']:
                risks.append("High Ethereum volatility")
            
        except Exception as e:
            logger.error(f"Error identifying risk factors: {e}")
        
        return risks
    
    def _identify_opportunities(self, macro_data: Dict, btc_data: Dict, eth_data: Dict) -> List[str]:
        """기회 요소 식별"""
        opportunities = []
        
        try:
            # 기술적 기회
            btc_levels = btc_data.get('key_levels', {})
            if btc_levels.get('distance_to_support', 0) > 5:
                opportunities.append("Bitcoin near support levels")
            
            eth_levels = eth_data.get('key_levels', {})
            if eth_levels.get('distance_to_support', 0) > 5:
                opportunities.append("Ethereum near support levels")
            
            # 도미넌스 기회
            tether_dominance = macro_data.get('tether_dominance', {})
            if tether_dominance.get('tether_dominance', 0) > 6:
                opportunities.append("High Tether dominance - potential reversal")
            
        except Exception as e:
            logger.error(f"Error identifying opportunities: {e}")
        
        return opportunities
    
    def _generate_trading_recommendations(self, btc_data: Dict, eth_data: Dict, macro_data: Dict, ai_analysis: Dict) -> Dict[str, any]:
        """거래 추천 생성"""
        try:
            # BTC 추천
            btc_recommendation = self._generate_crypto_recommendation(btc_data, 'BTC')
            
            # ETH 추천
            eth_recommendation = self._generate_crypto_recommendation(eth_data, 'ETH')
            
            # 종합 추천
            overall_recommendation = self._generate_overall_recommendation(btc_recommendation, eth_recommendation, macro_data)
            
            return {
                'btc_recommendation': btc_recommendation,
                'eth_recommendation': eth_recommendation,
                'overall_recommendation': overall_recommendation,
                'risk_management': self._generate_risk_management_advice(btc_data, eth_data, macro_data)
            }
            
        except Exception as e:
            logger.error(f"Error generating trading recommendations: {e}")
            return {}
    
    def _generate_crypto_recommendation(self, crypto_data: Dict, symbol: str) -> Dict[str, any]:
        """개별 암호화폐 추천"""
        try:
            technical = crypto_data.get('technical_analysis', {})
            key_levels = crypto_data.get('key_levels', {})
            
            # 기본 추천
            if technical.get('trend', 'neutral') == 'bullish':
                action = 'BUY'
                confidence = 'Medium'
            elif technical.get('trend', 'neutral') == 'bearish':
                action = 'SELL'
                confidence = 'Medium'
            else:
                action = 'HOLD'
                confidence = 'Low'
            
            return {
                'symbol': symbol,
                'action': action,
                'confidence': confidence,
                'entry_level': key_levels.get('support', 0),
                'target_level': key_levels.get('resistance', 0),
                'stop_loss': key_levels.get('s1', 0),
                'reasoning': f"Based on {technical.get('trend', 'neutral')} trend analysis"
            }
            
        except Exception as e:
            logger.error(f"Error generating crypto recommendation: {e}")
            return {}
    
    def _generate_overall_recommendation(self, btc_rec: Dict, eth_rec: Dict, macro_data: Dict) -> Dict[str, any]:
        """종합 추천 생성"""
        try:
            # 매크로 환경 고려
            macro_score = self._calculate_macro_score(macro_data)
            
            if macro_score > 60:
                market_bias = 'bullish'
            elif macro_score < 40:
                market_bias = 'bearish'
            else:
                market_bias = 'neutral'
            
            return {
                'market_bias': market_bias,
                'preferred_asset': 'BTC' if btc_rec.get('confidence', 'Low') > eth_rec.get('confidence', 'Low') else 'ETH',
                'portfolio_allocation': self._suggest_portfolio_allocation(btc_rec, eth_rec, macro_score),
                'key_message': self._generate_key_message(market_bias, btc_rec, eth_rec)
            }
            
        except Exception as e:
            logger.error(f"Error generating overall recommendation: {e}")
            return {}
    
    def _suggest_portfolio_allocation(self, btc_rec: Dict, eth_rec: Dict, macro_score: float) -> Dict[str, float]:
        """포트폴리오 할당 제안"""
        try:
            if macro_score > 60:  # 강세 시장
                return {'BTC': 60, 'ETH': 30, 'CASH': 10}
            elif macro_score < 40:  # 약세 시장
                return {'BTC': 20, 'ETH': 10, 'CASH': 70}
            else:  # 중립 시장
                return {'BTC': 40, 'ETH': 20, 'CASH': 40}
                
        except Exception as e:
            logger.error(f"Error suggesting portfolio allocation: {e}")
            return {'BTC': 50, 'ETH': 25, 'CASH': 25}
    
    def _generate_key_message(self, market_bias: str, btc_rec: Dict, eth_rec: Dict) -> str:
        """핵심 메시지 생성"""
        try:
            if market_bias == 'bullish':
                return "매크로 환경이 우호적입니다. 단계적 매수를 고려해보세요."
            elif market_bias == 'bearish':
                return "매크로 환경이 어려운 상황입니다. 현금 비중을 높이고 신중하게 접근하세요."
            else:
                return "시장이 불확실한 상황입니다. 리스크 관리를 중심으로 접근하세요."
                
        except Exception as e:
            logger.error(f"Error generating key message: {e}")
            return "시장 분석을 바탕으로 신중하게 투자하세요."
    
    def _generate_risk_management_advice(self, btc_data: Dict, eth_data: Dict, macro_data: Dict) -> List[str]:
        """리스크 관리 조언 생성"""
        try:
            advice = []
            
            # 변동성 기반 조언
            btc_volatility = btc_data.get('volatility_analysis', {}).get('level', 'normal')
            if btc_volatility in ['high', 'very_high']:
                advice.append("높은 변동성으로 인해 포지션 크기를 줄이세요")
            
            # 매크로 리스크 기반 조언
            macro_concerns = macro_data.get('macro_environment', {}).get('key_concerns', [])
            if macro_concerns:
                advice.append("매크로 불확실성으로 인해 손절매를 엄격히 관리하세요")
            
            # 기본 조언
            advice.extend([
                "투자 자금의 5-10% 이상 투자하지 마세요",
                "감정적 거래를 피하고 계획에 따라 실행하세요",
                "정기적으로 포트폴리오를 리밸런싱하세요"
            ])
            
            return advice
            
        except Exception as e:
            logger.error(f"Error generating risk management advice: {e}")
            return ["기본적인 리스크 관리 원칙을 따르세요"]


# 사용 예시
if __name__ == "__main__":
    analyzer = ComprehensiveMarketAnalysis()
    
    # 일일 종합 시장 리포트 생성
    daily_report = analyzer.generate_daily_market_report()
    
    if daily_report:
        print("=== 일일 종합 시장 리포트 ===")
        print(f"생성 시간: {daily_report.get('timestamp', 'N/A')}")
        print(f"종합 전망: {daily_report.get('comprehensive_outlook', {}).get('overall_sentiment', 'N/A')}")
    else:
        print("리포트 생성 실패") 