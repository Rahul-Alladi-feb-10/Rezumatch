# test.py - Fixed MongoDB connection with special characters in password

from pymongo import MongoClient
from urllib.parse import quote_plus

# Your credentials
username = "Rahul_Alladi"
password = "R@hul123"  # Contains special character @
cluster = "resume-cluster.dvxgpy6.mongodb.net"
app_name = "Resume-cluster"

# URL-encode the password
encoded_password = quote_plus(password)

# Build connection string with encoded password
connection_string = f"mongodb+srv://{username}:{encoded_password}@{cluster}/?appName={app_name}"

print(f"🔄 Connecting to MongoDB Atlas...")

try:
    client = MongoClient(connection_string)
    
    # Test connection
    client.admin.command('ping')
    
    print('✅ Connected to MongoDB Atlas!')
    print('📚 Databases:', client.list_database_names())
    
except Exception as e:
    print(f'❌ Connection failed: {str(e)}')