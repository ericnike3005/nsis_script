import feedparser
from google import genai
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import ccxt
import requests

app = FastAPI()

# 1. AI 설정 (사용자님의 키 적용)
client = genai.Client(api_key="AIzaSyBXNeUTagryt1qCVpw0Ulg4w9Hxfdm6khU")

def get_exchange_rate():
    """실시간 USD/KRW 환율 수집"""
    try:
        url = "https://open.er-api.com/v6/latest/USD"
        response = requests.get(url)
        data = response.json()
        return data['rates']['KRW']
    except:
        return 1400.0

@app.get("/check/{symbol}", response_class=HTMLResponse)
async def check_market(symbol: str):
    # (1) 데이터 수집
    try:
        exchange = ccxt.binance()
        ticker = exchange.fetch_ticker(f"{symbol.upper()}/USDT")
        price_usdt = ticker['last']
        
        krw_rate = get_exchange_rate()
        price_krw = price_usdt * krw_rate
        
        display_usdt = f"{price_usdt:,.2f} USDT"
        display_krw = f"{int(price_krw):,} 원"
        display_rate = f"현재 환율: 1$ = {krw_rate:,.1f}원"
    except:
        display_usdt, display_krw, display_rate = "조회 실패", "-", "환율 정보 없음"

    feed = feedparser.parse("https://cointelegraph.com/rss/tag/security")
    news_title = feed.entries[0].title if feed.entries else "뉴스 없음"
    news_link = feed.entries[0].link if feed.entries else "#"

    # (2) AI 분석
    try:
        prompt = f"뉴스: {news_title}\n이게 {symbol} 가격에 위험한가요? 리스크 점수(1~10)와 짧은 분석을 줄바꿈해서 출력해줘."
        response = client.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt)
        ai_result = response.text.replace("\n", "<br>")
    except:
        ai_result = "AI 분석 한도 초과 (잠시 후 다시 시도)"

    # (3) HTML (통합 테이블 레이아웃)
    html_content = f"""
    <html>
        <head>
            <title>{symbol.upper()} 통합 리포트</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <script>
                let timeLeft = 30;
                function startTimer() {{
                    const timerElement = document.getElementById('timer');
                    const countdown = setInterval(() => {{
                        timeLeft -= 1;
                        timerElement.innerText = timeLeft + "s";
                        if (timeLeft <= 0) {{
                            clearInterval(countdown);
                            location.reload();
                        }}
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
                        <table class="w-full text-left border-collapse">
                            <tbody>
                                <tr class="border-b border-slate-800/50">
                                    <td class="px-6 py-4 text-slate-500 font-medium">현재가 (USD)</td>
                                    <td class="px-6 py-4 text-2xl font-mono font-bold text-white text-right">{display_usdt}</td>
                                </tr>
                                <tr>
                                    <td class="px-6 py-4 text-amber-500/70 font-medium font-bold text-lg">환산가 (KRW)</td>
                                    <td class="px-6 py-4 text-3xl font-mono font-bold text-amber-500 text-right">{display_krw}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <div class="bg-slate-900 p-6 rounded-2xl border border-slate-800 shadow-2xl flex flex-col justify-center">
                        <p class="text-slate-500 text-xs font-bold uppercase tracking-wider mb-3">최신 보안 뉴스</p>
                        <a href="{news_link}" target="_blank" class="text-lg font-semibold text-slate-200 hover:text-amber-400 transition leading-tight">
                            {news_title} <span class="text-slate-600">🔗</span>
                        </a>
                    </div>
                </div>

                <div class="bg-slate-900 rounded-3xl overflow-hidden border border-slate-800 shadow-2xl">
                    <div class="bg-slate-800/50 px-8 py-4 border-b border-slate-700 flex items-center">
                        <span class="text-2xl mr-3">🧠</span>
                        <h2 class="text-xl font-bold text-white">AI 위협 및 심리 분석 지표</h2>
                    </div>
                    <div class="p-8 leading-relaxed text-lg text-slate-300">
                        <div class="bg-slate-950/50 p-6 rounded-xl border border-slate-800">
                            {ai_result}
                        </div>
                    </div>
                </div>
                
                <footer class="mt-12 text-center text-slate-600 text-xs italic">
                    실시간 자동 모니터링 시스템 작동 중 | 30초 간격 갱신
                </footer>
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)