from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔍💎 업비트 숨은 보석 찾기 - 규칙 테스트</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
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
            color: #feca57;
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
        }
        .criteria-item strong {
            color: #feca57;
        }
        .status {
            background: rgba(76, 175, 80, 0.2);
            border: 1px solid #4CAF50;
            border-radius: 10px;
            padding: 15px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <h1>🔍💎 업비트 숨은 보석 찾기</h1>
    <p style="font-size: 1.2em; opacity: 0.9;">규칙 표시 테스트 페이지</p>
    
    <div class="status">
        <h3>✅ 테스트 서버 정상 작동 중</h3>
        <p>이 페이지가 보인다면 웹 서버가 정상적으로 실행되고 있습니다.</p>
    </div>
    
    <div class="criteria-info">
        <h3>📊 현재 검색 조건</h3>
        <div class="criteria-grid">
            <div class="criteria-item">
                <strong>거래량:</strong> 100만원 이상/일
            </div>
            <div class="criteria-item">
                <strong>하락폭:</strong> ATH 대비 1% 이상
            </div>
            <div class="criteria-item">
                <strong>RSI:</strong> 10~90 (과매도/과매수 제외)
            </div>
            <div class="criteria-item">
                <strong>시가총액:</strong> 10억~10조원
            </div>
            <div class="criteria-item">
                <strong>변동성:</strong> 1~500% (안정적 범위)
            </div>
            <div class="criteria-item">
                <strong>거래량 증가:</strong> 0% 이상 (관대한 기준)
            </div>
        </div>
        <p style="margin-top: 15px; font-size: 0.9em; opacity: 0.8;">
            💡 조건을 만족하는 코인이 없으면 자동으로 더 관대한 기준을 적용합니다.
        </p>
    </div>
    
    <div style="background: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 10px; margin-top: 20px;">
        <h4>🎯 이것이 메인 서버에서 보여야 할 모습입니다!</h4>
        <p>만약 메인 서버(8080)에서 이런 규칙들이 안 보인다면:</p>
        <ul>
            <li>브라우저 새로고침 (Ctrl+F5 또는 Cmd+Shift+R)</li>
            <li>브라우저 캐시 클리어</li>
            <li>웹 서버 재시작</li>
        </ul>
    </div>
</body>
</html>
    '''

if __name__ == '__main__':
    print('🚀 테스트 서버 시작됨!')
    print('📋 브라우저에서 http://localhost:8081 로 접속하세요')
    print('💡 이 페이지에서 검색 조건이 올바르게 표시되는지 확인하세요')
    app.run(host='0.0.0.0', port=8081, debug=False) 