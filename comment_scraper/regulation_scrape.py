import time
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd

def get_id_list(driver):
    """Extracts comment IDs from the current page."""
    id_list = []
    elements = driver.find_elements(By.XPATH, "/html/body/section[5]/div/div/div/div/div[2]/div/div[3]/div/div/div[1]/div/div/ul/li[3]")
    
    for element in elements:
        try:
            id_list.append(element.text.split()[1])  # Extract the ID
        except Exception as e:
            print(f"Error extracting ID: {e}")
    
    return id_list



""""
//*[@id="study-1278437029"]/td[2]/div[2]/div/div[4]/p

//*[@id="study-1278397508"]/td[2]/div[2]/div/div[4]/p

//*[@id="study-1278404211"]/td[2]/div[2]/div/div[4]/p

"""
def get_comment_info(driver, ID):
    """Fetches comment details from a given comment ID."""
    try:
        driver.get(f"https://www.regulations.gov/comment/{ID}")
        time.sleep(3)
        
        date = driver.find_element(By.CLASS_NAME, 'js-posted-text').text
        comment = driver.find_element(By.CLASS_NAME, 'px-2').text
        
        return {'ID': ID, 'Date': date, 'Text': comment}
    except Exception as e:
        print(f"Error fetching comment {ID}: {e}")
        return None

def main():
    try:
        data = pd.read_csv('comments.csv')  # Load existing data
    except FileNotFoundError:
        data = pd.DataFrame(columns=['ID', 'Date', 'Text'])  # Create an empty DataFrame if file doesn't exist

    driver = webdriver.Chrome()
    new_data = []  # List to store new comments
    
    try:
        for i in range(1, 100):
            driver.get(f"https://www.regulations.gov/document/EPA-HQ-OPP-2024-0562-0001/comment?pageNumber={i}&sortBy=postedDate&sortDirection=desc")
            time.sleep(3)
            id_list = get_id_list(driver)
            
            for ID in id_list:
                if ID not in data['ID'].values:
                    print("Fetching comment:", ID)
                    info = get_comment_info(driver, ID)
                    if info:
                        new_data.append(info)
                    time.sleep(1)
    
    except Exception as e:
        print("Error occurred during execution:", e)
        traceback.print_exc()
    
    finally:
        driver.quit()  # Ensure WebDriver is properly closed
        
        if new_data:
            new_data_df = pd.DataFrame(new_data)
            updated_data = pd.concat([data, new_data_df], ignore_index=True)
            updated_data.to_csv('comments.csv', index=False)
            print("Data saved to comments.csv")
        else:
            print("No new data to save.")

    print("Data collection complete.")

if __name__ == "__main__":
    main()
