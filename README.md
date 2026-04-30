# 📚 Zotero Research Dashboard Generator

> Transform your Zotero annotations into a powerful, interactive research dashboard for comprehensive exams, literature reviews, and essay writing.

[![Made with Python](https://img.shields.io/badge/Made%20with-Python-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

<img width="2553" height="1361" alt="image" src="https://github.com/user-attachments/assets/b28e49d6-697d-4b99-a2f9-7244e9242c70" />



## 🎯 What is this?

This tool generates a **single-file HTML dashboard** from your Zotero database that helps you:

- 📝 **Organize** thousands of highlights into visual Kanban columns by category
- 🔍 **Filter** notes by folder, author, publication, year, category, and tags
- 📋 **Export** formatted notes and APA 7 citations for your essays
- 🏷️ **Track** paper-level tags (🔵) vs note-level tags (🔴) separately
- 📊 **Analyze** your research coverage with built-in statistics

**Perfect for:** PhD students, researchers, comprehensive exam prep, systematic literature reviews

---

## ✨ Features

### 📊 Three Powerful Views

| View | Purpose | Features |
|------|---------|----------|
| **📝 Kanban Notes** | Organize highlights by color | Color-coded columns, tag filtering, copy per-note |
| **📄 Abstracts** | Browse paper summaries | Full abstracts, search highlighting |
| **📚 Bibliography** | Reference management | Sortable table, quick citations |

### 🔧 Smart Filtering System

- **Multi-tag AND logic** - Select multiple tags to find notes with ALL selected tags
- **Cascading filters** - Options update based on your selections
- **Real-time search** - Highlights matching text across all fields
- **Search boxes** - Type to filter long dropdown lists instantly

### 📤 Export Functions

1. **📄 Export Notes** → Copy all filtered notes organized by paper and category
2. **📚 Copy Citations** → APA 7 bibliography of filtered papers, alphabetically sorted
3. **📋 Copy Citation** → Individual paper citation (button on each paper card)
4. **📋 Copy Note** → Individual note with full context (hover to reveal button)
5. **📊 Statistics** → Research overview with category breakdown and top tags

### 🏷️ Tag Visualization

- **🔵 Paper Tags** (blue) - Applied to entire papers in Zotero
- **🔴 Note Tags** (red/pink) - Applied to specific highlights
- **Visual distinction** helps you understand tag context at a glance

---

## 🚀 Quick Start

### Prerequisites

- **Zotero** installed with annotations in your library
- **Python 3.7+**
- **pandas** library

### Installation

```bash
# Install pandas
pip install pandas --break-system-packages

# Or without the flag on most systems
pip install pandas
```

### Basic Setup (3 steps)

#### 1️⃣ Download the Script

Save `zotero_dashboard_v2.5.0.py` to your computer.

#### 2️⃣ Configure Paths

Open the script and edit the top section:

```python
# Set your Zotero database location
ZOTERO_DB_PATH = os.path.expanduser("~/Zotero/zotero.sqlite")

# Where to save the HTML dashboard
OUTPUT_HTML_PATH = os.path.expanduser("~/Desktop/Zotero_Dashboard.html")
```

<details>
<summary><b>📁 Default paths by operating system</b></summary>

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

</details>

#### 3️⃣ Run the Script

```bash
python3 zotero_dashboard_v2.5.0.py
```

**That's it!** Open the generated HTML file in your browser.

---

## 🎨 Customizing Your Dashboard

### Understanding the Color System

The dashboard organizes your highlights into **categories** based on their **colors** in Zotero. You define the mapping.

#### Step 1: Find Your Zotero Colors

1. Open a PDF in Zotero
2. Highlight some text with a color
3. Look at the color picker - each color has a hex code like `#ffd400`
4. **Important:** Zotero has TWO shades per color (dark and light) - you need both

#### Step 2: Map Colors to Categories

Edit the `COLOR_MAPPING` section:

```python
COLOR_MAPPING = {
    # Yellow highlights → General concepts
    "#ffd400": "Yellow_General",    # Dark yellow
    "#faf4d1": "Yellow_General",    # Light yellow
    
    # Green highlights → Methodology  
    "#5fb236": "Green_Methods",     # Dark green
    "#e0f3d1": "Green_Methods",     # Light green
    
    # Your additional colors...
}
```

**Rules:**
- Category names use underscores: `Yellow_General` not `Yellow General`
- Both shades map to the same category
- Hex codes are case-insensitive (`#FFD400` = `#ffd400`)

#### Step 3: Customize Display Names

Edit the `CATEGORY_NAMES` section:

```python
CATEGORY_NAMES = {
    'Yellow_General': '💡 General Concepts',  # What users see
    'Green_Methods': '🔬 Methodology',
    # Emojis are optional but helpful!
}
```

#### Step 4: Set Display Order

Edit the `CATEGORY_ORDER` list:

```python
CATEGORY_ORDER = [
    'Yellow_General',   # Leftmost column in Kanban view
    'Green_Methods',    # Next column
    'Red_Critiques',    # Next column
    # ... order matters for visual organization
]
```

---

## 📋 Configuration Examples

### Example 1: Simple System (Beginners)

Minimal setup with just 3 categories:

```python
COLOR_MAPPING = {
    "#ffd400": "Important", "#faf4d1": "Important",
    "#5fb236": "Methods", "#e0f3d1": "Methods",
    "#ff6666": "Questions", "#fad1d5": "Questions",
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

Organized by thesis chapters:

```python
COLOR_MAPPING = {
    "#ffd400": "Theory", "#faf4d1": "Theory",
    "#5fb236": "Methods", "#e0f3d1": "Methods",
    "#e56eee": "Results", "#ffc4fb": "Results",
    "#a28ae5": "Discussion",
    "#ff6666": "Literature", "#fad1d5": "Literature",
}

CATEGORY_NAMES = {
    'Theory': '💭 Theoretical Framework',
    'Methods': '🔬 Research Methods',
    'Results': '📊 Key Findings',
    'Discussion': '💡 Analysis & Interpretation',
    'Literature': '📚 Literature Review',
}

CATEGORY_ORDER = ['Literature', 'Theory', 'Methods', 'Results', 'Discussion']
```

### Example 3: Comprehensive Exam Prep

Organized by exam topic areas:

```python
COLOR_MAPPING = {
    "#ffd400": "Theory1", "#faf4d1": "Theory1",          # Yellow
    "#5fb236": "Theory2", "#e0f3d1": "Theory2",          # Green
    "#e56eee": "Methods", "#ffc4fb": "Methods",          # Magenta
    "#a28ae5": "Empirical",                              # Purple
    "#ff6666": "Critiques", "#fad1d5": "Critiques",      # Red
    "#2ea8e5": "Future", "#f19837": "Important",         # Blue & Orange
}

CATEGORY_NAMES = {
    'Theory1': '🧠 Behavioral Ecology',
    'Theory2': '🌍 Conservation Biology',
    'Methods': '🔬 Research Methods',
    'Empirical': '📊 Case Studies',
    'Critiques': '⚠️ Critiques & Gaps',
    'Future': '🔮 Research Directions',
    'Important': '⭐ Exam-Critical',
}
```

---

## 💡 Usage Tips

### During Research Phase

1. **Be Consistent** - Use the same color for the same type of information across all papers
2. **Tag Strategically** - Add tags in Zotero for themes that cross color categories
3. **Use Both Tag Types**:
   - **Paper tags** 🔵 for broad themes (e.g., "primate behavior", "conservation")
   - **Note tags** 🔴 for specific points (e.g., "methodology critique", "key finding")

### While Writing

1. **Filter by multiple tags** to find notes spanning multiple themes
2. **Export filtered notes** to get an organized outline for a section
3. **Copy individual notes** as you write to maintain proper citations
4. **Use statistics** to identify under-researched areas

### Workflow Example

```
1. Writing a section on "foraging behavior in primates"
   ↓
2. Select tags: #foraging, #primates, #behavior
   ↓
3. Click "📄 Export Notes" → Get organized notes by paper
   ↓
4. Use as outline, copy individual notes as needed
   ↓
5. Click "📚 Copy Citations" → Paste into references
```

---

## 🔧 Troubleshooting

### Common Issues

<details>
<summary><b>❌ "Zotero database not found"</b></summary>

**Solutions:**
- Verify Zotero is installed
- Check the path in `ZOTERO_DB_PATH`
- Windows users: Use forward slashes `C:/Users/...` not `C:\Users\...`
- Try absolute path instead of `~` expansion
- Make sure you're pointing to `zotero.sqlite` not the Zotero application

</details>

<details>
<summary><b>❌ Empty columns or "No matching notes"</b></summary>

**Possible causes:**
1. **Wrong color mapping**
   - Your Zotero colors don't match `COLOR_MAPPING`
   - Missing the light or dark shade of a color
   - Solution: Highlight text in Zotero and check the exact hex codes

2. **Mismatched category names**
   - `COLOR_MAPPING` uses `"Yellow_General"`
   - But `CATEGORY_NAMES` uses `"yellow_general"` (different case!)
   - Solution: Category names must match EXACTLY (case-sensitive)

3. **Missing categories in order**
   - Categories defined but not in `CATEGORY_ORDER`
   - Solution: Add all categories to `CATEGORY_ORDER`

</details>

<details>
<summary><b>❌ "ModuleNotFoundError: No module named 'pandas'"</b></summary>

**Install pandas:**
```bash
# Fedora/Linux with externally managed Python
pip install pandas --break-system-packages

# Most other systems
pip install pandas

# Using pip3 explicitly
pip3 install pandas
```

</details>

<details>
<summary><b>❌ Colors appear but in wrong categories</b></summary>

**Check:**
1. Hex codes are correct (case doesn't matter)
2. Both light AND dark shades are mapped to the same category
3. No typos in category names between the three sections

**Debug approach:**
```python
# Add this temporarily after COLOR_MAPPING to see your colors
print("Colors in your mapping:", list(COLOR_MAPPING.keys()))
```

</details>

<details>
<summary><b>❌ Export/Copy buttons don't work</b></summary>

**Modern browsers required:**
- Chrome 63+
- Firefox 53+
- Safari 13.1+
- Edge 79+

**Clipboard permissions:**
- Some browsers require HTTPS for clipboard access
- Open the HTML file directly (not through file:// if possible)
- Try a different browser

</details>

---

## 📊 Understanding the Dashboard

### Note Card Anatomy

```
┌─────────────────────────────────────────────┐
│ 🔵 #primate-behavior  🔴 #diet-analysis     │ ← Tags
│ 🔵 #conservation                            │   (🔵 = Paper, 🔴 = Note)
├─────────────────────────────────────────────┤
│ "Primates in fragmented habitats exhibit   │ ← Your Highlight
│  reduced foraging efficiency..."            │
├─────────────────────────────────────────────┤
│ → Important for understanding habitat       │ ← Your Comment
│   quality impact on behavior                │
└─────────────────────────────────────────────┘
      ↑
   Copy button (appears on hover)
```

### Tag Filtering Logic

- **Single tag selected**: Shows notes with that tag
- **Multiple tags selected**: Shows notes with ALL selected tags (AND logic)
- **Paper tag (🔵)**: Matches any note from papers with that tag
- **Note tag (🔴)**: Matches only notes with that specific tag

---

## 🤝 Sharing with Colleagues

### Sharing Your Configuration

Want to help a colleague set up the same category system?

**Just share these 3 blocks from your script:**

```python
# 1. Color mapping
COLOR_MAPPING = {
    "#ffd400": "Yellow_General",
    # ... your mapping
}

# 2. Category names  
CATEGORY_NAMES = {
    'Yellow_General': '💡 General Concepts',
    # ... your names
}

# 3. Display order
CATEGORY_ORDER = [
    'Yellow_General',
    # ... your order
]
```

They can copy-paste these into their own script!

### Sharing the Dashboard (Read-Only)

The generated HTML file is **completely self-contained**. You can:

- ✅ Email it
- ✅ Put it on a shared drive
- ✅ Host it on a website
- ✅ Upload to Google Drive/Dropbox

**Note:** The recipient can view and search, but cannot modify your Zotero data (it's read-only).

---

## 🛡️ Privacy & Safety

### What the Script Does

✅ **Copies** your Zotero database to a temporary location  
✅ **Reads** annotations and metadata  
✅ **Generates** a standalone HTML file  
✅ **Deletes** the temporary copy  

### What the Script Does NOT Do

❌ **Never modifies** your original Zotero database  
❌ **Never uploads** your data anywhere  
❌ **Never requires** internet connection (works offline)  
❌ **Never installs** anything in Zotero  

### Best Practices

1. **Keep backups** - Zotero has built-in backup features, use them
2. **Test first** - Run on a small collection to verify it works
3. **Check permissions** - Ensure you have read access to Zotero database
4. **Secure your files** - The HTML contains all your notes, treat it accordingly

---

## 🎓 Advanced Usage

### Custom Color Schemes

You can create multiple configurations for different projects:

```bash
# Dissertation
python3 dashboard_dissertation.py

# Comprehensive exams
python3 dashboard_comps.py

# Course notes
python3 dashboard_teaching.py
```

Just duplicate the script and change the configuration!

### Automating Updates

**Linux/macOS:**
```bash
# Create a shell script
echo '#!/bin/bash
cd ~/Research
python3 zotero_dashboard_v2.5.0.py
echo "Dashboard updated!"
' > update_dashboard.sh

chmod +x update_dashboard.sh
./update_dashboard.sh
```

**Windows:**
```batch
REM Create update_dashboard.bat
@echo off
cd C:\Research
python zotero_dashboard_v2.5.0.py
echo Dashboard updated!
pause
```

### Integration with Writing Tools

The exported notes are plain text, perfect for:

- **Obsidian** - Copy notes directly into your vault
- **Notion** - Paste formatted notes into pages
- **Word/Google Docs** - Paste citations and notes
- **LaTeX** - Copy notes as comments in your .tex files

---

## 🐛 Getting Help

### Debug Mode

Add this after the imports to see what's happening:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Questions

**Q: Can I use this with Mendeley/EndNote?**  
A: No, this script is Zotero-specific. However, you can import your library into Zotero first.

**Q: Will this work with Zotero groups?**  
A: Yes! The script reads whatever is in your Zotero database, including group libraries.

**Q: Can I customize the HTML/CSS?**  
A: Yes! The HTML template is in the Python script. Search for `html_template = f'''` and modify the CSS section.

**Q: How often should I regenerate the dashboard?**  
A: Whenever you add new annotations. Since it's fast (usually <10 seconds), you can run it daily or after each reading session.

**Q: Can I filter by date added?**  
A: Not currently, but you can add a "Recent" tag to new papers in Zotero and filter by that.

---

## 📝 License & Attribution

**License:** MIT License - Free to use, modify, and share

**Citation:** If you use this in academic work, a mention is appreciated:
```
Ferreira Pereira, I. (2026). Zotero Research Dashboard Generator. 
GitHub repository.
```

---

## 🌟 Acknowledgments

Built with:
- Python 3
- pandas for data processing
- Vanilla JavaScript (no frameworks!)
- Love for research organization ❤️

Designed for researchers who:
- Have too many papers
- Love their highlights
- Need better ways to organize knowledge
- Value open-source tools

---

## 📮 Feedback & Contributions

Found a bug? Have a feature request? Want to share your configuration?

This tool is designed to be simple, focused, and maintainable. Contributions should keep that philosophy.

---

**Happy researching! 📚✨**

---

<div align="center">
<sub>Made with ☕ and 📖 by a researcher, for researchers</sub>
</div>
