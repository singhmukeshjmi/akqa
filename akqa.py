import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
import os

# Function to initialize WebDriver
def start_driver():
    """
    Sets up and starts a Microsoft Edge WebDriver with specific settings.
    This function makes the Edge browser open in full-screen mode and uses
    the correct driver, which is managed by EdgeChromiumDriverManager.
    :return: A WebDriver instance
    """
    # Ignore below commented code it works with ubuntu edge
    # options = webdriver.EdgeOptions()
    # options.add_argument("--start-maximized")  # Open browser in full screen
    # service = EdgeService(EdgeChromiumDriverManager().install())
    # driver = webdriver.Edge(service=service, options=options)
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  # Open browser in full screen
    driver = webdriver.Chrome(options=options)
    return driver


def goto_url(driver, url = "https://www.booking.com/flights/index.en-gb.html", timeout=10) -> dict:
    """
    This function opens the specified URL in a browser using the given WebDriver,
    and waits for a specific element to be visible on the page.
    :param driver: The Selenium WebDriver instance used to interact with the browser.
    :param url: The URL to navigate to (defaults to Booking.com flights page).
    :param timeout: The maximum time (in seconds) to wait for the element to be visible (defaults to 10 seconds).
    :return: True if the element is found and visible, False otherwise.
    """
    wait = WebDriverWait(driver, timeout=timeout)
    result = {}
    driver.get(url)
    print(f"{url} opened")
    try:
        element = wait.until(EC.visibility_of_element_located((By.XPATH, "//button[@data-ui-name='input_location_from_segment_0']")))
        print(f"{element} is found successfully")
        result['result'] = True
        return result
    except:
        error = "'Flying from' element not encountered even after polling for 10 seconds"
        result['result'] = False
        return result

def fill_airport_city(driver, xpath_parent, city_code) -> dict:
    """
    This function inputs the airports in the input boxes
    """
    wait = WebDriverWait(driver, timeout=10)
    result = {}
    try:
        from_field = driver.find_element(By.XPATH, xpath_parent)
        from_field.click()
        wait.until(lambda driver: from_field.get_attribute('aria-expanded') == 'true')
        # after aria-expanded true
        if from_field.get_attribute('aria-expanded') == 'true':
            combo_box_from_id = from_field.get_attribute('aria-describedby')
            combo_box_from = driver.find_element(By.XPATH, f'//div[@id="{combo_box_from_id}"]')
            combo_box_from_input = combo_box_from.find_element(By.TAG_NAME, 'input')
            combo_box_from_input.send_keys(city_code)
            xpath = '//ul[@id="flights-searchbox_suggestions"]/li'
            try:
                wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
            except Exception as e:
                error = "No options found for given city code"
                result['error'] = error
                result['result'] = False
                return result
            suggestions = combo_box_from.find_elements(By.XPATH, xpath)
            for i in suggestions:
                if city_code in i.text:
                    i.click()
                    break
        result['result'] = True
        return result
    except Exception as e:
        error = f"Caught Exception - {e}"
        result['error'] = error
        result['result'] = False
        return result


def fill_travellers(driver, adults = 1):
    """
    This function is static as of now
    """
    wait = WebDriverWait(driver, timeout=10)
    # Click count of travellers picker
    xpath = "//button[@data-ui-name='button_occupancy']"
    travellers = driver.find_element(By.XPATH, xpath)
    travellers.click()
    wait.until(lambda driver: travellers.get_attribute('aria-expanded') == 'true')
    traveller_node = travellers.get_attribute('aria-describedby')
    combo_box_traveller = driver.find_element(By.XPATH, f'//div[@id="{traveller_node}"]')
    travellers_count = combo_box_traveller.find_elements(By.XPATH, f'//input[@type="range"]')
    adults_minus = travellers_count[0].find_element(By.XPATH, "//button[@data-ui-name='button_occupancy_adults_minus']")
    adults_plus = travellers_count[0].find_element(By.XPATH, "//button[@data-ui-name='button_occupancy_adults_plus']")
    done_button = combo_box_traveller.find_element(By.XPATH, f'//button[@data-ui-name="button_occupancy_action_bar_done"]')
    done_button.click()
    wait.until(lambda driver: travellers.get_attribute('aria-expanded') == 'false')


def wait_for_visible_elements(driver, xpath, min_count):
    # Find the elements matching the XPath
    elements = driver.find_elements(By.XPATH, xpath)

    # Filter the elements to ensure they are visible
    visible_elements = [element for element in elements if element.is_displayed()]

    # Check if the number of visible elements meets the minimum required count
    return len(visible_elements) >= min_count

