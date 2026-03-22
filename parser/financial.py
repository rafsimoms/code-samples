import sys
import time
from bs4 import BeautifulSoup
import requests

def main():
    if len(sys.argv) != 3:
        raise ValueError("Неверное количество аргументов")

    ticker = sys.argv[1]
    field = sys.argv[2]

    url = f"https://finance.yahoo.com/quote/{ticker}/financials/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    session = requests.Session()
    session.headers.update(headers)
    r = session.get(url, timeout=10)
    if r.status_code != 200:
        raise ValueError("wrong ticker")

    soup = BeautifulSoup(r.text, "html.parser")
    rows = soup.find_all('div', class_=["row", "lv-0", "yf-t22klz"])
    ans = []

    cnt = 0
    flag = False
    for row in rows:
        if flag == True and cnt < 7:
            cnt += 1
            ans.append(row)
            continue
        elif flag == True and cnt >= 7:
            break
        title = row.find(title=f"{field}")
        if title:
            flag = True

    
    if len(ans) == 0:
        raise ValueError("wrong field of the table")
    time.sleep(5)
    res = []
    for row in ans:
        res.append(row.get_text(strip=True))
    print(tuple(res[1:]))

if __name__ == '__main__':
    main()
