from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
from sqlalchemy import create_engine

# Database connection parameters, Populate with youre postgre credentials
db_params = {
    'dbname': '',
    'user': '',
    'password': '',
    'host': '',
    'port': ''
}

# Setting up Chrome WebDriver
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
options.add_argument('--headless')  # Run Chrome in headless mode
driver = webdriver.Chrome(options=options)

# Initialize an empty DataFrame to store all tournament data
all_tournament_data = pd.DataFrame()

# Iterate through the years 2020-2023
for year in range(2020, 2024):
    try:
        print(f"Processing year {year}")  # Debug print
        
        # URL of the page listing all tournaments for the current year
        url = f"https://www.pgatour.com/schedule/{year}"
        
        # Load the page
        driver.get(url)
        time.sleep(5)  # Add a small delay to ensure all elements are loaded
        
        # Find all tournament links using CSS selector
        tournament_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='tournament'][class*='chakra-link css-']")
        tournament_urls = [link.get_attribute("href") for link in tournament_links]
        
        # Modify the URLs
        modified_urls = [url.split('?deviceId')[0] + '/leaderboard' for url in tournament_urls if 'masters-tournament' in url]

        # Iterate over each tournament URL
        for modified_url in modified_urls:
            try:
                print(f"Processing URL: {modified_url}")  # Debug print
                
                # Load the page for the current tournament
                driver.get(modified_url)
                time.sleep(5)  # Add a small delay to ensure all elements are loaded
                
                # Find the table
                table = driver.find_element(By.CSS_SELECTOR, "table.chakra-table")
                assert table, "Table not found"
                
                # Remove empty rows from the table
                driver.execute_script("""arguments[0].querySelectorAll("td.css-1au52ex").forEach((e) => e.parentElement.remove())""", table)
                
                # Get HTML of the table
                table_html = table.get_attribute("outerHTML")
                
                # Read HTML table into DataFrame
                tournament_data = pd.read_html(table_html)[0]
                
                # Add a column to store the tournament name
                tournament_data['Tournament'] = driver.find_element(By.CSS_SELECTOR, "h1.chakra-text.css-axbyz4").text
                tournament_data['Year'] = year
                # Append the tournament data to the DataFrame containing all tournament data
                all_tournament_data = pd.concat([all_tournament_data, tournament_data], ignore_index=True)
            except Exception as e:
                print(f"Failed to extract data from: {modified_url}")
                print(f"Error: {str(e)}")
    except Exception as e:
        print(f"Failed to process year {year}")
        print(f"Error: {str(e)}")

# Quit Selenium WebDriver
driver.quit()

all_tournament_data = all_tournament_data.loc[:, ~all_tournament_data.columns.str.contains('^Unnamed')]
# Connect to the database and write DataFrame to PostgreSQL table
try:
    engine = create_engine(f'postgresql://{db_params["user"]}:{db_params["password"]}@{db_params["host"]}:{db_params["port"]}/{db_params["dbname"]}')
    all_tournament_data.to_sql('pga_player_stats', engine, if_exists='replace', index=False)
    print("Data written to PostgreSQL table successfully.")
except Exception as e:
    print(f"Failed to write data to PostgreSQL table.")
    print(f"Error: {str(e)}")
