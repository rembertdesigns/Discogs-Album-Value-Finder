import tkinter as tk
from tkinter import messagebox, ttk
from io import BytesIO
import requests
import discogs_client
from requests_oauthlib import OAuth1Session
from PIL import Image, ImageTk

# Replace with your Discogs API credentials
consumer_key = 'mJEsOhslNJJbQVBpBxwF'
consumer_secret = 'VGacJtQoYmlQWjEZKlFaUBktxVNKfeyb'
user_agent = 'MyDiscogsApp/2.0'

# Discogs OAuth URLs
request_token_url = 'https://api.discogs.com/oauth/request_token'
authorize_url = 'https://www.discogs.com/oauth/authorize'
access_token_url = 'https://api.discogs.com/oauth/access_token'

def get_oauth_token():
    # Create OAuth1 session
    discogs_oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

    # Get request token (retry if expired)
    while True:
        try:
            fetch_response = discogs_oauth.fetch_request_token(request_token_url)
            resource_owner_key = fetch_response.get('oauth_token')
            resource_owner_secret = fetch_response.get('oauth_token_secret')
            break  # Exit the loop if successful
        except Exception as e:
            print(f"Request token error. Retrying... {e}")

    # Get authorization
    authorization_url = discogs_oauth.authorization_url(authorize_url)
    print(f'Please go here and authorize: {authorization_url}')
    verifier = input('Paste the verification code here: ')

    # Get the access token
    oauth_tokens = discogs_oauth.fetch_access_token(
        access_token_url,
        verifier=verifier
    )
    return oauth_tokens['oauth_token'], oauth_tokens['oauth_token_secret']

# Get OAuth token (you only need to do this once)
access_token, access_token_secret = get_oauth_token()

# Initialize Discogs client with OAuth
discogs = discogs_client.Client(
    user_agent,
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    token=access_token,
    secret=access_token_secret
)

CONDITIONS = ["Mint (M)", "Near Mint (NM or M-)", "Very Good Plus (VG+)", 
              "Very Good (VG)", "Good Plus (G+)", "Good (G)", "Fair (F)", "Poor (P)"]

def search_album():
    query = entry.get()
    condition = condition_var.get()
    try:
        # Try to search by query (album name or barcode)
        results = discogs.search(query, type='release')
        if results:
            display_result(results[0].id, condition)
        else:
            messagebox.showinfo("No Results", "No results found for the given query.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def get_historical_data(release_id):
    try:
        # Get marketplace statistics
        stats_url = f"https://api.discogs.com/marketplace/stats/{release_id}"
        response = requests.get(stats_url, headers={'Authorization': f"Discogs token={access_token}"})
        response.raise_for_status()
        stats_data = response.json()

        # Get price suggestions
        suggestions_url = f"https://api.discogs.com/marketplace/price_suggestions/{release_id}"
        response = requests.get(suggestions_url, headers={'Authorization': f"Discogs token={access_token}"})
        response.raise_for_status()
        suggestions_data = response.json()

        return {
            'stats': stats_data,
            'suggestions': suggestions_data
        }
    except Exception as e:
        messagebox.showerror("Error", f"Error retrieving market data: {str(e)}")
        return None

def display_result(release_id, condition):
    # Clear previous results
    for widget in result_frame.winfo_children():
        widget.destroy()

    try:
        release = discogs.release(release_id)
        market_data = get_historical_data(release_id)

        # Display album info
        tk.Label(result_frame, text=f"Title: {release.title}").pack()
        tk.Label(result_frame, text=f"Artist: {release.artists[0].name}").pack()
        tk.Label(result_frame, text=f"Year: {release.year}").pack()

        # Display pressing details
        tk.Label(result_frame, text=f"Format: {', '.join(release.formats[0]['descriptions'])}").pack()
        tk.Label(result_frame, text=f"Country: {release.country}").pack()

        # Display price information
        if market_data and 'suggestions' in market_data:
            estimated_price = market_data['suggestions'].get(condition, {}).get('value')
            if estimated_price:
                tk.Label(result_frame, text=f"Estimated {condition} Price: ${estimated_price:.2f}").pack()

        # Display market trend
        if market_data and 'stats' in market_data:
            stats = market_data['stats']
            if stats['num_for_sale'] is not None:
                tk.Label(result_frame, text=f"Current Listings: {stats['num_for_sale']}").pack()
            if stats['lowest_price'] is not None:
                tk.Label(result_frame, text=f"Lowest Price: ${stats['lowest_price']['value']:.2f} {stats['lowest_price']['currency']}").pack()
            if stats['blocked_from_sale']:
                tk.Label(result_frame, text="Note: This release is blocked from sale on Discogs").pack()
        else:
            tk.Label(result_frame, text="No marketplace data available").pack()

        # Display album cover
        try:
            image_url = release.images[0]['uri']
            response = requests.get(image_url)
            img = Image.open(BytesIO(response.content))
            img = img.resize((200, 200), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            label = tk.Label(result_frame, image=photo)
            label.image = photo
            label.pack()
        except Exception:
            tk.Label(result_frame, text="Image not available").pack()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Create main window
root = tk.Tk()
root.title("Vinyl Album Value Finder")

# Create and pack widgets
tk.Label(root, text="Enter Album Name or Barcode:").pack()
entry = tk.Entry(root, width=50)
entry.pack()

# Condition dropdown
tk.Label(root, text="Condition:").pack()
condition_var = tk.StringVar(root)
condition_var.set(CONDITIONS[0])  # default value
condition_dropdown = ttk.Combobox(root, textvariable=condition_var, values=CONDITIONS)
condition_dropdown.pack()

tk.Button(root, text="Search", command=search_album).pack()

result_frame = tk.Frame(root)
result_frame.pack(pady=20)

# Start the GUI event loop
root.mainloop()
