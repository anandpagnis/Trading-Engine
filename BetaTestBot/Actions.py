import pyautogui as pag
from PIL import Image
from pytesseract import pytesseract
import yfinance as yf

path = '/Users/anandp/Desktop/PythonFiles/TradingEngine/BetaTestBot/Assets'

def botpr(image):
    Cord = pag.locateCenterOnScreen(image ,confidence=0.8)
    pag.click(Cord.x/2,Cord.y/2)
    
def scrolltill(image):
    x=1
    while x==1:
        pag.scroll(-5)
        if(pag.locateCenterOnScreen(image ,confidence=0.8)):
            cod = pag.locateCenterOnScreen(image ,confidence=0.8)
            pag.click(cod.x/2,cod.y/2)
            x=0
        elif(pag.locateCenterOnScreen(f'{path}/EOP.png' ,confidence=0.8)):
            print("End of page reached")

def login():
    botpr(f'{path}/plus.png')
    pag.typewrite('Investopedia.com')
    pag.press('enter')
    pag.PAUSE = 3
    botpr(f'{path}/tradbut.png')
    pag.PAUSE = 3
    botpr(f'{path}/log.png')
    pag.PAUSE = 4
    pag.press('enter')

def exec_trade(ticker):
        pag.PAUSE = 2
        botpr(f'{path}/trade.png')
        pag.PAUSE = 2
        botpr(f'{path}/trade.png')
        pag.PAUSE = 2
        botpr(f'{path}/serch.png')
        pag.PAUSE=1
        pag.typewrite(ticker)
        pag.PAUSE=1
        pag.scroll(-2)
        pag.PAUSE=1
        pag.click()
        pag.PAUSE=1
        scrolltill(f'{path}/up.png')
        pag.click(clicks=9)
        scrolltill(f'{path}/preview.png')
        pag.PAUSE=1
        botpr(f'{path}/submit.png')
        
def sell_trade(ticker):
        pag.PAUSE = 1
        botpr(f'{path}/trade.png')
        pag.PAUSE = 1
        botpr(f'{path}/trade.png')
        pag.PAUSE = 1
        botpr(f'{path}/serch.png')
        pag.PAUSE=1
        pag.typewrite(ticker)
        pag.PAUSE=1
        pag.scroll(-2)
        pag.PAUSE=1
        pag.click()
        pag.PAUSE=1
        scrolltill(f'{path}/actionbut.png')
        pag.scroll(-1)
        pag.click()
        botpr(f'{path}/showmax.png')
        scrolltill(f'{path}/preview.png')
        pag.PAUSE=1
        botpr(f'{path}/submit.png')

        
def get_stock():
    ticker=input("Enter a ticker name")
    ch=input("do u want historical data? y or n")
    if(ch=='y'):
        st=input("Enter start date(YYYY-MM-DD): ")
        et=input("Enter end date(YYYY-MM-DD): ")
        df = yf.download(tickers=ticker,start=st,end=et,interval="1d")
        df.index = df.index.tz_localize(None)

        df.to_excel('stonks.xlsx')
    else:
        print("Time interval: 1m = <=7d, 5m = <=60d")
        per=input("Enter Time period(1d,2d,2m,3m,etc): ")
        invl=input("Enter Time interval (1m,5m,10,15m,1d,etc): ")
        df = yf.download(tickers=ticker,period=per,interval=invl)
        df.index = df.index.tz_localize(None)

        df.to_excel('stonks.xlsx')
        
def auto_get_stock(ticker_name):
    df = yf.download(tickers=ticker_name,period='5d',interval='1m')
    df.index = df.index.tz_localize(None)
    df.to_excel('stonks.xlsx')
    
    