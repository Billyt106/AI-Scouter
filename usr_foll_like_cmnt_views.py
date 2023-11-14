from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import pandas as pd
import os
import time
import instaloader


CSV_PATH = 'usernames_and_followers_likes_cmnts_views.csv'

def login_to_instagram(page, username, password):
    print("Logging in to Instagram...")
    page.goto('https://www.instagram.com/accounts/login/')
    page.wait_for_selector("input[name='username']", state="visible")
    page.fill("input[name='username']", username)
    page.fill("input[name='password']", password)
    page.click("button[type='submit']")
    time.sleep(5)  # Wait for login to complete

def navigate_to_reels(page):
    """Navigates to the Instagram Reels page."""
    print("Navigating to Reels...")
    page.goto('https://www.instagram.com/reels/')
    page.wait_for_load_state('domcontentloaded')
    print("Navigated to Reels.")

def scroll_to_next_reel(page):
    """Scrolls down to the next Instagram Reel."""
    print("Scrolling to the next Reel...")
    page.mouse.wheel(0, 500)
    page.wait_for_timeout(2000)
    print("Scrolled to the next Reel.")

def click_more_options_and_embed(page):
    """Clicks 'More Options', 'Embed', extracts the embed code, and extracts the username."""
    print("Clicking 'More Options' button...")
    more_options_button = page.query_selector('svg[aria-label="More"]')
    if more_options_button:
        more_options_button.click()
        print("Clicked 'More Options' button.")
        page.wait_for_timeout(2000)

        # Click 'Embed'
        embed_button = page.query_selector('text=Embed')
        if embed_button:
            embed_button.click()
            print("Clicked 'Embed'.")
            page.wait_for_timeout(2000)
            
            # Locate the embed code textarea
            embed_code_textarea = page.query_selector("textarea")
            if embed_code_textarea:
                embed_code = embed_code_textarea.input_value()
                print("Embed code extracted.")
                
                # Extract username from embed code
                username = extract_username_from_embed_code(embed_code)
                if username:
                    print("Username extracted:", username)
                    return username
                else:
                    print("Username could not be extracted.")
            else:
                print("Embed code textarea not found.")
        else:
            print("'Embed' option not found.")
    else:
        print("'More Options' button not found.")
    return None

def extract_username_from_embed_code(embed_code):
    """Extracts the Instagram username from the embed code."""
    soup = BeautifulSoup(embed_code, "html.parser")
    a_tag = soup.find("a", string=lambda text: "A post shared by" in text if text else False)
    if not a_tag:
        return None
    text_content = a_tag.get_text(strip=True)
    username = text_content.split('@')[-1].split(')')[0].strip()
    return username

def save_username_to_csv(username, followers_count, total_likes, total_comments, total_views, csv_path):
    """Saves the Instagram username, follower count, likes, comments, and views to a CSV file."""
    new_row = pd.DataFrame({
        'username': [username],
        'followers_count': [followers_count],
        'likes': [total_likes],
        'comments': [total_comments],
        'views': [total_views]  # Add views here
    })
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        df = new_row
    df.to_csv(csv_path, index=False)
    print(f"Username, followers, likes, comments, and views saved to {csv_path}")


def close_options_modal(page):
    """Closes the 'More Options' modal by clicking outside it twice."""
    print("Closing 'More Options' modal...")
    
    # Click outside the modal twice to close it
    page.mouse.click(10, 10)  # Click outside the modal (first click)
    page.wait_for_timeout(1000)
    
    page.mouse.click(10, 10)  # Click outside the modal again (second click)
    page.wait_for_timeout(1000)
    
    print("Closed 'More Options' modal.")
    
def parse_followers_count(followers_text):
    """Parse the followers count text to an integer."""
    followers_text = followers_text.lower().replace(',', '')
    multiplier = 1

    if 'k' in followers_text:
        multiplier = 1000
        followers_text = followers_text.replace('k', '')
    elif 'm' in followers_text:
        multiplier = 1000000
        followers_text = followers_text.replace('m', '')

    # For counts like '1,234' after removing 'k' or 'm'
    if '.' in followers_text:
        parts = followers_text.split('.')
        main_part = parts[0]
        decimal_part = parts[1]
        # Adjust the multiplier based on the number of decimal places
        multiplier /= 10 ** len(decimal_part)
        followers_text = main_part + decimal_part

    return int(float(followers_text) * multiplier)

