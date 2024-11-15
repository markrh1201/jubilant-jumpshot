from multiprocessing import Pool
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
from playwright._impl._errors import TimeoutError

# Function to scrape table data from a page
def scrape_table_data(page):
    html = page.inner_html("body")
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("tbody.Crom_body__UYOcU tr")
    data = [[td.get_text() for td in row.find_all("td")] for row in rows]
    return data

# Function to scrape data from a specific season
def scrape_season_data(url, season):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(url, timeout=60000)

        data = []
        page_number = 1

        while True:
            try:
                data += scrape_table_data(page)
                print(f"Scraped data from page {page_number} of season {season}.")

                next_button = page.query_selector("button[data-track='click'][data-type='controls'][data-pos='next']")
                if not next_button:
                    print(f"No next button found. Exiting loop for season {season}.")
                    break

                next_button.click(timeout=10000)
                page.wait_for_selector("tbody.Crom_body__UYOcU tr")
                page_number += 1
            except TimeoutError as e:
                print(f"Failed to navigate to the next page of season {season}: {e}")
                break
            except Exception as e:
                print(f"An error occurred for season {season}: {e}")
                break

        context.close()
        browser.close()
        return season, data

# Main function to execute the scraping process with multiprocessing
def main():
    urls_seasons = [
        ("https://www.nba.com/stats/players/boxscores?Season=2023-24&SeasonType=Regular+Season", "2023-24"),
        ("https://www.nba.com/stats/players/boxscores?Season=2022-23&SeasonType=Regular+Season", "2022-23"),
        ("https://www.nba.com/stats/players/boxscores?Season=2024-25&SeasonType=Regular+Season", "2024-25")
    ]

    with Pool(processes=len(urls_seasons)) as pool:
        results = pool.starmap(scrape_season_data, urls_seasons)

    box_score_col = [
        "Player", "Team", "Opponent", "Date", "Result", "Minutes", "Points", 
        "FGM", "FGA", "FG%", "3PM", "3PA", "3P%", "FTM", "FTA", "FT%", 
        "OREB", "DREB", "REB", "AST", "TO", "STL", "BLK", "PF", "+/-", "SPI"
    ]

    # Process results and create DataFrames for each season's data
    dfs = []
    for season, data in results:
        df = pd.DataFrame(data, columns=box_score_col)
        df['Season'] = season
        dfs.append(df)

    # Combine all DataFrames into one and save to a CSV
    df_combined = pd.concat(dfs)
    df_combined = df_combined.rename(columns=lambda x: x.strip())
    df_combined.drop([''])
       
    # Convert 'Date' column to datetime format
    df_combined['Date'] = pd.to_datetime(df_combined['Date'])
    df_combined = df_combined.sort_values(by=['Date', 'Opponent']) 
    df_combined.to_csv("player_boxscores.csv", index=False)
    
    print("Scraping completed. Data saved to player_boxscores.csv")

# Call the main function to start the scraping process
if __name__ == "__main__":
    main()
