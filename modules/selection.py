"""
modules/selection.py – Train & Seat Selection
"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException,NoSuchElementException

from config.config import JOURNEY,AUTOMATION # config values (train preference,retry settings)
from utils.browser import wait_for_element,wait_clickable,safe_click # helper browser utilities
from utils.logger import logger # logging system


def wait_for_results(driver)->bool:
 try:
  WebDriverWait(driver,30).until(
   EC.presence_of_element_located((By.XPATH,"//div[contains(@class,'tbis-div')]"))
  )  # wait until train cards appear
  logger.info("Train results loaded")
  return True
 except TimeoutException:
  logger.error("Train results did not load")
  return False


def get_available_trains(driver)->list[dict]:
 trains=[]
 try:
  rows=driver.find_elements(By.XPATH,"//div[contains(@class,'tbis-div')]")  # train result cards
  for row in rows:
   try:
    name=row.find_element(By.XPATH,".//div[contains(@class,'train-heading')]//strong").text.strip()  # train name
    number=name.split("(")[-1].replace(")","")  # extract train number
    depart=row.find_element(By.XPATH,".//div[contains(@class,'depart')]//strong").text.strip()  # departure time
    arrive=row.find_element(By.XPATH,".//div[contains(@class,'arrive')]//strong").text.strip()  # arrival time
    avail=row.find_element(By.XPATH,".//span[contains(text(),'AVL') or contains(text(),'AVAILABLE') or contains(text(),'RAC')]").text.strip()  # seat status

    trains.append({"number":number,"name":name,"depart":depart,"arrive":arrive,"availability":avail,"element":row})

   except NoSuchElementException:
    continue

  logger.info(f"Found {len(trains)} trains")

 except Exception as e:
  logger.error(f"Error scraping trains: {e}")

 return trains


def choose_train(trains:list[dict])->dict|None:
 preferred=JOURNEY.get("preferred_trains",[]) # preferred train list from config

 if preferred:
  for t in trains:
   if t["number"] in preferred:
    logger.info(f"Preferred train found {t['number']}")
    return t

 for t in trains:
  status=t.get("availability","").upper() # normalize availability text
  if any(x in status for x in ["AVAILABLE","AVL","RAC"]): # check seat availability keywords
   logger.info(f"Selecting train {t['number']}")
   return t

 logger.warning("No train available")
 return None


def click_book_now(driver,train:dict)->bool:
 try:
  book_btn=train["element"].find_element(By.XPATH,".//button[contains(@class,'train_Search')]") # locate book button inside train card
  driver.execute_script("arguments[0].scrollIntoView(true);",book_btn) # scroll to make button visible
  safe_click(driver,book_btn) # safe click wrapper to avoid Selenium click issues
  logger.info(f"Book Now clicked {train['number']}")
  time.sleep(2) # wait for next page load
  return True
 except Exception as e:
  logger.error(f"Book Now failed {e}")
  return False


def select_class_on_results(driver)->bool:
 try:
  class_tab=WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,f"//strong[contains(text(),'{JOURNEY['travel_class']}')]"))) # class tab like SL,3A,2A
  safe_click(driver,class_tab)
  time.sleep(1) # wait for seat availability update
  return True
 except TimeoutException:
  return True # not required in some layouts


def select_train(driver)->bool:
 logger.info("─── Starting Train Selection ───")
 if not wait_for_results(driver): # ensure results loaded
  return False

 for attempt in range(AUTOMATION["max_retries"]): # retry loop for seat availability
  trains=get_available_trains(driver) # scrape trains
  train=choose_train(trains) # choose best train

  if train:
   select_class_on_results(driver) # ensure correct class selected
   return click_book_now(driver,train) # click book button

  if AUTOMATION["auto_retry"]:
   logger.info(f"Retry {attempt+1}/{AUTOMATION['max_retries']} – seats unavailable, refreshing…")
   driver.refresh() # reload page to check again
   time.sleep(AUTOMATION["retry_interval"]) # wait before next retry
  else:
   break

 logger.error("No suitable train found after retries.")
 return False