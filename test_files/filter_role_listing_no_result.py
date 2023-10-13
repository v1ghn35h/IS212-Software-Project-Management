import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


driver = webdriver.Chrome()
driver.maximize_window()

# Login first
driver.get("http://localhost:8080")

# Enter staff id
staff_id = driver.find_element(By.ID, "staffId")
staff_id.clear()
staff_id.send_keys(1)

# Enter password
password = driver.find_element(By.ID, "password")
password.clear()
password.send_keys("john")

# Click login button
driver.find_element(By.ID, "login").click()

# Go to role listing page
text = driver.find_element(By.ID, "role_listings").click()

# Wait for 3 seconds (for the page to load)
time.sleep(3)

# Click the filters
search_bar = driver.find_element(By.ID, "category_Finance").click()
search_bar = driver.find_element(By.ID, "department_Finance").click()
search_bar = driver.find_element(By.ID, "0-20").click()

# Click apply filter button
driver.find_element(By.ID, "apply_filter_btn").click()

# Wait for 3 seconds (for the page to load)
time.sleep(3)

# Get the first role listing name
text = driver.find_element(By.ID, "filter_alert").text

# Check if role listing has the word software in it
assert "No role listings found based on your input filters" in text

print("TEST PASSED : FILTER ROLE LISTING STAFF NO RESULT")

print("Application title ", driver.title)
print("Application url is ", driver.current_url)
driver.quit()