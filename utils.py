import requests
import json

def load_meta():
    with open("./data/META.json", "r") as file:
        #Parse the JSON file into a Python dicitonary
        return json.load(file)
    
def save_meta(meta_json):
    with open("./data/META.json", "w") as file:
        # Serialize and save the JSON data
        json.dump(meta_json, file, indent=4) # indent=4 for pretty printing
    


def download_img(img_url: str, img_name: str):
    response = requests.get(img_url)

    if response.status_code == 200:
        with open(img_name, "wb") as file:
            #write the content of the response into the file
            file.write(response.content)
            print(f"Image {img_name} dowloaded to data dir")
    else:
        print("Failed to get image")