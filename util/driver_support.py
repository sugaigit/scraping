from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from typing import List, Optional
from selenium.webdriver.remote.webelement import WebElement 
from selenium.webdriver.support import expected_conditions as EC
import time

def find_element(driver, by=By.ID, value: Optional[str] = None, check_clickable: bool=False, timeout: int = 0, sleep_sec: int = 0.1) -> WebElement:
    if timeout == 0:
        element =  driver.find_element(by, value)
    else:
        if check_clickable:
            element = WebDriverWait(driver, timeout=timeout).until(EC.element_to_be_clickable((by, value)))
        else:
            element = WebDriverWait(driver, timeout=timeout).until(EC.presence_of_element_located((by, value)))
    time.sleep(sleep_sec)
    return element

def find_elements(driver, by=By.ID, value: Optional[str] = None, timeout: int = 0, sleep_sec: int = 0.1) -> List[WebElement]:
    if timeout == 0:
        elements = driver.find_elements(by, value)
    else:
        elements = WebDriverWait(driver, timeout=timeout).until(lambda d: d.find_elements(by, value))
    time.sleep(sleep_sec)
    return elements