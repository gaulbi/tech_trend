```bash

python verify_chromadb.py

python verify_chromadb.py --date 2025-11-29

python verify_chromadb.py --category "ai_hardware"

python verify_chromadb.py --database-path /path/to/embedding --date 2025-11-30

python verify_chromadb.py --help
```

---

## 📊 What This Script Shows

The script will tell you:

1. **Collection Statistics**
   - Total number of documents
   - Whether collection is empty

2. **Sample Metadata**
   - Shows first 5 documents
   - Displays metadata structure
   - Shows content snippets

3. **Metadata Field Analysis**
   - Lists all metadata fields found
   - Checks if `category` and `embedding_date` exist

4. **Category Breakdown**
   - How many documents per category
   - All unique category values

5. **Date Breakdown**
   - How many documents per date
   - Highlights your target date with ⭐

6. **Filter Testing**
   - Tests each category + date combination
   - Shows which combinations return results
   - Shows which combinations return 0 results
   - For failed combinations, shows available dates

7. **Recommendations**
   - Tells you if embeddings exist for target date
   - Lists available categories for that date
   - Suggests solutions if data is missing

---

## 🎯 Example Output
```
======================================================================
ChromaDB Verification Script
======================================================================
Database Path: data/embedding
Collection: tech_trends
Target Date: 2025-11-30
======================================================================

✅ Connected to ChromaDB
✅ Found collection: tech_trends

----------------------------------------------------------------------
COLLECTION STATISTICS
----------------------------------------------------------------------
Total documents: 1500

----------------------------------------------------------------------
TESTING FILTERS FOR DATE: 2025-11-30
----------------------------------------------------------------------

Testing category + date combinations:
  ✅ ai_hardware + 2025-11-30: 45 results
  ⚠️  software_engineering + 2025-11-30: 0 results
      (Category exists but not for date 2025-11-30)
      Available dates: ['2025-11-29']