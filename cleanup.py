#!/usr/bin/env python3
"""
Cleanup script to organize project for GitHub/Vercel deployment
Run this script to automatically remove unnecessary files and folders
"""

import os
import shutil

def delete_if_exists(path):
    """Delete file or folder if it exists"""
    try:
        if os.path.isfile(path):
            os.remove(path)
            print(f"✅ Deleted file: {path}")
        elif os.path.isdir(path):
            shutil.rmtree(path)
            print(f"✅ Deleted folder: {path}")
        else:
            print(f"⚠️  Not found: {path}")
    except Exception as e:
        print(f"❌ Error deleting {path}: {e}")

def main():
    print("🧹 Starting cleanup process...\n")
    
    # Files and folders to delete
    items_to_delete = [
        # Duplicate folder
        "ScamGuard",
        
        # Extra documentation files
        "COMPLETE_SUMMARY.txt",
        "MOBILE_TESTING_GUIDE.md",
        "QUICK_RESPONSIVE_REFERENCE.md",
        "QUICK_START.md",
        "RESPONSIVE_COMPLETE_SUMMARY.txt",
        "RESPONSIVE_DESIGN.md",
        "RESPONSIVE_SUMMARY.txt",
        "RESPONSIVE_SYSTEM_COMPLETE.md",
        "SYSTEM_READY.md",
        "VIDEO_STATUS.md",
        
        # IDE settings
        ".vscode",
        
        # Test reports
        "reports/scam_report_20260306_175312.txt",
    ]
    
    print("Deleting unnecessary files and folders:\n")
    for item in items_to_delete:
        delete_if_exists(item)
    
    print("\n" + "="*60)
    print("🎉 Cleanup complete!")
    print("="*60)
    print("\nYour project is now organized and ready for deployment!")
    print("\nNext steps:")
    print("1. Review the changes")
    print("2. Run: git init")
    print("3. Run: git add .")
    print("4. Run: git commit -m 'Initial commit'")
    print("5. Push to GitHub")
    print("6. Deploy on Vercel")
    print("\nSee CLEANUP_INSTRUCTIONS.md for detailed steps.")

if __name__ == "__main__":
    main()
