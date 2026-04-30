#!/usr/bin/env python3
"""
Zotero Research Dashboard Generator
====================================================
Generates an interactive HTML dashboard from your Zotero annotations.

Features:
- Kanban-style notes organized by highlight color
- Separate visualization of Paper Tags (blue) vs Note Tags (pink)
- Dual tag filtering: Primary + Secondary co-occurring tags with AND logic
- Case-insensitive tag matching (Climate = climate = CLIMATE)
- Three theme modes: Light, Dark, and Darker (AMOLED-friendly)
- Clickable links to open papers and annotations directly in Zotero
- Export functions: notes, APA 7 citations, statistics
- Per-note and per-paper copy buttons
- Real-time search with highlighting
- Three views: Notes, Abstracts, Bibliography

Author: Italo Ferreira Pereira
Version: 2.5.0 (April 2026)
"""

import sqlite3
import pandas as pd
import shutil
import os
import json
import sys

# ═══════════════════════════════════════════════════════════════════════════
# 🔧 USER CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

# PATHS
ZOTERO_DB_PATH = os.path.expanduser("~/Zotero/zotero.sqlite")
OUTPUT_HTML_PATH = os.path.expanduser("~/Desktop/Comps_Dashboard.html")
TEMP_DIR = os.path.expanduser("~/Documents/Zotero_Dashboard")

# COLOR MAPPING (Zotero highlight colors → Your categories)
COLOR_MAPPING = {
    "#ffd400": "Yellow_General",
    "#faf4d1": "Yellow_General",
    "#5fb236": "Green_Methods",
    "#e0f3d1": "Green_Methods",
    "#e56eee": "Magenta_Results",
    "#ffc4fb": "Magenta_Results",
    "#a28ae5": "Purple_Discussion",
    "#ff6666": "Red_Critiques_Refs",
    "#fad1d5": "Red_Critiques_Refs",
    "#2ea8e5": "Blue_Future",
    "#f19837": "Orange_Important",
    "#aaaaaa": "Gray_Glossary",
}

# CATEGORY NAMES (how they appear in dashboard)
CATEGORY_NAMES = {
    'Yellow_General':      '💡 General Concepts',
    'Green_Methods':       '🔬 Methodology',
    'Magenta_Results':     '📊 Results',
    'Purple_Discussion':   '💭 Discussion',
    'Red_Critiques_Refs':  '⚠️ Critiques & Refs',
    'Blue_Future':         '🔮 Future Directions',
    'Orange_Important':    '⭐ Key Insights',
    'Gray_Glossary':       '📖 Glossary',
    'Uncategorized':       '❓ Uncategorized'
}

# CATEGORY COLORS (for visual display)
CATEGORY_COLORS = {
    'Yellow_General':     '#f1c40f',
    'Green_Methods':      '#2ecc71',
    'Magenta_Results':    '#e56eee',
    'Purple_Discussion':  '#9c27b0',
    'Red_Critiques_Refs': '#e74c3c',
    'Blue_Future':        '#3498db',
    'Orange_Important':   '#e67e22',
    'Gray_Glossary':      '#95a5a6',
    'Uncategorized':      '#bdc3c7'
}

# DISPLAY ORDER (left to right in Kanban view)
CATEGORY_ORDER = [
    'Yellow_General', 'Green_Methods', 'Magenta_Results',
    'Purple_Discussion', 'Red_Critiques_Refs', 'Blue_Future',
    'Orange_Important', 'Gray_Glossary', 'Uncategorized'
]

# ═══════════════════════════════════════════════════════════════════════════
# END OF USER CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

print("="*80)
print("ZOTERO RESEARCH DASHBOARD GENERATOR v4.0")
print("="*80)
print(f"\nDatabase: {ZOTERO_DB_PATH}")
print(f"Output: {OUTPUT_HTML_PATH}")
print(f"Categories: {len(CATEGORY_NAMES)}\n")

# Validate paths
if not os.path.exists(ZOTERO_DB_PATH):
    print(f"❌ ERROR: Zotero database not found at: {ZOTERO_DB_PATH}")
    print("\nPlease edit ZOTERO_DB_PATH in the configuration section.")
    sys.exit(1)

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(os.path.dirname(OUTPUT_HTML_PATH), exist_ok=True)

# Copy database safely
temp_db_path = os.path.join(TEMP_DIR, "zotero_temp.sqlite")
print("📋 Copying database...")
shutil.copy2(ZOTERO_DB_PATH, temp_db_path)
conn = sqlite3.connect(temp_db_path)

# SQL Query with Paper Tags and Note Tags separated
query_notes = """
SELECT
    c.collectionName AS Topic_Folder,
    MAX(CASE WHEN f.fieldName = 'title' THEN dv.value END) AS Title,
    MAX(CASE WHEN f.fieldName = 'date' THEN dv.value END)  AS Year,
    MAX(CASE WHEN f.fieldName = 'publicationTitle' THEN dv.value END) AS Publication,
    (SELECT GROUP_CONCAT(cr.lastName, ', ')
       FROM itemCreators ic
       JOIN creators cr ON ic.creatorID = cr.creatorID
      WHERE ic.itemID = parent.itemID) AS Authors,
    ann.color,
    (SELECT GROUP_CONCAT(t.name, ', ')
       FROM itemTags it
       JOIN tags t ON it.tagID = t.tagID
      WHERE it.itemID = parent.itemID) AS Paper_Tags,
    (SELECT GROUP_CONCAT(t.name, ', ')
       FROM itemTags it
       JOIN tags t ON it.tagID = t.tagID
      WHERE it.itemID = ann.itemID) AS Note_Tags,
    ann.text    AS Highlight,
    ann.comment AS My_Comment,
    parent.key  AS Paper_Key,
    attachItem.key AS PDF_Attachment_Key,
    (SELECT key FROM items WHERE itemID = ann.itemID) AS Annotation_Item_Key
FROM items parent
JOIN itemAttachments att     ON parent.itemID = att.parentItemID
JOIN items attachItem        ON att.itemID = attachItem.itemID
JOIN itemAnnotations ann     ON attachItem.itemID = ann.parentItemID
LEFT JOIN collectionItems ci ON parent.itemID = ci.itemID
LEFT JOIN collections c      ON ci.collectionID = c.collectionID
LEFT JOIN itemData pd        ON parent.itemID = pd.itemID
LEFT JOIN fields f           ON pd.fieldID    = f.fieldID
LEFT JOIN itemDataValues dv  ON pd.valueID    = dv.valueID
WHERE ann.text IS NOT NULL OR ann.comment IS NOT NULL
GROUP BY parent.itemID, ann.itemID, c.collectionName
"""

query_abstracts = """
SELECT
    c.collectionName AS Topic_Folder,
    MAX(CASE WHEN f.fieldName = 'title' THEN dv.value END) AS Title,
    MAX(CASE WHEN f.fieldName = 'date' THEN dv.value END)  AS Year,
    MAX(CASE WHEN f.fieldName = 'publicationTitle' THEN dv.value END) AS Publication,
    (SELECT GROUP_CONCAT(cr.lastName, ', ')
       FROM itemCreators ic
       JOIN creators cr ON ic.creatorID = cr.creatorID
      WHERE ic.itemID = parent.itemID) AS Authors,
    MAX(CASE WHEN f.fieldName = 'abstractNote' THEN dv.value END) AS Abstract,
    parent.key AS Paper_Key
FROM items parent
LEFT JOIN collectionItems ci ON parent.itemID = ci.itemID
LEFT JOIN collections c      ON ci.collectionID = c.collectionID
LEFT JOIN itemData pd        ON parent.itemID = pd.itemID
LEFT JOIN fields f           ON pd.fieldID    = f.fieldID
LEFT JOIN itemDataValues dv  ON pd.valueID    = dv.valueID
GROUP BY parent.itemID, c.collectionName
HAVING MAX(CASE WHEN f.fieldName = 'abstractNote' THEN dv.value END) IS NOT NULL
"""

