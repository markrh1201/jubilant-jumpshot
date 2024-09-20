from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
from playwright._impl._errors import TimeoutError

# Function to scrape table data from a page
def scrape_table_data(page):
    # Extracting HTML content from the page
    html = page.inner_html("body")
    # Parsing HTML content using BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    # Selecting table rows from the HTML content
    rows = soup.select("tbody.Crom_body__UYOcU tr")
    # Extracting data from each row and storing in a list of lists
    data = [[td.get_text() for td in row.find_all("td")] for row in rows]
    return data

# Function to scrape data from a specific season
def scrape_season_data(page, url, season):
    # Navigating to the NBA stats website for the given season
    page.goto(url, timeout=60000)

    # List to store scraped data for the season
    data = []
    # Variable to track page number
    page_number = 1

    # Looping through pages until there are no more next buttons
    while True:
        try:
            # Scraping data from the current page
            data += scrape_table_data(page)
            print(f"Scraped data from page {page_number} of season {season}.")

            # Finding the next button
            next_button = page.query_selector("button[data-track='click'][data-type='controls'][data-pos='next']")
            # If no next button found, exit loop
            if not next_button:
                print(f"No next button found for season {season}. Exiting loop.")
                break

            # Clicking the next button
            next_button.click(timeout=5000)
            # Waiting for table data to load on the next page
            page.wait_for_selector("tbody.Crom_body__UYOcU tr")
            # Incrementing page number
            page_number += 1
        except TimeoutError as e:
            # Handling timeout error
            print(f"Failed to navigate to the next page of season {season}: {e}")
            print(f"Saving data for season {season} and exiting.")
            break
        except Exception as e:
            # Handling other exceptions
            print(f"An error occurred for season {season}: {e}")
            break

    return data

# Main function to execute the scraping process
def main():
    # Setting up Playwright
    with sync_playwright() as p:
        # Launching a Chromium browser
        browser = p.chromium.launch(headless=False)
        
        # Creating a new browsing context for 2023-24 season
        context_2023_24 = browser.new_context()
        page_2023_24 = context_2023_24.new_page()

        # URLs for the two seasons
        url_2023_24 = "https://www.nba.com/stats/players/boxscores?SeasonType=Regular+Season"
        url_2022_23 = "https://www.nba.com/stats/players/boxscores?Season=2022-23&SeasonType=Regular+Season"

        # Scraping data for 2023-24 season
        data_2023_24 = scrape_season_data(page_2023_24, url_2023_24, "2023-24")

        # Close the context for the 2023-24 season after scraping
        context_2023_24.close()

        # Creating a new browsing context for the 2022-23 season
        context_2022_23 = browser.new_context()
        page_2022_23 = context_2022_23.new_page()

        # Scraping data for the 2022-23 season
        data_2022_23 = scrape_season_data(page_2022_23, url_2022_23, "2022-23")

        # Close the context for the 2022-23 season after scraping
        context_2022_23.close()

        # Combining the data from both seasons
        combined_data = data_2023_24 + data_2022_23

        # Column names for the DataFrame
        columns = [
            "Player", "Team", "Opponent", "Date", "Result", "Minutes", "Points", 
            "FGM", "FGA", "FG%", "3PM", "3PA", "3P%", "FTM", "FTA", "FT%", 
            "OREB", "DREB", "REB", "AST", "TO", "STL", "BLK", "PF", "+/-", "SPI"
        ]

        # Creating a DataFrame from the combined data
        df = pd.DataFrame(combined_data, columns=columns)

        # Saving the combined DataFrame to a CSV file
        df.to_csv("regular_season_boxscores_combined_22-24.csv", index=False)
        print("Scraping completed and data saved to regular_season_boxscores_combined_22-24.csv.")

        # Close the browser after scraping both seasons
        browser.close()

# Call the main function to start the scraping process
main()
