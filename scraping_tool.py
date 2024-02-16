import datetime
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from util.logger import StreamAndFileLogger
from util.driver_support import find_element, find_elements
from util.spread_sheet_db import SpreadSheetDatabase

MAX_PAGE = 100
TODAY = datetime.datetime.now().strftime('%Y-%m-%d')

# Setup logger
logger = StreamAndFileLogger(
    log_file=f"./log/indeed_{TODAY}.log"
)

def main():

    logger.info("=== Process start ===")

    # Setup chrome driver
    options = Options()
    #options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    d = webdriver.Chrome(options=options)
    d.set_window_size('1200', '1000')

    # DB Access 
    logger.info("Get registered job id")
    ssdb = SpreadSheetDatabase()
    registered_job_ids = ssdb.get_registered_job_ids(datetime.datetime.now() - datetime.timedelta(days=1))
    

    # Link open
    d.get("https://secure.indeed.com/auth")

    job_type_list = [
        "正社員",
        "アルバイト",
        "派遣社員",
        "契約社員",
        "新卒",
        "業務委託",
        "請負",
        "嘱託社員",
        "インターン",
        "ボランティア",
    ]


    for job_type in job_type_list:
        page = 0
        while True:
            registered_cnt = 0

            d.get(f"https://jp.indeed.com/jobs?q={job_type}&start={page}&sort=date")

            elems = find_elements(d, By.CSS_SELECTOR, '#mosaic-provider-jobcards > ul > li')
            i = 0
            while i < len(elems):

                try:
                    elem = elems[i]

                    # 高さ0の項目はダミーなのでスキップ
                    if elem.rect["height"] == 0:
                        logger.info("Skip dummy job card")
                        i += 1
                        continue

                    data = [""] * 10

                    # registered_at
                    data[0] = TODAY
                    logger.debug("registered_atまで取得")
                    # job_id
                    try:
                        data[1] = find_element(elem, By.CLASS_NAME, "jcs-JobTitle").get_attribute("data-jk")
                    except Exception:
                        print("data[1]が見つからない")
                        time.sleep(600)
                        pass

                    logger.debug("job_idまで取得")
                    # 登録済みならスキップ
                    if data[1] in registered_job_ids:
                        logger.info("Skip registered job id")
                        registered_cnt += 1
                        i += 1
                        continue
                    else:
                        registered_job_ids.append(data[1])
                    

                    # job_title
                    data[2] = find_element(elem, By.CLASS_NAME, "jobTitle").text
                    logger.debug("job_titleまで取得")
                    # company_name
                    data[3] = find_element(elem, By.CSS_SELECTOR, "a[data-tn-element='companyName']").text#find_element(elem, By.CLASS_NAME, "companyName").text
                    logger.debug("company_nameまで取得")
                    # company_location
                    data[4] = "取得不能"#find_element(elem, By.CSS_SELECTOR, "div[data-testid='icon-location'] > div").text#",".join([find_element(elem, By.CLASS_NAME, "companyLocation").text])
                    logger.debug("company_locationまで取得")

                    url = None
                    try:
                        url = None #find_element(elem, By.CLASS_NAME, "more_loc").get_attribute("href")
                    except NoSuchElementException:
                        pass

                    if url is not None:
                        try:
                            d.execute_script(f"window.open('{url}')")
                            d.switch_to.window(d.window_handles[1])  # switch new tab

                            for more_loc in find_elements(d, By.CLASS_NAME, "companyLocation"):
                                if more_loc.text not in data[4]:
                                    data[4] = data[4] + f",{more_loc.text}"
                        except NoSuchElementException:
                            pass
                        finally:
                            d.close()
                            d.switch_to.window(d.window_handles[0])  # switch original tab
                            
                    # salary_snippet
                    salary_snippet = find_elements(elem, By.CLASS_NAME, "salary-snippet-container")
                    data[5] = None if len(salary_snippet) == 0 else salary_snippet[0].text

                    # job_type
                    job_type_a = find_elements(elem, By.CLASS_NAME, "metadata")
                    data[6] = None if len(job_type_a) == 0 else job_type_a[-1].text

                    # application_tag
                    data[7] = ",".join([x.text for x in find_elements(elem, By.CSS_SELECTOR, ".jobsearch-JobCard-tagContainer > span")])
                    print("application_tag取得")
                    # ssdb.insert_data(data)

                    # job_snippet
                    data[8] = "取得不可"#find_element(elem, By.CLASS_NAME, "job-snippet").text
                    print("job_snippet取得")
                    # ssdb.insert_data(data)

                    try:
                        url = f"https://jp.indeed.com/viewjob?jk={data[1]}"
                        d.execute_script(f"window.open('{url}')")
                        d.switch_to.window(d.window_handles[1])  # switch new tab

                        # job_tag
                        data[9] = ",".join([x.text.replace(",", "_") for x in find_elements(d, By.CLASS_NAME, "css-8fx8lh")])
                        print("job_tag取得")
                        # ssdb.insert_data(data)
                        logger.debug("job_tagまで取得")
                        ssdb.insert_data(data)
                    finally:
                        logger.debug("finallyを実行")
                        d.close()
                        d.switch_to.window(d.window_handles[0])  # switch original tab

                    logger.info(f"Register job id={data[1]} | {data[2]}")
                    # print("インサート！")
                    # ssdb.insert_data(data)

                except NoSuchElementException:
                    # ポップアップ閉じるための処理
                    # find_element(d, By.CLASS_NAME, "css-yi9ndv").click()
                    logger.info("Close popup")
                    continue
                except Exception as e:
                    logger.exception("Unkown error occured")
                    exit()

                i += 1
            
            page += 10

            if registered_cnt >= 15 or page > MAX_PAGE:
                break

    logger.info("=== Process completed ====")

if __name__ == "__main__":
    main()