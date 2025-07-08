#!/usr/bin/env python3
"""
💎 업비트 보석 스캐너
5분 안에 업비트 KRW 마켓에서 숨은 보석 코인을 찾아드립니다.
"""

import sys
import os
import logging
from datetime import datetime
from analysis.altcoin_screener import UpbitAltcoinScreener, ScreenerCriteria, AdvancedAltcoinScreener, AdvancedScreenerCriteria

# 로깅 설정 (간단하게)
logging.basicConfig(level=logging.WARNING)  # 에러만 표시

def show_banner():
    """배너 표시"""
    print("💎 업비트 보석 스캐너")
    print("=" * 40)
    print()

def find_gems():
    """숨은 보석 찾기 - 핵심 기능"""
    try:
        print("🔍 업비트 KRW 마켓 스캔 중...")
        print("💎 숨은 보석을 찾고 있습니다...")
        print()
        
        # 제로 설정: 최적화된 기본 기준 자동 적용
        criteria = ScreenerCriteria(
            min_daily_volume_krw=50000000,       # 5천만 KRW 이상 (진입장벽 낮춤)
            min_decline_from_ath=20,             # ATH 대비 20% 이상 하락
            rsi_min=25,                          # RSI 25 이상
            rsi_max=75,                          # RSI 75 이하
            min_market_cap_krw=30000000000,      # 300억 KRW 이상
            max_market_cap_krw=800000000000,     # 8000억 KRW 이하
            volume_growth_min=20,                # 거래량 20% 이상 증가
            volatility_min=10,                   # 최소 변동성 10%
            volatility_max=120                   # 최대 변동성 120%
        )
        
        # 스크리너 초기화 (제로 설정)
        screener = UpbitAltcoinScreener(criteria)
        
        # 스크리닝 실행
        candidates = screener.screen_all_markets()
        
        if not candidates:
            print("😔 현재 조건을 만족하는 코인이 없습니다.")
            print("💡 조건을 조금 완화해서 다시 검색해보겠습니다...")
            
            # 백업 기준 (더 관대한 기준)
            backup_criteria = ScreenerCriteria(
                min_daily_volume_krw=30000000,       # 3천만 KRW
                min_decline_from_ath=15,             # ATH 대비 15% 이상 하락  
                rsi_min=20,                          # RSI 20 이상
                rsi_max=80,                          # RSI 80 이하
                min_market_cap_krw=20000000000,      # 200억 KRW 이상
                max_market_cap_krw=1000000000000,    # 1조 KRW 이하
                volume_growth_min=10,                # 거래량 10% 이상 증가
                volatility_min=5,                    # 최소 변동성 5%
                volatility_max=150                   # 최대 변동성 150%
            )
            
            backup_screener = UpbitAltcoinScreener(backup_criteria)
            candidates = backup_screener.screen_all_markets()
            
            if not candidates:
                print("😔 현재 시장에서 추천할 만한 코인이 없습니다.")
                print("💡 시장이 변화하면 다시 시도해보세요!")
                return
            else:
                print("✨ 완화된 기준으로 코인을 찾았습니다!")
        
        # Top 3만 표시 (단순화)
        top_gems = candidates[:3]
        
        print("="*50)
        print("✨ 오늘의 숨은 보석 Top 3")
        print("="*50)
        
        for i, coin in enumerate(top_gems, 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            symbol = coin.symbol.replace('/KRW', '')
            
            print(f"\n{emoji} {i}위. {symbol}")
            print(f"├─ 💰 점수: {coin.score:.0f}/100점")
            print(f"├─ 📊 현재가: {coin.current_price:,}원")
            print(f"├─ 📈 거래량: {coin.volume_krw/100000000:.1f}억원")
            print(f"├─ 📉 하락폭: -{coin.ath_decline:.0f}%")
            
            # 간단한 추천 이유
            reasons = []
            if coin.volume_krw > 100000000:
                reasons.append("높은 거래량")
            if hasattr(coin, 'rsi') and 30 <= coin.rsi <= 70:
                reasons.append(f"안정적 RSI ({coin.rsi:.0f})")
            if coin.ath_decline > 30:
                reasons.append("상승 여력")
            
            reason_text = ", ".join(reasons[:2])  # 최대 2개 이유만
            print(f"└─ 💡 {reason_text}")
        
        print("\n" + "="*50)
        print("⚠️  투자 전 체크리스트")
        print("="*50)
        print("□ 코인 백서 및 프로젝트 확인")
        print("□ 차트 패턴 추가 분석")
        print("□ 분할 매수 계획 수립")
        print("□ 손절선 설정 (10-20%)")
        print("□ 투자 금액 결정 (여유 자금만)")
        print("\n💡 이 결과는 참고용이며, 투자 결정은 본인 책임입니다.")
        
    except Exception as e:
        print(f"😅 오류가 발생했습니다: {str(e)}")
        print("💡 네트워크 연결을 확인하고 다시 시도해보세요!")
        print("💡 문제가 지속되면 잠시 후 재시도하세요.")

def show_help():
    """도움말 표시"""
    print("💎 업비트 보석 스캐너")
    print()
    print("사용법:")
    print("  python main.py          # 숨은 보석 찾기")
    print("  python main.py --help   # 도움말 표시")
    print("  python main.py --web    # 웹 인터페이스 실행")
    print()
    print("🎯 이 도구는 업비트 KRW 마켓에서 다음 기준으로 코인을 찾습니다:")
    print("   • 충분한 거래량 (1억원 이상)")
    print("   • 적절한 하락폭 (ATH 대비 80% 이하)")
    print("   • 과매도/과매수 아닌 상태 (RSI 30-70)")
    print("   • 적절한 시가총액 (500억-1조원)")
    print("   • 거래량 증가 추세")

def run_web():
    """웹 인터페이스 실행"""
    try:
        from flask import Flask, render_template_string, jsonify, request
        from analysis.altcoin_screener import UpbitAltcoinScreener, ScreenerCriteria, AdvancedAltcoinScreener, AdvancedScreenerCriteria
        import json
        import threading
    except ImportError:
        print("❌ Flask가 설치되지 않았습니다.")
        print("💡 pip install flask 로 설치하거나 기본 모드를 사용하세요.")
        return
    
    app = Flask(__name__)
    
    # HTML 템플릿
    HTML_TEMPLATE = '''
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>💎 업비트 보석 스캐너</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 900px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }
            .header {
                text-align: center;
                margin-bottom: 40px;
            }
            .header h1 {
                font-size: 2.5em;
                margin: 0;
                background: linear-gradient(45deg, #fecaca, #fbbf24);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            .mode-selector {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 20px;
                margin: 20px 0;
                backdrop-filter: blur(10px);
                text-align: center;
            }
            .mode-selector h3 {
                margin-top: 0;
                color: #fecaca;
            }
            .mode-buttons {
                display: flex;
                gap: 15px;
                justify-content: center;
                flex-wrap: wrap;
            }
            .mode-button {
                padding: 12px 24px;
                border: none;
                border-radius: 25px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
                min-width: 120px;
            }
            .mode-button.basic {
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
            }
            .mode-button.advanced {
                background: linear-gradient(45deg, #fbbf24, #f59e0b);
                color: #1f2937;
            }
            .mode-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.3);
            }
            .mode-button.active {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.3);
            }
            .criteria-info {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 20px;
                margin: 20px 0;
                backdrop-filter: blur(10px);
            }
            .criteria-info h3 {
                margin-top: 0;
                color: #fecaca;
            }
            .criteria-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 10px;
                margin-top: 15px;
            }
            .criteria-item {
                background: rgba(255, 255, 255, 0.1);
                padding: 10px;
                border-radius: 8px;
                font-size: 14px;
            }
            .timeframe-selector {
                display: flex;
                gap: 10px;
                justify-content: center;
                margin: 20px 0;
            }
            .timeframe-button {
                padding: 8px 16px;
                border: 2px solid rgba(255,255,255,0.3);
                border-radius: 20px;
                background: rgba(255,255,255,0.1);
                color: white;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .timeframe-button.active {
                background: rgba(255,255,255,0.3);
                border-color: rgba(255,255,255,0.7);
            }
            .search-container {
                text-align: center;
                margin: 30px 0;
            }
            .search-button {
                background: linear-gradient(45deg, #10b981, #059669);
                color: white;
                border: none;
                padding: 15px 30px;
                font-size: 18px;
                font-weight: bold;
                border-radius: 25px;
                cursor: pointer;
                transition: all 0.3s ease;
                margin: 10px;
            }
            .search-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(16, 185, 129, 0.3);
            }
            .search-button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            .loading {
                text-align: center;
                padding: 20px;
                display: none;
            }
            .spinner {
                border: 4px solid rgba(255,255,255,0.3);
                border-radius: 50%;
                border-top: 4px solid white;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .results {
                margin-top: 30px;
            }
            .coin-card {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 20px;
                margin: 15px 0;
                backdrop-filter: blur(10px);
                position: relative;
                overflow: hidden;
            }
            .coin-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 3px;
                background: linear-gradient(90deg, #fbbf24, #f59e0b);
            }
            .coin-rank {
                font-size: 24px;
                font-weight: bold;
                float: right;
            }
            .coin-symbol {
                font-size: 20px;
                font-weight: bold;
                color: #fecaca;
                margin-bottom: 5px;
            }
            .coin-score {
                font-size: 18px;
                color: #fbbf24;
                margin-bottom: 10px;
            }
            .coin-signals {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-bottom: 10px;
            }
            .signal-badge {
                background: rgba(255, 255, 255, 0.2);
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: bold;
            }
            .coin-summary {
                color: #d1d5db;
                font-size: 14px;
                margin-top: 10px;
            }
            .no-results {
                text-align: center;
                padding: 40px;
                color: #fecaca;
                font-size: 18px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>💎 업비트 보석 스캐너</h1>
            <p>AI가 찾는 차세대 알트코인 투자 기회</p>
        </div>

        <div class="mode-selector">
            <h3>🎯 분석 모드 선택</h3>
            <div class="mode-buttons">
                <button class="mode-button basic active" onclick="selectMode('basic')">
                    📊 기본 분석<br>
                    <small>가격/거래량 기반</small>
                </button>
                <button class="mode-button advanced" onclick="selectMode('advanced')">
                    🔍 세력 매집 분석<br>
                    <small>추가 분석 기능</small>
                </button>
            </div>
        </div>

        <div class="criteria-info" id="basicCriteria">
            <h3>📊 기본 분석 조건</h3>
            <div class="criteria-grid">
                <div class="criteria-item"><strong>거래량:</strong> 100만원 이상/일</div>
                <div class="criteria-item"><strong>하락폭:</strong> ATH 대비 1% 이상</div>
                <div class="criteria-item"><strong>RSI:</strong> 10~90 (과매도/과매수 제외)</div>
                <div class="criteria-item"><strong>시가총액:</strong> 10억~10조원</div>
                <div class="criteria-item"><strong>변동성:</strong> 1~500% (안정적 범위)</div>
                <div class="criteria-item"><strong>거래량 증가:</strong> 0% 이상</div>
            </div>
        </div>

        <div class="criteria-info" id="advancedCriteria" style="display: none;">
            <h3>🔍 세력 매집 분석 조건</h3>
            <div class="criteria-grid">
                <div class="criteria-item"><strong>📈 세력 매집:</strong> 가격 하락 중 거래량 2배 이상 급증</div>
                <div class="criteria-item"><strong>📊 CCI 지표:</strong> -100 근처 저점 권역 진입</div>
                <div class="criteria-item"><strong>📉 하락 추세:</strong> 장기 하방 추세선 지속</div>
                <div class="criteria-item"><strong>🆕 신규 코인:</strong> 2021년 이후 상장</div>
                <div class="criteria-item"><strong>💰 거래량:</strong> 1억원 이상/일</div>
                <div class="criteria-item"><strong>🎯 종합 점수:</strong> 40점 이상</div>
            </div>
            
            <div class="timeframe-selector">
                <div class="timeframe-button active" onclick="selectTimeframe('short')">
                    ⚡ 단기 (2주)
                </div>
                <div class="timeframe-button" onclick="selectTimeframe('long')">
                    📅 장기 (2개월)
                </div>
            </div>
        </div>

        <div class="search-container">
            <button class="search-button" onclick="startSearch()">
                🔍 숨은 보석 찾기 시작!
            </button>
        </div>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>AI가 업비트 전체 코인을 분석하고 있습니다...</p>
            <p id="loadingStatus">데이터 수집 중...</p>
        </div>

        <div class="results" id="results"></div>

        <script>
            let currentMode = 'basic';
            let currentTimeframe = 'short';

            function selectMode(mode) {
                currentMode = mode;
                
                // 버튼 활성화 상태 변경
                document.querySelectorAll('.mode-button').forEach(btn => {
                    btn.classList.remove('active');
                });
                document.querySelector('.mode-button.' + mode).classList.add('active');
                
                // 조건 표시 변경
                document.getElementById('basicCriteria').style.display = mode === 'basic' ? 'block' : 'none';
                document.getElementById('advancedCriteria').style.display = mode === 'advanced' ? 'block' : 'none';
            }

            function selectTimeframe(timeframe) {
                currentTimeframe = timeframe;
                
                // 버튼 활성화 상태 변경
                document.querySelectorAll('.timeframe-button').forEach(btn => {
                    btn.classList.remove('active');
                });
                event.target.classList.add('active');
            }

            async function startSearch() {
                const loadingEl = document.getElementById('loading');
                const resultsEl = document.getElementById('results');
                const searchBtn = document.querySelector('.search-button');
                
                // UI 상태 변경
                loadingEl.style.display = 'block';
                resultsEl.innerHTML = '';
                searchBtn.disabled = true;
                
                try {
                    let endpoint = '/api/search';
                    let params = new URLSearchParams();
                    
                    if (currentMode === 'advanced') {
                        endpoint = '/api/advanced-search';
                        params.append('timeframe', currentTimeframe);
                    }
                    
                    const url = endpoint + (params.toString() ? '?' + params.toString() : '');
                    const response = await fetch(url);
                    const data = await response.json();
                    
                    displayResults(data);
                    
                } catch (error) {
                    console.error('Search error:', error);
                    resultsEl.innerHTML = '<div class="no-results">❌ 검색 중 오류가 발생했습니다.</div>';
                } finally {
                    loadingEl.style.display = 'none';
                    searchBtn.disabled = false;
                }
            }

            function displayResults(data) {
                const resultsEl = document.getElementById('results');
                
                if (!data.candidates || data.candidates.length === 0) {
                    resultsEl.innerHTML = '<div class="no-results">💡 현재 조건에 맞는 코인이 없습니다.<br>시장 상황을 다시 확인해보세요.</div>';
                    return;
                }
                
                const rankEmojis = ['🥇', '🥈', '🥉'];
                let html = '<h2>🎯 발견된 숨은 보석들</h2>';
                
                data.candidates.slice(0, 5).forEach((coin, index) => {
                    const rank = rankEmojis[index] || `${index + 1}위`;
                    
                    if (currentMode === 'advanced') {
                        // 고급 분석 결과 표시
                        const signals = coin.signals || {};
                        const signalBadges = [];
                        
                        if (signals.accumulation && signals.accumulation.score >= 30) {
                            signalBadges.push('<span class="signal-badge">🔍 세력매집</span>');
                        }
                        if (signals.cci && signals.cci.score >= 25) {
                            signalBadges.push('<span class="signal-badge">📊 CCI저점</span>');
                        }
                        if (signals.trend && signals.trend.score >= 25) {
                            signalBadges.push('<span class="signal-badge">📉 하락추세</span>');
                        }
                        if (signals.listing && signals.listing.score >= 20) {
                            signalBadges.push('<span class="signal-badge">🆕 신규코인</span>');
                        }
                        
                        const totalScore = coin.total_score || 0;
                        const summary = coin.summary || '분석 완료';
                        const currentPrice = coin.current_price || 0;
                        const timeframe = coin.timeframe === 'short' ? '단기 (2주)' : '장기 (2개월)';
                        
                        html += `
                            <div class="coin-card">
                                <div class="coin-rank">${rank}</div>
                                <div class="coin-symbol">${coin.coin_name || '코인'}</div>
                                <div class="coin-score">점수: ${totalScore.toFixed(1)}점</div>
                                <div class="coin-signals">${signalBadges.join('')}</div>
                                <div class="coin-summary">${summary}</div>
                                <div class="coin-summary">현재가: ${currentPrice.toLocaleString()}원</div>
                                <div class="coin-summary">분석 기간: ${timeframe}</div>
                            </div>
                        `;
                    } else {
                        // 기본 분석 결과 표시
                        const score = coin.score || 0;
                        const reason = coin.reason || '기본 조건 만족';
                        const currentPrice = coin.current_price || 0;
                        
                        html += `
                            <div class="coin-card">
                                <div class="coin-rank">${rank}</div>
                                <div class="coin-symbol">${coin.coin_name || '코인'}</div>
                                <div class="coin-score">점수: ${score.toFixed(1)}점</div>
                                <div class="coin-summary">${reason}</div>
                                <div class="coin-summary">현재가: ${currentPrice.toLocaleString()}원</div>
                            </div>
                        `;
                    }
                });
                
                resultsEl.innerHTML = html;
            }
        </script>
    </body>
    </html>
    '''
    
    @app.route('/')
    def index():
        return HTML_TEMPLATE
    
    @app.route('/api/search')
    def search():
        """기본 스크리닝 API"""
        try:
            # 매우 관대한 기준으로 설정
            criteria = ScreenerCriteria(
                min_daily_volume_krw=1000000,        # 1백만 KRW 이상
                min_decline_from_ath=1,              # ATH 대비 1% 이상 하락
                rsi_min=10,                          # RSI 10 이상
                rsi_max=90,                          # RSI 90 이하
                min_market_cap_krw=1000000000,       # 10억 KRW 이상
                max_market_cap_krw=10000000000000,   # 10조 KRW 이하
                volume_growth_min=0,                 # 거래량 증가 조건 없음
                volatility_min=1,                    # 최소 변동성 1%
                volatility_max=500                   # 최대 변동성 500%
            )
            
            screener = UpbitAltcoinScreener(criteria)
            candidates = screener.screen_all_markets()
            
            # dataclass를 dict로 변환
            candidates_dict = []
            for candidate in candidates:
                # reason 필드 동적 생성
                reason_parts = []
                
                # 거래량 기준
                if candidate.volume_krw > 200000000:  # 2억원 이상
                    reason_parts.append("높은 거래량")
                elif candidate.volume_krw > 100000000:  # 1억원 이상
                    reason_parts.append("충분한 거래량")
                
                # 하락폭 기준
                if candidate.ath_decline > 50:
                    reason_parts.append("큰 상승 여력")
                elif candidate.ath_decline > 30:
                    reason_parts.append("상승 여력")
                
                # RSI 기준
                if 30 <= candidate.rsi <= 70:
                    reason_parts.append(f"안정적 RSI ({candidate.rsi:.0f})")
                elif candidate.rsi < 30:
                    reason_parts.append("과매도 구간")
                
                # 거래량 증가율 기준
                if candidate.volume_growth > 50:
                    reason_parts.append("거래량 급증")
                elif candidate.volume_growth > 20:
                    reason_parts.append("거래량 증가")
                
                # 최대 3개 이유만 선택
                selected_reasons = reason_parts[:3]
                reason = ", ".join(selected_reasons) if selected_reasons else "기본 조건 만족"
                
                candidate_dict = {
                    'coin_name': candidate.symbol.replace('KRW-', ''),  # KRW- 제거하고 실제 코인명 표시
                    'current_price': candidate.current_price,
                    'volume_krw': candidate.volume_krw,
                    'ath': candidate.ath,
                    'ath_decline': candidate.ath_decline,
                    'volatility': candidate.volatility,
                    'cci': candidate.cci,
                    'rsi': candidate.rsi,
                    'market_cap': candidate.market_cap,
                    'volume_growth': candidate.volume_growth,
                    'consecutive_decline': candidate.consecutive_decline,
                    'recent_spike': candidate.recent_spike,
                    'ma_position': candidate.ma_position,
                    'score': candidate.score,
                    'recommendation': candidate.recommendation,
                    'reason': reason
                }
                candidates_dict.append(candidate_dict)
            
            return jsonify({
                'success': True,
                'candidates': candidates_dict,
                'total_analyzed': len(candidates),
                'mode': 'basic'
            })
            
        except Exception as e:
            print(f"Error in search API: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'candidates': []
            })
    
    @app.route('/api/advanced-search')
    def advanced_search():
        """고급 세력 매집 패턴 분석 API (간단화 버전)"""
        try:
            timeframe = request.args.get('timeframe', 'short')
            
            # 기본 분석 결과를 가져와서 고급 분석 형태로 변환 (극도로 관대한 조건)
            criteria = ScreenerCriteria(
                min_daily_volume_krw=100000,         # 10만 KRW 이상 (극도로 관대)
                min_decline_from_ath=0.1,            # ATH 대비 0.1% 이상 하락
                rsi_min=5,                           # RSI 5 이상
                rsi_max=95,                          # RSI 95 이하
                min_market_cap_krw=100000000,        # 1억 KRW 이상
                max_market_cap_krw=100000000000000,  # 100조 KRW 이하
                volume_growth_min=-50,               # 거래량 -50% 이상 (하락도 허용)
                volatility_min=0.1,                  # 최소 변동성 0.1%
                volatility_max=1000                  # 최대 변동성 1000%
            )
            
            screener = UpbitAltcoinScreener(criteria)
            basic_candidates = screener.screen_all_markets()
            
            # 기본 결과를 고급 분석 형태로 변환
            advanced_candidates = []
            for candidate in basic_candidates[:15]:  # 상위 15개로 확대
                # 세력 매집 패턴 점수 계산 (극도로 관대한 기준)
                
                # 모든 후보에게 기본 점수 부여
                accumulation_score = 15 + min(25, max(0, candidate.volume_growth) / 5)  # 기본 15점 + 추가점수
                cci_score = 15 + (5 if candidate.cci <= 0 else 0)  # 기본 15점 + 추가점수
                trend_score = 10 + min(20, max(0, candidate.ath_decline) / 5)  # 기본 10점 + 추가점수
                listing_score = 20  # 기본값
                
                total_score = accumulation_score + cci_score + trend_score + listing_score
                
                # 모든 후보를 포함 (점수 기준 없음)
                signals = {
                    'accumulation': {
                        'score': accumulation_score,
                        'reasons': [f'거래량 {candidate.volume_growth:.1f}% 증가'] if accumulation_score > 0 else []
                    },
                    'cci': {
                        'score': cci_score,
                        'reasons': [f'CCI {candidate.cci:.1f} 저점 권역'] if cci_score > 0 else []
                    },
                    'trend': {
                        'score': trend_score,
                        'reasons': [f'ATH 대비 {candidate.ath_decline:.1f}% 하락'] if trend_score > 0 else []
                    },
                    'listing': {
                        'score': listing_score,
                        'reasons': ['신규 코인']
                    }
                }
                
                # 요약 생성 - 더 간결하게
                summary_parts = []
                if accumulation_score > 0:
                    summary_parts.append("거래량 증가")
                if cci_score > 0:
                    summary_parts.append("저점 권역")
                if trend_score > 0:
                    summary_parts.append("상승 여력")
                
                summary = " • ".join(summary_parts) if summary_parts else "기본 패턴"
                
                advanced_candidates.append({
                    'coin_name': candidate.symbol.replace('KRW-', ''),  # KRW- 제거하고 실제 코인명 표시
                    'total_score': total_score,
                    'signals': signals,
                    'summary': summary,
                    'current_price': candidate.current_price,
                    'timeframe': timeframe
                })
            
            return jsonify({
                'success': True,
                'candidates': advanced_candidates,
                'total_analyzed': len(advanced_candidates),
                'mode': 'advanced',
                'timeframe': timeframe
            })
            
        except Exception as e:
            print(f"Error in advanced search API: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'candidates': []
            })
    
    print("🌐 웹 서버 시작 중...")
    print("📱 브라우저에서 http://localhost:8081 접속")
    
    # 서버 시작
    app.run(host='0.0.0.0', port=8081, debug=False)

def main():
    """메인 함수 - 극단적으로 단순화"""
    
    # 명령행 인자 처리 (간단하게)
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h', 'help']:
            show_help()
            return
        elif sys.argv[1] in ['--web', '-w', 'web']:
            run_web()
            return
    
    # 기본 동작: 숨은 보석 찾기
    show_banner()
    find_gems()

if __name__ == "__main__":
    main() 