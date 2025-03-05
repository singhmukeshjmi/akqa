from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from selenium.webdriver.common.keys import Keys
import time

# Function to initialize WebDriver
def start_driver():
    """
    Sets up and starts a Microsoft Edge WebDriver with specific settings.

    This function makes the Edge browser open in full-screen mode and uses
    the correct driver, which is managed by EdgeChromiumDriverManager.

    :return: A WebDriver instance for Microsoft Edge.
    """
    options = webdriver.EdgeOptions()
    options.add_argument("--start-maximized")  # Open browser in full screen
    service = EdgeService(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=service, options=options)
    return driver


def goto_url(driver, url = "https://www.booking.com/flights/index.en-gb.html", timeout=10):
    """
    This function opens the specified URL in a browser using the given WebDriver,
    and waits for a specific element to be visible on the page.

    :param driver: The Selenium WebDriver instance used to interact with the browser.
    :param url: The URL to navigate to (defaults to Booking.com flights page).
    :param timeout: The maximum time (in seconds) to wait for the element to be visible (defaults to 10 seconds).
    :return: True if the element is found and visible, False otherwise.
    """
    wait = WebDriverWait(driver, timeout=timeout)
    driver.get(url)
    try:
        element = wait.until(EC.visibility_of_element_located((By.XPATH, "//button[@data-ui-name='input_location_from_segment_0']")))
        print(f"{element} is found successfully")
        return True
    except:
        print("'Flying from' element not encountered even after polling for 10 seconds")
        return False

def fill_airport_city(driver, xpath_parent, city_code):
    """
    
    :return: 
    """
    wait = WebDriverWait(driver, timeout=10)
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
                wait.until(EC.visibility_of_element_located(By.XPATH, xpath))
            except Exception as e:
                print("No options found for given city code")
                return False
            suggestions = combo_box_from.find_elements(By.XPATH, xpath)
            for i in suggestions:
                if city_code in i.text:
                    i.click()
        return True
    except Exception as e:
        print(f"Caught Exception - {e}")
        return False


# Function to search flights
def search_flights(driver, departure = "DEL", destination = "BOM", date_string = None):
    wait = WebDriverWait(driver, timeout=10)
    if not date_string:
        travel_date = datetime.today().date()
    else:
        travel_date = datetime.strptime(date_string, '%Y-%m-%d')
        if travel_date < datetime.today().date():
            print("Sorry you are trying a past date")
            return False

    goto_url(driver)
    # Click "From" and enter departure city
    flying_from_xpath = "//button[@data-ui-name='input_location_from_segment_0']"
    fill_airport_city(driver, xpath_parent=flying_from_xpath, city_code=departure)

    # Click "Flying To" and enter destination city
    flying_to_xpath = "//button[@data-ui-name='input_location_to_segment_0']"
    fill_airport_city(driver, xpath_parent=flying_to_xpath, city_code=destination)


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
    wait.until(lambda driver: travellers.get_attribute('aria-expanded') == 'false')


    # Click Search
    search_button = driver.find_element(By.XPATH, "//button[@data-ui-name='button_search_submit']")
    search_button.click()


    # Verify results
    try:
        wait.until(EC.visibility_of_element_located((By.XPATH, "//div[starts-with(@id,'flight-card-')]")))
        flight_results = driver.find_elements(By.XPATH, "//div[starts-with(@id,'flight-card-')]")
        result = []
        for i in range(len(flight_results)):
            price = driver.find_element(By.XPATH, f"//div[starts-with(@id,'flight-card-{i}')]//descendant::div[@data-testid='flight_card_price_main_price']").text
            carrier = driver.find_element(By.XPATH, f"//div[starts-with(@id,'flight-card-{i}')]//descendant::div[@data-testid='flight_card_carrier_0']").text
            departure_time = driver.find_element(By.XPATH, f"//div[starts-with(@id,'flight-card-{i}')]//descendant::div[@data-testid='flight_card_segment_departure_time_0']").text
            destination_time = driver.find_element(By.XPATH, f"//div[starts-with(@id,'flight-card-{i}')]//descendant::div[@data-testid='flight_card_segment_destination_time_0']").text
            departure_airport = driver.find_element(By.XPATH, f"//div[starts-with(@id,'flight-card-{i}')]//descendant::div[@data-testid='flight_card_segment_departure_airport_0']").text
            destination_airport = driver.find_element(By.XPATH, f"//div[starts-with(@id,'flight-card-{i}')]//descendant::div[@data-testid='flight_card_segment_destination_airport_0']").text
            departure_date = driver.find_element(By.XPATH, f"//div[starts-with(@id,'flight-card-{i}')]//descendant::div[@data-testid='flight_card_segment_departure_date_0']").text
            destination_date = driver.find_element(By.XPATH, f"//div[starts-with(@id,'flight-card-{i}')]//descendant::div[@data-testid='flight_card_segment_destination_date_0']").text
            stops = driver.find_element(By.XPATH, f"//div[starts-with(@id,'flight-card-{i}')]//descendant::span[@data-testid='flight_card_segment_stops_0']").text
            # Direct, 1 stop
            duration = driver.find_element(By.XPATH, f"//div[starts-with(@id,'flight-card-{i}')]//descendant::div[@data-testid='flight_card_segment_duration_0']").text
            result.append({'price':price, 'carrier':carrier, 'departure_time':departure_time, 'destination_time':destination_time, 'departure_airport':departure_airport,
                    'destination_airport':destination_airport, 'departure_date':departure_date, 'destination_date':destination_date, 'stops':stops, 'duration':duration})


        # driver.find_element(By.XPATH, "//button[@data-testid='flight_card_price_open_price_popover']").click()
        # print(f"✅ Flights found for {departure} to {destination} on {travel_date}")

        # xpath = "//div[@role='dialog']"
        # xpath = "//button/span[text()='Refresh']"
    except:
        print(f"❌ No flights found for {departure} to {destination} on {travel_date}")



# Main execution
if __name__ == "__main__":
    print("Starting the webdriver")
    driver = start_driver()
    print("webdriver started successfully")

    search_flights(driver)

    # Test Case 1: Search valid flights (DEL to BOM, Today)
    # search_flights(driver, "Delhi", "Mumbai", "2025-03-05")

    # Test Case 2: Invalid Input
    # search_flights(driver, "XYZ", "Mumbai", "2025-03-06")

    # Test Case 3: No Flights Available
    # search_flights(driver, "Delhi", "Antarctica", "2025-03-07")

    driver.quit()
