import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = int(os.environ.get('ADMIN_ID', 0)) if os.environ.get('ADMIN_ID') else None
ALLOWED_USERS = [int(id.strip()) for id in os.environ.get('ALLOWED_USERS', '').split(',') if id.strip()] if os.environ.get('ALLOWED_USERS') else []