# Function to search flights
def search_flights(driver, departure = "DEL", destination = "BOM", date_string = None):
    wait = WebDriverWait(driver, timeout=15)
    if not date_string:
        travel_date = datetime.today().date()
        date_string = datetime.strftime(travel_date, '%Y-%m-%d')
    else:
        travel_date = datetime.strptime(date_string, '%Y-%m-%d')
        if travel_date.date() < datetime.today().date():
            error = "Sorry you are trying a past date"
            return {'Success': False, 'error':error}

    open_url = goto_url(driver)
    assert open_url['result'], f"Failed to goto given url, error - {open_url['error']}"
    oneway_checkbox = driver.find_element(By.XPATH, '//input[@value="ONEWAY"]')
    if not oneway_checkbox.is_selected():
        oneway_checkbox.click()
    assert oneway_checkbox.is_selected(), "ONEWAY checkbox is not selected"
    print("ONEWAY is selected")

    # Click "From" and enter departure city
    flying_from_xpath = "//button[@data-ui-name='input_location_from_segment_0']"
    from_filled = fill_airport_city(driver, xpath_parent=flying_from_xpath, city_code=departure)
    assert from_filled['result'], f"Failed to fill flying from city, error - {from_filled['error']}"

    # Click "Flying To" and enter destination city
    flying_to_xpath = "//button[@data-ui-name='input_location_to_segment_0']"
    filled_to = fill_airport_city(driver, xpath_parent=flying_to_xpath, city_code=destination)
    assert filled_to['result'], f"Failed to fill flying to city, error - {filled_to['error']}"


    # Click date picker
    xpath = "//button[@data-ui-name='button_date_segment_0']"
    date_picker = driver.find_element(By.XPATH, xpath)
    date_picker.click()
    wait.until(lambda driver: date_picker.get_attribute('aria-expanded') == 'true')
    date_node = date_picker.get_attribute('aria-describedby')
    date_node_body = driver.find_element(By.XPATH, f'//div[@id="{date_node}"]')
    calender_body = date_node_body.find_element(By.XPATH, '//div[@data-ui-name="calendar_body"]')
    buttons = calender_body.find_elements(By.TAG_NAME, 'button')
    months = calender_body.find_elements(By.XPATH, "//div[@class='Calendar-module__monthWrapper___0cg7E']")
    months_list_str = [i.find_element(By.TAG_NAME, 'h3').text for i in months]
    months_list_datetime = [datetime.strptime(i, '%B %Y').month for i in months_list_str]
    if travel_date.month not in months_list_datetime:
        if travel_date.month < min(months_list_datetime):
            buttons[0].click()
        else:
            buttons[1].click()
        buttons = calender_body.find_elements(By.TAG_NAME, 'button')
        months = calender_body.find_elements(By.XPATH, "//div[@class='Calendar-module__monthWrapper___0cg7E']")
        calender_body = date_node_body.find_element(By.XPATH, '//div[@data-ui-name="calendar_body"]')
    date_integer_element = calender_body.find_element(By.XPATH, f"//span[@data-date='{date_string}']")
    date_integer_element.click()
    wait.until(lambda driver: date_picker.get_attribute('aria-expanded') == 'false')

    fill_travellers(driver)

    # Click Search
    search_button = driver.find_element(By.XPATH, "//button[@data-ui-name='button_search_submit']")
    search_button.click()

    result = {}
    # Verify results
    try:
        wait.until(EC.visibility_of_element_located((By.XPATH, "//div[starts-with(@id,'flight-card-')]")))
        time.sleep(2)
        flight_results = driver.find_elements(By.XPATH, "//div[starts-with(@id,'flight-card-')]")
        print(f"count of flights found - {len(flight_results)}")
        os.makedirs("screenshots", exist_ok=True)
        result = []
        for i in range(len(flight_results)):
            price = driver.find_element(By.XPATH, f"//div[starts-with(@id,'flight-card-{i}')]//descendant::div[@data-testid='flight_card_price_main_price']").text
            carrier = driver.find_elements(By.XPATH, "//div[contains(@class,'jtOMN')]")[i].text
            assert wait.until(lambda driver: len(driver.find_elements(By.XPATH, "//div[contains(@class,'VsqoD')]"))>=(2*i))
            departure_time = driver.find_elements(By.XPATH, "//div[contains(@class,'VsqoD')]")[2*i].text
            destination_time = driver.find_elements(By.XPATH, "//div[contains(@class,'VsqoD')]")[2*i + 1].text

            departure_city_date = driver.find_elements(By.XPATH, "//div[contains(@class,'wZzxo styles')]")[2*i].text
            destination_city_date = driver.find_elements(By.XPATH, "//div[contains(@class,'wZzxo styles')]")[2*i + 1].text
            departure_airport = departure_city_date.split('·')[0].strip(' ')
            destination_airport = destination_city_date.split('·')[0].strip(' ')
            departure_date = departure_city_date.split('·')[1].strip(' ')
            destination_date = destination_city_date.split('·')[1].strip(' ')
            stops = driver.find_elements(By.XPATH, "//div[contains(@class,'OMHYW')]")[i].text
            duration = driver.find_elements(By.XPATH, "//div[contains(@class,'e8JzK')]")[i].text
            result.append({'price':price, 'carrier':carrier, 'departure_time':departure_time, 'destination_time':destination_time, 'departure_airport':departure_airport,
                    'destination_airport':destination_airport, 'departure_date':departure_date, 'destination_date':destination_date, 'stops':stops, 'duration':duration})
            # Also capturing screenshots for further reference
            flight_results[i].screenshot(f'screenshots/flight_card_{i}.jpg')
            print(f"Screenshot saved at - screenshots/flight_card_{i}.jpg")
            # Ignore below code - it works with ubuntu edge browser
            # carrier = driver.find_element(By.XPATH, f"//div[starts-with(@id,'flight-card-{i}')]//descendant::div[@data-testid='flight_card_carrier_0']").text
            # departure_time = driver.find_element(By.XPATH, f"//div[starts-with(@id,'flight-card-{i}')]//descendant::div[@data-testid='flight_card_segment_departure_time_0']").text
            # destination_time = driver.find_element(By.XPATH, f"//div[starts-with(@id,'flight-card-{i}')]//descendant::div[@data-testid='flight_card_segment_destination_time_0']").text
            # departure_airport = driver.find_element(By.XPATH, f"//div[starts-with(@id,'flight-card-{i}')]//descendant::div[@data-testid='flight_card_segment_departure_airport_0']").text
            # destination_airport = driver.find_element(By.XPATH, f"//div[starts-with(@id,'flight-card-{i}')]//descendant::div[@data-testid='flight_card_segment_destination_airport_0']").text
            # departure_date = driver.find_element(By.XPATH, f"//div[starts-with(@id,'flight-card-{i}')]//descendant::div[@data-testid='flight_card_segment_departure_date_0']").text
            # destination_date = driver.find_element(By.XPATH, f"//div[starts-with(@id,'flight-card-{i}')]//descendant::div[@data-testid='flight_card_segment_destination_date_0']").text
            # stops = driver.find_element(By.XPATH, f"//div[starts-with(@id,'flight-card-{i}')]//descendant::span[@data-testid='flight_card_segment_stops_0']").text
            # # Direct, 1 stop
            # duration = driver.find_element(By.XPATH, f"//div[starts-with(@id,'flight-card-{i}')]//descendant::div[@data-testid='flight_card_segment_duration_0']").text
            # result.append({'price':price})
        driver.quit()
        print("driver closed")
        return {'Success': True, 'result':result}

        # Ignore below comments this would be used to handle refresh dialog box
        # xpath = "//div[@role='dialog']"
        # xpath = "//button/span[text()='Refresh']"
    except:
        error = f"No flights found for {departure} to {destination} on {travel_date}"
        driver.quit()
        print("driver closed")
        return {'error' : error, 'Success' : False}

def test_flakyness(iterations = 5):
    for i in range(iterations):
        driver = start_driver()
        result = search_flights(driver)
        if not result['Success']:
            print(f"Flakyness test failed in {i+1}th iteration")


# Main execution
if __name__ == "__main__":
    print("Starting the webdriver")
    driver = start_driver()
    assert driver, "WEBDRIVER is not started"
    print("webdriver started successfully")
    result = search_flights(driver)

    # Test Case 1: Search valid flights (DEL to BOM, Today)
    # result = search_flights(driver, "Delhi", "Mumbai", "2025-03-05")

    # Test Case 2: Invalid Input
    # result = search_flights(driver, "XYZ", "Mumbai", "2025-03-06")

    # Test Case 3: No Flights Available
    # result = search_flights(driver, "Jaipur", "Adampur", "2025-03-07")

    assert result['Success'], f"Failed due to error - {result['error']}"
    print(f"result - {result['result']}")

