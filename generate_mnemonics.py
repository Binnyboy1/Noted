#!/usr/bin/env python3
"""
Windows-Optimized Vocabulary Mnemonic Generator
This script is specifically designed for Windows 10 users.

pip install google-generativeai python-dotenv --quiet
python generate_mnemonics.py
"""

import csv
import os
import time
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load variables from .env file into the environment
load_dotenv()

# Check for required modules and provide helpful error messages
try:
    import google.generativeai as genai
except ImportError:
    print("❌ Error: google-generativeai not found")
    print("Please install it by running:")
    print("pip install google-generativeai")
    print("\nPress any key to exit...")
    input()
    sys.exit(1)

def check_api_key():
    """Check if API key is available."""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY environment variable not set")
        print("\nTo set it up:")
        print("1. Go to https://makersuite.google.com/app/apikey")
        print("2. Create a new API key")
        print("3. Run this command in Command Prompt:")
        print("   set GOOGLE_API_KEY=your-api-key-here")
        print("\nPress any key to exit...")
        input()
        sys.exit(1)
    return api_key

def setup_gemini():
    """Initialize Gemini AI with API key."""
    api_key = check_api_key()
    genai.configure(api_key=api_key)
    # Use a current, valid model name like 'gemini-1.5-flash'
    return genai.GenerativeModel('gemini-1.5-flash')

def create_mnemonic_prompt(word: str, definition: str) -> str:
    """Create an optimized prompt for mnemonic generation."""
    return f"""Create a powerful mnemonic device for the vocabulary word "{word}" with definition "{definition}".

Instructions:
1. Use vivid, memorable imagery that connects to the word's meaning
2. Incorporate wordplay, rhymes, or phonetic similarities when possible  
3. Create a short story or visual scene (2-3 sentences max)
4. Make it personal and emotionally engaging
5. Include word breakdown if the word has meaningful roots/prefixes/suffixes

Format your response as just the mnemonic (no labels or extra text).

Example:
Word: "Gregarious" (sociable, enjoying company of others)
Response: Imagine Greg (gregarious) throwing a huge party - he's so social that he invites everyone in the neighborhood. The word starts with "Greg" who loves to "gather" people together.

Now create a mnemonic for: {word} - {definition}"""

def generate_mnemonic(model, word: str, definition: str, max_retries: int = 3) -> str:
    """Generate a mnemonic for a given word and definition."""
    prompt = create_mnemonic_prompt(word, definition)
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            mnemonic = response.text.strip()
            return mnemonic
        
        except Exception as e:
            print(f"   ⚠️  Attempt {attempt + 1} failed: {str(e)[:50]}...")
            if attempt < max_retries - 1:
                print("   🔄 Retrying in 2 seconds...")
                time.sleep(2)
            else:
                return f"Unable to generate mnemonic (API error)"

def find_csv_files():
    """Find CSV files in current directory."""
    current_dir = Path.cwd()
    csv_files = list(current_dir.glob("*.csv"))
    return csv_files

def select_csv_file():
    """Interactive CSV file selection."""
    csv_files = find_csv_files()
    
    if not csv_files:
        print("❌ No CSV files found in current directory")
        print(f"Current directory: {Path.cwd()}")
        print("\nPlease:")
        print("1. Create a CSV file with format: word,definition,mnemonic")
        print("2. Place it in this directory")
        print("3. Run the script again")
        print("\nPress any key to exit...")
        input()
        sys.exit(1)
    
    if len(csv_files) == 1:
        return str(csv_files[0])
    
    print("📁 Multiple CSV files found:")
    for i, file in enumerate(csv_files, 1):
        print(f"  {i}. {file.name}")
    
    while True:
        try:
            choice = input(f"\nSelect file (1-{len(csv_files)}): ").strip()
            index = int(choice) - 1
            if 0 <= index < len(csv_files):
                return str(csv_files[index])
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a number.")

