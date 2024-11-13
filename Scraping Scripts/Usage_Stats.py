from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from playwright._impl._errors import TimeoutError

# Function to scrape table data from a page
def scrape_table_data(page):
    html = page.inner_html("body")
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("tbody.Crom_body__UYOcU tr")
    data = [[td.get_text() for td in row.find_all("td")] for row in rows]
    return data

# Function to scrape data from a specific nba.com stat table
def scrape_season_data(page, url, season):
    page.goto(url, timeout=60000)
    data = []
    page_number = 1
    while True:
        try:
            data += scrape_table_data(page)
            print(f"Scraped data from page {page_number} of season {season}.")
            next_button = page.query_selector("button[data-track='click'][data-type='controls'][data-pos='next']")
            if not next_button:
                print(f"No next button found for season {season}. Exiting loop.")
                break
            next_button.click(timeout=5000)
            page.wait_for_selector("tbody.Crom_body__UYOcU tr")
            page_number += 1
        except TimeoutError as e:
            print(f"TimeoutError: {e}")
            break
        except Exception as e:
            print(f"An error occurred for season {season}: {e}")
            break
    return data

# Main function to execute the scraping process
def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Scraping box score data for the 2023-24 and 2022-23 seasons
        url_2023_24 = "https://www.nba.com/stats/players/boxscores?SeasonType=Regular+Season&Season=2023-24"
        data_2023_24 = scrape_season_data(page, url_2023_24, "2023-24")

        url_2022_23 = "https://www.nba.com/stats/players/boxscores?SeasonType=Regular+Season&Season=2022-23"
        data_2022_23 = scrape_season_data(page, url_2022_23, "2022-23")

        # Scraping traditional player stats for the 2022-23 and 2021-22 seasons
        url_trad_2022_23 = "https://www.nba.com/stats/players/traditional?Season=2022-23&SeasonType=Regular+Season"
        trad_data_2022_23 = scrape_season_data(page, url_trad_2022_23, "2022-23")

        url_trad_2021_22 = "https://www.nba.com/stats/players/traditional?Season=2021-22&SeasonType=Regular+Season"
        trad_data_2021_22 = scrape_season_data(page, url_trad_2021_22, "2021-22")
        
        # Scraping player usage stats for 2022-23 and 2021-2022 seasons
        url_usage_2022_23 = "https://www.nba.com/stats/players/usage?Season=2022-23&SeasonType=Regular+Season"
        usage_data_2022_23 = scrape_season_data(page, url_usage_2022_23, "2022-23")
        
        url_usage_2021_22 = "https://www.nba.com/stats/players/usage?Season=2021-22&SeasonType=Regular+Season"
        usage_data_2021_22 = scrape_season_data(page, url_usage_2021_22, "2021-22")
        
        browser.close()

        # Combine seasons of data 
        combined_boxscore_data = data_2023_24 + data_2022_23
        combined_trad_data_21_23 = trad_data_2022_23 + trad_data_2021_22
        combined_usage_data_21_23 = usage_data_2021_22 + usage_data_2022_23
        
        # Column names for boxscores
        boxscore_col = [
            "Player", "Team", "Opponent", "Date", "Result", "Minutes", "Points", 
            "FGM", "FGA", "FG%", "3PM", "3PA", "3P%", "FTM", "FTA", "FT%", 
            "OREB", "DREB", "REB", "AST", "TO", "STL", "BLK", "PF", "+/-", "SPI"
        ]

        # Column names for traditional stats
        trad_col = [
            "Index", "Player", "Team", "Age", "GP", "W", "L", "Min", "PTS", "FGM", "FGA", "FG%", 
            "3PM", "3PA", "3P%", "FTM", "FTA", "FT%", "OREB", "DREB", "REB", "AST", 
            "TOV", "STL", "BLK", "PF", "FP", "DD2", "TD3", "+/-"
        ]
        
        usage_col = [
            'Index', 'Player', 'TEAM', 'AGE', 'GP', 'W', 'L', 'MIN', 'USG%', 
            '%FGM', '%FGA', '%3PM', '%3PA', '%FTM', '%FTA', '%OREB', '%DREB', 
            '%REB', '%AST', '%TOV', '%STL', '%BLK', '%BLKA', '%PF', '%PFD', '%PTS'
        ]

        # Create DataFrames
        df_boxscores = pd.DataFrame(combined_boxscore_data, columns=boxscore_col)
        df_traditional_21_23 = pd.DataFrame(combined_trad_data_21_23, columns=trad_col).drop(columns=['Index'])
        
        df_usage_21_23 = pd.DataFrame(combined_usage_data_21_23, columns=usage_col).drop(columns=['Index'])

        # Function to determine the season of a box score based on the date
        def determine_season(date_str):
            game_date = datetime.strptime(date_str, "%m/%d/%Y")
            if game_date >= datetime(2023, 10, 1):
                return "2023-24"
            else:
                return "2022-23"

        # Add a 'Season' column to boxscore DataFrame
        df_boxscores['Season'] = df_boxscores['Date'].apply(determine_season)

        # Merge boxscores with appropriate traditional stats
        df_combined_22_23 = pd.merge(df_boxscores[df_boxscores['Season'] == "2022-23"], df_traditional_21_23, on="Player", how="inner")
        df_combined_23_24 = pd.merge(df_boxscores[df_boxscores['Season'] == "2023-24"], df_traditional_21_23, on="Player", how="inner")

        # Combine both merged DataFrames
        df_final_combined = pd.concat([df_combined_22_23, df_combined_23_24])

        # Save the final combined DataFrame to a CSV file
        df_final_combined.to_csv("combined_boxscores_and_trad_stats_22-24.csv", index=False)
        print("Data saved to combined_boxscores_and_trad_stats_22-24.csv.")

# Call the main function to start the scraping process
main()