def get_followers_count(page, username):
    """Gets the number of followers for a given username."""
    profile_url = f'https://www.instagram.com/{username}/'
    page.goto(profile_url)
    page.wait_for_selector('header section ul li a span', state='visible')  # Adjust the selector based on the current Instagram layout
    followers_element = page.query_selector('header section ul li a span')
    followers_count_text = followers_element.inner_text()

    # Use the helper function to parse the text to an integer
    followers_count = parse_followers_count(followers_count_text)
    return followers_count
def get_total_likes_of_last_reels(username, max_reels=10):
    L = instaloader.Instaloader()

    try:
        profile = instaloader.Profile.from_username(L.context, username)
        posts = profile.get_posts()

        total_likes = 0
        count = 0

        for post in posts:
            if post.is_video and count < max_reels:
                total_likes += post.likes
                count += 1
            if count == max_reels:
                break

        return total_likes
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"The profile {username} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return None
def get_total_comments_of_last_reels(username, max_reels=10):
    L = instaloader.Instaloader()

    try:
        profile = instaloader.Profile.from_username(L.context, username)
        posts = profile.get_posts()

        total_comments = 0
        count = 0

        for post in posts:
            if post.is_video and count < max_reels:
                total_comments += post.comments  # Fetches the number of comments on the post
                count += 1
            if count == max_reels:
                break

        return total_comments
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"The profile {username} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return None
def get_total_views_of_last_reels(username, max_reels=10):
    L = instaloader.Instaloader()

    try:
        profile = instaloader.Profile.from_username(L.context, username)
        posts = profile.get_posts()

        total_views = 0
        count = 0

        for post in posts:
            if post.is_video and count < max_reels:
                total_views += post.video_view_count  # Fetches the number of views on the reel
                count += 1
            if count == max_reels:
                break

        return total_views
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"The profile {username} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return None

def main():
    """Main function to run the Instagram scraper."""
    instagram_username = '106recordsofficial'
    instagram_password = 'Pakistanzindabad123'
    if not instagram_username or not instagram_password:
        raise ValueError("Instagram credentials are not set.")

    with sync_playwright() as p:
        browser = p.webkit.launch(headless=False)  # Set headless=True to run without opening a browser window
        page = browser.new_page()
        login_to_instagram(page, instagram_username, instagram_password)

        num_users_logged = 0
        max_users_to_log = None  # Set this to an integer if you want to limit the number of users

        try:
            while max_users_to_log is None or num_users_logged < max_users_to_log:
                navigate_to_reels(page)
                user_input = input("Options: [log/skip/exit]: ").strip().lower()
                if user_input == 'log':
                    username = click_more_options_and_embed(page)
                    if username:
                        try:
                            followers_count = get_followers_count(page, username)
                            total_likes = get_total_likes_of_last_reels(username)
                            total_comments = get_total_comments_of_last_reels(username)
                            total_views = get_total_views_of_last_reels(username)  # Fetch total views

                            if total_likes is not None:
                                print(f"Total likes from the last 10 reels for {username}: {total_likes}")
                            if total_comments is not None:
                                print(f"Total comments from the last 10 reels for {username}: {total_comments}")
                            if total_views is not None:
                                print(f"Total views from the last 10 reels for {username}: {total_views}")

                            save_username_to_csv(username, followers_count, total_likes, total_comments, total_views, CSV_PATH)
                            print(f"Stored {username} with {followers_count} followers, {total_likes} likes, {total_comments} comments, and {total_views} views from last 10 reels.")
                        except Exception as e:
                            print(f"An error occurred while getting information for {username}: {e}")
                        close_options_modal(page)
                        num_users_logged += 1
                    else:
                        close_options_modal(page)
                elif user_input == 'skip':
                    print("Skipping to the next Reel...")
                    scroll_to_next_reel(page)
                elif user_input == 'exit':
                    print("Exiting the program.")
                    break
                else:
                    print("Invalid input. Please enter 'log', 'skip', or 'exit'.")

        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
            print("Closing browser...")
            browser.close()

if __name__ == "__main__":
    main()

