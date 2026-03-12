#!/usr/bin/env python3
"""
File organization script - Moves all documentation to proper folders
"""

import os
import shutil

def create_folder(path):
    """Create folder if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"✅ Created folder: {path}")

def move_file(source, destination):
    """Move file to destination"""
    try:
        if os.path.exists(source):
            # Create destination folder if needed
            dest_folder = os.path.dirname(destination)
            if dest_folder:
                create_folder(dest_folder)
            
            shutil.move(source, destination)
            print(f"✅ Moved: {source} → {destination}")
        else:
            print(f"⚠️  Not found: {source}")
    except Exception as e:
        print(f"❌ Error moving {source}: {e}")

def delete_item(path):
    """Delete file or folder"""
    try:
        if os.path.isfile(path):
            os.remove(path)
            print(f"✅ Deleted file: {path}")
        elif os.path.isdir(path):
            shutil.rmtree(path)
            print(f"✅ Deleted folder: {path}")
    except Exception as e:
        print(f"❌ Error deleting {path}: {e}")

def main():
    print("📁 Organizing project files...\n")
    
    # Create necessary folders
    print("Creating folder structure...")
    create_folder("docs/guides")
    create_folder("docs/deployment")
    create_folder("docs/archive")
    
    print("\n" + "="*60)
    print("Moving documentation files to docs/ folder...")
    print("="*60 + "\n")
    
    # Move deployment-related files
    deployment_files = {
        "DEPLOYMENT_CHECKLIST.md": "docs/deployment/DEPLOYMENT_CHECKLIST.md",
        "CLEANUP_INSTRUCTIONS.md": "docs/deployment/CLEANUP_INSTRUCTIONS.md",
        "START_HERE.md": "docs/START_HERE.md",
    }
    
    for source, dest in deployment_files.items():
        move_file(source, dest)
    
    # Move guide files
    guide_files = {
        "PROJECT_ORGANIZATION_COMPLETE.md": "docs/guides/PROJECT_ORGANIZATION.md",
        "QUICK_RESPONSIVE_REFERENCE.md": "docs/guides/RESPONSIVE_REFERENCE.md",
    }
    
    for source, dest in guide_files.items():
        move_file(source, dest)
    
    # Move old/duplicate documentation to archive
    archive_files = [
        "COMPLETE_SUMMARY.txt",
        "MOBILE_TESTING_GUIDE.md",
        "QUICK_START.md",
        "RESPONSIVE_COMPLETE_SUMMARY.txt",
        "RESPONSIVE_DESIGN.md",
        "RESPONSIVE_SUMMARY.txt",
        "RESPONSIVE_SYSTEM_COMPLETE.md",
        "SYSTEM_READY.md",
        "VIDEO_STATUS.md",
    ]
    
    print("\n" + "="*60)
    print("Moving old documentation to archive...")
    print("="*60 + "\n")
    
    for file in archive_files:
        if os.path.exists(file):
            move_file(file, f"docs/archive/{file}")
    
    # Delete duplicate ScamGuard folder
    print("\n" + "="*60)
    print("Removing duplicate folders...")
    print("="*60 + "\n")
    
    if os.path.exists("ScamGuard"):
        delete_item("ScamGuard")
    
    # Delete IDE settings
    if os.path.exists(".vscode"):
        delete_item(".vscode")
    
    # Clean up old docs folder files
    print("\n" + "="*60)
    print("Cleaning up old documentation...")
    print("="*60 + "\n")
    
    old_docs = [
        "docs/CHANGES_SUMMARY.md",
        "docs/DEMO_SAMPLES.md",
        "docs/DIRECTORY_TREE.txt",
        "docs/FEATURES.md",
        "docs/FINAL_FIX_SUMMARY.md",
        "docs/FOLDER_GUIDE.md",
        "docs/HOW_TO_ACCESS.md",
        "docs/INDEX.md",
        "docs/ISSUES_FIXED.md",
        "docs/LATEST_UPDATES.md",
        "docs/NEW_FEATURES.md",
        "docs/ORGANIZATION_SUMMARY.md",
        "docs/PROJECT_STRUCTURE.md",
        "docs/SETUP_EMAIL_AND_VIDEOS.md",
        "docs/SIDEBAR_FIX.md",
        "docs/SIDEBAR_IMPROVEMENTS.md",
        "docs/SIDEBAR_LEFT.md",
        "docs/START_HERE.md",
        "docs/TOGGLE_FEATURE_SUMMARY.md",
        "docs/TOGGLE_SIDEBAR_GUIDE.md",
    ]
    
    for file in old_docs:
        if os.path.exists(file):
            delete_item(file)
    
    # Clean up test reports
    print("\n" + "="*60)
    print("Cleaning up test reports...")
    print("="*60 + "\n")
    
    if os.path.exists("reports/scam_report_20260306_175312.txt"):
        delete_item("reports/scam_report_20260306_175312.txt")
    
    print("\n" + "="*60)
    print("🎉 Organization Complete!")
    print("="*60)
    print("\nFinal structure:")
    print("""
    scamguard/
    ├── app.py
    ├── config.py
    ├── requirements.txt
    ├── vercel.json
    ├── .gitignore
    ├── README.md
    ├── cleanup.py
    ├── cleanup.bat
    ├── organize_files.py (this script)
    ├── docs/
    │   ├── START_HERE.md
    │   ├── DEPLOYMENT.md
    │   ├── QUICKSTART.md
    │   ├── TROUBLESHOOTING.md
    │   ├── deployment/
    │   │   ├── DEPLOYMENT_CHECKLIST.md
    │   │   └── CLEANUP_INSTRUCTIONS.md
    │   ├── guides/
    │   │   ├── PROJECT_ORGANIZATION.md
    │   │   └── RESPONSIVE_REFERENCE.md
    │   └── archive/ (old docs)
    ├── static/
    │   ├── css/
    │   └── videos/
    ├── templates/
    ├── scripts/
    ├── reports/
    └── tests/
    """)
    print("\nNext steps:")
    print("1. Review the organized structure")
    print("2. Read docs/START_HERE.md")
    print("3. Run: git init")
    print("4. Run: git add .")
    print("5. Run: git commit -m 'Initial commit'")
    print("6. Push to GitHub and deploy!")

if __name__ == "__main__":
    main()
