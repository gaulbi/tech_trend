#!/usr/bin/env python3
"""
Diagnostic script to identify directory structure issues.
Run this to see what's actually in your data directory.
"""
import yaml
from pathlib import Path
from datetime import date


def diagnose_structure():
    """Diagnose the directory structure."""
    
    print("=" * 70)
    print("DIRECTORY STRUCTURE DIAGNOSTIC")
    print("=" * 70)
    
    # Load config
    config_path = Path('config.yaml')
    if not config_path.exists():
        print("❌ config.yaml not found!")
        return
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    base_path = Path(config['tech-trend-analysis']['analysis-report'])
    print(f"\n1. Base Path: {base_path.absolute()}")
    print(f"   Exists: {base_path.exists()}")
    
    if not base_path.exists():
        print(f"   ❌ Base directory does not exist!")
        print(f"   Create it with: mkdir -p {base_path}")
        return
    
    # List feed dates
    print(f"\n2. Feed Date Directories:")
    feed_dates = sorted([d for d in base_path.iterdir() if d.is_dir()])
    
    if not feed_dates:
        print(f"   ❌ No feed date directories found!")
        print(f"   Expected structure: {base_path}/YYYY-MM-DD/")
        return
    
    for feed_date_dir in feed_dates:
        print(f"   ✓ {feed_date_dir.name}")
    
    # Check today's date
    today = date.today().strftime('%Y-%m-%d')
    today_path = base_path / today
    print(f"\n3. Today's Date ({today}):")
    print(f"   Path: {today_path}")
    print(f"   Exists: {today_path.exists()}")
    
    if not today_path.exists():
        print(f"   ℹ️  Using most recent date: {feed_dates[-1].name}")
        check_date = feed_dates[-1]
    else:
        check_date = today_path
    
    # Check categories - CORRECTED: Look for .json files directly
    print(f"\n4. Categories in {check_date.name}:")
    json_files = list(check_date.glob('*.json'))
    
    if not json_files:
        print(f"   ❌ No JSON files found!")
        print(f"   Expected structure: {check_date}/{{category_name}}.json")
        all_files = list(check_date.iterdir())
        print(f"   Files in directory: {[f.name for f in all_files]}")
        return
    
    for json_file in json_files:
        category_name = json_file.stem
        print(f"\n   📄 {json_file.name} (Category: {category_name})")
        print(f"      Size: {json_file.stat().st_size} bytes")
        
        # Validate JSON structure
        try:
            import json
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            print(f"      ✓ Valid JSON")
            print(f"      ✓ Category: {data.get('category', 'N/A')}")
            print(f"      ✓ Trends: {len(data.get('trends', []))}")
            
            if data.get('trends'):
                trend = data['trends'][0]
                print(f"      ✓ Sample trend: {trend.get('topic', 'N/A')}")
                print(f"         - score: {trend.get('score', 'N/A')}")
                print(f"         - keywords: {len(trend.get('search_keywords', []))}")
            
        except json.JSONDecodeError as e:
            print(f"      ❌ Invalid JSON: {str(e)}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    valid_categories = []
    for json_file in json_files:
        try:
            import json as json_module
            with open(json_file, 'r') as f:
                data = json_module.load(f)
            if 'category' in data and 'trends' in data:
                valid_categories.append(json_file.stem)
        except:
            pass
    
    if valid_categories:
        print(f"✓ Found {len(valid_categories)} valid categories:")
        for cat in valid_categories:
            print(f"  - {cat}")
        print(f"\nYou can run:")
        print(f"  python article-generator.py --feed_date {check_date.name}")
        print(f"  python article-generator.py --feed_date {check_date.name} --category {valid_categories[0]}")
    else:
        print("❌ No valid categories found!")
        print("\nExpected structure:")
        print(f"  {base_path}/")
        print(f"    └── YYYY-MM-DD/")
        print(f"        ├── category1.json")
        print(f"        ├── category2.json")
        print(f"        └── category3.json")


if __name__ == '__main__':
    try:
        diagnose_structure()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()