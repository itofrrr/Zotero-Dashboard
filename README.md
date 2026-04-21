# Zotero Research Dashboard Generator

Transform your Zotero annotations into an interactive research dashboard for writing essays and comprehensive exams.

## Features

- 📋 **Kanban Notes View** - Organize highlights by color-coded categories
- 📄 **Abstracts View** - Browse paper abstracts
- 📚 **Bibliography View** - Sortable reference table
- 🔍 **Multi-Filter System** - Search by folder, title, author, publication, year, category, and tags
- 📋 **Export Functions** - Copy citations (APA 7), export notes, view statistics
- 🏷️ **Multi-Tag Selection** - Filter notes by multiple tags simultaneously

## Quick Start

### 1. Install Requirements

```bash
pip install pandas --break-system-packages
```

### 2. Configure the Script

Open `comps_dashboard_multitag.py` and edit the configuration section at the top:

#### Set Your Zotero Database Path

```python
# Default locations by OS:
# Windows: C:/Users/YourName/Zotero/zotero.sqlite
# macOS: ~/Zotero/zotero.sqlite
# Linux: ~/Zotero/zotero.sqlite

ZOTERO_DB_PATH = os.path.expanduser("~/Zotero/zotero.sqlite")
```

#### Set Output Location

```python
OUTPUT_HTML_PATH = os.path.expanduser("~/Desktop/Comps_Dashboard.html")
```

### 3. Customize Color Mapping

Match the script to YOUR Zotero highlight color scheme:

#### Finding Your Zotero Colors

1. In Zotero, highlight some text
2. Click the highlight color in the PDF reader
3. Note the hex color code (e.g., `#ffd400`)
4. Zotero has two shades per color - map both

#### Example Configuration

```python
COLOR_MAPPING = {
    # Yellow → General concepts (I use yellow for main ideas)
    "#ffd400": "Yellow_General",
    "#faf4d1": "Yellow_General",
    
    # Green → Methodology (I use green for methods)
    "#5fb236": "Green_Methods",
    "#e0f3d1": "Green_Methods",
    
    # Red → Critiques (I use red for problems/critiques)
    "#ff6666": "Red_Critiques",
    "#fad1d5": "Red_Critiques",
    
    # Add more colors as needed...
}
```

#### Customize Category Names

```python
CATEGORY_NAMES = {
    'Yellow_General': '💡 Main Ideas',      # Your custom name
    'Green_Methods': '🔬 Methods',
    'Red_Critiques': '⚠️ Problems',
}
```

#### Set Category Display Order

```python
CATEGORY_ORDER = [
    'Yellow_General',   # Leftmost column
    'Green_Methods',
    'Red_Critiques',    # Rightmost column
]
```

### 4. Run the Script

```bash
python3 comps_dashboard_multitag.py
```

The HTML dashboard will be created at your specified output location.

## Configuration Examples

### Example 1: Simple 3-Category System

```python
COLOR_MAPPING = {
    "#ffd400": "Important",
    "#faf4d1": "Important",
    "#5fb236": "Methods",
    "#e0f3d1": "Methods",
    "#ff6666": "Questions",
    "#fad1d5": "Questions",
}

CATEGORY_NAMES = {
    'Important': '⭐ Key Points',
    'Methods': '🔬 Methodology',
    'Questions': '❓ To Explore',
    'Uncategorized': '📝 Other'
}

CATEGORY_ORDER = ['Important', 'Methods', 'Questions', 'Uncategorized']
```

### Example 2: Dissertation Structure

```python
COLOR_MAPPING = {
    "#ffd400": "Theory",
    "#faf4d1": "Theory",
    "#5fb236": "Methods",
    "#e0f3d1": "Methods",
    "#e56eee": "Results",
    "#ffc4fb": "Results",
    "#a28ae5": "Discussion",
    "#ff6666": "Literature",
    "#fad1d5": "Literature",
}

CATEGORY_NAMES = {
    'Theory': '💭 Theoretical Framework',
    'Methods': '🔬 Methods',
    'Results': '📊 Findings',
    'Discussion': '💡 Analysis',
    'Literature': '📚 Literature Review',
}
```

### Example 3: Different OS Paths

**Windows:**
```python
ZOTERO_DB_PATH = "C:/Users/YourName/Zotero/zotero.sqlite"
OUTPUT_HTML_PATH = "C:/Users/YourName/Desktop/Dashboard.html"
```

**macOS:**
```python
ZOTERO_DB_PATH = os.path.expanduser("~/Zotero/zotero.sqlite")
OUTPUT_HTML_PATH = os.path.expanduser("~/Desktop/Dashboard.html")
```

**Linux:**
```python
ZOTERO_DB_PATH = os.path.expanduser("~/Zotero/zotero.sqlite")
OUTPUT_HTML_PATH = os.path.expanduser("~/Desktop/Dashboard.html")
```

## Using the Dashboard

### Filtering

- **Search boxes** - Type to filter folders, titles, authors, publications
- **Tags** - Select multiple tags to filter notes
- **Categories** - Filter by highlight color category
- **Text search** - Highlight matching text across all notes

### Export Features

1. **📄 Export Notes** - Copy all filtered notes to clipboard (organized by paper and category)
2. **📚 Copy Citations** - Generate APA 7 bibliography of filtered papers
3. **📋 Copy Citation** (per paper) - Copy individual paper citation
4. **📋 Copy** (per note) - Copy individual note with context
5. **📊 Statistics** - View overview of your research database

### Views

- **📝 My Kanban Notes** - Color-coded columns by category
- **📄 Abstracts** - Read paper abstracts
- **📚 Bibliography** - Sortable reference table

## Troubleshooting

### "Zotero database not found"

- Check that Zotero is installed
- Verify the path in `ZOTERO_DB_PATH`
- On Windows, use forward slashes: `C:/Users/...`

### "No matching notes" or empty columns

- Check your `COLOR_MAPPING` matches your Zotero colors
- Make sure both light and dark shades are mapped
- Check that category names match between `COLOR_MAPPING`, `CATEGORY_NAMES`, and `CATEGORY_ORDER`

### Colors don't match

- Zotero color codes are case-insensitive
- Both `#FFD400` and `#ffd400` will work
- The script automatically converts to lowercase

### Missing pandas

```bash
# Fedora/Linux
pip install pandas --break-system-packages

# Other systems
pip install pandas
```

## Tips for Best Results

1. **Be consistent** - Use the same colors for the same types of highlights
2. **Use tags** - Add tags to your Zotero annotations for finer filtering
3. **Organize folders** - Group papers by topic in Zotero collections
4. **Regular exports** - Run the script periodically as you add new annotations
5. **Backup** - The script copies your database safely, but always keep Zotero backups

## Sharing Your Configuration

Want to share your configuration with colleagues? Just share:
1. The `COLOR_MAPPING` dictionary
2. The `CATEGORY_NAMES` dictionary
3. The `CATEGORY_ORDER` list

They can paste these into their own copy of the script!

## Support

This script reads your Zotero database in read-only mode - it never modifies your Zotero data.

For issues or questions, check that:
- Your configuration section is properly formatted (commas, quotes, brackets)
- All category names match exactly between the three dictionaries
- File paths are correct for your operating system
