from multiprocessing import Pool
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
from playwright._impl._errors import TimeoutError

# Function to scrape team stats data from a page
def scrape_table_data(page):
    html = page.inner_html("body")
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("tbody.Crom_body__UYOcU tr")
    data = [[td.get_text() for td in row.find_all("td")[1:]] for row in rows]  # Skip the INDEX column
    return data

# Function to scrape data from a specific season URL
def scrape_season_data(url, season):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(url, timeout=60000)

        # Scrape data directly since stats are on a single page
        data = scrape_table_data(page)
        print(f"Scraped data for season {season}.")

        context.close()
        browser.close()
        return season, data

# Main function to execute the scraping process with multiprocessing
def main():
    
    team_abbreviations = {
    "Atlanta Hawks": "ATL",
    "Boston Celtics": "BOS",
    "Brooklyn Nets": "BKN",
    "Charlotte Hornets": "CHA",
    "Chicago Bulls": "CHI",
    "Cleveland Cavaliers": "CLE",
    "Dallas Mavericks": "DAL",
    "Denver Nuggets": "DEN",
    "Detroit Pistons": "DET",
    "Golden State Warriors": "GSW",
    "Houston Rockets": "HOU",
    "Indiana Pacers": "IND",
    "LA Clippers": "LAC",
    "Los Angeles Lakers": "LAL",
    "Memphis Grizzlies": "MEM",
    "Miami Heat": "MIA",
    "Milwaukee Bucks": "MIL",
    "Minnesota Timberwolves": "MIN",
    "New Orleans Pelicans": "NOP",
    "New York Knicks": "NYK",
    "Oklahoma City Thunder": "OKC",
    "Orlando Magic": "ORL",
    "Philadelphia 76ers": "PHI",
    "Phoenix Suns": "PHX",
    "Portland Trail Blazers": "POR",
    "Sacramento Kings": "SAC",
    "San Antonio Spurs": "SAS",
    "Toronto Raptors": "TOR",
    "Utah Jazz": "UTA",
    "Washington Wizards": "WAS"
    }
    
    
    urls_seasons = [
        ("https://www.nba.com/stats/teams/advanced?Season=2024-25", "2024-25"),
        ("https://www.nba.com/stats/teams/advanced?Season=2023-24", "2023-24"),
        ("https://www.nba.com/stats/teams/advanced?Season=2022-23", "2022-23")
    ]

    with Pool(processes=len(urls_seasons)) as pool:
        results = pool.starmap(scrape_season_data, urls_seasons)

    # Columns based on the structure provided, excluding INDEX
    team_stats_columns = [
        "Team", "GP", "W", "L", "MIN", "OffRtg", "DefRtg", "NetRtg", "AST%", 
        "AST/TO", "AST Ratio", "OREB%", "DREB%", "REB%", "TOV%", "eFG%", 
        "TS%", "PACE", "PIE", "POSS"
    ]

    # Process results and create DataFrames for each season's data
    dfs = []
    for season, data in results:
        df = pd.DataFrame(data, columns=team_stats_columns)
        df['Season'] = season
        dfs.append(df)
        
        # Map team names to abbreviations
        df['Team'] = df['Team'].map(team_abbreviations)

    # Combine all DataFrames into one and save to a CSV
    df_combined = pd.concat(dfs)
    df_combined = df_combined.rename(columns=lambda x: x.strip())
    
    # Save to CSV file
    df_combined.to_csv("team_advanced_stats.csv", index=False)
    print("Scraping completed. Data saved to team_advanced_stats.csv")

# Call the main function to start the scraping process
if __name__ == "__main__":
    main()
