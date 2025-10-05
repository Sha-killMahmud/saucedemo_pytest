import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

pause = 1
@pytest.fixture(scope="session")
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    driver.get("https://www.saucedemo.com/")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "user-name")))
    login(driver, "standard_user", "secret_sauce")
    yield driver
    driver.quit()

def sleep():
    time.sleep(pause)

def login(driver, username, password):
    driver.find_element(By.ID, "user-name").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "login-button").click()
    sleep()

def add_to_cart(driver, product_name):
    products = driver.find_elements(By.CLASS_NAME, "inventory_item")
    for product in products:
        name = product.find_element(By.CLASS_NAME, "inventory_item_name").text
        if name == product_name:
            product.find_element(By.TAG_NAME, "button").click()
            break
    sleep()

def remove_from_cart(driver, product_name):
    products = driver.find_elements(By.CLASS_NAME, "inventory_item")
    for product in products:
        name = product.find_element(By.CLASS_NAME, "inventory_item_name").text
        if name == product_name:
            product.find_element(By.TAG_NAME, "button").click()
            break
    sleep()

def go_to_cart(driver):
    driver.find_element(By.ID, "shopping_cart_container").click()
    sleep()

def checkout(driver, first_name, last_name, postal_code):
    driver.find_element(By.ID, "checkout").click()
    driver.find_element(By.ID, "first-name").send_keys(first_name)
    driver.find_element(By.ID, "last-name").send_keys(last_name)
    driver.find_element(By.ID, "postal-code").send_keys(postal_code)
    driver.find_element(By.ID, "continue").click()
    sleep()

def get_cart_items(driver):
    go_to_cart(driver)
    items = driver.find_elements(By.CLASS_NAME, "cart_item")
    result = []
    for item in items:
        name = item.find_element(By.CLASS_NAME, "inventory_item_name").text
        price = item.find_element(By.CLASS_NAME, "inventory_item_price").text
        qty = item.find_element(By.CLASS_NAME, "cart_quantity").text
        desc = item.find_element(By.CLASS_NAME, "inventory_item_desc").text
        result.append({'name' :name, 'price' :price, 'qty' : qty, 'desc' : desc})
    sleep()
    return result


@pytest.mark.order(1)
def test_order_confirmation(setup_driver):
    driver = setup_driver
    add_to_cart(driver, "Sauce Labs Bike Light")
    go_to_cart(driver)
    checkout(driver, "Shakil", "Mahmud", "1205")
    driver.find_element(By.ID, "finish").click()
    confirmation_text = driver.find_element(By.CLASS_NAME, "complete-header").text
    assert "Thank you" in confirmation_text
    sleep()

@pytest.mark.order(2)
def test_order_cancel(setup_driver):
    driver = setup_driver
    add_to_cart(driver, "Sauce Labs Bike Light")
    go_to_cart(driver)
    checkout(driver, "Shakil", "Mahmud", "1205")
    driver.find_element(By.ID, "cancel").click()
    homepage = "https://www.saucedemo.com/inventory.html"
    assert homepage in driver.current_url
    sleep()

@pytest.mark.order(3)
def test_checkout_details_verification(setup_driver):
    driver = setup_driver
    products_to_add = ['Sauce Labs Bike Light' , 'Sauce Labs Bolt T-Shirt']
    for product in products_to_add:
        add_to_cart(driver, product)

    go_to_cart(driver)
    checkout(driver, "Shakil", "Mahmud", "1205")
    items = get_cart_items(driver)
    actual_names = [item['name'] for item in items]
    for expected in products_to_add:
        assert expected in actual_names, f'Expected {expected} in cart but not found!'
    sleep()
