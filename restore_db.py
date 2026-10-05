import shutil
import os
import glob

def restore_database(backup_file=None):
    # Define paths
    db_path = os.path.join('db.sqlite3')
    backup_dir = os.path.join('backups')
    
    # If no specific backup file is provided, use the most recent one
    if backup_file is None:
        backup_files = glob.glob(os.path.join(backup_dir, 'db_backup_*.sqlite3'))
        if not backup_files:
            print("No backup files found")
            return False
        backup_file = max(backup_files, key=os.path.getctime)
    
    # Restore the database
    try:
        shutil.copy2(backup_file, db_path)
        print(f"Database restored successfully from {backup_file}")
        return True
    except Exception as e:
        print(f"Error restoring database: {str(e)}")
        return False

if __name__ == "__main__":
    restore_database() 