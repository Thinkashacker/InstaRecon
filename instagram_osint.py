import instaloader
import re
import os
import zipfile

def extract_contacts(text):
    emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    phones = re.findall(r'\+?\d[\d\s\-]{7,}\d', text)
    return emails, phones

def zip_folder(folder_path, zip_name):
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, start=folder_path)
                zipf.write(filepath, arcname)

def download_instagram_profile(username, login_user, login_pass):
    L = instaloader.Instaloader(download_videos=True, download_comments=False, save_metadata=False)
    
    try:
        L.login(login_user, login_pass)
        print("Logged in successfully.")
    except Exception as e:
        print(f"Login failed: {e}")
        return
    
    try:
        profile = instaloader.Profile.from_username(L.context, username)
    except Exception as e:
        print(f"Error fetching profile: {e}")
        return
    
    target_folder = username
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    
    print(f"Downloading posts for {username}...")
    for post in profile.get_posts():
        L.download_post(post, target=target_folder)
    
    print(f"Downloading highlights for {username}...")
    highlights_folder = os.path.join(target_folder, "highlights")
    if not os.path.exists(highlights_folder):
        os.makedirs(highlights_folder)
    for highlight in profile.get_highlights():
        highlight_folder = os.path.join(highlights_folder, highlight.title)
        if not os.path.exists(highlight_folder):
            os.makedirs(highlight_folder)
        for item in highlight.get_items():
            L.download_storyitem(item, target=highlight_folder)
    
    bio = profile.biography
    emails, phones = extract_contacts(bio)
    
    print(f"Extracted emails: {emails}")
    print(f"Extracted phone numbers: {phones}")
    
    zip_name = f"{username}_instagram_data.zip"
    zip_folder(target_folder, zip_name)
    print(f"Data zipped into {zip_name}")

if __name__ == "__main__":
    user = input("Enter Instagram username to download: ")
    login_user = input("Enter your Instagram login username: ")
    login_pass = input("Enter your Instagram login password: ")
    download_instagram_profile(user, login_user, login_pass)