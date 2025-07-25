#!/usr/bin/env python3
"""
Pre-deployment checklist for Personality Test
"""

import os
import json
import sys

def check_file_exists(filename, description):
    """Check if a file exists"""
    if os.path.exists(filename):
        print(f"✅ {description}: {filename}")
        return True
    else:
        print(f"❌ {description}: {filename} - MISSING!")
        return False

def check_json_valid(filename):
    """Check if JSON file is valid"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            json.load(f)
        print(f"✅ JSON valid: {filename}")
        return True
    except Exception as e:
        print(f"❌ JSON invalid: {filename} - {e}")
        return False

def main():
    print("🚀 Personality Test - Pre-deployment Check")
    print("=" * 50)
    
    all_good = True
    
    # Check required files
    required_files = [
        ("requirements_irt.txt", "Python requirements"),
        ("package.json", "Node.js package file"),
        ("simple_backend.py", "Backend server"),
        ("src/App.js", "React main component"),
        ("src/App.css", "Application styles"),
        ("public/index.html", "HTML template"),
        ("public/admin.html", "Admin dashboard"),
        (".gitignore", "Git ignore file"),
        ("README.md", "Project documentation")
    ]
    
    print("\n📁 Checking required files...")
    for filename, description in required_files:
        if not check_file_exists(filename, description):
            all_good = False
    
    # Check JSON files
    json_files = ["package.json"]
    print("\n📋 Checking JSON files...")
    for filename in json_files:
        if os.path.exists(filename):
            if not check_json_valid(filename):
                all_good = False
    
    # Check Python imports
    print("\n🐍 Checking Python dependencies...")
    try:
        import fastapi
        import uvicorn
        import pydantic
        print("✅ FastAPI dependencies available")
    except ImportError as e:
        print(f"❌ Python dependency missing: {e}")
        all_good = False
    
    # Check if Git is initialized
    print("\n📦 Checking Git status...")
    if os.path.exists(".git"):
        print("✅ Git repository initialized")
    else:
        print("⚠️  Git not initialized - run 'git init' first")
    
    # Summary
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 All checks passed! Ready for deployment!")
        print("\nNext steps:")
        print("1. Run: git add .")
        print("2. Run: git commit -m 'Ready for deployment'")
        print("3. Create GitHub repository")
        print("4. Push to GitHub")
        print("5. Deploy on Render")
        print("\nSee DEPLOYMENT-GUIDE.md for detailed instructions")
    else:
        print("❌ Some issues need to be fixed before deployment")
        print("Please resolve the issues above and run this check again")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())
