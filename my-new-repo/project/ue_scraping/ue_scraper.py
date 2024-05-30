# Set up Environment
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import json
from lxml import html
from itertools import zip_longest
import pandas as pd
import time
import random
import re
import pytz
from datetime import datetime, date
import google.oauth2.credentials
import pandas_gbq

# Today
today = date.today()
print("today: ",today)

# Date + time
update_time = datetime.fromtimestamp(time.time())
print("current_time:",update_time)

# Start_time
start=time.perf_counter()

# Upload address.csv
df = pd.read_csv('/home/ubuntu/Documents/address_20240329.csv')

city = df['city'].tolist()
town = df['town'].tolist()
address = df['address'].tolist()

# Set up chromedriver
web_driver_path = '/usr/bin/chromedriver'

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('start-maximized')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--disable-browser-side-navigation')
chrome_options.add_argument('enable-automation')
chrome_options.add_argument('--disable-infobars')
chrome_options.add_argument('enable-features=NetworkServiceInProcess')

service = Service(web_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

with open('/home/ubuntu/Documents/mkt_1_cookie.json') as f:
    cookies = json.load(f)

# Begin to control Uber Eats browser
url = "https://www.ubereats.com/tw"
driver.get(url)
time.sleep(random.randint(5, 10))

# Add cookie.json into Uber Eats browser
# cookieStore.getAll().then(result => console.log(result))
# Be sure to remove all 'SameSite' in cookie.json. 
# reference: https://ithelp.ithome.com.tw/articles/10278362
# reference: https://stackoverflow.com/questions/62031865/selenium-message-invalid-argument-invalid-samesite

for cookie in cookies:
    driver.add_cookie(cookie)
driver.refresh()
time.sleep(random.randint(5, 10))

col_html_content = []
col_html_address = []

for i in address[0:10]: 
    #  --- 切換地址 ---
    try:
        #找到輸入地址的地方
        driver.find_element(By.XPATH,'//*[@id="wrapper"]/header/div/div/div/div/div/div[3]/div[1]/div[2]/a/div[1]').click() 
        time.sleep(2)
        #進入變更區域。
        driver.find_element(By.XPATH,'//*[@id="wrapper"]/div[3]/div/div/div[2]/div[3]/div/div[2]/div[1]/div[2]/a').click()
        time.sleep(2)
        #選取變更區域。
        getblock1 = driver.find_element(By.XPATH,'//*[@id="location-typeahead-location-manager-input"]')
        #輸入要變更的地址。
        getblock1.send_keys(i) 
        time.sleep(3)
        #按下Enter送出地址
        getblock1.send_keys('\ue007')
        time.sleep(3)
        print(i, "換地址成功","當前地址：",driver.find_element(By.XPATH,'//*[@id="wrapper"]/header/div/div/div/div/div/div[3]/div[1]/div[2]/a/div[1]').text)
        
        #  --- 展開更多店家 

        for click in range(1,12):
            try:
                driver.find_element(By.XPATH,'//*[@id="main-content"]/div/div[5]/div/div/button').click()
                time.sleep(2)
            except:
                pass
        print(i,"更多店家展開完成")
        time.sleep(3)
        
        #  --- 開始爬取整頁資料 ---

        html_content = driver.page_source
        col_html_content.append(html_content)
        col_html_address.append(i)
        print(i,"資料爬取完成")    

       # --- 單一地址資料抓取結束 ---     
    except:
        try:
            # 關閉搜尋視窗
            driver.find_element(By.XPATH,'//*[@id="wrapper"]/div[3]/div/div/div[2]/div[2]/button').click()
            driver.find_element(By.XPATH,'//*[@id="wrapper"]/div[3]/div/div/div[2]/div[2]/button').click()
            print(i,"找不到該地址","當前地址：",driver.find_element(By.XPATH,'//*[@id="wrapper"]/header/div/div/div/div/div/div[3]/div[1]/div[2]/a/div[1]').text)
        except:
            pass
        pass       
print("地址查詢完成")

# Retry if count of HTML less than expected numbers
retry = 1

if len(col_html_address) < 10 and retry <= 4:
    retry += 1
    time.sleep(random.uniform(10, 20)) # retry after few seconds
    from selenium.webdriver.common.by import By
    for i in address[0:10]: 
        #  --- 切換地址 ---
        try:
            #找到輸入地址的地方
            driver.find_element(By.XPATH,'//*[@id="wrapper"]/header/div/div/div/div/div/div[3]/div[1]/div[2]/a/div[1]').click() 
            time.sleep(2)
            #進入變更區域。
            driver.find_element(By.XPATH,'//*[@id="wrapper"]/div[3]/div/div/div[2]/div[3]/div/div[2]/div[1]/div[2]/a').click()
            time.sleep(2)
            #選取變更區域。
            getblock1 = driver.find_element(By.XPATH,'//*[@id="location-typeahead-location-manager-input"]')
            #輸入要變更的地址。
            getblock1.send_keys(i) 
            time.sleep(3)
            #按下Enter送出地址
            getblock1.send_keys('\ue007')
            time.sleep(3)
            print(i, "換地址成功","當前地址：",driver.find_element(By.XPATH,'//*[@id="wrapper"]/header/div/div/div/div/div/div[3]/div[1]/div[2]/a/div[1]').text)
            
            #  --- 展開更多店家 

            for click in range(1,12):
                try:
                    driver.find_element(By.XPATH,'//*[@id="main-content"]/div/div[5]/div/div/button').click()
                    time.sleep(2)
                except:
                    pass
            print(i,"更多店家展開完成")
            time.sleep(3)
            
            #  --- 開始爬取整頁資料 ---

            html_content = driver.page_source
            col_html_content.append(html_content)
            col_html_address.append(i)
            print(i,"資料爬取完成")    

        # --- 單一地址資料抓取結束 ---     
        except:
            try:
                # 關閉搜尋視窗
                driver.find_element(By.XPATH,'//*[@id="wrapper"]/div[3]/div/div/div[2]/div[2]/button').click()
                driver.find_element(By.XPATH,'//*[@id="wrapper"]/div[3]/div/div/div[2]/div[2]/button').click()
                print(i,"找不到該地址","當前地址：",driver.find_element(By.XPATH,'//*[@id="wrapper"]/header/div/div/div/div/div/div[3]/div[1]/div[2]/a/div[1]').text)
            except:
                pass
            pass       
    print("地址查詢完成")
else:
    pass

# Close the browser   
driver.quit()

# Get HTML data
scrape_time = [update_time] * len (col_html_content)
html_data= pd.DataFrame({'html_address':col_html_address,'html_content':col_html_content, 'scrape_time_utc': scrape_time})
print(html_data.head(5))

col_swimlane = []
col_vendor = []
col_delivery_fee = []
col_delivery_time = []
col_comment = []
col_address = []
col_city = []
col_town = []

# UE swimlane
# switch html
for a in range(10):
    try:
        tree = html.fromstring(col_html_content[a])
    # switch swimlane
        for k in range(1,40):
            try:
                xpath_swimlane = f'//*[@id="main-content"]/div/div[5]/div/div/div[2]/div[{k}]/div/section/div[1]/div[1]/div/div[1]/a/div'
                swimlane = tree.xpath(xpath_swimlane)
                for m in range(1,5):
                    try:
                        for l in range(1,5):
                            try:
                                xpath_vendor_name = f'//*[@id="main-content"]/div/div[5]/div/div/div[2]/div[{k}]/div/section/div[2]/ul[{m}]/li[{l}]/div/div/div/div[2]/div[1]/div[1]/div'
                                xpath_delivery_fee = f'//*[@id="main-content"]/div/div[5]/div/div/div[2]/div[{k}]/div/section/div[2]/ul[{m}]/li[{l}]/div/div/div/div[2]/div[2]/div[1]/span/div/span/span'
                                xpath_delivery_time = f'//*[@id="main-content"]/div/div[5]/div/div/div[2]/div[{k}]/div/section/div[2]/ul[{m}]/li[{l}]/div/div/div/div[2]/div[2]/div[2]/span[2]/div'
                                xpath_comment = f'//*[@id="main-content"]/div/div[5]/div/div/div[2]/div[{k}]/div/section/div[2]/ul[{m}]/li[{l}]/div/div/div/div[2]/div[1]/span'
                                vendor_name = tree.xpath(xpath_vendor_name)
                                delivery_fee = tree.xpath(xpath_delivery_fee)
                                delivery_time = tree.xpath(xpath_delivery_time)
                                comment = tree.xpath(xpath_comment)
                                for d,e,f,g,h in zip_longest(swimlane,vendor_name, delivery_fee, delivery_time, comment, fillvalue=None):
                                    if d is not None and e is not None and f is not None and g is not None and h is not None:
                                        col_swimlane.append(d.text_content())
                                        col_address.append(col_html_address[a])
                                        col_vendor.append(e.text_content())
                                        col_delivery_fee.append(f.text_content())
                                        col_delivery_time.append(g.text_content())
                                        col_comment.append(h.text_content())
                                    else:
                                        pass
                            except:
                                pass
                    except:
                        pass
            except: 
                pass
    except:
        pass
print("Complete Swimlane Scraping!")

# count of swimlane data
print("address", len(col_address),"swimlane", len(col_swimlane),"vendor_name", len(col_vendor),"delivery_fee",len(col_delivery_fee),"delivery_time",len(col_delivery_time),"commment",len(col_comment))

# UE nearby vendors
for a in range(10):
    try:
        tree = html.fromstring(col_html_content[a])
        for m in range(20,700):
            try: 
                xpath_vendor_name = f'//*[@id="main-content"]/div/div[5]/div/div/div[2]/div[{m}]/div/div/div/div/div[2]/div[1]/div/div'
                xpath_delivery_fee = f'//*[@id="main-content"]/div/div[5]/div/div/div[2]/div[{m}]/div/div/div/div/div[2]/div[2]/div[1]/span/div/span/span[1]'
                xpath_delivery_time = f'//*[@id="main-content"]/div/div[5]/div/div/div[2]/div[{m}]/div/div/div/div/div[2]/div[2]/div[2]/span[2]/div'
                xpath_comment = f'//*[@id="main-content"]/div/div[5]/div/div/div[2]/div[{m}]/div/div/div/div/div[2]/div[1]/span'
                vendor_name = tree.xpath(xpath_vendor_name)
                delivery_fee = tree.xpath(xpath_delivery_fee)
                delivery_time = tree.xpath(xpath_delivery_time)
                comment = tree.xpath(xpath_comment)
                for e,f,g,h in zip_longest(vendor_name, delivery_fee, delivery_time, comment, fillvalue=None):
                    if e is not None and f is not None and g is not None and h is not None:
                        col_swimlane.append("附近店家")
                        col_address.append(col_html_address[a])
                        col_vendor.append(e.text_content())
                        col_delivery_fee.append(f.text_content())
                        col_delivery_time.append(g.text_content())
                        col_comment.append(h.text_content()) 
                    else:
                        pass
            except:
                pass
    except:
        pass
print("Complete Nearby Vendors Scraping!")

# count of swimlane + nearby vendors data
print("address", len(col_address), "swimlane", len(col_swimlane), "vendor_name", len(col_vendor), "delivery_fee", len(col_delivery_fee), "delivery_time", len(col_delivery_time), "commment", len(col_comment))

# Create DataFrame
ue_data = pd.DataFrame({
    'address': col_address,
    'swimlane': col_swimlane,
    'vendor_name': col_vendor,
    'delivery_fee': col_delivery_fee,
    'delivery_time': col_delivery_time,
    'comment': col_comment
})
ue_data.fillna(0, inplace=True)
print(ue_data.head(5))

# Organize final dataframe
user = "0901352237"
user = [user] * len (col_delivery_fee)
update_time_utc = [update_time] * len (col_delivery_fee)
date = [today] * len (col_delivery_fee)

data= pd.DataFrame({'date_utc':date,
                    'update_time_utc':update_time_utc,
                    'address':col_address,
                    'swimlane':col_swimlane, 
                    'vendor_name':col_vendor, 
                    'delivery_fee':col_delivery_fee,
                    'delivery_time':col_delivery_time,
                    'comment':col_comment,'user':user})

result = pd.merge(data, df, on ='address', how = 'left')
result['user'] = result['user'].astype(str)


# Extracting values using lambda and apply functions
result = result.assign(
    df_value=result["delivery_fee"].apply(lambda x: float(x.split("TWD 費用")[0]) if isinstance(x, str) and "TWD 費用" in x else 0),
    dt_value=result["delivery_time"].apply(lambda x: int(x.split("–")[1].split()[0]) if isinstance(x, str) and "–" in x else 0),
    comment_score=result["comment"].apply(lambda x: float(x.split('獲得')[1].split('顆星')[0]) if isinstance(x, str) and '獲得' in x and '顆星' in x else 0),
    comment_count=pd.to_numeric(result["comment"].str.split("根據 ").str[1].str.split(" ").str[0], errors='coerce').fillna(0).astype('Int64')
)

result['rank'] = result.groupby("address").cumcount() + 1

# Reordering columns
result = result[['rank', 'user', 'date_utc', 'update_time_utc', 'city', 'town', 
                 'address', 'swimlane', 'vendor_name', 'delivery_fee', 'df_value', 
                 'delivery_time', 'dt_value', 'comment', 'comment_score', 'comment_count']]

print(result.head(5))
print(result.dtypes)

# 將 DataFrame 儲存成 CSV 檔案
# csv_file_path = str(update_time) + ".csv"
# result.to_csv(csv_file_path, index=False)  # index=False 表示不要儲存 DataFrame 的索引

print(f'DataFrame 已儲存成 CSV 檔案：{csv_file_path}')

# Upload dataframe to GCP
f = open('/home/ubuntu/Documents/gcp_user_account.json')
credential = json.load(f)

credentials = google.oauth2.credentials.Credentials(
    credential['token'],
    refresh_token=credential['refresh_token'],
    token_uri=credential['token_uri'],
    client_id=credential['client_id'],
    client_secret=credential['client_secret']
    )

pandas_gbq.context.credentials = credentials

project_id = "foodpanda-tw-bigquery"
table_id = 'md_office.aws_ue_df'

# Append table on GCP
pandas_gbq.to_gbq(result, 
                  destination_table = table_id, 
                  project_id = project_id, 
                  if_exists = 'append')

# Complete UE scraper
end=time.perf_counter()
print("執行時間: %f 秒" % (end-start))
