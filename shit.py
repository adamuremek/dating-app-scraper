import requests
import json
from Tinder import TinderDriver



        

if __name__ == "__main__":
    driver: TinderDriver = TinderDriver()
    driver.start()

    print("8==========D~")

    #TODO 1: Some photos can be a boomerang video with an mp4 link. find out how to get that.
    #TODO 2: Find way to scrape spotify
    #TODO 3: Find way to scrape instagram

    user_in = ""
    img_url_set = set()
    while user_in != "n":
        user_in = input("harvest women? (y/n)\n")

        if user_in == "y":
            #harvest(driver, img_url_set)
            pass
        elif user_in == "cur_photo":
            print(driver.current_photo_url)
        elif user_in == "open_profile":
            driver.open_profile()
        elif user_in == "close_profile":
            driver.close_profile()
        elif user_in == "nope":
            driver.nope()
        elif user_in == "like":
            driver.like()
        elif user_in == "next_photo":
            driver.next_photo()
        elif user_in == "login":
            driver.login()


        elif user_in == "num":
            print(driver.photo_count)
        elif user_in == "general":
            print(driver.general_info)
        elif user_in == "lifestyle":
            print(driver.lifestyle)
        elif user_in == "basics":
            print(driver.basics)
        elif user_in == "passions":
            print(driver.passions)
        elif user_in == "bio":
            print(driver.bio)
        elif user_in == "name":
            print(driver.name)
        elif user_in == "age":
            print(driver.age)


        elif user_in == "pronouns":
            print(driver.pronouns)
        elif user_in == "rt":
            print(driver.relationship_type)
        elif user_in == "rg":
            print(driver.relationship_goals)
        elif user_in == "lang":
            print(driver.languages)


    print("no more harvesting :( sad")


    driver.quit()