# shopify_integration.py

import shopify
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Shopify API credentials from .env
SHOP_URL = os.getenv("SHOP_URL")
ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")

# Set up the Shopify session
shopify.ShopifyResource.set_site(f"https://{SHOP_URL}")
session = shopify.Session(SHOP_URL, "2025-01", ACCESS_TOKEN)
shopify.ShopifyResource.activate_session(session)

# Test by fetching shop data
shop = shopify.Shop.current()
print(shop)
