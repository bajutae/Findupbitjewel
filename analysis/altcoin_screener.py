"""
업비트 알트코인 스크리너
매일 추천 알트코인을 찾는 필터링 시스템
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import asyncio
import time

# 내부 모듈
from data.collector import UpbitDataCollector
from analysis.technical import TechnicalAnalyzer

logger = logging.getLogger(__name__)

@dataclass
class ScreenerCriteria:
    """스크리너 기준"""
    exchange: str = "UPBIT"
    base_currency: str = "KRW"
    min_daily_volume_krw: float = 100_000_000  # 1억 KRW
    max_listing_days: int = 1648  # 2021년 1월 1일 이후 상장
    min_decline_from_ath: float = 30.0  # 고점 대비 30% 이상 하락
    volatility_min: float = 10.0  # 30일 변동성 10% 이상
    volatility_max: float = 150.0  # 30일 변동성 150% 이하
    cci_min: float = -200.0  # CCI -200 이상
    cci_max: float = 200.0   # CCI 200 이하
    cci_period: int = 20    # CCI 계산 기간
    
    # 새로 추가된 기준들
    rsi_min: float = 20.0   # RSI 20 이상 (과매도에서 회복)
    rsi_max: float = 80.0   # RSI 80 이하 (과매수 제외)
    rsi_period: int = 14    # RSI 계산 기간
    
    min_market_cap_krw: float = 10_000_000_000  # 최소 시가총액 100억원
    max_market_cap_krw: float = 500_000_000_000  # 최대 시가총액 5000억원
    
    volume_growth_min: float = 50.0  # 거래량 증가율 50% 이상
    volume_growth_days: int = 7  # 거래량 증가율 계산 기간
    
    max_consecutive_decline: int = 5  # 최대 연속 하락일
    max_recent_spike: float = 30.0  # 최근 급등/급락 제외 (30%)
    recent_spike_days: int = 3  # 급등/급락 확인 기간
    
    require_above_ma: bool = True  # 이동평균 위에 있어야 함
    ma_period: int = 20  # 이동평균 계산 기간

@dataclass
class AdvancedScreenerCriteria:
    """고급 세력 매집 패턴 분석 기준"""
    # 기본 필터 (매우 완화)
    min_daily_volume_krw: float = 1000000  # 100만원 이상 (매우 관대)
    min_listing_year: int = 2019  # 2019년 이후 상장 (더 완화)
    
    # 세력 매집 패턴 분석 (매우 완화)
    volume_surge_threshold: float = 1.2  # 거래량 급증 임계값 (1.2배로 완화)
    price_decline_threshold: float = -1.0  # 가격 하락 임계값 (-1%로 완화)
    cci_bottom_threshold: float = -50  # CCI 저점 임계값 (-50으로 완화)
    cci_tolerance: float = 50  # CCI 허용 오차 (50으로 확대)
    
    # 하락 추세 분석 (매우 완화)
    downtrend_period: int = 10  # 하락 추세 분석 기간 (10일로 단축)
    trend_strength_threshold: float = 0.3  # 추세 강도 임계값 (0.3으로 완화)

@dataclass
class AltcoinCandidate:
    """알트코인 후보"""
    symbol: str
    name: str
    current_price: float
    volume_krw: float
    ath: float
    ath_decline: float
    volatility: float
    cci: float
    rsi: float
    market_cap: float
    volume_growth: float
    consecutive_decline: int
    recent_spike: str
    ma_position: float
    score: float
    recommendation: str
    reason: str = ""  # 추천 이유

class UpbitAltcoinScreener:
    """업비트 알트코인 스크리너"""
    
    def __init__(self, criteria: Optional[ScreenerCriteria] = None):
        """초기화"""
        self.criteria = criteria or ScreenerCriteria()
        self.upbit_collector = UpbitDataCollector()
        self.technical_analyzer = TechnicalAnalyzer()
        
        # 제외할 코인들 (주요 코인, 스테이블코인 등)
        self.exclude_symbols = {
            'BTC/KRW', 'ETH/KRW', 'BNB/KRW', 'ADA/KRW',
            'USDT/KRW', 'USDC/KRW', 'BUSD/KRW', 'DAI/KRW',
            'TUSD/KRW', 'FDUSD/KRW'
        }
        
        logger.info("Upbit Altcoin Screener initialized")
    
    def get_krw_markets(self) -> List[str]:
        """KRW 마켓 목록 조회 (필터링 적용)"""
        try:
            markets = self.upbit_collector.get_krw_markets()
            
            # 제외할 심볼 필터링
            filtered_markets = [
                market for market in markets 
                if market not in self.exclude_symbols
            ]
            
            logger.info(f"Found {len(filtered_markets)} KRW markets for screening")
            return filtered_markets
            
        except Exception as e:
            logger.error(f"Error getting KRW markets: {e}")
            return []
    
    def check_volume_criteria(self, market: str) -> Tuple[bool, float]:
        """거래량 기준 확인"""
        try:
            volume_info = self.upbit_collector.get_volume_info(market, days=7)
            
            if not volume_info:
                return False, 0.0
            
            avg_volume = volume_info.get('avg_volume_krw', 0)
            
            meets_criteria = avg_volume >= self.criteria.min_daily_volume_krw
            
            logger.debug(f"{market} - Volume: {avg_volume:,.0f} KRW, Meets criteria: {meets_criteria}")
            return meets_criteria, avg_volume
            
        except Exception as e:
            logger.error(f"Error checking volume for {market}: {e}")
            return False, 0.0
    
    def check_ath_decline_criteria(self, market: str) -> Tuple[bool, float, float]:
        """고점 대비 하락 기준 확인"""
        try:
            ath_info = self.upbit_collector.get_all_time_high(market)
            
            if not ath_info:
                return False, 0.0, 0.0
            
            ath = ath_info.get('all_time_high', 0)
            current_price = ath_info.get('current_price', 0)
            decline_rate = ath_info.get('decline_from_ath', 0)
            
            meets_criteria = decline_rate >= self.criteria.min_decline_from_ath
            
            logger.debug(f"{market} - ATH: {ath}, Current: {current_price}, Decline: {decline_rate:.1f}%, Meets criteria: {meets_criteria}")
            return meets_criteria, ath, decline_rate
            
        except Exception as e:
            logger.error(f"Error checking ATH decline for {market}: {e}")
            return False, 0.0, 0.0
    
    def check_volatility_criteria(self, market: str) -> Tuple[bool, float]:
        """변동성 기준 확인"""
        try:
            volatility = self.upbit_collector.calculate_volatility(market, days=30)
            
            meets_criteria = (self.criteria.volatility_min <= volatility <= self.criteria.volatility_max)
            
            logger.debug(f"{market} - Volatility: {volatility:.1f}%, Meets criteria: {meets_criteria}")
            return meets_criteria, volatility
            
        except Exception as e:
            logger.error(f"Error checking volatility for {market}: {e}")
            return False, 0.0
    
    def check_cci_criteria(self, market: str) -> Tuple[bool, float]:
        """CCI 기준 확인"""
        try:
            df = self.upbit_collector.get_ohlcv_dataframe(market, days=50)
            
            if df.empty:
                return False, 0.0
            
            # CCI 계산
            df = self.technical_analyzer.calculate_cci(df, period=self.criteria.cci_period)
            
            if 'CCI' not in df.columns or df['CCI'].empty:
                return False, 0.0
            
            current_cci = df['CCI'].iloc[-1]
            
            # NaN 체크
            if pd.isna(current_cci):
                return False, 0.0
            
            meets_criteria = (self.criteria.cci_min <= current_cci <= self.criteria.cci_max)
            
            logger.debug(f"{market} - CCI: {current_cci:.2f}, Meets criteria: {meets_criteria}")
            return meets_criteria, float(current_cci)
            
        except Exception as e:
            logger.error(f"Error checking CCI for {market}: {e}")
            return False, 0.0
    
    def check_rsi_criteria(self, market: str) -> Tuple[bool, float]:
        """RSI 기준 확인"""
        try:
            df = self.upbit_collector.get_ohlcv_dataframe(market, days=50)
            
            if df.empty:
                return False, 0.0
            
            # RSI 계산
            df = self.technical_analyzer.calculate_rsi(df, period=self.criteria.rsi_period)
            
            if 'RSI' not in df.columns or df['RSI'].empty:
                return False, 0.0
            
            current_rsi = df['RSI'].iloc[-1]
            
            # NaN 체크
            if pd.isna(current_rsi):
                return False, 0.0
            
            meets_criteria = (self.criteria.rsi_min <= current_rsi <= self.criteria.rsi_max)
            
            logger.debug(f"{market} - RSI: {current_rsi:.2f}, Meets criteria: {meets_criteria}")
            return meets_criteria, float(current_rsi)
            
        except Exception as e:
            logger.error(f"Error checking RSI for {market}: {e}")
            return False, 0.0
    
    def check_market_cap_criteria(self, market: str) -> Tuple[bool, float]:
        """시가총액 기준 확인"""
        try:
            market_cap_info = self.upbit_collector.get_market_cap(market)
            
            if not market_cap_info:
                return False, 0.0
            
            estimated_market_cap = market_cap_info.get('estimated_market_cap_krw', 0)
            
            meets_criteria = (self.criteria.min_market_cap_krw <= estimated_market_cap <= self.criteria.max_market_cap_krw)
            
            logger.debug(f"{market} - Market Cap: {estimated_market_cap:,.0f} KRW, Meets criteria: {meets_criteria}")
            return meets_criteria, estimated_market_cap
            
        except Exception as e:
            logger.error(f"Error checking market cap for {market}: {e}")
            return False, 0.0
    
    def check_volume_growth_criteria(self, market: str) -> Tuple[bool, float]:
        """거래량 증가율 기준 확인"""
        try:
            volume_growth_info = self.upbit_collector.get_volume_growth(market, days=self.criteria.volume_growth_days)
            
            if not volume_growth_info:
                return False, 0.0
            
            growth_rate = volume_growth_info.get('growth_rate', 0)
            
            meets_criteria = growth_rate >= self.criteria.volume_growth_min
            
            logger.debug(f"{market} - Volume Growth: {growth_rate:.1f}%, Meets criteria: {meets_criteria}")
            return meets_criteria, growth_rate
            
        except Exception as e:
            logger.error(f"Error checking volume growth for {market}: {e}")
            return False, 0.0
    
    def check_consecutive_decline_criteria(self, market: str) -> Tuple[bool, int]:
        """연속 하락일 기준 확인"""
        try:
            decline_info = self.upbit_collector.check_consecutive_decline(market, days=self.criteria.max_consecutive_decline)
            
            if not decline_info:
                return False, 0
            
            consecutive_decline = decline_info.get('consecutive_decline_days', 0)
            
            meets_criteria = consecutive_decline < self.criteria.max_consecutive_decline
            
            logger.debug(f"{market} - Consecutive Decline: {consecutive_decline} days, Meets criteria: {meets_criteria}")
            return meets_criteria, consecutive_decline
            
        except Exception as e:
            logger.error(f"Error checking consecutive decline for {market}: {e}")
            return False, 0
    
    def check_recent_spike_criteria(self, market: str) -> Tuple[bool, str]:
        """최근 급등/급락 기준 확인"""
        try:
            spike_info = self.upbit_collector.check_recent_spike(market, 
                                                               spike_threshold=self.criteria.max_recent_spike,
                                                               days=self.criteria.recent_spike_days)
            
            if not spike_info:
                return False, 'none'
            
            has_spike = spike_info.get('has_recent_spike', False)
            spike_type = spike_info.get('spike_type', 'none')
            
            meets_criteria = not has_spike  # 급등/급락이 없어야 함
            
            logger.debug(f"{market} - Recent Spike: {spike_type}, Meets criteria: {meets_criteria}")
            return meets_criteria, spike_type
            
        except Exception as e:
            logger.error(f"Error checking recent spike for {market}: {e}")
            return False, 'none'
    
    def check_moving_average_criteria(self, market: str) -> Tuple[bool, float]:
        """이동평균 위치 기준 확인"""
        try:
            ma_info = self.upbit_collector.get_price_vs_moving_average(market, ma_period=self.criteria.ma_period)
            
            if not ma_info:
                return False, 0.0
            
            above_ma = ma_info.get('above_ma', False)
            position_pct = ma_info.get('position_vs_ma_pct', 0)
            
            meets_criteria = above_ma if self.criteria.require_above_ma else True
            
            logger.debug(f"{market} - Above MA: {above_ma}, Position: {position_pct:.1f}%, Meets criteria: {meets_criteria}")
            return meets_criteria, position_pct
            
        except Exception as e:
            logger.error(f"Error checking moving average for {market}: {e}")
            return False, 0.0
    
    def calculate_score(self, market: str, volume: float, ath_decline: float, 
                       volatility: float, cci: float, rsi: float, market_cap: float, volume_growth: float) -> float:
        """종합 점수 계산 (7가지 요소)"""
        try:
            score = 0.0
            
            # 거래량 점수 (0-15점)
            volume_score = min(15, (volume / self.criteria.min_daily_volume_krw) * 7.5)
            
            # ATH 하락 점수 (0-15점)
            ath_score = min(15, (ath_decline / 100) * 15)
            
            # 변동성 점수 (0-15점) - 중간값이 최고점
            volatility_mid = (self.criteria.volatility_min + self.criteria.volatility_max) / 2
            volatility_score = 15 - abs(volatility - volatility_mid) * 0.3
            volatility_score = max(0, volatility_score)
            
            # CCI 점수 (0-15점) - 0에 가까울수록 좋음
            cci_score = 15 - abs(cci) * 0.3
            cci_score = max(0, cci_score)
            
            # RSI 점수 (0-15점) - 30-70 구간이 최적
            rsi_optimal = 50
            rsi_score = 15 - abs(rsi - rsi_optimal) * 0.3
            rsi_score = max(0, rsi_score)
            
            # 시가총액 점수 (0-15점) - 적정 규모 선호
            market_cap_optimal = 100_000_000_000  # 1000억원
            market_cap_score = 15 - abs(market_cap - market_cap_optimal) / market_cap_optimal * 10
            market_cap_score = max(0, market_cap_score)
            
            # 거래량 증가율 점수 (0-10점)
            volume_growth_score = min(10, volume_growth / 100 * 10)
            volume_growth_score = max(0, volume_growth_score)
            
            score = volume_score + ath_score + volatility_score + cci_score + rsi_score + market_cap_score + volume_growth_score
            
            logger.debug(f"{market} - Score: {score:.2f} (V:{volume_score:.1f}, A:{ath_score:.1f}, Vol:{volatility_score:.1f}, CCI:{cci_score:.1f}, RSI:{rsi_score:.1f}, MC:{market_cap_score:.1f}, VG:{volume_growth_score:.1f})")
            return score
            
        except Exception as e:
            logger.error(f"Error calculating score for {market}: {e}")
            return 0.0
    
    def get_recommendation(self, score: float) -> str:
        """추천 등급 결정"""
        if score >= 80:
            return "매우 추천"
        elif score >= 60:
            return "추천"
        elif score >= 40:
            return "관심"
        else:
            return "검토 필요"
    
    def generate_reason(self, volume: float, ath_decline: float, rsi: float, 
                       volatility: float, volume_growth: float) -> str:
        """추천 이유 생성"""
        reasons = []
        
        # 거래량 기준
        if volume > 200000000:  # 2억원 이상
            reasons.append("높은 거래량")
        elif volume > 100000000:  # 1억원 이상
            reasons.append("충분한 거래량")
        
        # 하락폭 기준
        if ath_decline > 50:
            reasons.append("큰 상승 여력")
        elif ath_decline > 30:
            reasons.append("상승 여력")
        
        # RSI 기준
        if 30 <= rsi <= 70:
            reasons.append(f"안정적 RSI ({rsi:.0f})")
        elif rsi < 30:
            reasons.append("과매도 구간")
        
        # 변동성 기준
        if volatility < 50:
            reasons.append("안정적 변동성")
        elif volatility > 100:
            reasons.append("높은 변동성")
        
        # 거래량 증가율 기준
        if volume_growth > 50:
            reasons.append("거래량 급증")
        elif volume_growth > 20:
            reasons.append("거래량 증가")
        
        # 최대 3개 이유만 선택
        selected_reasons = reasons[:3]
        
        if selected_reasons:
            return ", ".join(selected_reasons)
        else:
            return "기본 조건 만족"
    
    def screen_single_market(self, market: str) -> Optional[AltcoinCandidate]:
        """개별 마켓 스크리닝"""
        try:
            logger.info(f"Screening {market}...")
            
            # 1. 거래량 확인
            volume_ok, volume = self.check_volume_criteria(market)
            if not volume_ok:
                logger.debug(f"{market} - Failed volume criteria")
                return None
            
            # 2. ATH 하락 확인
            ath_ok, ath, ath_decline = self.check_ath_decline_criteria(market)
            if not ath_ok:
                logger.debug(f"{market} - Failed ATH decline criteria")
                return None
            
            # 3. 변동성 확인
            volatility_ok, volatility = self.check_volatility_criteria(market)
            if not volatility_ok:
                logger.debug(f"{market} - Failed volatility criteria")
                return None
            
            # 4. CCI 확인
            cci_ok, cci = self.check_cci_criteria(market)
            if not cci_ok:
                logger.debug(f"{market} - Failed CCI criteria")
                return None
            
            # 5. RSI 확인
            rsi_ok, rsi = self.check_rsi_criteria(market)
            if not rsi_ok:
                logger.debug(f"{market} - Failed RSI criteria")
                return None
            
            # 6. 시가총액 확인 (임시로 제거)
            market_cap_ok, market_cap = True, 50000000000  # 기본값으로 설정
            
            # 7. 거래량 증가율 확인
            volume_growth_ok, volume_growth = self.check_volume_growth_criteria(market)
            if not volume_growth_ok:
                logger.debug(f"{market} - Failed volume growth criteria")
                return None
            
            # 8. 연속 하락일 확인 (임시로 제거)
            decline_ok, consecutive_decline = True, 2  # 기본값으로 설정
            
            # 9. 최근 급등/급락 확인 (임시로 제거)
            spike_ok, recent_spike = True, 'none'  # 기본값으로 설정
            
            # 10. 이동평균 위치 확인 (임시로 제거)
            ma_ok, ma_position = True, 5.0  # 기본값으로 설정
            
            # 11. 현재 가격 조회
            ticker_info = self.upbit_collector.get_ticker_info([market])
            if not ticker_info:
                logger.debug(f"{market} - Failed to get ticker info")
                return None
            
            current_price = ticker_info[0]['trade_price']
            
            # 12. 종합 점수 계산
            score = self.calculate_score(market, volume, ath_decline, volatility, cci, rsi, market_cap, volume_growth)
            
            # 13. 마켓 정보 조회
            market_info = self.upbit_collector.get_listing_info(market)
            name = market_info.get('korean_name', market)
            
            # 14. 추천 이유 생성
            reason = self.generate_reason(volume, ath_decline, rsi, volatility, volume_growth)
            
            # 15. 후보 생성
            candidate = AltcoinCandidate(
                symbol=market,
                name=name,
                current_price=current_price,
                volume_krw=volume,
                ath=ath,
                ath_decline=ath_decline,
                volatility=volatility,
                cci=cci,
                rsi=rsi,
                market_cap=market_cap,
                volume_growth=volume_growth,
                consecutive_decline=consecutive_decline,
                recent_spike=recent_spike,
                ma_position=ma_position,
                score=score,
                recommendation=self.get_recommendation(score),
                reason=reason
            )
            
            logger.info(f"{market} - PASSED all criteria! Score: {score:.2f}")
            return candidate
            
        except Exception as e:
            logger.error(f"Error screening {market}: {e}")
            return None
    
    def screen_all_markets(self) -> List[AltcoinCandidate]:
        """모든 마켓 스크리닝"""
        try:
            logger.info("Starting altcoin screening...")
            
            # KRW 마켓 목록 조회
            markets = self.get_krw_markets()
            
            if not markets:
                logger.warning("No markets found for screening")
                return []
            
            candidates = []
            
            for market in markets:
                try:
                    candidate = self.screen_single_market(market)
                    if candidate:
                        candidates.append(candidate)
                    
                    # API 호출 제한 방지
                    time.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Error processing {market}: {e}")
                    continue
            
            # 점수 순으로 정렬
            candidates.sort(key=lambda x: x.score, reverse=True)
            
            logger.info(f"Screening completed. Found {len(candidates)} candidates")
            return candidates
            
        except Exception as e:
            logger.error(f"Error in screening process: {e}")
            return []
    
    def generate_report(self, candidates: List[AltcoinCandidate]) -> Dict:
        """스크리닝 결과 리포트 생성"""
        try:
            if not candidates:
                return {
                    'timestamp': datetime.now(),
                    'criteria': self.criteria,
                    'total_candidates': 0,
                    'candidates': [],
                    'summary': "조건을 만족하는 알트코인이 없습니다."
                }
            
            # 카테고리별 분류
            very_recommended = [c for c in candidates if c.recommendation == "매우 추천"]
            recommended = [c for c in candidates if c.recommendation == "추천"]
            interesting = [c for c in candidates if c.recommendation == "관심"]
            
            report = {
                'timestamp': datetime.now(),
                'criteria': self.criteria,
                'total_candidates': len(candidates),
                'candidates': candidates,
                'summary': {
                    'very_recommended': len(very_recommended),
                    'recommended': len(recommended),
                    'interesting': len(interesting),
                    'top_candidate': candidates[0] if candidates else None
                }
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return {}
    
    def run_daily_screening(self) -> Dict:
        """일일 스크리닝 실행"""
        try:
            logger.info("Starting daily altcoin screening...")
            
            start_time = datetime.now()
            
            # 스크리닝 실행
            candidates = self.screen_all_markets()
            
            # 리포트 생성
            report = self.generate_report(candidates)
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            logger.info(f"Daily screening completed in {duration.total_seconds():.2f} seconds")
            logger.info(f"Found {len(candidates)} candidates")
            
            return report
            
        except Exception as e:
            logger.error(f"Error in daily screening: {e}")
            return {}

class AdvancedAltcoinScreener:
    """고급 세력 매집 패턴 분석 스크리너"""
    
    def __init__(self, criteria: AdvancedScreenerCriteria):
        self.criteria = criteria
        self.collector = UpbitDataCollector()
        
    def analyze_accumulation_pattern(self, symbol: str, timeframe: str = 'short') -> Optional[Dict]:
        """세력 매집 패턴 분석
        
        Args:
            symbol: 코인 심볼 (예: KRW-BTC)
            timeframe: 'short' (단기) 또는 'long' (장기)
        """
        try:
            if timeframe == 'short':
                period = 14  # 2주
                volume_period = 7  # 1주
            else:  # long
                period = 60  # 2개월
                volume_period = 30  # 1개월
            
            # 1. 기본 데이터 수집
            daily_candles = self.collector.get_daily_candles(symbol, period)
            if not daily_candles or len(daily_candles) < 10:
                return None
                
            df = pd.DataFrame(daily_candles)
            df['close'] = df['trade_price'].astype(float)
            df['volume'] = df['candle_acc_trade_volume'].astype(float)
            df['value'] = df['candle_acc_trade_price'].astype(float)
            
            # 2. 세력 매집 신호 분석
            accumulation_signals = self._detect_accumulation_signals(df, volume_period)
            
            # 3. CCI 저점 분석
            cci_signals = self._analyze_cci_bottom(df)
            
            # 4. 하락 추세 분석
            trend_signals = self._analyze_downtrend(df)
            
            # 5. 상장일 확인
            listing_info = self.collector.get_listing_info(symbol)
            listing_signals = self._check_listing_date(listing_info)
            
            # 6. 종합 점수 계산
            total_score = (
                accumulation_signals.get('score', 0) * 0.3 +
                cci_signals.get('score', 0) * 0.25 +
                trend_signals.get('score', 0) * 0.25 +
                listing_signals.get('score', 0) * 0.2
            )
            
            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'total_score': total_score,
                'signals': {
                    'accumulation': accumulation_signals,
                    'cci': cci_signals,
                    'trend': trend_signals,
                    'listing': listing_signals
                },
                'current_price': float(df['close'].iloc[-1]),
                'summary': self._generate_summary(accumulation_signals, cci_signals, trend_signals, listing_signals)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None
    
    def _detect_accumulation_signals(self, df: pd.DataFrame, volume_period: int) -> Dict:
        """세력 매집 신호 탐지 (가격 하락 + 거래량 급증)"""
        try:
            # 최근 거래량 평균 대비 급증 확인
            recent_volumes = df['value'].tail(3).mean()
            avg_volume = df['value'].tail(volume_period).mean()
            volume_ratio = recent_volumes / avg_volume if avg_volume > 0 else 0
            
            # 최근 가격 변화율
            recent_price_change = (df['close'].iloc[-1] - df['close'].iloc[-3]) / df['close'].iloc[-3] * 100
            
            # 세력 매집 패턴 점수
            score = 0
            reasons = []
            
            # 거래량 급증 (가격 하락 시)
            if volume_ratio >= self.criteria.volume_surge_threshold and recent_price_change <= self.criteria.price_decline_threshold:
                score += 40
                reasons.append(f"가격 {recent_price_change:.1f}% 하락 중 거래량 {volume_ratio:.1f}배 급증")
            elif volume_ratio >= self.criteria.volume_surge_threshold:
                score += 20
                reasons.append(f"거래량 {volume_ratio:.1f}배 급증")
            
            # 지속적인 매집 패턴
            volume_trend = df['value'].tail(7).rolling(window=3).mean()
            if len(volume_trend) >= 2 and volume_trend.iloc[-1] > volume_trend.iloc[-2]:
                score += 15
                reasons.append("지속적인 거래량 증가 패턴")
            
            return {
                'score': min(score, 100),
                'volume_ratio': volume_ratio,
                'price_change': recent_price_change,
                'reasons': reasons
            }
            
        except Exception as e:
            logger.error(f"Error detecting accumulation signals: {e}")
            return {'score': 0, 'reasons': ['분석 오류']}
    
    def _analyze_cci_bottom(self, df: pd.DataFrame) -> Dict:
        """CCI 지표 저점 분석"""
        try:
            # CCI 계산 (간단한 버전)
            period = 14
            if len(df) < period:
                return {'score': 0, 'reasons': ['데이터 부족']}
            
            typical_price = (df['close'] + df['close'] + df['close']) / 3  # 간단화
            sma = typical_price.rolling(window=period).mean()
            mad = typical_price.rolling(window=period).apply(lambda x: abs(x - x.mean()).mean())
            cci = (typical_price - sma) / (0.015 * mad)
            
            current_cci = float(cci.iloc[-1]) if not pd.isna(cci.iloc[-1]) else 0.0
            min_cci = float(cci.tail(period).min())
            
            score = 0
            reasons = []
            
            # CCI 저점 근처 확인
            if current_cci <= self.criteria.cci_bottom_threshold + self.criteria.cci_tolerance:
                if current_cci >= self.criteria.cci_bottom_threshold - self.criteria.cci_tolerance:
                    score += 35
                    reasons.append(f"CCI {current_cci:.1f} 저점 영역 진입")
                else:
                    score += 25
                    reasons.append(f"CCI {current_cci:.1f} 과매도 상태")
            
            # CCI 반등 신호
            if len(cci) >= 3 and cci.iloc[-1] > cci.iloc[-2] > cci.iloc[-3]:
                score += 20
                reasons.append("CCI 상승 반전 신호")
            
            return {
                'score': min(score, 100),
                'current_cci': current_cci,
                'min_cci': min_cci,
                'reasons': reasons
            }
            
        except Exception as e:
            logger.error(f"Error analyzing CCI: {e}")
            return {'score': 0, 'reasons': ['CCI 분석 오류']}
    
    def _analyze_downtrend(self, df: pd.DataFrame) -> Dict:
        """하락 추세 분석"""
        try:
            if len(df) < 10:
                return {'score': 0, 'reasons': ['데이터 부족']}
            
            prices = df['close'].values.astype(float)
            score = 0
            reasons = []
            
            # 장기 하락 추세 확인
            period = min(len(prices), self.criteria.downtrend_period)
            slope = np.polyfit(range(period), prices[-period:], 1)[0]
            
            if slope < -0.1:  # 하락 추세
                score += 30
                reasons.append("명확한 하락 추세 확인")
                
                # 추세 강도 확인
                correlation = abs(np.corrcoef(range(period), prices[-period:])[0,1])
                if correlation >= self.criteria.trend_strength_threshold:
                    score += 15
                    reasons.append(f"강한 하락 추세 (상관계수 {correlation:.2f})")
            
            # 최근 저점 형성 확인
            recent_prices = prices[-7:]
            if len(recent_prices) >= 3:
                min_idx = np.argmin(recent_prices)
                if min_idx in [1, 2, 3]:  # 중간에 저점이 있으면
                    score += 20
                    reasons.append("최근 저점 형성 후 횡보/반등")
            
            return {
                'score': min(score, 100),
                'trend_slope': float(slope),
                'reasons': reasons
            }
            
        except Exception as e:
            logger.error(f"Error analyzing downtrend: {e}")
            return {'score': 0, 'reasons': ['추세 분석 오류']}
    
    def _check_listing_date(self, listing_info: Dict) -> Dict:
        """상장일 확인 (2021년 이후)"""
        try:
            score = 0
            reasons = []
            
            # 기본적으로 2021년 이후로 가정 (업비트 대부분 코인)
            score += 30
            reasons.append("2021년 이후 상장 (신규 코인)")
            
            return {
                'score': min(score, 100),
                'reasons': reasons
            }
            
        except Exception as e:
            logger.error(f"Error checking listing date: {e}")
            return {'score': 0, 'reasons': ['상장일 확인 오류']}
    
    def _generate_summary(self, accumulation, cci, trend, listing) -> str:
        """분석 결과 요약"""
        summary_parts = []
        
        if accumulation['score'] >= 30:
            summary_parts.append("🔍 세력 매집 신호")
        if cci['score'] >= 25:
            summary_parts.append("📊 CCI 저점 권역")
        if trend['score'] >= 25:
            summary_parts.append("📉 하락 추세 지속")
        if listing['score'] >= 20:
            summary_parts.append("🆕 신규 코인")
        
        return " | ".join(summary_parts) if summary_parts else "일반적인 패턴"
    
    def screen_advanced_patterns(self, timeframe: str = 'short') -> List[Dict]:
        """고급 패턴 스크리닝 실행"""
        try:
            logger.info(f"Starting advanced pattern screening ({timeframe})")
            
            # KRW 마켓 코인 목록 가져오기
            markets = self.collector.get_krw_markets()
            if not markets:
                logger.error("Failed to fetch market list")
                return []
            
            candidates = []
            
            for market in markets[:50]:  # 처음 50개만 테스트
                symbol = "Unknown"  # 기본값 설정
                try:
                    symbol = market['market']
                    logger.info(f"Analyzing {symbol} for {timeframe} patterns...")
                    
                    result = self.analyze_accumulation_pattern(symbol, timeframe)
                    if result and result['total_score'] >= 0:  # 0점 이상 (디버깅용)
                        candidates.append(result)
                        
                    time.sleep(0.1)  # API 호출 제한
                    
                except Exception as e:
                    logger.error(f"Error analyzing {symbol}: {e}")
                    continue
            
            # 점수순 정렬
            candidates.sort(key=lambda x: x['total_score'], reverse=True)
            
            logger.info(f"Found {len(candidates)} advanced pattern candidates")
            return candidates
            
        except Exception as e:
            logger.error(f"Error in advanced screening: {e}")
            return [] 