def process_csv(input_file: str):
    """Process CSV file and generate mnemonics."""
    # Setup Gemini
    print("🔧 Initializing Gemini AI...")
    try:
        model = setup_gemini()
        print("✅ Gemini AI initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing Gemini: {e}")
        print("\nPress any key to exit...")
        input()
        return
    
    # Read CSV
    words_data = []
    try:
        with open(input_file, 'r', newline='', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            words_data = list(csv_reader)
    except FileNotFoundError:
        print(f"❌ Error: File '{input_file}' not found")
        print("\nPress any key to exit...")
        input()
        return
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        print("\nPress any key to exit...")
        input()
        return
    
    if not words_data:
        print("❌ No data found in CSV file")
        print("\nPress any key to exit...")
        input()
        return
    
    print(f"\n📚 Processing {len(words_data)} vocabulary words...")
    print("="*50)
    
    # Create backup
    backup_file = f"{input_file}.backup"
    try:
        with open(input_file, 'r', encoding='utf-8') as src, \
             open(backup_file, 'w', encoding='utf-8') as dst:
            dst.write(src.read())
        print(f"💾 Backup created: {backup_file}")
    except Exception as e:
        print(f"⚠️  Warning: Could not create backup: {e}")
    
    # Process each word
    updated_data = []
    processed_count = 0
    
    for i, row in enumerate(words_data):
        if len(row) < 2:
            print(f"⚠️  Skipping row {i+1}: insufficient data")
            updated_data.append(row)
            continue
        
        word = row[0].strip()
        definition = row[1].strip()
        existing_mnemonic = row[2].strip() if len(row) > 2 else ""
        
        print(f"\n🔄 Processing ({i+1}/{len(words_data)}): '{word}'")
        
        # Generate mnemonic if none exists or if it's empty
        if not existing_mnemonic:
            print("   🧠 Generating mnemonic...")
            mnemonic = generate_mnemonic(model, word, definition)
            
            # Truncate display for readability
            display_mnemonic = mnemonic[:80] + "..." if len(mnemonic) > 80 else mnemonic
            print(f"   ✨ Generated: {display_mnemonic}")
            processed_count += 1
            
            # Add delay to avoid rate limiting
            time.sleep(1.5)
        else:
            mnemonic = existing_mnemonic
            print("   📝 Using existing mnemonic")
        
        # Ensure we have exactly 3 columns
        updated_row = [word, definition, mnemonic]
        updated_data.append(updated_row)
    
    # Write updated CSV
    try:
        with open(input_file, 'w', newline='', encoding='utf-8') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerows(updated_data)
        
        print(f"\n{'='*50}")
        print(f"✅ Success! Generated {processed_count} new mnemonics")
        print(f"📁 Updated file: {input_file}")
        print(f"💾 Backup saved: {backup_file}")
        print(f"\n🎉 Ready to upload to your flashcard app!")
        
    except Exception as e:
        print(f"❌ Error writing CSV: {e}")
        print("🔄 Restoring from backup...")
        try:
            with open(backup_file, 'r', encoding='utf-8') as src, \
                 open(input_file, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
            print("✅ File restored from backup")
        except Exception as restore_error:
            print(f"❌ Could not restore backup: {restore_error}")

def main():
    print("🧠 Windows Vocabulary Mnemonic Generator")
    print("=" * 40)
    print(f"📁 Working directory: {Path.cwd()}")
    
    # Check if script was called with filename argument
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        if not os.path.exists(csv_file):
            print(f"❌ File not found: {csv_file}")
            csv_file = select_csv_file()
    else:
        csv_file = select_csv_file()
    
    print(f"\n📄 Selected file: {csv_file}")
    
    # Confirm before processing
    confirm = input("\nProceed with mnemonic generation? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("Operation cancelled.")
        return
    
    process_csv(csv_file)
    
    print("\nPress any key to exit...")
    input()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user")
        print("Press any key to exit...")
        input()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Press any key to exit...")
        input()