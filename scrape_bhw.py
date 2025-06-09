#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import sys
from datetime import datetime

def get_threads():
    url = "https://www.blackhatworld.com/forums/freebies-giveaways.174/?order=post_date&direction=desc"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        sys.exit(1)

    soup = BeautifulSoup(response.text, 'html.parser')
    threads = []
    
    # Find all thread items
    thread_items = soup.find_all('div', class_='structItem--thread')
    
    for item in thread_items:
        # Get thread title first
        title_element = item.find('div', class_='structItem-title')
        if not title_element:
            continue
        
        # Get the anchor tag for the thread link
        link_element = title_element.find('a', href=True)
        if not link_element:
            continue
        thread_url = link_element['href']
        # Ensure the URL is absolute
        if thread_url.startswith('/'):
            thread_url = f"https://www.blackhatworld.com{thread_url}"
        
        title = title_element.get_text(strip=True)
        
        # Skip if it's a sticky or announcement thread
        if (title.startswith('Sticky') or 
            title.startswith('Please Read:') or 
            'structItem--isSticky' in item.get('class', []) or 
            'structItem--isAnnouncement' in item.get('class', [])):
            continue
        
        # Get timestamp
        time_element = item.find('time')
        if not time_element:
            continue
        timestamp = time_element.get('datetime', '')
        
        threads.append({
            'title': title,
            'timestamp': timestamp,
            'url': thread_url
        })
        
        # Stop after getting 3 non-sticky threads
        if len(threads) >= 3:
            break
    
    return threads

def main():
    threads = get_threads()
    
    print("\nTop 5 Recent Threads (excluding sticky):")
    print("-" * 80)
    
    for i, thread in enumerate(threads, 1):
        print(f"{i}. {thread['title']} ({thread['url']})")
        print(f"   Posted: {thread['timestamp']}")
        print()

if __name__ == "__main__":
    main() 