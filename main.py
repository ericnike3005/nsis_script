import feedparser
from google import genai
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import ccxt
import requests

app = FastAPI()

# 1. AI 설정 (보안을 위해 API 키는 향후 환경변수(.env)로 관리하시는 것을 추천합니다)
client = genai.Client(api_key="AIzaSyBXNeUTagryt1qCVpw0Ulg4w9Hxfdm6khU")

def get_exchange_rate():
    """실시간 환율 수집 (백업 경로 추가)"""
    try:
        url = "https://open.er-api.com/v6/latest/USD"
        response = requests.get(url, timeout=3) # 타임아웃 3초로 단축
        return response.json()['rates']['KRW']
    except:
        try:
            url = "https://api.exchangerate-api.com/v4/latest/USD"
            response = requests.get(url, timeout=3)
            return response.json()['rates']['KRW']
        except:
            return 1420.0

# [핵심 개선] async def -> def 로 변경하여 동기 라이브러리 충돌 방지
@app.get("/check/{symbol}", response_class=HTMLResponse)
def check_market(symbol: str):
    
    # (1) 데이터 수집: 예외 처리 및 타임아웃 명시
    try:
        # 무한 로딩 방지를 위해 3초 타임아웃 설정
        exchange = ccxt.bybit({'timeout': 3000}) 
        ticker = exchange.fetch_ticker(f"{symbol.upper()}/USDT")
        price_usdt = ticker['last']
        
        krw_rate = get_exchange_rate()
        price_krw = price_usdt * krw_rate
        
        display_usdt = f"{price_usdt:,.2f} USDT"
        display_krw = f"{int(price_krw):,} 원"
        display_rate = f"실시간 환율 적용: 1$ = {krw_rate:,.1f}원"
    except Exception as e:
        display_usdt, display_krw, display_rate = "거래소 연결 지연", "-", "일시적인 네트워크 오류"

    # (2) 뉴스 수집 (RSS)
    try:
        feed = feedparser.parse("https://cointelegraph.com/rss/tag/security")
        original_news_title = feed.entries[0].title if feed.entries else "뉴스 수집 중..."
        news_link = feed.entries[0].link if feed.entries else "#"
    except:
        original_news_title = "뉴스 데이터를 불러올 수 없습니다."
        news_link = "#"

    # (3) AI 번역 및 분석 (최신 모델 적용 및 2단계 분리)
    translated_title = original_news_title
    ai_result = "AI가 현재 분석을 준비 중입니다."
    
    try:
        if original_news_title not in ["뉴스 수집 중...", "뉴스 데이터를 불러올 수 없습니다."]:
            # Step A: 영어 뉴스 제목을 한글로 번역
            trans_response = client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=f"다음 영문 뉴스 제목을 한국어로 자연스럽게 번역해. 딱 번역된 문장만 출력해:\n{original_news_title}"
            )
            translated_title = trans_response.text.strip()
            
            # Step B: 번역된 한글 제목으로 리스크 분석
            risk_prompt = f"뉴스 제목: {translated_title}\n이 뉴스가 {symbol} 가격에 위험한 요소인가요? 리스크 점수(1~10)와 이유를 1줄로 명확하게 작성해주세요."
            risk_response = client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=risk_prompt
            )
            ai_result = risk_response.text.replace("\n", "<br>")
    except Exception as e:
        ai_result = f"AI 연동 지연 중입니다. 잠시 후 새로고침 해주세요."

    # (4) 디자인 (기존 유지, 뉴스 제목 변수만 교체)
    html_content = f"""
    <html>
        <head>
            <title>{symbol.upper()} 리얼타임 리포트</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <script>
                let timeLeft = 30;
                function startTimer() {{
                    const timerElement = document.getElementById('timer');
                    const countdown = setInterval(() => {{
                        timeLeft -= 1;
                        timerElement.innerText = timeLeft + "s";
                        if (timeLeft <= 0) {{ clearInterval(countdown); location.reload(); }}
                    }}, 1000);
                }}
                window.onload = startTimer;
            </script>
        </head>
        <body class="bg-slate-950 text-slate-200 font-sans p-6 md:p-12">
            <div class="max-w-5xl mx-auto">
                <header class="flex justify-between items-end mb-8 border-b border-slate-800 pb-6">
                    <div>
                        <h1 class="text-5xl font-extrabold text-amber-500 tracking-tight">{symbol.upper()} <span class="text-slate-500 text-2xl">Monitor</span></h1>
                        <p class="text-slate-500 mt-2 font-mono">{display_rate}</p>
                    </div>
                    <div class="flex items-center space-x-3">
                        <div id="timer" class="text-amber-500 font-mono text-xl font-bold bg-slate-900 px-3 py-1 rounded-lg border border-slate-800 shadow-inner">30s</div>
                        <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
                            <span class="w-2 h-2 mr-2 bg-emerald-500 rounded-full animate-pulse"></span>
                            Live System
                        </span>
                    </div>
                </header>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <div class="md:col-span-2 bg-slate-900 rounded-2xl border border-slate-800 shadow-2xl overflow-hidden">
                        <div class="bg-slate-800/50 px-6 py-3 border-b border-slate-700">
                            <h3 class="text-sm font-bold text-slate-400 uppercase tracking-widest">실시간 시세 현황</h3>
                        </div>
                        <table class="w-full text-left">
                            <tbody>
                                <tr class="border-b border-slate-800/50">
                                    <td class="px-6 py-4 text-slate-500">현재가 (USD)</td>
                                    <td class="px-6 py-4 text-2xl font-mono font-bold text-white text-right">{display_usdt}</td>
                                </tr>
                                <tr>
                                    <td class="px-6 py-4 text-amber-500/70 font-bold text-lg text-right" colspan="2">
                                        <span class="text-sm text-slate-500 font-normal mr-4">원화 환산</span>
                                        {display_krw}
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <div class="bg-slate-900 p-6 rounded-2xl border border-slate-800 shadow-2xl flex flex-col justify-center">
                        <p class="text-slate-500 text-xs font-bold uppercase tracking-wider mb-3">최신 보안 뉴스</p>
                        <a href="{news_link}" target="_blank" class="text-lg font-semibold text-slate-200 hover:text-amber-400 transition leading-tight">{translated_title} 🔗</a>
                    </div>
                </div>

                <div class="bg-slate-900 rounded-3xl overflow-hidden border border-slate-800 shadow-2xl">
                    <div class="bg-slate-800/50 px-8 py-4 border-b border-slate-700 flex items-center"><span class="text-2xl mr-3">🧠</span><h2 class="text-xl font-bold text-white">AI 위협 및 심리 분석 지표</h2></div>
                    <div class="p-8 text-lg text-slate-300"><div class="bg-slate-950/50 p-6 rounded-xl border border-slate-800">{ai_result}</div></div>
                </div>
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)