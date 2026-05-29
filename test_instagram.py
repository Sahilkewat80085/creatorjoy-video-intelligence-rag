import sys
import instaloader
import json

def test_instagram(url):
    print(f"Testing Instagram Extraction for URL: {url}")
    
    # Extract shortcode from URL
    shortcode = url.rstrip('/').split('/')[-1]
    
    L = instaloader.Instaloader()
    
    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        print(f"Creator: {post.owner_username}")
        print(f"Caption: {post.caption}")
        print(f"Likes: {post.likes}")
        print(f"Comments: {post.comments}")
        print(f"Views: {post.video_view_count if post.is_video else 'Not a video'}")
        print(f"Hashtags: {post.caption_hashtags}")
        
        print("\nNote: Follower count of the creator is not directly available from the Post object without fetching the Profile object (which may require login and cause rate limits).")
        try:
            profile = instaloader.Profile.from_username(L.context, post.owner_username)
            print(f"Followers: {profile.followers}")
        except Exception as e:
            print(f"Could not fetch follower count: {e}")
            
    except Exception as e:
        print(f"Error extracting Instagram data: {e}")

if __name__ == "__main__":
    test_url = sys.argv[1] if len(sys.argv) > 1 else "https://www.instagram.com/reel/C8qLZZmP4O-/"
    test_instagram(test_url)
