# Vinyl Album Value Finder

## Description

The Vinyl Album Value Finder is a Python application that allows users to search for vinyl records and retrieve their current market value and availability information from Discogs. This tool is perfect for vinyl collectors, sellers, and enthusiasts who want to quickly assess the value of their records or potential purchases.

## Features

- Search for vinyl records by album name or barcode
- Retrieve current market statistics from Discogs
- Display estimated prices based on record condition
- Show lowest price currently available on Discogs
- Indicate if a record is blocked from sale on Discogs
- Display album cover art (when available)
- User-friendly GUI built with Tkinter

## Requirements

- Python 3.7+
- Discogs API credentials (Consumer Key and Consumer Secret)

## Installation

1. Clone this repository:
git clone https://github.com/rembertdesigns/discogs-album-value-finder.git

2. Navigate to the project directory:
cd vinyl-album-value-finder

3. Install the required dependencies:
pip install -r requirements.txt

## Configuration

1. Obtain Discogs API credentials:
- Go to https://www.discogs.com/settings/developers
- Create a new application to get your Consumer Key and Consumer Secret

2. Open `vinyl_value_finder.py` and replace the placeholder credentials with your own:
```python
consumer_key = 'YOUR_CONSUMER_KEY'
consumer_secret = 'YOUR_CONSUMER_SECRET'
