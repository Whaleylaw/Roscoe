#!/usr/bin/env python3
"""
Test script to explore the Kentucky Court Directory API response format.
"""

import requests
import json
from bs4 import BeautifulSoup
import pandas as pd

# Base URL
BASE_URL = "https://kcoj.kycourts.net"
API_ENDPOINT = "/ContactList/Search/Results"

def parse_html_table(html_content):
    """Parse the HTML table from the response."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the table
    table = soup.find('table', {'id': 'addressList'})
    if not table:
        print("No table found with id='addressList'")
        return None

    # Extract headers
    headers = []
    thead = table.find('thead')
    if thead:
        header_row = thead.find('tr')
        if header_row:
            headers = [th.text.strip() for th in header_row.find_all('th')]

    print(f"Table headers: {headers}")

    # Extract rows
    rows = []
    tbody = table.find('tbody')
    if tbody:
        for tr in tbody.find_all('tr'):
            cells = [td.text.strip() for td in tr.find_all('td')]
            if cells:
                rows.append(cells)

    print(f"Number of rows: {len(rows)}")

    if rows:
        # Create DataFrame
        df = pd.DataFrame(rows, columns=headers if headers else None)
        return df
    return None


def test_api_request(category="Circuit Judges", county="Fayette"):
    """Test a single API request to understand response format."""
    url = f"{BASE_URL}{API_ENDPOINT}"

    params = {
        "SelectedCategory": category,
        "SelectedCounty": county
    }

    print(f"Testing API Request")
    print(f"URL: {url}")
    print(f"Category: {category}, County: {county}")
    print("-" * 80)

    try:
        # Use GET request
        response = requests.get(url, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
        print(f"Response Length: {len(response.content)} bytes")
        print("-" * 80)

        if response.status_code == 200:
            # Parse the HTML table
            df = parse_html_table(response.text)

            if df is not None and len(df) > 0:
                print("\nExtracted Data:")
                print(df.to_string())
                print(f"\nData shape: {df.shape}")
                print(f"Columns: {list(df.columns)}")
            else:
                print("\nNo rows in table body - checking for inline data")

                # Save full HTML for inspection
                with open('/tmp/court_response.html', 'w') as f:
                    f.write(response.text)
                print("Full HTML saved to /tmp/court_response.html")

                # Look for script tags with data
                soup = BeautifulSoup(response.text, 'html.parser')
                scripts = soup.find_all('script')
                print(f"\nFound {len(scripts)} script tags")

                # Print any scripts that might contain data
                for i, script in enumerate(scripts):
                    if script.string and len(script.string.strip()) > 100:
                        print(f"\nScript {i+1} (first 500 chars):")
                        print(script.string[:500])

    except Exception as e:
        print(f"Request failed: {e}")


if __name__ == "__main__":
    print("Kentucky Court Directory API Test\n")
    test_api_request()
