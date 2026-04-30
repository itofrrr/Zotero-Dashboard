# 📚 Zotero Research Dashboard Generator

> Transform your Zotero annotations into an interactive research dashboard for comprehensive exams, literature reviews, and writing.

[![Made with Python](https://img.shields.io/badge/Made%20with-Python-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Latest Release](https://img.shields.io/badge/version-2.5.0-brightgreen.svg)](https://github.com/itofrrr/Zotero-Dashboard/releases/latest)

---

<img width="2553" height="1361" alt="Dashboard preview showing Kanban board with research notes" src="https://github.com/user-attachments/assets/b28e49d6-697d-4b99-a2f9-7244e9242c70" />

---

## 🚀 Quick Start (3 Steps)

### 1. Install Python & Dependencies
Open a terminal and run:
```bash
pip install pandas
```

### 2. Download & Configure

1. Download [`zotero_dashboard_v2_5_0.py`](https://github.com/itofrrr/Zotero-Dashboard/releases/latest)
2. Open the file and edit these two lines (top of the script):

```python
ZOTERO_DB_PATH = "/path/to/your/Zotero/zotero.sqlite"
OUTPUT_HTML_PATH = "~/Desktop/Dashboard.html"
```

<details>
<summary>📁 Where is my Zotero database?</summary>

- **Windows:** `C:/Users/YourName/Zotero/zotero.sqlite`
- **macOS:** `~/Zotero/zotero.sqlite`
- **Linux:** `~/Zotero/zotero.sqlite`

Or in Zotero: Edit → Preferences → Advanced → Files and Folders → "Data Directory Location"
</details>

### 3. Run
Open a terminal and run:
```bash
python3 zotero_dashboard_v2_5_0.py
```

Open the generated HTML file. **Done!**

---

## 🎯 What Does This Do?

Generates a **single-file HTML dashboard** from your Zotero database that lets you:

| Feature | What It Does |
|---------|-------------|
| **📊 Kanban Board** | Organize highlights by color into visual columns |
| **🏷️ Dual Tag Filters** | Find notes by primary tags + co-occurring tags (AND logic) |
| **🔍 Smart Search** | Real-time filtering with text highlighting |
| **📋 Quick Export** | Copy formatted notes, APA citations, or individual highlights |
| **🌓 Three Themes** | Light, Dark, or Darker (AMOLED) modes |
| **🔗 Zotero Links** | Click papers/notes to open directly in Zotero |
| **📊 Three Views** | Notes (Kanban), Abstracts (summaries), Bibliography (table) |

**Some uses:** PhD students, comprehensive exams, systematic reviews, literature analysis

---

## ✨ Key Features

### 🏷️ Dual Tag Filtering System
- **Primary Filter:** Select your main topic tags
- **Secondary Filter:** Shows only tags that co-occur with primary selection
- **AND Logic:** Notes must have ALL selected tags
- **Case-Insensitive:** `Climate = climate = CLIMATE`

### 📝 Two Tag Types
- **🔵 Paper Tags** (blue) - Applied to entire papers in Zotero
- **🔴 Note Tags** (red/pink) - Applied to individual highlights
- Visual distinction helps you understand tag scope instantly

### 🔗 Zotero Integration
- Click any **paper title** → Opens paper in Zotero library
- Click any **note card** → Opens PDF at that exact annotation
- Seamless workflow between dashboard and source materials

### 🌓 Three Theme Modes
- **🌙 Light Mode** - Clean, bright interface
- **☀️ Dark Mode** - Comfortable dark grays
- **🌑 Darker Mode** - Pure black (AMOLED-friendly, saves battery)

### 📤 Export Options
1. **Export Notes** - All filtered notes organized by paper
2. **Copy Citations** - APA 7 bibliography of filtered papers
3. **Copy Note** - Individual note with context (hover button)
4. **Copy Citation** - Individual paper citation

---

## 🎨 Customization

### Color Categories

The dashboard organizes highlights by **color**. You map Zotero colors to custom categories.

**Example Configuration:**

```python
# Map Zotero colors to categories
COLOR_MAPPING = {
    "#ffd400": "Theory",    "#faf4d1": "Theory",     # Yellow
    "#5fb236": "Methods",   "#e0f3d1": "Methods",    # Green  
    "#ff6666": "Results",   "#fad1d5": "Results",    # Red
    "#a28ae5": "Discussion",                         # Purple
}

# Display names for each category
CATEGORY_NAMES = {
    'Theory': '💭 Theoretical Framework',
    'Methods': '🔬 Methodology',
    'Results': '📊 Key Findings',
    'Discussion': '💡 Analysis',
}

# Column order (left to right)
CATEGORY_ORDER = ['Theory', 'Methods', 'Results', 'Discussion']
```

**Note:** Each Zotero color has a dark and light shade - map both to the same category.

### Finding Your Colors

1. Open a PDF in Zotero
2. Highlight text with different colors
3. Note the hex codes from the color picker
4. Add both shades to `COLOR_MAPPING`

---

## 📋 Common Use Cases

### Comprehensive Exam Prep
```python
CATEGORY_NAMES = {
    'Theory1': '🧠 Behavioral Ecology',
    'Theory2': '🌍 Conservation Biology',
    'Methods': '🔬 Research Methods',
    'Empirical': '📊 Case Studies',
    'Critiques': '⚠️ Gaps & Limitations',
}
```

### Dissertation Structure
```python
CATEGORY_NAMES = {
    'Literature': '📚 Literature Review',
    'Theory': '💭 Theory',
    'Methods': '🔬 Methods',
    'Results': '📊 Results',
    'Discussion': '💡 Discussion',
}
```

### Simple 3-Category System
```python
CATEGORY_NAMES = {
    'Important': '⭐ Key Points',
    'Methods': '🔬 Methodology',
    'Questions': '❓ To Explore',
}
```

---

## 💡 Workflow Tips

### During Reading
1. **Use consistent colors** - Same color = same type of information
2. **Tag strategically** in Zotero:
   - **Paper tags** 🔵 for broad themes (`conservation`, `primates`)
   - **Note tags** 🔴 for specific points (`methodology-critique`, `key-finding`)

### While Writing
1. Select multiple tags to find intersecting themes
2. Export filtered notes as an organized outline
3. Copy individual notes with citations as you write
4. Use bibliography view to generate reference lists

### Example Workflow
```
Writing about "primate foraging behavior"
  ↓
Select tags: #foraging + #primates + #behavior
  ↓
Export Notes → Organized outline by paper
  ↓
Copy individual notes while writing
  ↓
Copy Citations → Paste into references
```

---

## 🔧 Troubleshooting

### "Database not found"
- Check `ZOTERO_DB_PATH` points to `zotero.sqlite`
- Windows: Use forward slashes `C:/Users/...`
- Find location: Zotero → Edit → Preferences → Advanced → Data Directory

### Empty columns
- Your Zotero colors don't match `COLOR_MAPPING`
- Check both light AND dark shades are mapped
- Category names must match exactly (case-sensitive)

### No matching notes
- Verify category names in `COLOR_MAPPING`, `CATEGORY_NAMES`, and `CATEGORY_ORDER` match exactly
- Check filters aren't too restrictive (try "All" in dropdowns)

### Copy/Export buttons don't work
- Use a modern browser (Chrome 63+, Firefox 53+, Safari 13.1+)
- Open HTML file directly (don't view source)
- Check browser clipboard permissions

### ModuleNotFoundError: pandas
```bash
# Linux/Fedora
pip install pandas --break-system-packages

# Most systems
pip install pandas
```

---

## 🛡️ Privacy & Safety

**What it does:**
- ✅ Reads your Zotero database (read-only)
- ✅ Generates a standalone HTML file
- ✅ Works completely offline

**What it doesn't do:**
- ❌ Never modifies your Zotero database
- ❌ Never uploads data anywhere
- ❌ Never requires internet connection
- ❌ No installation in Zotero required

The generated HTML file is self-contained and portable - safe to share, email, or backup.

---

## 📊 Advanced Features

### Multiple Dashboards
Create separate configurations for different projects:

```bash
# Dissertation
python3 dashboard_dissertation.py

# Comps
python3 dashboard_comps.py

# Teaching
python3 dashboard_teaching.py
```

### Automation (Optional)

**Linux/macOS:**
```bash
#!/bin/bash
cd ~/Research
python3 zotero_dashboard_v2_5_0.py
echo "Dashboard updated!"
```

**Windows:**
```batch
@echo off
cd C:\Research
python zotero_dashboard_v2_5_0.py
pause
```

---

## 📝 System Requirements

- **Python:** 3.6 or higher
- **Dependencies:** pandas
- **Zotero:** Any version with annotations
- **Browser:** Chrome 63+, Firefox 53+, Safari 13.1+, Edge 79+

**Platforms:** Windows, macOS, Linux

---

## 🆕 What's New in v2.5.0

### 🌑 Triple Theme System
- Light, Dark, and Darker modes
- Click theme button to cycle through all three
- Darker mode: Pure black backgrounds for AMOLED displays

### 🔗 Zotero Integration (v2.4.x)
- Click paper titles to open in Zotero
- Click note cards to open PDF at exact annotation
- URI scheme integration for seamless workflow

### 🏷️ Enhanced Tag Filtering (v2.3.0)
- Dual tag filters: Primary + Secondary co-occurring
- Case-insensitive tag matching
- Visual tag indicators (🔵 Paper / 🔴 Note)

[See full changelog](https://github.com/itofrrr/Zotero-Dashboard/releases)

---

## 🤝 Contributing

Found a bug? Have a feature idea? Contributions welcome!


---

## 📄 License

MIT License - Free to use, modify, and distribute.

**Academic Citation:**
```
Ferreira Pereira, I. (2026). Zotero Research Dashboard Generator. 
GitHub: https://github.com/itofrrr/Zotero-Dashboard
```

---

## 🙏 Acknowledgments

Built for researchers who:
- Manage hundreds of papers
- Love highlighting but hate disorganization  
- Need better tools for literature synthesis
- Value open-source, offline-first software

**Made with:** Python, pandas, vanilla JavaScript, and ☕

---

<div align="center">

**Happy readings with your research! 📚✨**

<sub>Built by a researcher while procrastinating work, so that others don't have to </sub>

</div>
