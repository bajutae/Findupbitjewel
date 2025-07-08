"""
기술적 분석 모듈
RSI, MACD, 이동평균, 볼린저 밴드, 도미넌스 분석 등
"""

import pandas as pd
import numpy as np
try:
    import ta
except ImportError:
    ta = None  # ta 라이브러리가 없는 경우 None으로 설정
from typing import Dict, List, Tuple, Optional, Union
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    """기술적 분석기"""
    
    def __init__(self):
        """초기화"""
        self.indicators = {}
        if ta is None:
            logger.warning("ta library not installed. Some indicators may not work.")
        
    def calculate_moving_averages(self, df: pd.DataFrame, 
                                 periods: List[int] = [5, 10, 20, 50, 200]) -> pd.DataFrame:
        """이동평균 계산"""
        try:
            for period in periods:
                df[f'MA_{period}'] = df['close'].rolling(window=period).mean()
                
            logger.info(f"Successfully calculated moving averages for periods: {periods}")
            return df
            
        except Exception as e:
            logger.error(f"Error calculating moving averages: {e}")
            return df
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """RSI 계산"""
        try:
            if ta is not None:
                df['RSI'] = ta.momentum.RSIIndicator(df['close'], window=period).rsi()
            else:
                # ta 라이브러리가 없을 경우 수동 계산
                df['RSI'] = self._calculate_rsi_manual(df['close'], period)
            
            # RSI 신호 생성
            df['RSI_signal'] = 'neutral'
            df.loc[df['RSI'] > 70, 'RSI_signal'] = 'overbought'
            df.loc[df['RSI'] < 30, 'RSI_signal'] = 'oversold'
            
            logger.info("Successfully calculated RSI")
            return df
            
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return df
    
    def _calculate_rsi_manual(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """RSI 수동 계산"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi  # type: ignore
    
    def calculate_macd(self, df: pd.DataFrame, fast: int = 12, 
                      slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """MACD 계산"""
        try:
            if ta is not None:
                macd_indicator = ta.trend.MACD(df['close'], window_fast=fast, 
                                              window_slow=slow, window_sign=signal)
                
                df['MACD'] = macd_indicator.macd()
                df['MACD_signal'] = macd_indicator.macd_signal()
                df['MACD_histogram'] = macd_indicator.macd_diff()
            else:
                # ta 라이브러리가 없을 경우 수동 계산
                ema_fast = df['close'].ewm(span=fast).mean()
                ema_slow = df['close'].ewm(span=slow).mean()
                df['MACD'] = ema_fast - ema_slow
                df['MACD_signal'] = df['MACD'].ewm(span=signal).mean()
                df['MACD_histogram'] = df['MACD'] - df['MACD_signal']
            
            # MACD 신호 생성
            df['MACD_trend'] = 'neutral'
            df.loc[(df['MACD'] > df['MACD_signal']) & 
                   (df['MACD'].shift(1) <= df['MACD_signal'].shift(1)), 'MACD_trend'] = 'bullish'
            df.loc[(df['MACD'] < df['MACD_signal']) & 
                   (df['MACD'].shift(1) >= df['MACD_signal'].shift(1)), 'MACD_trend'] = 'bearish'
            
            logger.info("Successfully calculated MACD")
            return df
            
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return df
    
    def calculate_bollinger_bands(self, df: pd.DataFrame, 
                                 period: int = 20, std_dev: float = 2) -> pd.DataFrame:
        """볼린저 밴드 계산"""
        try:
            if ta is not None:
                bollinger = ta.volatility.BollingerBands(df['close'], window=period, window_dev=std_dev)
                
                df['BB_upper'] = bollinger.bollinger_hband()
                df['BB_middle'] = bollinger.bollinger_mavg()
                df['BB_lower'] = bollinger.bollinger_lband()
            else:
                # ta 라이브러리가 없을 경우 수동 계산
                df['BB_middle'] = df['close'].rolling(window=period).mean()
                bb_std = df['close'].rolling(window=period).std()
                df['BB_upper'] = df['BB_middle'] + (bb_std * std_dev)
                df['BB_lower'] = df['BB_middle'] - (bb_std * std_dev)
            
            df['BB_width'] = (df['BB_upper'] - df['BB_lower']) / df['BB_middle']
            
            # 볼린저 밴드 신호 생성
            df['BB_signal'] = 'neutral'
            df.loc[df['close'] > df['BB_upper'], 'BB_signal'] = 'overbought'
            df.loc[df['close'] < df['BB_lower'], 'BB_signal'] = 'oversold'
            
            logger.info("Successfully calculated Bollinger Bands")
            return df
            
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            return df
    
    def calculate_stochastic(self, df: pd.DataFrame, k_period: int = 14, 
                           d_period: int = 3) -> pd.DataFrame:
        """스토캐스틱 계산"""
        try:
            if ta is not None:
                stoch = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close'], 
                                                       window=k_period, smooth_window=d_period)
                
                df['Stoch_K'] = stoch.stoch()
                df['Stoch_D'] = stoch.stoch_signal()
            else:
                # ta 라이브러리가 없을 경우 수동 계산
                lowest_low = df['low'].rolling(window=k_period).min()
                highest_high = df['high'].rolling(window=k_period).max()
                df['Stoch_K'] = 100 * (df['close'] - lowest_low) / (highest_high - lowest_low)
                df['Stoch_D'] = df['Stoch_K'].rolling(window=d_period).mean()
            
            # 스토캐스틱 신호 생성
            df['Stoch_signal'] = 'neutral'
            df.loc[(df['Stoch_K'] > 80) & (df['Stoch_D'] > 80), 'Stoch_signal'] = 'overbought'
            df.loc[(df['Stoch_K'] < 20) & (df['Stoch_D'] < 20), 'Stoch_signal'] = 'oversold'
            
            logger.info("Successfully calculated Stochastic")
            return df
            
        except Exception as e:
            logger.error(f"Error calculating Stochastic: {e}")
            return df
    
    def calculate_cci(self, df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """CCI (Commodity Channel Index) 계산"""
        try:
            if ta is not None:
                df['CCI'] = ta.trend.CCIIndicator(df['high'], df['low'], df['close'], window=period).cci()
            else:
                # ta 라이브러리가 없을 경우 수동 계산
                typical_price = (df['high'] + df['low'] + df['close']) / 3
                sma_tp = typical_price.rolling(window=period).mean()
                
                # Mean deviation 계산
                mean_deviation = typical_price.rolling(window=period).apply(
                    lambda x: np.mean(np.abs(x - x.mean())), raw=True
                )
                
                # CCI 계산
                df['CCI'] = (typical_price - sma_tp) / (0.015 * mean_deviation)
            
            # CCI 신호 생성
            df['CCI_signal'] = 'neutral'
            df.loc[df['CCI'] > 100, 'CCI_signal'] = 'overbought'
            df.loc[df['CCI'] < -100, 'CCI_signal'] = 'oversold'
            
            logger.info("Successfully calculated CCI")
            return df
            
        except Exception as e:
            logger.error(f"Error calculating CCI: {e}")
            return df
    
    def calculate_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """거래량 지표 계산"""
        try:
            # 거래량 이동평균
            df['Volume_MA'] = df['volume'].rolling(window=20).mean()
            
            # 거래량 비율
            df['Volume_ratio'] = df['volume'] / df['Volume_MA']
            
            # OBV (On-Balance Volume) 수동 계산
            df['OBV'] = (df['close'].diff() > 0).astype(int) * df['volume']
            df['OBV'] = df['OBV'].cumsum()
            
            # 거래량 신호 생성
            df['Volume_signal'] = 'normal'
            df.loc[df['Volume_ratio'] > 2, 'Volume_signal'] = 'high'
            df.loc[df['Volume_ratio'] < 0.5, 'Volume_signal'] = 'low'
            
            logger.info("Successfully calculated volume indicators")
            return df
            
        except Exception as e:
            logger.error(f"Error calculating volume indicators: {e}")
            return df
    
    def detect_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """차트 패턴 감지"""
        try:
            # 삼각수렴 패턴 감지
            df['Triangle_pattern'] = self._detect_triangle_pattern(df)
            
            # 상승/하락 웨지 패턴 감지
            df['Wedge_pattern'] = self._detect_wedge_pattern(df)
            
            # 지지/저항선 식별
            df['Support_level'] = self._calculate_support_resistance(df, 'support')
            df['Resistance_level'] = self._calculate_support_resistance(df, 'resistance')
            
            logger.info("Successfully detected chart patterns")
            return df
            
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
            return df
    
    def _detect_triangle_pattern(self, df: pd.DataFrame, window: int = 20) -> pd.Series:
        """삼각수렴 패턴 감지"""
        try:
            # 고점과 저점의 추세선 계산
            highs = df['high'].rolling(window=window).max()
            lows = df['low'].rolling(window=window).min()
            
            # 고점 추세선의 기울기
            high_slope = highs.diff(window) / window
            # 저점 추세선의 기울기
            low_slope = lows.diff(window) / window
            
            # 삼각수렴: 고점은 하락, 저점은 상승
            triangle_condition = (high_slope < 0) & (low_slope > 0)
            
            return triangle_condition.astype(str).replace({'True': 'triangle', 'False': 'none'})
            
        except Exception as e:
            logger.error(f"Error detecting triangle pattern: {e}")
            return pd.Series(['none'] * len(df), index=df.index)
    
    def _detect_wedge_pattern(self, df: pd.DataFrame, window: int = 20) -> pd.Series:
        """웨지 패턴 감지"""
        try:
            # 고점과 저점의 기울기 계산
            def calculate_slope(series: pd.Series) -> float:
                try:
                    if len(series) < 2:
                        return 0.0
                    return float(np.polyfit(range(len(series)), series.values, 1)[0])
                except:
                    return 0.0
            
            high_slope = df['high'].rolling(window=window).apply(calculate_slope, raw=False)  # type: ignore
            low_slope = df['low'].rolling(window=window).apply(calculate_slope, raw=False)  # type: ignore
            
            # 상승 웨지: 둘 다 상승하지만 고점 기울기가 더 가파름
            rising_wedge = (high_slope > 0) & (low_slope > 0) & (high_slope > low_slope)
            
            # 하락 웨지: 둘 다 하락하지만 저점 기울기가 더 가파름
            falling_wedge = (high_slope < 0) & (low_slope < 0) & (abs(low_slope) > abs(high_slope))
            
            pattern = pd.Series(['none'] * len(df), index=df.index)
            pattern[rising_wedge] = 'rising_wedge'
            pattern[falling_wedge] = 'falling_wedge'
            
            return pattern
            
        except Exception as e:
            logger.error(f"Error detecting wedge pattern: {e}")
            return pd.Series(['none'] * len(df), index=df.index)
    
    def _calculate_support_resistance(self, df: pd.DataFrame, 
                                    level_type: str, window: int = 20) -> pd.Series:
        """지지/저항선 계산"""
        try:
            if level_type == 'support':
                # 지지선: 최근 저점들의 평균
                return df['low'].rolling(window=window).min()
            else:
                # 저항선: 최근 고점들의 평균
                return df['high'].rolling(window=window).max()
                
        except Exception as e:
            logger.error(f"Error calculating {level_type} levels: {e}")
            return pd.Series([0] * len(df), index=df.index)
    
    def analyze_trend(self, df: pd.DataFrame) -> Dict[str, str]:
        """종합 트렌드 분석"""
        try:
            latest = df.iloc[-1]
            
            # 단기 트렌드 (5일 vs 20일 이동평균)
            if latest['close'] > latest['MA_5'] > latest['MA_20']:
                short_trend = 'bullish'
            elif latest['close'] < latest['MA_5'] < latest['MA_20']:
                short_trend = 'bearish'
            else:
                short_trend = 'neutral'
            
            # 중기 트렌드 (20일 vs 50일 이동평균)
            if latest['MA_20'] > latest['MA_50']:
                medium_trend = 'bullish'
            elif latest['MA_20'] < latest['MA_50']:
                medium_trend = 'bearish'
            else:
                medium_trend = 'neutral'
            
            # 장기 트렌드 (50일 vs 200일 이동평균)
            if latest['MA_50'] > latest['MA_200']:
                long_trend = 'bullish'
            elif latest['MA_50'] < latest['MA_200']:
                long_trend = 'bearish'
            else:
                long_trend = 'neutral'
            
            # 종합 트렌드
            trends = [short_trend, medium_trend, long_trend]
            bullish_count = trends.count('bullish')
            bearish_count = trends.count('bearish')
            
            if bullish_count >= 2:
                overall_trend = 'bullish'
            elif bearish_count >= 2:
                overall_trend = 'bearish'
            else:
                overall_trend = 'neutral'
            
            return {
                'short_term': short_trend,
                'medium_term': medium_trend,
                'long_term': long_trend,
                'overall': overall_trend
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trend: {e}")
            return {'short_term': 'neutral', 'medium_term': 'neutral', 
                   'long_term': 'neutral', 'overall': 'neutral'}
    
    def get_trading_signals(self, df: pd.DataFrame) -> Dict[str, str]:
        """매매 신호 생성"""
        try:
            latest = df.iloc[-1]
            signals = {}
            
            # RSI 신호
            signals['rsi'] = latest['RSI_signal']
            
            # MACD 신호
            signals['macd'] = latest['MACD_trend']
            
            # 볼린저 밴드 신호
            signals['bollinger'] = latest['BB_signal']
            
            # 스토캐스틱 신호
            signals['stochastic'] = latest['Stoch_signal']
            
            # 거래량 신호
            signals['volume'] = latest['Volume_signal']
            
            # 종합 신호
            bullish_signals = [sig for sig in signals.values() if sig in ['bullish', 'oversold']]
            bearish_signals = [sig for sig in signals.values() if sig in ['bearish', 'overbought']]
            
            if len(bullish_signals) >= 3:
                signals['overall'] = 'strong_buy'
            elif len(bullish_signals) >= 2:
                signals['overall'] = 'buy'
            elif len(bearish_signals) >= 3:
                signals['overall'] = 'strong_sell'
            elif len(bearish_signals) >= 2:
                signals['overall'] = 'sell'
            else:
                signals['overall'] = 'hold'
            
            return signals
            
        except Exception as e:
            logger.error(f"Error generating trading signals: {e}")
            return {'overall': 'hold'}
    
    def full_analysis(self, df: pd.DataFrame) -> Dict[str, any]:
        """전체 기술적 분석 수행"""
        try:
            # 모든 지표 계산
            df = self.calculate_moving_averages(df)
            df = self.calculate_rsi(df)
            df = self.calculate_macd(df)
            df = self.calculate_bollinger_bands(df)
            df = self.calculate_stochastic(df)
            df = self.calculate_volume_indicators(df)
            df = self.detect_patterns(df)
            
            # 분석 결과 생성
            analysis = {
                'timestamp': datetime.now(),
                'current_price': df['close'].iloc[-1],
                'trend_analysis': self.analyze_trend(df),
                'trading_signals': self.get_trading_signals(df),
                'key_levels': {
                    'support': df['Support_level'].iloc[-1],
                    'resistance': df['Resistance_level'].iloc[-1]
                },
                'indicators': {
                    'rsi': df['RSI'].iloc[-1],
                    'macd': df['MACD'].iloc[-1],
                    'macd_signal': df['MACD_signal'].iloc[-1],
                    'bb_position': (df['close'].iloc[-1] - df['BB_lower'].iloc[-1]) / 
                                  (df['BB_upper'].iloc[-1] - df['BB_lower'].iloc[-1])
                },
                'patterns': {
                    'triangle': df['Triangle_pattern'].iloc[-1],
                    'wedge': df['Wedge_pattern'].iloc[-1]
                }
            }
            
            logger.info("Successfully completed full technical analysis")
            return analysis
            
        except Exception as e:
            logger.error(f"Error in full analysis: {e}")
            return {}


    def multi_timeframe_analysis(self, multi_data: Dict[str, pd.DataFrame]) -> Dict[str, any]:
        """다중 시간봉 분석"""
        try:
            timeframe_analysis = {}
            
            for timeframe, df in multi_data.items():
                if df.empty:
                    continue
                
                # 각 시간봉별로 기술적 분석 실행
                analysis = self.full_analysis(df.copy())
                
                # 시간봉별 특화 분석
                if timeframe == '1h':
                    analysis['timeframe_focus'] = 'short_term_momentum'
                    analysis['volatility_analysis'] = self._analyze_hourly_volatility(df)
                elif timeframe == '4h':
                    analysis['timeframe_focus'] = 'medium_term_trend'
                    analysis['swing_analysis'] = self._analyze_swing_patterns(df)
                elif timeframe == '1d':
                    analysis['timeframe_focus'] = 'long_term_trend'
                    analysis['daily_structure'] = self._analyze_daily_structure(df)
                elif timeframe == '1M':
                    analysis['timeframe_focus'] = 'macro_trend'
                    analysis['monthly_outlook'] = self._analyze_monthly_outlook(df)
                
                timeframe_analysis[timeframe] = analysis
            
            # 다중 시간봉 종합 분석
            consensus_analysis = self._get_timeframe_consensus(timeframe_analysis)
            
            result = {
                'timeframe_analysis': timeframe_analysis,
                'consensus': consensus_analysis
            }
            
            logger.info("Successfully completed multi-timeframe analysis")
            return result
            
        except Exception as e:
            logger.error(f"Error in multi-timeframe analysis: {e}")
            return {}
    
    def _analyze_hourly_volatility(self, df: pd.DataFrame) -> Dict[str, any]:
        """1시간봉 변동성 분석"""
        try:
            recent_volatility = df['close'].tail(24).std()
            avg_volatility = df['close'].rolling(window=24).std().mean()
            
            return {
                'recent_24h_volatility': recent_volatility,
                'average_volatility': avg_volatility,
                'volatility_ratio': recent_volatility / avg_volatility if avg_volatility > 0 else 1,
                'volatility_signal': 'high' if recent_volatility > avg_volatility * 1.5 else 'normal'
            }
        except Exception as e:
            logger.error(f"Error analyzing hourly volatility: {e}")
            return {}
    
    def _analyze_swing_patterns(self, df: pd.DataFrame) -> Dict[str, any]:
        """4시간봉 스윙 패턴 분석"""
        try:
            recent_data = df.tail(20)
            
            # 고점/저점 식별
            highs = recent_data['high'].rolling(window=3, center=True).max() == recent_data['high']
            lows = recent_data['low'].rolling(window=3, center=True).min() == recent_data['low']
            
            swing_highs = recent_data.loc[highs, 'high'].tolist()
            swing_lows = recent_data.loc[lows, 'low'].tolist()
            
            # 스윙 트렌드 분석
            if len(swing_highs) >= 2 and len(swing_lows) >= 2:
                higher_highs = swing_highs[-1] > swing_highs[-2]
                higher_lows = swing_lows[-1] > swing_lows[-2]
                
                if higher_highs and higher_lows:
                    swing_trend = 'uptrend'
                elif not higher_highs and not higher_lows:
                    swing_trend = 'downtrend'
                else:
                    swing_trend = 'sideways'
            else:
                swing_trend = 'insufficient_data'
            
            return {
                'swing_trend': swing_trend,
                'swing_highs_count': len(swing_highs),
                'swing_lows_count': len(swing_lows),
                'latest_swing_high': swing_highs[-1] if swing_highs else None,
                'latest_swing_low': swing_lows[-1] if swing_lows else None
            }
        except Exception as e:
            logger.error(f"Error analyzing swing patterns: {e}")
            return {}
    
    def _analyze_daily_structure(self, df: pd.DataFrame) -> Dict[str, any]:
        """일봉 구조 분석"""
        try:
            recent_data = df.tail(50)
            
            # 주요 이동평균선 정렬
            current_price = recent_data['close'].iloc[-1]
            ma_20 = recent_data['close'].rolling(window=20).mean().iloc[-1]
            ma_50 = recent_data['close'].rolling(window=50).mean().iloc[-1]
            
            # 이동평균선 배치 분석
            if current_price > ma_20 > ma_50:
                ma_structure = 'bullish_alignment'
            elif current_price < ma_20 < ma_50:
                ma_structure = 'bearish_alignment'
            else:
                ma_structure = 'mixed_alignment'
            
            return {
                'ma_structure': ma_structure,
                'price_vs_ma20': ((current_price - ma_20) / ma_20 * 100) if ma_20 > 0 else 0,
                'price_vs_ma50': ((current_price - ma_50) / ma_50 * 100) if ma_50 > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error analyzing daily structure: {e}")
            return {}
    
    def _analyze_monthly_outlook(self, df: pd.DataFrame) -> Dict[str, any]:
        """월봉 전망 분석"""
        try:
            recent_data = df.tail(12)
            
            # 장기 트렌드 분석
            start_price = recent_data['close'].iloc[0]
            end_price = recent_data['close'].iloc[-1]
            
            yearly_performance = ((end_price - start_price) / start_price * 100) if start_price > 0 else 0
            
            # 월별 변동성 분석
            monthly_returns = recent_data['close'].pct_change().dropna()
            volatility = monthly_returns.std() * 100
            
            return {
                'yearly_performance': yearly_performance,
                'monthly_volatility': volatility,
                'trend_strength': 'strong' if abs(yearly_performance) > 50 else 'moderate' if abs(yearly_performance) > 20 else 'weak',
                'market_phase': 'bull' if yearly_performance > 20 else 'bear' if yearly_performance < -20 else 'sideways'
            }
        except Exception as e:
            logger.error(f"Error analyzing monthly outlook: {e}")
            return {}
    
    def _get_timeframe_consensus(self, timeframe_analysis: Dict[str, any]) -> Dict[str, any]:
        """다중 시간봉 합의 분석"""
        try:
            # 각 시간봉별 트렌드 수집
            trends = {}
            signals = {}
            
            for timeframe, analysis in timeframe_analysis.items():
                if 'trend_analysis' in analysis:
                    trends[timeframe] = analysis['trend_analysis']
                if 'trading_signals' in analysis:
                    signals[timeframe] = analysis['trading_signals']
            
            # 트렌드 합의 계산
            trend_consensus = self._calculate_trend_consensus(trends)
            
            # 신호 합의 계산
            signal_consensus = self._calculate_signal_consensus(signals)
            
            return {
                'trend_consensus': trend_consensus,
                'signal_consensus': signal_consensus,
                'confluence_strength': self._calculate_confluence_strength(trends, signals)
            }
        except Exception as e:
            logger.error(f"Error calculating timeframe consensus: {e}")
            return {}
    
    def _calculate_trend_consensus(self, trends: Dict[str, Dict]) -> Dict[str, any]:
        """트렌드 합의 계산"""
        trend_weights = {'1h': 0.1, '4h': 0.3, '1d': 0.4, '1M': 0.2}
        
        bullish_weight = 0
        bearish_weight = 0
        
        for timeframe, trend_data in trends.items():
            weight = trend_weights.get(timeframe, 0.25)
            
            if trend_data.get('overall') == 'bullish':
                bullish_weight += weight
            elif trend_data.get('overall') == 'bearish':
                bearish_weight += weight
        
        if bullish_weight > bearish_weight * 1.5:
            consensus = 'bullish'
        elif bearish_weight > bullish_weight * 1.5:
            consensus = 'bearish'
        else:
            consensus = 'neutral'
        
        return {
            'consensus': consensus,
            'bullish_weight': bullish_weight,
            'bearish_weight': bearish_weight,
            'confidence': max(bullish_weight, bearish_weight)
        }
    
    def _calculate_signal_consensus(self, signals: Dict[str, Dict]) -> Dict[str, any]:
        """신호 합의 계산"""
        signal_weights = {'1h': 0.15, '4h': 0.35, '1d': 0.35, '1M': 0.15}
        
        buy_weight = 0
        sell_weight = 0
        
        for timeframe, signal_data in signals.items():
            weight = signal_weights.get(timeframe, 0.25)
            
            if signal_data.get('overall') in ['buy', 'strong_buy']:
                buy_weight += weight
            elif signal_data.get('overall') in ['sell', 'strong_sell']:
                sell_weight += weight
        
        if buy_weight > sell_weight * 1.2:
            consensus = 'buy'
        elif sell_weight > buy_weight * 1.2:
            consensus = 'sell'
        else:
            consensus = 'hold'
        
        return {
            'consensus': consensus,
            'buy_weight': buy_weight,
            'sell_weight': sell_weight,
            'confidence': max(buy_weight, sell_weight)
        }
    
    def _calculate_confluence_strength(self, trends: Dict, signals: Dict) -> str:
        """합의 강도 계산"""
        try:
            agreement_count = 0
            total_count = 0
            
            for timeframe in trends.keys():
                if timeframe in signals:
                    trend = trends[timeframe].get('overall', 'neutral')
                    signal = signals[timeframe].get('overall', 'hold')
                    
                    # 트렌드와 신호가 일치하는지 확인
                    if (trend == 'bullish' and signal in ['buy', 'strong_buy']) or \
                       (trend == 'bearish' and signal in ['sell', 'strong_sell']) or \
                       (trend == 'neutral' and signal == 'hold'):
                        agreement_count += 1
                    
                    total_count += 1
            
            if total_count == 0:
                return 'insufficient_data'
            
            agreement_ratio = agreement_count / total_count
            
            if agreement_ratio >= 0.75:
                return 'strong'
            elif agreement_ratio >= 0.5:
                return 'moderate'
            else:
                return 'weak'
                
        except Exception as e:
            logger.error(f"Error calculating confluence strength: {e}")
            return 'unknown'


# 사용 예시
if __name__ == "__main__":
    # 샘플 데이터 생성 (실제로는 데이터 수집기에서 받아옴)
    from data.collector import CryptoDataCollector
    
    collector = CryptoDataCollector()
    analyzer = TechnicalAnalyzer()
    
    # BTC 데이터 분석
    btc_data = collector.get_historical_data('BTC/USDT', days=100)
    if not btc_data.empty:
        analysis = analyzer.full_analysis(btc_data)
        print("BTC Technical Analysis:", analysis) 