print("🔍 Querying database...")
df_notes = pd.read_sql_query(query_notes, conn)
df_abstracts = pd.read_sql_query(query_abstracts, conn)
conn.close()
os.remove(temp_db_path)

# Data normalization
print("🔧 Processing data...")
df_notes["Year"] = df_notes["Year"].str.extract(r"(\d{4})").fillna("Unknown")
df_abstracts["Year"] = df_abstracts["Year"].str.extract(r"(\d{4})").fillna("Unknown")

df_notes["Category"] = (
    df_notes["color"]
    .str.strip()
    .str.lower()
    .map({k.lower(): v for k, v in COLOR_MAPPING.items()})
    .fillna("Uncategorized")
)

df_notes.fillna("", inplace=True)
df_abstracts.fillna("", inplace=True)

print(f"✅ Found {len(df_notes)} notes from {df_notes['Title'].nunique()} papers")
print(f"✅ Found {len(df_abstracts)} abstracts")

# Prepare JSON for HTML
notes_json = json.dumps(df_notes.to_dict(orient="records"), ensure_ascii=False)
abstracts_json = json.dumps(df_abstracts.to_dict(orient="records"), ensure_ascii=False)
cat_mapping_js = json.dumps(CATEGORY_NAMES)
cat_colors_js = json.dumps(CATEGORY_COLORS)
cat_order_js = json.dumps(CATEGORY_ORDER)

# Generate HTML
print("📝 Generating HTML...")

html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Research Dashboard</title>
<style>
* {{box-sizing:border-box;-webkit-tap-highlight-color:transparent}}
body {{touch-action:pan-x pan-y}}

:root {{
  --bg-primary: #f0f2f5;
  --bg-secondary: #fff;
  --bg-tertiary: #f8f9fa;
  --bg-input: #fcfcfc;
  --bg-hover: #ebeef2;
  --text-primary: #2c3e50;
  --text-secondary: #7f8c8d;
  --text-muted: #999;
  --border-color: #e0e0e0;
  --border-light: #eee;
  --shadow-sm: rgba(0,0,0,.08);
  --shadow-md: rgba(0,0,0,.04);
  --accent-blue: #2196f3;
  --accent-dark: #34495e;
  --highlight-bg: #fff176;
  --highlight-text: #000;
  --note-bg: #fdfbf7;
  --note-border: #e8e0d0;
  --comment-bg: #f0f7ff;
  --comment-border: #c4ddf1;
  --tag-paper-bg: #e8f4f8;
  --tag-paper-text: #2980b9;
  --tag-note-bg: #f9ebea;
  --tag-note-text: #c0392b;
}}

body.dark-mode {{
  --bg-primary: #1a1a1a;
  --bg-secondary: #2d2d2d;
  --bg-tertiary: #3a3a3a;
  --bg-input: #242424;
  --bg-hover: #404040;
  --text-primary: #e0e0e0;
  --text-secondary: #b0b0b0;
  --text-muted: #808080;
  --border-color: #404040;
  --border-light: #4a4a4a;
  --shadow-sm: rgba(0,0,0,.3);
  --shadow-md: rgba(0,0,0,.2);
  --accent-blue: #42a5f5;
  --accent-dark: #5a6c7d;
  --highlight-bg: #ffd54f;
  --highlight-text: #000;
  --note-bg: #3a3530;
  --note-border: #5a5040;
  --comment-bg: #2d3a4a;
  --comment-border: #4a5a6a;
  --tag-paper-bg: #2d4a5a;
  --tag-paper-text: #64b5f6;
  --tag-note-bg: #4a2d2d;
  --tag-note-text: #ef5350;
}}

body.darker-mode {{
  --bg-primary: #000000;
  --bg-secondary: #0a0a0a;
  --bg-tertiary: #151515;
  --bg-input: #0d0d0d;
  --bg-hover: #1f1f1f;
  --text-primary: #e8e8e8;
  --text-secondary: #a0a0a0;
  --text-muted: #707070;
  --border-color: #2a2a2a;
  --border-light: #333333;
  --shadow-sm: rgba(0,0,0,.5);
  --shadow-md: rgba(0,0,0,.4);
  --accent-blue: #42a5f5;
  --accent-dark: #4a5a6a;
  --highlight-bg: #ffeb3b;
  --highlight-text: #000;
  --note-bg: #1a1510;
  --note-border: #3a3020;
  --comment-bg: #0f1a25;
  --comment-border: #2a3a4a;
  --tag-paper-bg: #1a2a35;
  --tag-paper-text: #64b5f6;
  --tag-note-bg: #2a1515;
  --tag-note-text: #ef5350;
}}

