import instaloader
import sys

def get_engagement_rate(username):
    # Initialize Instaloader
    L = instaloader.Instaloader()

    try:
        # Load the profile
        profile = instaloader.Profile.from_username(L.context, username)
    except instaloader.exceptions.ProfileNotExistsException:
        print("The profile does not exist.")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    # Initialize variables to store total likes, comments, and number of posts
    total_likes = 0
    total_comments = 0
    posts_count = 0

    try:
        # Iterate over the posts and sum up the likes and comments
        for post in profile.get_posts():
            total_likes += post.likes
            total_comments += post.comments
            posts_count += 1
            if posts_count >= 10:  # Limit to the last 10 posts for this example
                break
    except Exception as e:
        print(f"An error occurred while retrieving posts: {e}")
        return

    # Calculate the engagement rate
    followers = profile.followers
    if followers == 0:
        print("The profile has 0 followers, cannot calculate engagement rate.")
        return

    engagement_rate = ((total_likes + total_comments) / followers) * 100

    # Print the results
    print(f"\nInstagram Engagement Rate Analysis for @{username}")
    print(f"Total Likes: {total_likes}")
    print(f"Total Comments: {total_comments}")
    print(f"Followers: {followers}")
    print(f"Engagement Rate: {engagement_rate:.2f}%")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = input("Enter the Instagram username: ")

    get_engagement_rate(username)
