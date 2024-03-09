import hashlib
import re
import time
import requests
import json
import random
import xml.etree.ElementTree as ET
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from urllib.parse import unquote

class TinderDriver:
    __icon_map: dict = {
        "pets" : "Pets",
        "drink_of_choice" : "Drinking",
        "smoking" : "Smoking",
        "420" : "Cannabis",
        "workout" : "Workout",
        "appetite" : "Dietary Preference",
        "social_media" : "Social Media",
        "sleeping_habits" : "Sleeping Habits",
        "astrological_sign" : "Zodiac",
        "education" : "Education",
        "kids" : "Family Plans",
        "covid_comfort" : "COVID Vaccine",
        "mbti" : "Personality Type",
        "communication_style" : "Communication Style",
        "love_language" : "Love Style"
    }

    #SVG hashcodes being mapped to the topic the SVG icons represent
    #IMPORTANT!!! If the SVG icons for basic info change, these hashcodes must be updated
    __svg_hash_map: dict = {
        "056c95d622b5e9e7860a5005fce51dd5916bfec61610c191715a1e4f64442754" : "Job Title",
        "91f462a99539d7764f68b6d7415d8c26798ca2b93fa3ef202be772effcdbab44" : "Height",
        "e53eb5454a3fcc0bd7b90c55f0d236ed31c7171b67113e6b698464b2c5f92ae8" : "School",
        "d5bf2c89f2bb55dfe9c52ed7a22d316eb1d1e8c0a80064ba4a316bfb49af3d3b" : "Living In",
        "33e98e451e5b457d5b9fa697f53b849b2516d5167e0e9e9e23fd4422fb5ed5bc" : "Distance From Me",
        "5529bb33506f1f908d4b995ea60c4f539415a7f4bd37e9da42330bc535c745c9" : "Gender"
    }

    __element_xpath_identifiers: dict = {
        "landing_page_login_btn" : [
            "//a[@href='https://tinder.onelink.me/9K8a/3d4abb81' and @class='c1p6lbu0 Miw(120px)' and @data-size='medium']"
            ],
        "login_with_phone_btn" : [
            "//button[@aria-label='Log in with phone number']"
        ],
        "phone_num_field" : [
            "//input[@autocomplete='tel' and @name='phone_number' and @type='tel']"
        ],
        "proceed_btn" : [
            "//button[contains(@class, 'c1p6lbu0') and @type='button'][.//descendant::*[text()='Next']]",
            "//button[contains(@class, 'c1p6lbu0') and @type='button'][.//descendant::*[text()='Continue']]",
            "//button[contains(@class, 'c1p6lbu0') and @type='button'][.//descendant::*[text()='Confirm email']]"
        ],
        "code_field" : [
            "//input[@aria-label='OTP code digit 1' and @type='tel']"
        ],
        "location_perm_accept_btn" : [
            "//button[contains(@class, 'c1p6lbu0') and @type='button'][.//descendant::*[text()='Allow']]"
        ],
        "notification_perm_deny_btn" : [
            "//button[contains(@class, 'c1p6lbu0') and @type='button'][.//descendant::*[text()='I’ll miss out']]"
        ]
    }

    __home_url = "https://tinder.com/"
    
    def __init__(self) -> None:
        #Scope level constants
        webdriver_path = "./geckodriver"
        firefox_bin_path = "/Applications/Firefox.app/Contents/Macos/firefox"
        #profile_path = "C:\\Users\\aruem\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\7czmkvtf.default-release"
        profile_path = "/Users/adamuremek/Library/Application Support/Firefox/Profiles/nlglewdi.default-release"
        

        #Configure Firefox options and driver
        firefox_options = Options()
        #Allow access to location by default
        firefox_options.set_preference("geo.enabled", True)
        firefox_options.set_preference("geo.provider.use_corelocation", True)
        firefox_options.set_preference("geo.prompt.testing", True)
        firefox_options.set_preference("geo.prompt.testing.allow", True)
        #firefox_options.binary_location = firefox_bin_path
        firefox_options.profile = profile_path

        service = Service(executable_path=webdriver_path)

        #Start the firefox driver
        self.driver = webdriver.Firefox(service=service, options=firefox_options)
        self.driver.set_window_size(1000, 1000)


        self.profile_is_open = False
        self.logged_in = False
    
    def __get_list_data(self, src_header: str, start_at_sibling_child: bool=False) -> list:
        element_list: list = []

        # 1. Locate the the lifestyle <h2> element
        try:
            h2_element = self.driver.find_element(By.XPATH, f"//h2[contains(., '{src_header}')]")
        except:
            # Return an empty list if the section with the given name cannot be found
            return element_list

        # 2. Navigate to its sibling
        sibling_element = h2_element.find_element(By.XPATH, "./following-sibling::*[1]")

        # 3. Iterate over the sibling's child elements. Pull children from the first child of the sibling when specified.
        if start_at_sibling_child:
            child_elements = sibling_element.find_element(By.XPATH, "./*[1]").find_elements(By.XPATH, "./*")
        else:
            child_elements = sibling_element.find_elements(By.XPATH, "./*")

        
        for child in child_elements:
            element_list.append(child.text)
        
        return element_list
    
    def __get_dict_data(self, src_header) -> dict:
        element_dict: dict = {}

        # 1. Locate the the lifestyle <h2> element
        try:
            h2_element = self.driver.find_element(By.XPATH, f"//h2[contains(., '{src_header}')]")
        except:
            # Return an empty dictionary if the section with the given name cannot be found
            return element_dict

        # 2. Navigate to its sibling
        sibling_element = h2_element.find_element(By.XPATH, "./following-sibling::*[1]")

        # 3. Collect the sibling's child elements
        child_elements = sibling_element.find_elements(By.XPATH, "./*")

        # 4. Expand any collapsed elements (+num more tags)
        try:
            collapsed_element = sibling_element.find_element(By.XPATH, ".//*[contains(text(), 'more')]")
            self.driver.execute_script("arguments[0].click();", collapsed_element)
            
            # Re-find elements after a probable front end dynamic modification
            h2_element = self.driver.find_element(By.XPATH, f"//h2[contains(., '{src_header}')]")
            sibling_element = h2_element.find_element(By.XPATH, "./following-sibling::*[1]")
            child_elements = sibling_element.find_elements(By.XPATH, "./*")
        except:
            pass

        for child in child_elements:
            icon_element = child.find_element(By.XPATH, ".//img")
            src_url = icon_element.get_attribute("src")

            pattern = r"\/([^\/]+)@[1-3]x\.png"

            is_match = re.search(pattern, src_url)

            if is_match:
                icon_type = is_match.group(1)
                element_dict[TinderDriver.__icon_map[icon_type]] = child.text
            else:
                raise Exception(f"Error: Icon with url '{src_url} does not match provided pattern!'")

        return element_dict
    
    def __run_key_action(self, key_action) -> None:
        main_div = self.driver.find_element(By.ID, "Tinder")

        # Create an ActionChains object passing the driver instance
        actions = ActionChains(self.driver)

        # Move to the element, perform a key down and key up (release)
        actions.move_to_element(main_div).key_down(key_action).key_up(key_action).perform()

    def __get_element(self, element_name: str, max_wait_time: int = 5) -> WebElement:
        if element_name not in TinderDriver.__element_xpath_identifiers:
            raise ValueError(f"'{element_name}' is not a defined element!")

        wait = WebDriverWait(self.driver, max_wait_time)
        for path in TinderDriver.__element_xpath_identifiers[element_name]:
            try:
                element = wait.until(
                    EC.presence_of_element_located((By.XPATH, path))
                )
                return element
            except:
                continue

            
        raise Exception(f"Could not find element with paths given by {element_name}")

    def __get_element_content(self, xpath_str: str) -> str:
        try:
            element_div = self.driver.find_element(By.XPATH, xpath_str)
            return element_div.text
        except:
            return ""

    def __simulate_pause(self, duration: float=0.0) -> None:
        if duration:
            time.sleep(duration)
        else:
            time.sleep(random.uniform(0.5, 1))

    #==Decorators==#
    def __enforce_open_profile(func):
        def wrapper(self, *args, **kwargs):
            if not self.profile_is_open:
                self.open_profile()
            
            return func(self, *args, **kwargs)

        return wrapper

    @property
    @__enforce_open_profile
    def general_info(self):
        info_dict: dict = {}
        # Get the div body that contains all the general info beneth the profile picture
        general_info_div = self.driver.find_element(By.XPATH, "//div[@class='Typs(body-1-regular)']")
        # Get all child divs parented tot eh general info div
        child_divs = general_info_div.find_elements(By.XPATH, "./div")

        for child in child_divs:
            #For some reason, it is a known issue that you cant get svg tags with .//svg using xpath, this alternative must be used
            #Get the svg element and the div containing the info content
            svg_element = child.find_element(By.XPATH, ".//*[name()='svg']")
            content_element = child.find_element(By.XPATH, "./div[not(.//*[name()='svg'])]")

            #Load the svg html into an xml tree and wipe the attributes
            svg_content = svg_element.get_attribute("outerHTML")
            svg_root = ET.fromstring(svg_content)
            svg_root.attrib.clear()

            #Hash the svg using sha256
            hashobj = hashlib.sha256()
            hashobj.update(ET.tostring(svg_root, encoding="utf-8"))
            svg_hashcode = hashobj.hexdigest()
            
            #Store data in result
            info_dict[TinderDriver.__svg_hash_map[svg_hashcode]] = content_element.text

        return info_dict
    
    @property
    @__enforce_open_profile
    def bio(self) -> str:
        #div_parent = self.driver.find_element(By.XPATH, "//div[@class='Px(16px) Py(12px) Us(t) C($c-ds-text-secondary) BreakWord Whs(pl) Typs(body-1-regular)']")
        #content_div = div_parent.find_element(By.XPATH, "./*")
        element_xpath = "//div[@class='Px(16px) Py(12px) Us(t) C($c-ds-text-secondary) BreakWord Whs(pl) Typs(body-1-regular)']/*"
        content = self.__get_element_content(element_xpath)
        return content

    @property
    @__enforce_open_profile
    def name(self) -> str:
        #name_element = self.driver.find_element(By.XPATH, "//h1[@class='Typs(display-1-strong) Fxs(1) Fxw(w) Pend(8px) M(0) D(i)']")
        content = self.__get_element_content("//h1[@class='Typs(display-1-strong) Fxs(1) Fxw(w) Pend(8px) M(0) D(i)']")
        return content
    
    @property
    @__enforce_open_profile
    def age(self) -> str:
        #age_element = self.driver.find_element(By.XPATH, "//span[contains(@aria-label, 'years')]")
        content = self.__get_element_content("//span[contains(@aria-label, 'years')]")
        return content

    @property
    @__enforce_open_profile
    def basics(self) -> dict:
        return self.__get_dict_data("Basics")
    
    @property
    @__enforce_open_profile
    def lifestyle(self) -> dict:
        return self.__get_dict_data("Lifestyle")

    @property
    @__enforce_open_profile
    def passions(self) -> list:
        return self.__get_list_data("Passions", True)

    @property
    @__enforce_open_profile
    def pronouns(self) -> list:
        return self.__get_list_data("Pronouns")
    
    @property
    @__enforce_open_profile
    def relationship_type(self) -> list:
        return self.__get_list_data("Relationship Type")
    
    @property
    @__enforce_open_profile
    def relationship_goals(self) ->str:
        element_xpath = """
            //div[contains(@class, 'D(f)') and contains(@class, 'Jc(c)') and contains(@class, 'Fxd(c)')]
            /div[contains(@class, 'Typs(subheading-1)') and contains(@class, 'CenterAlign')]
        """
        content = self.__get_element_content(element_xpath)
        return content

    @property
    @__enforce_open_profile
    def languages(self) -> list:
        return self.__get_list_data("Languages I Know")

    @property
    @__enforce_open_profile
    def photo_count(self) -> int:
        try:
            photo_tablist_element = self.driver.find_element(By.XPATH, "//div[contains(@aria-label, 'photos')]")
        except:
            return -1
        
        photo_tablist_el_children = photo_tablist_element.find_elements(By.XPATH, "./*")

        return len(photo_tablist_el_children)

    @property
    @__enforce_open_profile
    def current_photo_url(self) -> str:
        photo_el_xpath = "//span[@aria-hidden='false']//div[@role='img']"
        try:
            photo_element = self.driver.find_element(By.XPATH, photo_el_xpath)
        except:
            return ""

        style_attribute = photo_element.get_attribute('style')
        url_match = re.search(r'url\(["\']?(https://images-ssl\.gotinder\.com/u/.*?)["\']?\)', style_attribute)

        if url_match:
            # Extract the URL
            encoded_url = url_match.group(1)
            # Decode the URL
            decoded_url = unquote(encoded_url)
            return decoded_url
        else:
            return ""
            

    def start(self) -> None:
        #Load tinder page
        print("Tinder driver is starting up...")
        self.driver.get(TinderDriver.__home_url)
        print("Tinder driver has started!")
    
    def quit(self) -> None:
        print("Tinder driver shutting down...")
        self.driver.quit()
        print("Tinder driver shut down!")

    
    def login(self) -> None:
        self.__get_element("landing_page_login_btn").click()
        #self.__simulate_pause(3.0)

        self.__get_element("login_with_phone_btn").click()
        #self.__simulate_pause(3.0)

        self.__get_element("phone_num_field").send_keys("9897800239")
        #self.__simulate_pause(3.0)

        self.__get_element("proceed_btn").click()
        #self.__simulate_pause(3.0)

        auth_code = self.__get_element("code_field", 20)
        code = input("Enter text verification code:\n")
        auth_code.send_keys(code)
        #self.__simulate_pause(3.0)
        
        self.__get_element("proceed_btn").click()
        self.__simulate_pause(3.0)

        auth_code = self.__get_element("code_field", 20)
        auth_code.click()
        code = input("Enter email verification code:\n")
        auth_code.send_keys(code)
        #self.__simulate_pause(3.0)

        self.__get_element("proceed_btn").click()
        #self.__simulate_pause(3.0)

        self.__get_element("location_perm_accept_btn").click()
        self.__simulate_pause(3.0)

        self.__get_element("notification_perm_deny_btn").click()
        #self.__simulate_pause(3.0)

        print("Successfully logged in!")
        


    def open_profile(self) -> None:
        self.__run_key_action(Keys.ARROW_UP)
        self.profile_is_open = True
        self.__simulate_pause()
    
    def close_profile(self) -> None:
        self.__run_key_action(Keys.ARROW_DOWN)
        self.profile_is_open = False
        self.__simulate_pause()

    def next_photo(self) -> None:
        self.__run_key_action(Keys.SPACE)
        self.__simulate_pause()

    def nope(self) -> None:
        self.__run_key_action(Keys.ARROW_LEFT)
        self.__simulate_pause()

    def like(self) -> None:
        self.__run_key_action(Keys.ARROW_RIGHT)
        self.__simulate_pause()

    

        