body {{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg-primary);margin:0;display:flex;height:100vh;overflow:hidden;color:var(--text-primary);transition:background .3s,color .3s}}
#sidebar {{flex:0 0 300px;background:var(--bg-secondary);padding:20px 18px;box-shadow:2px 0 8px var(--shadow-sm);overflow-y:auto;z-index:10;border-right:1px solid var(--border-color)}}
#sidebar h2 {{margin:0 0 16px;font-size:17px;letter-spacing:.3px;color:var(--text-primary)}}
.dark-mode-toggle {{width:100%;padding:8px;background:var(--bg-tertiary);border:1px solid var(--border-color);border-radius:6px;cursor:pointer;text-align:center;font-weight:600;font-size:12px;margin-bottom:12px;color:var(--text-primary);transition:.15s;touch-action:manipulation}}
.dark-mode-toggle:hover {{background:var(--bg-hover)}}
.btn-group button {{display:block;width:100%;padding:10px 12px;margin-bottom:6px;background:var(--bg-tertiary);border:1px solid var(--border-color);border-radius:6px;cursor:pointer;text-align:left;font-weight:600;font-size:13px;transition:.15s;color:var(--text-secondary);touch-action:manipulation}}
.btn-group button.active {{background:var(--accent-dark);color:#fff;border-color:var(--accent-dark)}}
.btn-group button:hover:not(.active) {{background:var(--bg-hover)}}
.filter-group {{margin-top:12px}}
.filter-group label {{display:block;font-size:10px;font-weight:700;color:var(--text-secondary);margin-bottom:4px;text-transform:uppercase;letter-spacing:.6px}}
.filter-group select,.filter-group input {{width:100%;padding:7px 8px;border-radius:5px;border:1px solid var(--border-color);font-size:12.5px;background:var(--bg-input);color:var(--text-primary);touch-action:manipulation}}
.filter-group select {{margin-top:4px}}
.filter-search-box {{width:100%;padding:5px 8px;border:1px solid var(--border-color);border-radius:4px;font-size:11px;margin-bottom:4px;background:var(--bg-input);font-family:inherit;color:var(--text-primary)}}
.filter-search-box::placeholder {{color:var(--text-muted);font-style:italic}}
#tag-filter, #tag-filter-2 {{width:100%;padding:4px;border-radius:5px;border:1px solid var(--border-color);font-size:11.5px;background:var(--bg-input);max-height:300px;margin-top:4px;color:var(--text-primary)}}
#tag-filter option, #tag-filter-2 option {{padding:5px 8px;border-radius:3px;margin-bottom:2px}}
#tag-filter option:checked, #tag-filter-2 option:checked {{background:var(--accent-blue);color:#fff;font-weight:600}}
.clear-btn,.export-btn {{margin-top:8px;width:100%;padding:8px;background:#3498db;color:#fff;border:none;border-radius:6px;cursor:pointer;font-weight:700;font-size:11px;touch-action:manipulation}}
.clear-btn {{background:#e74c3c}}
.clear-btn:hover {{background:#c0392b}}
.export-btn:hover {{background:#2980b9}}
#main {{flex:1;padding:24px 28px;overflow-y:auto}}
mark {{background:var(--highlight-bg);color:var(--highlight-text);padding:0 2px;border-radius:2px;font-weight:700}}
.paper-group {{background:var(--bg-secondary);padding:22px;margin-bottom:26px;border-radius:10px;box-shadow:0 2px 6px var(--shadow-md);border-top:4px solid var(--accent-dark);min-width:min-content;position:relative}}
.paper-group h3 {{margin:0 0 6px;font-size:16px;line-height:1.35;padding-right:80px;color:var(--text-primary)}}
.zotero-link {{color:var(--text-primary);text-decoration:none;cursor:pointer;transition:.2s;touch-action:manipulation}}
.zotero-link:hover {{color:var(--accent-blue);text-decoration:underline}}
.open-in-zotero {{display:inline-block;margin-left:8px;font-size:.75em;color:var(--text-secondary);font-weight:normal;opacity:.6;transition:.2s;touch-action:manipulation}}
.open-in-zotero:hover {{opacity:1;color:var(--accent-blue)}}
.note-card {{background:var(--bg-secondary);border:1px solid var(--border-color);border-left:5px solid var(--border-color);border-radius:7px;padding:13px;margin-bottom:12px;box-shadow:0 1px 3px var(--shadow-md);position:relative;cursor:pointer;transition:.2s}}
.note-card:hover {{box-shadow:0 2px 8px var(--shadow-sm);transform:translateY(-1px)}}
.paper-meta {{font-size:.85em;color:var(--text-secondary);margin-bottom:16px;border-bottom:1px solid var(--border-light);padding-bottom:12px;line-height:1.45}}
.copy-citation-btn {{position:absolute;top:20px;right:20px;padding:6px 12px;background:#3498db;color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:11px;font-weight:600;transition:.2s;touch-action:manipulation}}
.copy-citation-btn:hover {{background:#2980b9;transform:translateY(-1px)}}
.copy-citation-btn:active {{transform:translateY(0)}}
.kanban-board {{display:flex;gap:16px;overflow-x:auto;padding-bottom:12px;align-items:flex-start}}
.kanban-column {{flex:0 0 360px;background:var(--bg-tertiary);border-radius:8px;padding:14px;border-top:5px solid var(--border-color);max-height:720px;overflow-y:auto}}
.kanban-column h4 {{border-bottom:1px solid var(--border-color);padding-bottom:8px;margin:0 0 12px;font-size:13px;display:flex;justify-content:space-between;align-items:center;color:var(--text-primary)}}
.copy-note-btn {{position:absolute;top:8px;right:8px;padding:4px 8px;background:#95a5a6;color:#fff;border:none;border-radius:3px;cursor:pointer;font-size:10px;font-weight:600;opacity:0;transition:.2s;z-index:2;touch-action:manipulation}}
.note-card:hover .copy-note-btn {{opacity:1}}
.copy-note-btn:hover {{background:#7f8c8d}}
.tag {{display:inline-block;padding:3px 9px;border-radius:12px;font-size:.78em;margin-bottom:8px;margin-right:4px;font-weight:600;border:1px solid transparent}}
.paper-tag {{background:var(--tag-paper-bg);color:var(--tag-paper-text);border-color:var(--tag-paper-bg)}}
.note-tag {{background:var(--tag-note-bg);color:var(--tag-note-text);border-color:var(--tag-note-bg)}}
.tag.highlighted {{background:var(--accent-dark);color:#fff;border-color:var(--accent-dark);box-shadow:0 0 4px rgba(0,0,0,0.15)}}
.tag-count {{background:var(--accent-dark);color:#fff;padding:2px 6px;border-radius:8px;font-size:.75em;margin-left:4px;font-weight:700}}
.highlight-box {{background:var(--note-bg);padding:10px 12px;border:1px solid var(--note-border);font-style:italic;color:var(--text-primary);font-size:.92em;margin-bottom:8px;border-radius:4px;line-height:1.55}}
.comment-box {{background:var(--comment-bg);padding:10px 12px;border:1px solid var(--comment-border);color:var(--text-primary);font-size:.92em;border-radius:4px;border-left:3px solid #3498db;line-height:1.55}}
table {{width:100%;border-collapse:collapse;background:var(--bg-secondary);border-radius:8px;overflow:hidden}}
th,td {{padding:10px 12px;text-align:left;border-bottom:1px solid var(--border-light);font-size:.88em;color:var(--text-primary)}}
th {{background:var(--accent-dark);color:#fff;font-size:.82em;text-transform:uppercase}}
</style>
</head>
<body>

<div id="sidebar">
  <h2>Research Control</h2>
  <button class="dark-mode-toggle" onclick="toggleDarkMode()">🌙 Dark Mode</button>
  <div class="btn-group">
    <button id="btn-notes" class="active" onclick="setView('notes')">📝 My Kanban Notes</button>
    <button id="btn-abstracts" onclick="setView('abstracts')">📄 Abstracts</button>
    <button id="btn-biblio" onclick="setView('biblio')">📚 Bibliography</button>
  </div>

  <div class="filter-group">
    <label>Folder</label>
    <input type="text" class="filter-search-box" id="folder-search" placeholder="🔍 Search folders..." onkeyup="filterDropdown('folder-filter','folder-search')">
    <select id="folder-filter" onchange="triggerRender()"></select>
  </div>
  <div class="filter-group">
    <label>Title</label>
    <input type="text" class="filter-search-box" id="title-search" placeholder="🔍 Search titles..." onkeyup="filterDropdown('title-filter','title-search')">
    <select id="title-filter" onchange="triggerRender()"></select>
  </div>
  <div class="filter-group">
    <label>Author</label>
    <input type="text" class="filter-search-box" id="author-search" placeholder="🔍 Search authors..." onkeyup="filterDropdown('author-filter','author-search')">
    <select id="author-filter" onchange="triggerRender()"></select>
  </div>
  <div class="filter-group">
    <label>Publication</label>
    <input type="text" class="filter-search-box" id="pub-search" placeholder="🔍 Search publications..." onkeyup="filterDropdown('pub-filter','pub-search')">
    <select id="pub-filter" onchange="triggerRender()"></select>
  </div>
  <div class="filter-group">
    <label>Year</label>
    <select id="year-filter" onchange="triggerRender()"></select>
  </div>
  <div class="filter-group" id="cat-filter-container">
    <label>Category</label>
    <select id="cat-filter" onchange="triggerRender()"></select>
  </div>
  <div class="filter-group" id="tag-filter-container">
    <label>Tags <span style="font-weight:normal;color:#999">(🔵 Paper 🔴 Note)</span></label>
    <input type="text" class="filter-search-box" id="tag-search" placeholder="🔍 Search tags..." onkeyup="filterTagDropdown()">
    <select id="tag-filter" multiple size="12" onchange="handleTagSelection()"></select>
  </div>
  <div class="filter-group" id="tag-filter-container-2">
    <label>Secondary Tags <span style="font-weight:normal;color:#999">(co-occurring)</span></label>
    <input type="text" class="filter-search-box" id="tag-search-2" placeholder="🔍 Search tags..." onkeyup="filterTagDropdown2()">
    <select id="tag-filter-2" multiple size="12" onchange="handleTagSelection2()"></select>
  </div>
  <div class="filter-group">
    <label>Text Search</label>
    <input type="text" id="search-box" placeholder="Highlight matches…" onkeyup="debounceSearch()">
  </div>

  <button class="clear-btn" onclick="resetFilters()">Reset All Filters</button>
  <button class="export-btn" onclick="exportFilteredNotes()">📄 Export Notes</button>
  <button class="export-btn" onclick="copyBibliography()">📚 Copy Citations</button>
  <button class="export-btn" onclick="toggleStats()">📊 Statistics</button>
  <div id="stats-panel" style="display:none;margin-top:12px;padding:12px;background:#f8f9fa;border-radius:6px;font-size:11px;"></div>
  <div id="result-count" style="margin-top:16px;font-size:11px;color:#95a5a6;text-align:center;font-weight:600;"></div>
</div>

<div id="main">
  <div id="content-area"></div>
</div>

<script>
const notes = JSON_NOTES_PLACEHOLDER;
const abstracts = JSON_ABSTRACTS_PLACEHOLDER;

const paperMap = new Map();
[...abstracts, ...notes].forEach(item => {{
    if (!paperMap.has(item.Title) && item.Title) {{
        paperMap.set(item.Title, {{
            Title: item.Title,
            Year: item.Year,
            Authors: item.Authors,
            Folder: item.Topic_Folder,
            Publication: item.Publication || 'N/A',
            Paper_Key: item.Paper_Key
        }});
    }}
}});
const papersList = Array.from(paperMap.values()).sort((a, b) => b.Year - a.Year);

const catMapping = {cat_mapping_js};
const catColors = {cat_colors_js};
const catOrder = {cat_order_js};

let currentView = 'notes';
let searchTimeout = null;
let selectedTags = new Set();
let selectedTags2 = new Set();

function esc(s) {{ return s.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&'); }}
function applyHighlight(text, term) {{
    if (!term || term.length < 2) return text;
    return text.replace(new RegExp(`(${{esc(term)}})`, 'gi'), '<mark>$1</mark>');
}}
function escapeHTML(str) {{
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
              .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}}

function getMergedTags(note) {{
    const pTags = note.Paper_Tags ? note.Paper_Tags.split(',').map(t => t.trim().toLowerCase()).filter(t => t) : [];
    const nTags = note.Note_Tags ? note.Note_Tags.split(',').map(t => t.trim().toLowerCase()).filter(t => t) : [];
    return [...new Set([...pTags, ...nTags])];
}}

function getOriginalCaseTags(note) {{
    const pTags = note.Paper_Tags ? note.Paper_Tags.split(',').map(t => t.trim()).filter(t => t) : [];
    const nTags = note.Note_Tags ? note.Note_Tags.split(',').map(t => t.trim()).filter(t => t) : [];
    return {{ paper: pTags, note: nTags }};
}}

function handleTagSelection() {{
    const select = document.getElementById('tag-filter');
    selectedTags = new Set(Array.from(select.selectedOptions).map(opt => opt.value));
    updateTagDropdown2();
    triggerRender();
}}

function handleTagSelection2() {{
    const select = document.getElementById('tag-filter-2');
    selectedTags2 = new Set(Array.from(select.selectedOptions).map(opt => opt.value));
    triggerRender();
}}

function filterTagDropdown() {{
    const select = document.getElementById('tag-filter');
    const searchTerm = document.getElementById('tag-search').value.toLowerCase();
    Array.from(select.options).forEach(option => {{
        option.style.display = option.text.toLowerCase().includes(searchTerm) ? '' : 'none';
    }});
}}

function filterTagDropdown2() {{
    const select = document.getElementById('tag-filter-2');
    const searchTerm = document.getElementById('tag-search-2').value.toLowerCase();
    Array.from(select.options).forEach(option => {{
        option.style.display = option.text.toLowerCase().includes(searchTerm) ? '' : 'none';
    }});
}}

function filterDropdown(selectId, searchId) {{
    const select = document.getElementById(selectId);
    const searchTerm = document.getElementById(searchId).value.toLowerCase();
    Array.from(select.options).forEach(option => {{
        if (option.value === 'All') {{
            option.style.display = '';
            return;
        }}
        option.style.display = option.text.toLowerCase().includes(searchTerm) ? '' : 'none';
    }});
}}

function updateTagDropdown() {{
    const select = document.getElementById('tag-filter');
    if (!select) return;

    const fFolder = document.getElementById('folder-filter').value;
    const fTitle  = document.getElementById('title-filter').value;
    const fYear   = document.getElementById('year-filter').value;
    const fAuthor = document.getElementById('author-filter').value;
    const fPub    = document.getElementById('pub-filter').value;
    const fCat    = document.getElementById('cat-filter')?.value || 'All';

    const availableTags = new Map();
    notes.forEach(n => {{
        if (fFolder !== 'All' && n.Topic_Folder !== fFolder) return;
        if (fTitle  !== 'All' && n.Title !== fTitle) return;
        if (fYear   !== 'All' && n.Year  !== fYear)  return;
        if (fPub    !== 'All' && n.Publication !== fPub) return;
        if (fAuthor !== 'All' && !n.Authors.split(',').map(a => a.trim()).includes(fAuthor)) return;
        if (fCat    !== 'All' && n.Category !== fCat) return;

        const originalTags = getOriginalCaseTags(n);
        [...originalTags.paper, ...originalTags.note].forEach(tag => {{
            const tagLower = tag.toLowerCase();
            if (!availableTags.has(tagLower)) {{
                availableTags.set(tagLower, tag);
            }}
        }});
    }});

    const allAvailableTags = Array.from(availableTags.entries()).sort((a, b) => a[0].localeCompare(b[0]));
    select.innerHTML = '';
    allAvailableTags.forEach(([tagLower, tagOriginal]) => {{
        const option = document.createElement('option');
        option.value = tagLower;
        option.text = '#' + tagOriginal;
        if (selectedTags.has(tagLower)) option.selected = true;
        select.add(option);
    }});
    if (document.getElementById('tag-search')?.value) filterTagDropdown();
    updateTagDropdown2();
}}

function updateTagDropdown2() {{
    const select = document.getElementById('tag-filter-2');
    if (!select) return;

    const fFolder = document.getElementById('folder-filter').value;
    const fTitle  = document.getElementById('title-filter').value;
    const fYear   = document.getElementById('year-filter').value;
    const fAuthor = document.getElementById('author-filter').value;
    const fPub    = document.getElementById('pub-filter').value;
    const fCat    = document.getElementById('cat-filter')?.value || 'All';

    const coOccurringTags = new Map();
    
    if (selectedTags.size === 0) {{
        select.innerHTML = '<option disabled>Select primary tags first</option>';
        return;
    }}

    notes.forEach(n => {{
        if (fFolder !== 'All' && n.Topic_Folder !== fFolder) return;
        if (fTitle  !== 'All' && n.Title !== fTitle) return;
        if (fYear   !== 'All' && n.Year  !== fYear)  return;
        if (fPub    !== 'All' && n.Publication !== fPub) return;
        if (fAuthor !== 'All' && !n.Authors.split(',').map(a => a.trim()).includes(fAuthor)) return;
        if (fCat    !== 'All' && n.Category !== fCat) return;

        const noteTags = getMergedTags(n);
        let hasAllPrimaryTags = true;
        for (const tag of selectedTags) {{
            if (!noteTags.includes(tag)) {{
                hasAllPrimaryTags = false;
                break;
            }}
        }}

        if (hasAllPrimaryTags) {{
            const originalTags = getOriginalCaseTags(n);
            [...originalTags.paper, ...originalTags.note].forEach(tag => {{
                const tagLower = tag.toLowerCase();
                if (!selectedTags.has(tagLower) && !coOccurringTags.has(tagLower)) {{
                    coOccurringTags.set(tagLower, tag);
                }}
            }});
        }}
    }});

    const allCoOccurringTags = Array.from(coOccurringTags.entries()).sort((a, b) => a[0].localeCompare(b[0]));
    select.innerHTML = '';
    
    if (allCoOccurringTags.length === 0) {{
        select.innerHTML = '<option disabled>No co-occurring tags</option>';
        return;
    }}

    allCoOccurringTags.forEach(([tagLower, tagOriginal]) => {{
        const option = document.createElement('option');
        option.value = tagLower;
        option.text = '#' + tagOriginal;
        if (selectedTags2.has(tagLower)) option.selected = true;
        select.add(option);
    }});
    if (document.getElementById('tag-search-2')?.value) filterTagDropdown2();
}}

function updateDropdowns() {{
    const fFolder = document.getElementById('folder-filter').value;
    const fTitle  = document.getElementById('title-filter').value;
    const fYear   = document.getElementById('year-filter').value;
    const fAuthor = document.getElementById('author-filter').value;
    const fPub    = document.getElementById('pub-filter').value;
    const fCat    = document.getElementById('cat-filter')?.value || 'All';

    const baseData = currentView === 'notes' ? notes : currentView === 'abstracts' ? abstracts : papersList;

    const getFilteredFor = (ignore) => {{
        return baseData.filter(item => {{
            const folder = item.Topic_Folder || item.Folder;
            if (ignore !== 'folder' && fFolder !== 'All' && folder !== fFolder) return false;
            if (ignore !== 'title'  && fTitle  !== 'All' && item.Title !== fTitle) return false;
            if (ignore !== 'year'   && fYear   !== 'All' && item.Year  !== fYear)  return false;
            if (ignore !== 'pub'    && fPub    !== 'All' && item.Publication !== fPub) return false;
            if (ignore !== 'author' && fAuthor !== 'All' && !item.Authors.split(',').map(a => a.trim()).includes(fAuthor)) return false;
            if (currentView === 'notes' && ignore !== 'cat' && fCat !== 'All' && item.Category !== fCat) return false;
            return true;
        }});
    }};

    const rebuild = (id, ignore, field, isArray = false) => {{
        const sel = document.getElementById(id);
        if (!sel) return;
        const prev = sel.value;
        const vals = new Set();
        getFilteredFor(ignore).forEach(i => {{
            let v = i[field];
            if (field === 'Topic_Folder' && i.Folder) v = i.Folder;
            if (v) {{
                if (isArray) {{
                    v.split(',').forEach(x => {{ if (x.trim()) vals.add(x.trim()); }});
                }} else {{
                    vals.add(v);
                }}
            }}
        }});
        let sorted = [...vals].sort();
        if (field === 'Year') sorted.sort((a, b) => b - a);

        sel.innerHTML = `<option value="All">All ${{id.split('-')[0]}}s</option>`;
        sorted.forEach(v => sel.add(new Option(
            id === 'cat-filter' ? (catMapping[v] || v) : v,
            v
        )));
        if (prev !== 'All' && vals.has(prev)) sel.value = prev;
    }};

    rebuild('folder-filter', 'folder', 'Topic_Folder');
    rebuild('title-filter', 'title', 'Title');
    rebuild('year-filter', 'year', 'Year');
    rebuild('author-filter', 'author', 'Authors', true);
    rebuild('pub-filter', 'pub', 'Publication');
    if (currentView === 'notes') {{
        rebuild('cat-filter', 'cat', 'Category');
        updateTagDropdown();
    }}
}}

function triggerRender() {{
    updateDropdowns();
    const term    = document.getElementById('search-box').value.toLowerCase();
    const fFolder = document.getElementById('folder-filter').value;
    const fTitle  = document.getElementById('title-filter').value;
    const fYear   = document.getElementById('year-filter').value;
    const fAuthor = document.getElementById('author-filter').value;
    const fPub    = document.getElementById('pub-filter').value;
    const el      = document.getElementById('content-area');
    const counter = document.getElementById('result-count');

    if (currentView === 'notes') {{
        const fCat = document.getElementById('cat-filter').value;

        const filtered = notes.filter(n => {{
            if (fFolder !== 'All' && n.Topic_Folder !== fFolder) return false;
            if (fTitle  !== 'All' && n.Title !== fTitle) return false;
            if (fYear   !== 'All' && n.Year  !== fYear)  return false;
            if (fPub    !== 'All' && n.Publication !== fPub) return false;
            if (fAuthor !== 'All' && !n.Authors.split(',').map(a => a.trim()).includes(fAuthor)) return false;
            if (fCat    !== 'All' && n.Category !== fCat) return false;

            if (selectedTags.size > 0) {{
                const allItemTags = getMergedTags(n);
                for (const tag of selectedTags) {{
                    if (!allItemTags.includes(tag)) return false;
                }}
            }}
            if (selectedTags2.size > 0) {{
                const allItemTags = getMergedTags(n);
                for (const tag of selectedTags2) {{
                    if (!allItemTags.includes(tag)) return false;
                }}
            }}
            if (term && !(n.Title + n.Highlight + n.My_Comment + n.Authors).toLowerCase().includes(term)) return false;
            return true;
        }});

        const grouped = {{}};
        filtered.forEach(n => {{
            if (!grouped[n.Title]) grouped[n.Title] = [];
            grouped[n.Title].push(n);
        }});

        let html = '';
        for (const [title, group] of Object.entries(grouped)) {{
            const f = group[0];
            const authors = f.Authors.split(',').map(a => a.trim());
            let aStr = authors.length === 1 ? authors[0] :
                       (authors.length === 2 ? authors[0] + ', & ' + authors[1] :
                        authors.slice(0, -1).join(', ') + ', & ' + authors[authors.length - 1]);
            const citation = `${{aStr}}. (${{f.Year}}). ${{title}}. ${{f.Publication}}.`;

            html += `<div class="paper-group">`;
            html += `<button class="copy-citation-btn" onclick="copyCitation('${{escapeHTML(citation)}}')">📋 Copy Citation</button>`;
            html += `<h3><a href="#" class="zotero-link" onclick="openInZotero('${{f.Paper_Key}}', event)">${{applyHighlight(title, term)}}</a> (${{f.Year}})<span class="open-in-zotero" onclick="openInZotero('${{f.Paper_Key}}', event)" title="Open in Zotero">🔗</span></h3>`;
            html += `<div class="paper-meta">📁 ${{f.Topic_Folder}} &nbsp;·&nbsp; ✍️ ${{applyHighlight(f.Authors, term)}} &nbsp;·&nbsp; 📰 ${{applyHighlight(f.Publication, term)}}</div>`;
            html += `<div class="kanban-board">`;

            const catGroups = {{}};
            group.forEach(n => {{
                if (!catGroups[n.Category]) catGroups[n.Category] = [];
                catGroups[n.Category].push(n);
            }});

            catOrder.forEach(cat => {{
                if (!catGroups[cat]) return;
                const color = catColors[cat] || '#ccc';
                const items = catGroups[cat];
                html += `<div class="kanban-column" style="border-top-color:${{color}}">`;
                html += `<h4><span>${{catMapping[cat]}}</span><span class="col-count" style="color:${{color}}">${{items.length}}</span></h4>`;

                items.forEach(n => {{
                    const originalTags = getOriginalCaseTags(n);
                    const pTags = originalTags.paper;
                    const nTags = originalTags.note;
                    const mergedTagsLower = getMergedTags(n);

                    const noteData = {{
                        title: title,
                        year: f.Year,
                        authors: f.Authors,
                        category: catMapping[cat],
                        tags: mergedTagsLower.join(', '),
                        highlight: n.Highlight || '',
                        comment: n.My_Comment || ''
                    }};

                    html += `<div class="note-card" style="border-left-color:${{color}}" data-note="${{escapeHTML(JSON.stringify(noteData))}}" onclick="openAnnotationInZotero('${{n.PDF_Attachment_Key}}', '${{n.Annotation_Item_Key}}', event)" title="Click to open in Zotero">`;
                    html += `<button class="copy-note-btn" onclick="copyNoteFromCard(this, event)">📋 Copy</button>`;

                    const rendered = new Set();
                    let matchCount = 0;

                    pTags.forEach(tag => {{
                        const tagLower = tag.toLowerCase();
                        if (!rendered.has(tagLower)) {{
                            rendered.add(tagLower);
                            const isSelected = selectedTags.has(tagLower) || selectedTags2.has(tagLower);
                            if (isSelected) matchCount++;
                            const extraClass = isSelected ? ' highlighted' : '';
                            html += `<div class="tag paper-tag${{extraClass}}" title="Paper tag">🔵 #${{applyHighlight(tag, term)}}</div>`;
                        }}
                    }});

                    nTags.forEach(tag => {{
                        const tagLower = tag.toLowerCase();
                        if (!rendered.has(tagLower)) {{
                            rendered.add(tagLower);
                            const isSelected = selectedTags.has(tagLower) || selectedTags2.has(tagLower);
                            if (isSelected) matchCount++;
                            const extraClass = isSelected ? ' highlighted' : '';
                            html += `<div class="tag note-tag${{extraClass}}" title="Note tag">🔴 #${{applyHighlight(tag, term)}}</div>`;
                        }}
                    }});

                    if (matchCount > 1) html += `<span class="tag-count">${{matchCount}} matching</span>`;

                    if (n.Highlight) html += `<div class="highlight-box">${{applyHighlight(n.Highlight.replace(/\\n/g, '<br>'), term)}}</div>`;
                    if (n.My_Comment) html += `<div class="comment-box">${{applyHighlight(n.My_Comment.replace(/\\n/g, '<br>'), term)}}</div>`;
                    html += `</div>`;
                }});
                html += `</div>`;
            }});
            html += `</div></div>`;
        }}
        el.innerHTML = html || '<p style="text-align:center;margin-top:60px;color:#95a5a6">No matching notes.</p>';
        counter.textContent = `${{filtered.length}} note(s) across ${{Object.keys(grouped).length}} paper(s)`;

    }} else if (currentView === 'abstracts') {{
        const filtered = abstracts.filter(a => {{
            if (fFolder !== 'All' && a.Topic_Folder !== fFolder) return false;
            if (fTitle  !== 'All' && a.Title !== fTitle) return false;
            if (fYear   !== 'All' && a.Year  !== fYear) return false;
            if (fPub    !== 'All' && a.Publication !== fPub) return false;
            if (fAuthor !== 'All' && !a.Authors.split(',').map(x => x.trim()).includes(fAuthor)) return false;
            if (term && !(a.Title + a.Abstract).toLowerCase().includes(term)) return false;
            return true;
        }});

        let html = '';
        filtered.forEach(a => {{
            const authors = a.Authors.split(',').map(au => au.trim());
            let aStr = authors.length === 1 ? authors[0] :
                       (authors.length === 2 ? authors[0] + ', & ' + authors[1] :
                        authors.slice(0, -1).join(', ') + ', & ' + authors[authors.length - 1]);
            const citation = `${{aStr}}. (${{a.Year}}). ${{a.Title}}. ${{a.Publication}}.`;

            html += `<div class="paper-group">`;
            html += `<button class="copy-citation-btn" onclick="copyCitation('${{escapeHTML(citation)}}')">📋 Copy Citation</button>`;
            html += `<h3><a href="#" class="zotero-link" onclick="openInZotero('${{a.Paper_Key}}', event)">${{applyHighlight(a.Title, term)}}</a> (${{a.Year}})<span class="open-in-zotero" onclick="openInZotero('${{a.Paper_Key}}', event)" title="Open in Zotero">🔗</span></h3>`;
            html += `<div class="paper-meta">📁 ${{a.Topic_Folder}} &nbsp;·&nbsp; ✍️ ${{a.Authors}}</div>`;
            html += `<div style="line-height:1.6;font-size:.93em">${{applyHighlight(a.Abstract.replace(/\\n/g, '<br><br>'), term)}}</div>`;
            html += `</div>`;
        }});
        el.innerHTML = html || '<p style="text-align:center;margin-top:60px;color:#95a5a6">No matching abstracts.</p>';
        counter.textContent = `${{filtered.length}} abstract(s)`;

    }} else {{
        const filtered = papersList.filter(p => {{
            if (fFolder !== 'All' && p.Folder !== fFolder) return false;
            if (fTitle  !== 'All' && p.Title  !== fTitle) return false;
            if (fYear   !== 'All' && p.Year   !== fYear) return false;
            if (fPub    !== 'All' && p.Publication !== fPub) return false;
            if (fAuthor !== 'All' && !p.Authors.split(',').map(x => x.trim()).includes(fAuthor)) return false;
            if (term && !(p.Title + p.Authors + p.Publication).toLowerCase().includes(term)) return false;
            return true;
        }});

        let html = '<table><thead><tr><th>Year</th><th>Authors</th><th>Title</th><th>Publication</th></tr></thead><tbody>';
        filtered.forEach(p => {{
            const titleLink = `<a href="#" class="zotero-link" onclick="openInZotero('${{p.Paper_Key}}', event)">${{applyHighlight(p.Title, term)}}</a>`;
            html += `<tr><td>${{p.Year}}</td><td>${{applyHighlight(p.Authors, term)}}</td><td>${{titleLink}}</td><td>${{applyHighlight(p.Publication, term)}}</td></tr>`;
        }});
        el.innerHTML = html + '</tbody></table>';
        counter.textContent = `${{filtered.length}} paper(s)`;
    }}
}}

function debounceSearch() {{
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(triggerRender, 250);
}}

function toggleDarkMode() {{
    const body = document.body;
    const button = document.querySelector('.dark-mode-toggle');
    
    // Cycle: Light → Dark → Darker → Light
    if (body.classList.contains('darker-mode')) {{
        // Currently Darker, go to Light
        body.classList.remove('darker-mode');
        button.textContent = '🌙 Dark Mode';
        localStorage.setItem('themeMode', 'light');
    }} else if (body.classList.contains('dark-mode')) {{
        // Currently Dark, go to Darker
        body.classList.remove('dark-mode');
        body.classList.add('darker-mode');
        button.textContent = '🌑 Darker Mode';
        localStorage.setItem('themeMode', 'darker');
    }} else {{
        // Currently Light, go to Dark
        body.classList.add('dark-mode');
        button.textContent = '☀️ Light Mode';
        localStorage.setItem('themeMode', 'dark');
    }}
}}

function loadDarkModePreference() {{
    const themeMode = localStorage.getItem('themeMode');
    const button = document.querySelector('.dark-mode-toggle');
    
    if (themeMode === 'dark') {{
        document.body.classList.add('dark-mode');
        button.textContent = '☀️ Light Mode';
    }} else if (themeMode === 'darker') {{
        document.body.classList.add('darker-mode');
        button.textContent = '🌑 Darker Mode';
    }} else {{
        button.textContent = '🌙 Dark Mode';
    }}
}}

function openInZotero(itemKey, event) {{
    if (event) {{
        event.preventDefault();
        event.stopPropagation();
    }}
    if (!itemKey || itemKey === 'undefined') {{
        console.error('Invalid item key:', itemKey);
        showToast('❌ Cannot open: Invalid item key');
        return;
    }}
    const zoteroUrl = `zotero://select/library/items/${{itemKey}}`;
    console.log('Opening Zotero item:', zoteroUrl);
    window.open(zoteroUrl, '_self');
}}

function openAnnotationInZotero(pdfKey, annotationKey, event) {{
    if (event) {{
        event.preventDefault();
        event.stopPropagation();
    }}
    if (!pdfKey || pdfKey === 'undefined' || !annotationKey || annotationKey === 'undefined') {{
        console.error('Invalid keys - PDF:', pdfKey, 'Annotation:', annotationKey);
        showToast('❌ Cannot open: Invalid keys');
        return;
    }}
    // Open PDF at specific annotation location
    const zoteroUrl = `zotero://open-pdf/library/items/${{pdfKey}}?annotation=${{annotationKey}}`;
    console.log('Opening Zotero PDF at annotation:', zoteroUrl);
    window.open(zoteroUrl, '_self');
}}

function setView(view) {{
    currentView = view;
    document.querySelectorAll('.btn-group button').forEach(b => b.classList.remove('active'));
    document.getElementById('btn-' + view).classList.add('active');
    document.getElementById('cat-filter-container').style.display = view === 'notes' ? 'block' : 'none';
    document.getElementById('tag-filter-container').style.display = view === 'notes' ? 'block' : 'none';
    document.getElementById('tag-filter-container-2').style.display = view === 'notes' ? 'block' : 'none';
    triggerRender();
}}

function resetFilters() {{
    ['folder-filter', 'title-filter', 'year-filter', 'author-filter', 'pub-filter', 'cat-filter'].forEach(id => {{
        const el = document.getElementById(id);
        if (el) el.value = 'All';
    }});
    ['folder-search', 'title-search', 'author-search', 'pub-search', 'tag-search', 'tag-search-2'].forEach(id => {{
        const el = document.getElementById(id);
        if (el) {{
            el.value = '';
            const select = document.getElementById(id.replace('-search', '-filter'));
            if (select) Array.from(select.options).forEach(opt => opt.style.display = '');
        }}
    }});
    selectedTags.clear();
    selectedTags2.clear();
    const tagSelect = document.getElementById('tag-filter');
    if (tagSelect) Array.from(tagSelect.options).forEach(opt => opt.selected = false);
    const tagSelect2 = document.getElementById('tag-filter-2');
    if (tagSelect2) Array.from(tagSelect2.options).forEach(opt => opt.selected = false);
    document.getElementById('search-box').value = '';
    triggerRender();
}}

// ══════════════════════════════════════════════════════════
// EXPORT & WRITING HELPER FUNCTIONS
// ══════════════════════════════════════════════════════════

function exportFilteredNotes() {{
    const term    = document.getElementById('search-box').value.toLowerCase();
    const fFolder = document.getElementById('folder-filter').value;
    const fTitle  = document.getElementById('title-filter').value;
    const fYear   = document.getElementById('year-filter').value;
    const fAuthor = document.getElementById('author-filter').value;
    const fPub    = document.getElementById('pub-filter').value;
    const fCat    = document.getElementById('cat-filter').value;

    const filtered = notes.filter(n => {{
        if (fFolder !== 'All' && n.Topic_Folder !== fFolder) return false;
        if (fTitle  !== 'All' && n.Title !== fTitle) return false;
        if (fYear   !== 'All' && n.Year  !== fYear)  return false;
        if (fPub    !== 'All' && n.Publication !== fPub) return false;
        if (fAuthor !== 'All' && !n.Authors.split(',').map(a => a.trim()).includes(fAuthor)) return false;
        if (fCat    !== 'All' && n.Category !== fCat) return false;

        if (selectedTags.size > 0) {{
            const allItemTags = getMergedTags(n);
            for (const tag of selectedTags) {{
                if (!allItemTags.includes(tag)) return false;
            }}
        }}
        if (selectedTags2.size > 0) {{
            const allItemTags = getMergedTags(n);
            for (const tag of selectedTags2) {{
                if (!allItemTags.includes(tag)) return false;
            }}
        }}
        if (term && !(n.Title + n.Highlight + n.My_Comment + n.Authors).toLowerCase().includes(term)) return false;
        return true;
    }});

    const grouped = {{}};
    filtered.forEach(n => {{
        if (!grouped[n.Title]) grouped[n.Title] = [];
        grouped[n.Title].push(n);
    }});

    let exportText = `EXPORTED NOTES - ${{new Date().toLocaleDateString()}}\\n`;
    exportText += `Total: ${{filtered.length}} notes from ${{Object.keys(grouped).length}} papers\\n`;
    if (selectedTags.size > 0) {{
        exportText += `Primary Tags: ${{Array.from(selectedTags).join(', ')}}\\n`;
    }}
    if (selectedTags2.size > 0) {{
        exportText += `Secondary Tags: ${{Array.from(selectedTags2).join(', ')}}\\n`;
    }}
    exportText += '='.repeat(80) + '\\n\\n';

    for (const [title, group] of Object.entries(grouped)) {{
        const first = group[0];
        exportText += `${{title}} (${{first.Year}})\\n`;
        exportText += `Authors: ${{first.Authors}}\\n`;
        exportText += `Publication: ${{first.Publication}}\\n`;
        exportText += `Folder: ${{first.Topic_Folder}}\\n`;
        exportText += '-'.repeat(80) + '\\n\\n';

        const byCategory = {{}};
        group.forEach(n => {{
            if (!byCategory[n.Category]) byCategory[n.Category] = [];
            byCategory[n.Category].push(n);
        }});

        catOrder.forEach(cat => {{
            if (!byCategory[cat]) return;
            exportText += `  [${{catMapping[cat]}}]\\n`;
            byCategory[cat].forEach(n => {{
                const allTags = getMergedTags(n);
                if (allTags.length > 0) exportText += `    Tags: ${{allTags.join(', ')}}\\n`;
                if (n.Highlight) exportText += `    "${{n.Highlight}}"\\n`;
                if (n.My_Comment) exportText += `    → ${{n.My_Comment}}\\n`;
                exportText += '\\n';
            }});
        }});

        exportText += '\\n' + '='.repeat(80) + '\\n\\n';
    }}

    navigator.clipboard.writeText(exportText).then(() => {{
        showToast(`✅ Exported ${{filtered.length}} notes to clipboard!`);
    }}).catch(() => {{
        const blob = new Blob([exportText], {{ type: 'text/plain' }});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `notes_export_${{new Date().toISOString().split('T')[0]}}.txt`;
        a.click();
        showToast('✅ Downloaded notes as file');
    }});
}}

function copyBibliography() {{
    const term    = document.getElementById('search-box').value.toLowerCase();
    const fFolder = document.getElementById('folder-filter').value;
    const fTitle  = document.getElementById('title-filter').value;
    const fYear   = document.getElementById('year-filter').value;
    const fAuthor = document.getElementById('author-filter').value;
    const fPub    = document.getElementById('pub-filter').value;

    const paperTitles = new Set();
    const filtered = notes.filter(n => {{
        if (fFolder !== 'All' && n.Topic_Folder !== fFolder) return false;
        if (fTitle  !== 'All' && n.Title !== fTitle) return false;
        if (fYear   !== 'All' && n.Year  !== fYear)  return false;
        if (fPub    !== 'All' && n.Publication !== fPub) return false;
        if (fAuthor !== 'All' && !n.Authors.split(',').map(a => a.trim()).includes(fAuthor)) return false;

        if (selectedTags.size > 0) {{
            const allItemTags = getMergedTags(n);
            for (const tag of selectedTags) {{
                if (!allItemTags.includes(tag)) return false;
            }}
        }}
        if (selectedTags2.size > 0) {{
            const allItemTags = getMergedTags(n);
            for (const tag of selectedTags2) {{
                if (!allItemTags.includes(tag)) return false;
            }}
        }}
        if (term && !(n.Title + n.Highlight + n.My_Comment + n.Authors).toLowerCase().includes(term)) return false;
        paperTitles.add(n.Title);
        return true;
    }});

    const papers = papersList.filter(p => paperTitles.has(p.Title)).sort((a, b) => {{
        const authorA = a.Authors.split(',')[0].trim();
        const authorB = b.Authors.split(',')[0].trim();
        return authorA.localeCompare(authorB);
    }});

    let bibText = '';
    papers.forEach((p, index) => {{
        const authors = p.Authors.split(',').map(a => a.trim());
        let authorString;
        if (authors.length === 1) {{
            authorString = authors[0];
        }} else if (authors.length === 2) {{
            authorString = authors[0] + ', & ' + authors[1];
        }} else if (authors.length > 2) {{
            const lastAuthor = authors[authors.length - 1];
            const otherAuthors = authors.slice(0, -1).join(', ');
            authorString = otherAuthors + ', & ' + lastAuthor;
        }}

        bibText += `${{authorString}}. (${{p.Year}}). ${{p.Title}}. ${{p.Publication}}.`;
        if (index < papers.length - 1) bibText += '\\n\\n';
    }});

    navigator.clipboard.writeText(bibText).then(() => {{
        showToast(`✅ Copied ${{papers.length}} APA citations!`);
    }}).catch(() => {{
        showToast('❌ Failed to copy citations');
    }});
}}

function toggleStats() {{
    const panel = document.getElementById('stats-panel');
    if (panel.style.display === 'none') {{
        const totalPapers = new Set(notes.map(n => n.Title)).size;
        const totalNotes = notes.length;
        const avgNotesPerPaper = (totalNotes / totalPapers).toFixed(1);

        const catCounts = {{}};
        notes.forEach(n => {{
            catCounts[n.Category] = (catCounts[n.Category] || 0) + 1;
        }});

        const tagCounts = {{}};
        notes.forEach(n => {{
            getMergedTags(n).forEach(tag => {{
                tagCounts[tag] = (tagCounts[tag] || 0) + 1;
            }});
        }});
        const topTags = Object.entries(tagCounts)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5)
            .map(([tag, count]) => `#${{tag}} (${{count}})`);

        let statsHTML = `<strong>📊 Research Overview</strong><br><br>`;
        statsHTML += `<strong>Overall:</strong><br>`;
        statsHTML += `• ${{totalPapers}} papers<br>`;
        statsHTML += `• ${{totalNotes}} total notes<br>`;
        statsHTML += `• ${{avgNotesPerPaper}} notes per paper (avg)<br><br>`;

        statsHTML += `<strong>By Category:</strong><br>`;
        catOrder.forEach(cat => {{
            if (catCounts[cat]) {{
                const pct = ((catCounts[cat] / totalNotes) * 100).toFixed(1);
                statsHTML += `• ${{catMapping[cat]}}: ${{catCounts[cat]}} (${{pct}}%)<br>`;
            }}
        }});

        statsHTML += `<br><strong>Top 5 Tags:</strong><br>`;
        topTags.forEach(tag => {{
            statsHTML += `• ${{tag}}<br>`;
        }});

        panel.innerHTML = statsHTML;
        panel.style.display = 'block';
    }} else {{
        panel.style.display = 'none';
    }}
}}

function copyCitation(citation) {{
    navigator.clipboard.writeText(citation).then(() => {{
        showToast('✅ Citation copied!');
    }}).catch(() => {{
        showToast('❌ Failed to copy citation');
    }});
}}

function copyNoteFromCard(button, event) {{
    if (event) {{
        event.preventDefault();
        event.stopPropagation();
    }}
    const noteCard = button.closest('.note-card');
    const noteData = JSON.parse(noteCard.getAttribute('data-note'));

    let noteText = `${{noteData.title}} (${{noteData.year}})\\n`;
    noteText += `Authors: ${{noteData.authors}}\\n`;
    noteText += `Category: ${{noteData.category}}\\n`;
    if (noteData.tags) noteText += `Tags: ${{noteData.tags}}\\n`;
    noteText += `\\n`;
    if (noteData.highlight) noteText += `Highlight: "${{noteData.highlight}}"\\n`;
    if (noteData.comment) noteText += `Comment: ${{noteData.comment}}\\n`;

    navigator.clipboard.writeText(noteText).then(() => {{
        showToast('✅ Note copied!');
    }}).catch(() => {{
        showToast('❌ Failed to copy note');
    }});
}}

function showToast(message) {{
    const toast = document.createElement('div');
    toast.textContent = message;
    toast.style.cssText = 'position:fixed;top:20px;right:20px;background:#27ae60;color:#fff;padding:12px 20px;border-radius:6px;font-weight:600;z-index:9999;box-shadow:0 4px 12px rgba(0,0,0,.15);';
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2000);
}}

window.onload = function() {{
    loadDarkModePreference();
    updateDropdowns();
    triggerRender();
}};
</script>
</body>
</html>'''

# Inject JSON data
final_html = html_template.replace("JSON_NOTES_PLACEHOLDER", notes_json).replace("JSON_ABSTRACTS_PLACEHOLDER", abstracts_json)

with open(OUTPUT_HTML_PATH, "w", encoding="utf-8") as f:
    f.write(final_html)

print(f"\n✅ Dashboard generated successfully!")
print(f"📍 Location: {OUTPUT_HTML_PATH}")
print("="*80)
print("\nConfiguration Summary:")
print(f"  • Categories: {len(CATEGORY_NAMES)}")
print(f"  • Color mappings: {len(COLOR_MAPPING)}")
print(f"  • Notes with Paper Tags: {len([n for n in df_notes.to_dict('records') if n['Paper_Tags']])}")
print(f"  • Notes with Note Tags: {len([n for n in df_notes.to_dict('records') if n['Note_Tags']])}")
print("="*80)
