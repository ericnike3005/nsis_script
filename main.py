from fastapi import FastAPI
from fastapi.responses import FileResponse # 👈 파일을 던져주기 위한 도구 추가
import yfinance as yf
import uvicorn

app = FastAPI()

# 1. 사용자가 처음 접속하면, 아까 만든 'index.html' 파일을 던져줍니다!
@app.get("/")
def show_dashboard():
    return FileResponse("index.html")

# 2. 버튼을 눌렀을 때 데이터를 처리하는 뒷문 로직입니다.
@app.get("/dividend/{ticker}")
def show_dividends(ticker: str):
    stock = yf.Ticker(ticker)
    
    # 배당금 정리
    dividends = stock.dividends.tail().to_dict()
    clean_dividends = {str(date): amount for date, amount in dividends.items()}

    # 현재 주가 가져오기
    try:
        current_price = stock.fast_info['last_price']
    except:
        current_price = 0
        
    # 최신 뉴스 3개 훔쳐오기 (옵션 2 기능)
    try:
        raw_news = stock.news[:3]
        news_list = [{"title": n['title'], "link": n['link'], "publisher": n['publisher']} for n in raw_news]
    except:
        news_list = []
    
    # 3. HTML 파일 쪽으로 배당금, 주가, 뉴스를 한 번에 포장해서 던져줍니다.
    return {
        "ticker": ticker.upper(),
        "current_price": current_price,
        "data": clean_dividends,
        "news": news_list
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)