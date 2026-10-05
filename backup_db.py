import shutil
import os
from datetime import datetime

def backup_database():
    # Get the current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Define paths
    db_path = os.path.join('db.sqlite3')
    backup_dir = os.path.join('backups')
    backup_path = os.path.join(backup_dir, f'db_backup_{timestamp}.sqlite3')
    
    # Create backups directory if it doesn't exist
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Copy the database file
    try:
        shutil.copy2(db_path, backup_path)
        print(f"Database backed up successfully to {backup_path}")
        return True
    except Exception as e:
        print(f"Error backing up database: {str(e)}")
        return False

if __name__ == "__main__":
    backup_database() 