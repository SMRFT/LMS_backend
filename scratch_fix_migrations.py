import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

host = os.environ.get('GLOBAL_DB_HOST')
db_name = os.environ.get('HR_DB_NAME', 'HR')

client = MongoClient(host)
db = client[db_name]
migrations = db['django_migrations']

# Delete all core and admin migrations to start fresh
res = migrations.delete_many({'app': {'$in': ['core', 'admin', 'authtoken']}})
print(f"Deleted {res.deleted_count} migration records.")

client.close()
