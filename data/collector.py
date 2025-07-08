"""
업비트 데이터 수집 모듈 - 간단한 API 호출 버전
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import logging
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
import urllib3

# SSL 경고 비활성화
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UpbitDataCollector:
    """업비트 데이터 수집기 (직접 API 호출)"""
    
    def __init__(self):
        """초기화"""
        self.base_url = "https://api.upbit.com"
        
        # 캐시 설정
        self.cache = {}
        self.cache_timeout = 300  # 5분 캐시
        
        logger.info("Upbit Data Collector (direct API) initialized")
    
    def get_all_markets(self) -> List[Dict]:
        """모든 마켓 정보 조회"""
        try:
            url = f"{self.base_url}/v1/market/all"
            response = requests.get(url, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Successfully fetched {len(data)} markets from Upbit")
                return data
            else:
                logger.error(f"Error fetching markets: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching all markets: {e}")
            return []
    
    def get_krw_markets(self) -> List[str]:
        """KRW 마켓 목록 조회"""
        try:
            markets = self.get_all_markets()
            krw_markets = [market['market'] for market in markets if market['market'].startswith('KRW-')]
            
            logger.info(f"Found {len(krw_markets)} KRW markets")
            return krw_markets
            
        except Exception as e:
            logger.error(f"Error fetching KRW markets: {e}")
            return []
    
    def get_ticker_info(self, markets: List[str]) -> List[Dict]:
        """현재 시세 조회"""
        try:
            if not markets:
                return []
                
            # 마켓 목록을 쿼리 파라미터로 변환
            markets_param = ','.join(markets)
            url = f"{self.base_url}/v1/ticker"
            params = {'markets': markets_param}
            
            response = requests.get(url, params=params, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Successfully fetched ticker info for {len(data)} markets")
                return data
            else:
                logger.error(f"Error fetching ticker info: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching ticker info: {e}")
            return []
    
    def get_candles_daily(self, market: str, count: int = 200) -> List[Dict]:
        """일별 캔들 조회"""
        try:
            url = f"{self.base_url}/v1/candles/days"
            params = {'market': market, 'count': count}
            
            response = requests.get(url, params=params, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Successfully fetched daily candles for {market}")
                return data
            else:
                logger.error(f"Error fetching daily candles: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching daily candles for {market}: {e}")
            return []
    
    def get_volume_info(self, market: str, days: int = 30) -> Dict:
        """거래량 정보 조회"""
        try:
            candles = self.get_candles_daily(market, days)
            
            if not candles:
                return {}
            
            volumes = [candle['candle_acc_trade_price'] for candle in candles]
            
            volume_info = {
                'market': market,
                'avg_volume_krw': sum(volumes) / len(volumes),
                'latest_volume_krw': volumes[0] if volumes else 0,
                'max_volume_krw': max(volumes) if volumes else 0,
                'min_volume_krw': min(volumes) if volumes else 0,
                'volume_trend': self._calculate_volume_trend(volumes[:7])  # 최근 7일
            }
            
            logger.info(f"Successfully calculated volume info for {market}")
            return volume_info
            
        except Exception as e:
            logger.error(f"Error calculating volume info for {market}: {e}")
            return {}
    
    def _calculate_volume_trend(self, volumes: List[float]) -> str:
        """거래량 트렌드 계산"""
        if len(volumes) < 2:
            return 'neutral'
        
        recent_avg = sum(volumes[:3]) / 3 if len(volumes) >= 3 else volumes[0]
        older_avg = sum(volumes[3:]) / (len(volumes) - 3) if len(volumes) > 3 else volumes[-1]
        
        if recent_avg > older_avg * 1.2:
            return 'increasing'
        elif recent_avg < older_avg * 0.8:
            return 'decreasing'
        else:
            return 'stable'
    
    def get_ohlcv_dataframe(self, market: str, days: int = 200) -> pd.DataFrame:
        """OHLCV 데이터를 DataFrame으로 변환"""
        try:
            candles = self.get_candles_daily(market, days)
            
            if not candles:
                return pd.DataFrame()
            
            # DataFrame으로 변환
            df_data = []
            for candle in candles:
                df_data.append({
                    'timestamp': candle['candle_date_time_utc'],
                    'open': candle['opening_price'],
                    'high': candle['high_price'],
                    'low': candle['low_price'],
                    'close': candle['trade_price'],
                    'volume': candle['candle_acc_trade_volume']
                })
            
            df = pd.DataFrame(df_data)
            
            # 타임스탬프 처리
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            
            # 숫자 타입으로 변환
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            logger.info(f"Successfully converted {market} candles to DataFrame")
            return df
            
        except Exception as e:
            logger.error(f"Error converting {market} candles to DataFrame: {e}")
            return pd.DataFrame()
    
    def get_all_time_high(self, market: str) -> Dict:
        """역대 최고가 조회"""
        try:
            candles = self.get_candles_daily(market, 200)
            
            if not candles:
                return {}
            
            highs = [candle['high_price'] for candle in candles]
            max_high = max(highs)
            current_price = candles[0]['trade_price']  # 최신 가격
            
            # 고점 대비 하락률 계산
            decline_rate = (max_high - current_price) / max_high * 100
            
            ath_info = {
                'market': market,
                'all_time_high': max_high,
                'current_price': current_price,
                'decline_from_ath': decline_rate
            }
            
            logger.info(f"Successfully calculated ATH info for {market}")
            return ath_info
            
        except Exception as e:
            logger.error(f"Error calculating ATH for {market}: {e}")
            return {}
    
    def calculate_volatility(self, market: str, days: int = 30) -> float:
        """변동성 계산"""
        try:
            df = self.get_ohlcv_dataframe(market, days)
            
            if df.empty:
                return 0.0
            
            # 일별 수익률 계산
            df['daily_return'] = df['close'].pct_change()
            
            # 변동성 계산 (표준편차)
            volatility = df['daily_return'].std() * np.sqrt(252) * 100  # 연환산 %
            
            logger.info(f"Successfully calculated volatility for {market}: {volatility:.2f}%")
            return volatility
            
        except Exception as e:
            logger.error(f"Error calculating volatility for {market}: {e}")
            return 0.0
    
    def get_volume_growth(self, market: str, days: int = 7) -> Dict:
        """거래량 증가율 계산"""
        try:
            df = self.get_ohlcv_dataframe(market, days * 2)
            
            if df.empty or len(df) < days * 2:
                return {}
            
            # 최근 기간과 이전 기간으로 나누기
            recent_volume = df['volume'].iloc[-days:].mean()
            previous_volume = df['volume'].iloc[-days*2:-days].mean()
            
            # 증가율 계산
            growth_rate = 0.0
            if previous_volume > 0:
                growth_rate = ((recent_volume - previous_volume) / previous_volume) * 100
            
            volume_growth = {
                'market': market,
                'recent_avg_volume': recent_volume,
                'previous_avg_volume': previous_volume,
                'growth_rate': growth_rate,
                'trend': 'increasing' if growth_rate > 20 else 'decreasing' if growth_rate < -20 else 'stable'
            }
            
            logger.info(f"Successfully calculated volume growth for {market}: {growth_rate:.1f}%")
            return volume_growth
            
        except Exception as e:
            logger.error(f"Error calculating volume growth for {market}: {e}")
            return {}
    
    def get_listing_info(self, market: str) -> Dict:
        """코인 상장 정보 조회"""
        try:
            cache_key = f"listing_info_{market}"
            
            # 캐시 확인
            if cache_key in self.cache:
                cached_time, cached_data = self.cache[cache_key]
                if time.time() - cached_time < self.cache_timeout:
                    return cached_data
            
            # 상장 정보 조회 (업비트는 공개 정보가 제한적)
            info = {
                'korean_name': market.replace('KRW-', '').replace('-', ''),
                'english_name': market.replace('KRW-', '').replace('-', ''),
                'listing_date': None,
                'total_supply': None,
                'circulating_supply': None
            }
            
            # 캐시 저장
            self.cache[cache_key] = (time.time(), info)
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting listing info for {market}: {e}")
            return {}
    
    def get_market_cap(self, market: str) -> Dict:
        """시가총액 정보 조회 (추정)"""
        try:
            ticker_info = self.get_ticker_info([market])
            
            if not ticker_info:
                return {'market_cap_krw': 50000000000, 'estimated': True}
            
            current_price = ticker_info[0]['trade_price']
            
            # 시가총액 추정 (매우 간단한 추정)
            estimated_market_cap = current_price * 1000000  # 임의의 공급량 가정
            
            return {
                'market_cap_krw': estimated_market_cap,
                'estimated': True,
                'current_price': current_price
            }
            
        except Exception as e:
            logger.error(f"Error calculating market cap for {market}: {e}")
            return {'market_cap_krw': 50000000000, 'estimated': True}
    
    def get_daily_candles(self, market: str, count: int = 200) -> List[Dict]:
        """일별 캔들 데이터 조회 (get_candles_daily와 동일)"""
        return self.get_candles_daily(market, count)
    
    def check_consecutive_decline(self, market: str, days: int = 3) -> Dict:
        """연속 하락 일수 확인"""
        try:
            candles = self.get_candles_daily(market, days * 2)
            
            if not candles or len(candles) < days:
                return {'consecutive_decline': 0, 'is_declining': False}
            
            consecutive_count = 0
            for i in range(min(days, len(candles) - 1)):
                current_price = candles[i]['trade_price']
                previous_price = candles[i + 1]['trade_price']
                
                if current_price < previous_price:
                    consecutive_count += 1
                else:
                    break
            
            return {
                'consecutive_decline': consecutive_count,
                'is_declining': consecutive_count >= days
            }
            
        except Exception as e:
            logger.error(f"Error checking consecutive decline for {market}: {e}")
            return {'consecutive_decline': 0, 'is_declining': False}
    
    def check_recent_spike(self, market: str, days: int = 7) -> Dict:
        """최근 급등 확인"""
        try:
            candles = self.get_candles_daily(market, days * 2)
            
            if not candles or len(candles) < days:
                return {'spike_type': 'none', 'max_change': 0}
            
            max_change = 0
            spike_type = 'none'
            
            for i in range(min(days, len(candles) - 1)):
                current_price = candles[i]['trade_price']
                previous_price = candles[i + 1]['trade_price']
                
                change_percent = ((current_price - previous_price) / previous_price) * 100
                
                if abs(change_percent) > abs(max_change):
                    max_change = change_percent
                    
                    if change_percent > 20:
                        spike_type = 'strong_up'
                    elif change_percent > 10:
                        spike_type = 'moderate_up'
                    elif change_percent < -20:
                        spike_type = 'strong_down'
                    elif change_percent < -10:
                        spike_type = 'moderate_down'
            
            return {
                'spike_type': spike_type,
                'max_change': max_change
            }
            
        except Exception as e:
            logger.error(f"Error checking recent spike for {market}: {e}")
            return {'spike_type': 'none', 'max_change': 0}
    
    def get_price_vs_moving_average(self, market: str, ma_period: int = 20) -> Dict:
        """현재 가격과 이동평균 비교"""
        try:
            candles = self.get_candles_daily(market, ma_period + 10)
            
            if not candles or len(candles) < ma_period:
                return {'position': 0, 'ma_value': 0, 'current_price': 0}
            
            # 현재 가격
            current_price = candles[0]['trade_price']
            
            # 이동평균 계산
            prices = [candle['trade_price'] for candle in candles[:ma_period]]
            ma_value = sum(prices) / len(prices)
            
            # 이동평균 대비 위치 계산 (%)
            position = ((current_price - ma_value) / ma_value) * 100
            
            return {
                'position': position,
                'ma_value': ma_value,
                'current_price': current_price
            }
            
        except Exception as e:
            logger.error(f"Error calculating price vs MA for {market}: {e}")
            return {'position': 0, 'ma_value': 0, 'current_price': 0}

# 사용 예시
if __name__ == "__main__":
    collector = UpbitDataCollector()
    
    # KRW 마켓 목록 조회
    krw_markets = collector.get_krw_markets()
    print(f"KRW Markets: {len(krw_markets)}")
    
    # 시세 정보 조회
    if krw_markets:
        ticker_info = collector.get_ticker_info(krw_markets[:5])  # 처음 5개만
        print(f"Ticker Info: {len(ticker_info)} items")
        
        # 첫 번째 마켓의 상세 정보
        if ticker_info:
            market = ticker_info[0]['market']
            print(f"\nDetailed info for {market}:")
            
            # 거래량 정보
            volume_info = collector.get_volume_info(market)
            print(f"Volume Info: {volume_info}")
            
            # 변동성 계산
            volatility = collector.calculate_volatility(market)
            print(f"Volatility: {volatility:.2f}%") 