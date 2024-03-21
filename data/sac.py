import requests
import csv
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

url = "https://www.sac.or.kr/site/main/program/getProgramCalList"
headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Cookie": "JSESSIONID=Ui3eAQv89YPqgGtDR1BUmPmzC0B2K11bob1KXwWm2mdR2VVZnR0yW2yQfQwQr965.amV1c19kb21haW4vc2FjXzQ=; NCPVPCLBTG=81d6b0a941e609d20ebb4d699f4a21faca71f336c8fe33c8c0713772b71077a6; _fwb=2005h34cJBHwnHaDIomvmG6.1710230459036; cacheForm=%7B%22cal_top_year%22%3A2024%2C%22cal_top_month%22%3A3%2C%22gubunTab%22%3A%22%EC%9D%8C%EC%95%85%EB%8B%B9%22%7D; wcs_bt=1c898909a1bc7d0:1710230464",
    "Host": "www.sac.or.kr",
    "Origin": "https://www.sac.or.kr",
    "Referer": "https://www.sac.or.kr/site/main/program/schedule?tab=1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"'
}

concert_hall_performances = []

# 프로그램 실행 날짜를 기준으로 12개월 데이터 수집
now = datetime.now()
for i in range(12):
    target_date = now + timedelta(days=30 * i)
    data = {
        "searchYear": str(target_date.year),
        "searchMonth": str(target_date.month),
        "searchFirstDay": "1",
        "searchLastDay": "31",
        "CATEGORY_PRIMARY": "2"
    }

    response = requests.post(url, data=data, headers=headers)
    json_data = response.json()

    for key in json_data.keys():
        if isinstance(key, str) and key.isdigit():
            for performance in json_data[key]:
                if performance["PLACE_NAME"] == "콘서트홀":
                    date = datetime.strptime(performance["BEGIN_DATE"], "%Y.%m.%d")
                    if date.date() >= now.date():
                        name = performance["PROGRAM_SUBJECT"]
                        sn = performance["SN"]
                        price = performance.get("PRICE_INFO", "가격 정보 없음")  # 가격 정보가 없는 경우 기본값 설정
                        ticket_open_date = performance.get("TICKET_OPEN_DATE", "예매 일정 없음")
                        link = f"https://www.sac.or.kr/site/main/show/show_view?SN={sn}"

                        concert_hall_performances.append({
                            "name": name,
                            "date": date.strftime("%Y-%m-%d"),
                            "link": link,
                            "price": price,
                            "ticket_open_date": ticket_open_date
                    })

# Visit each link and extract additional information
for performance in concert_hall_performances:
    link = performance["link"]

    # Send a GET request to the link
    response = requests.get(link)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the ul element with class "cwa-tab"
    cwa_tab = soup.find("ul", class_="cwa-tab")

    if cwa_tab:
        # Find all the li elements within the "cwa-tab"
        li_elements = cwa_tab.find_all("li")

        if len(li_elements) > 0:
            # Check the content of each li element
            for index, li in enumerate(li_elements):
                if "작품소개" in li.get_text():
                    # Find the corresponding "ctl-sub" div based on the index
                    ctl_sub = soup.select(f".cwa-tab-list .ctl-sub:nth-of-type({index + 1})")

                    if ctl_sub:
                        # Extract all the displayed text from the corresponding "ctl-sub" div
                        additional_info = ctl_sub[0].get_text(strip=True, separator="\n")

                        # Replace newline characters with <br> tags
                        #additional_info = additional_info.replace("\n", "<br>")

                        performance["additional_info"] = additional_info
                        break
            else:
                performance["additional_info"] = "작품소개 not found"
        else:
            performance["additional_info"] = "No li elements found"
    else:
        performance["additional_info"] = "cwa-tab not found"

# 날짜순으로 정렬하기 위해 'date' 필드를 기준으로 concert_hall_performances 리스트를 정렬합니다.
concert_hall_performances.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'), reverse=False)

# CSV 파일로 저장
with open("sac.csv", "w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=["name", "date", "link", "price", "ticket_open_date", "additional_info"], quoting=csv.QUOTE_ALL)
    writer.writeheader()
    writer.writerows(concert_hall_performances)

print("결과가 sac.csv 파일로 저장되었습니다.")