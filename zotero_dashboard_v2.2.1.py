#!/usr/bin/env python3
"""
Comps Research Dashboard Generator
===================================
Reads a Zotero SQLite database and produces a standalone HTML dashboard with:
  - Faceted (cascading) sidebar filters
  - Discrete Kanban columns per highlight color category
  - Real-time search highlighting via <mark> tags
  - Left-border color coding on note cards
  - Three views: Kanban Notes, Abstracts, Bibliography table
  - MULTI-TAG SELECTION with visual highlighting
  - Export features for essay writing

CONFIGURATION INSTRUCTIONS:
1. Set your Zotero database path below
2. Customize the color mapping to match YOUR Zotero highlight colors
3. Set the output location for the HTML file
4. Run the script: python3 comps_dashboard_multitag.py

Fix log (v3):
  - Added multi-select tag filter with checkboxes
  - Visual distinction for papers with multiple selected tags
  - Tag badges show count when multiple tags match
  - Export and citation features
  - Per-note and per-paper copy buttons
Fix log (Tags Restored):
  - SQL now pulls tags from BOTH the parent paper and the highlight/annotation
  - HTML safely escapes JSON to prevent apostrophes from breaking the UI rendering
"""

import sqlite3
import pandas as pd
import shutil
import os
import json
import sys

# ───────────────────────────────────────────────────────────────────────────
# ▼ USER CONFIGURATION - CUSTOMIZE THIS SECTION
# ───────────────────────────────────────────────────────────────────────────

# ─── PATHS ─────────────────────────────────────────────────────────────────
# Where is your Zotero database?
# Default locations:
#   - Windows: C:/Users/YourName/Zotero/zotero.sqlite
#   - macOS: ~/Zotero/zotero.sqlite
#   - Linux: ~/Zotero/zotero.sqlite
ZOTERO_DB_PATH = os.path.expanduser("~/Zotero/zotero.sqlite")

# Where should the HTML dashboard be saved?
OUTPUT_HTML_PATH = os.path.expanduser("~/Desktop/Comps_Dashboard.html")

# Temporary working directory (will be created if doesn't exist)
TEMP_DIR = os.path.expanduser("~/Documents/Zotero_Dashboard")

# ─── COLOR MAPPING ─────────────────────────────────────────────────────────
# Map Zotero highlight colors to categories
#
# To find your Zotero colors:
# 1. In Zotero, highlight some text
# 2. Right-click the highlight → "Show in Library"
# 3. The color codes are: #RRGGBB (e.g., #ffd400 for yellow)
#
# Tips:
# - Zotero has two shades per color (dark and light)
# - List BOTH shades for each category
# - Category names should use underscores (e.g., "Yellow_General")
# - You can add/remove categories as needed

COLOR_MAPPING = {
    # Yellow highlights – General concepts
    "#ffd400": "Yellow_General",
    "#faf4d1": "Yellow_General",

    # Green highlights – Methodology
    "#5fb236": "Green_Methods",
    "#e0f3d1": "Green_Methods",

    # Magenta highlights – Results
    "#e56eee": "Magenta_Results",
    "#ffc4fb": "Magenta_Results",

    # Purple highlights – Discussion
    "#a28ae5": "Purple_Discussion",

    # Red highlights – Critiques & References
    "#ff6666": "Red_Critiques_Refs",
    "#fad1d5": "Red_Critiques_Refs",

    # Blue highlights – Future Directions
    "#2ea8e5": "Blue_Future",

    # Orange highlights – Important/Key Insights
    "#f19837": "Orange_Important",

    # Gray highlights – Glossary/Definitions
    "#aaaaaa": "Gray_Glossary",
}

# ─── CATEGORY DISPLAY NAMES ────────────────────────────────────────────────
# How should categories appear in the dashboard?
# Format: 'CategoryName': 'emoji Display Name'

CATEGORY_NAMES = {
    'Yellow_General': '🟡 General Concepts',
    'Green_Methods': '🟢 Methodology',
    'Magenta_Results': '💗 Results',
    'Purple_Discussion': '🟣 Discussion',
    'Red_Critiques_Refs': '🔴 Critiques & Refs',
    'Blue_Future': '🔵 Future Directions',
    'Orange_Important': '🟠 Key Insights',
    'Gray_Glossary': '⚪ Glossary',
    'Uncategorized': '⚪ Uncategorized'
}

# ─── CATEGORY COLORS IN DASHBOARD ──────────────────────────────────────────
# Visual colors for category columns in the Kanban view

CATEGORY_COLORS = {
    'Yellow_General': '#f1c40f',
    'Green_Methods': '#2ecc71',
    'Magenta_Results': '#e56eee',
    'Purple_Discussion': '#9c27b0',
    'Red_Critiques_Refs': '#e74c3c',
    'Blue_Future': '#3498db',
    'Orange_Important': '#e67e22',
    'Gray_Glossary': '#95a5a6',
    'Uncategorized': '#bdc3c7'
}

# ─── CATEGORY DISPLAY ORDER ────────────────────────────────────────────────
# Order in which categories appear (left to right) in Kanban view

CATEGORY_ORDER = [
    'Yellow_General',
    'Green_Methods',
    'Magenta_Results',
    'Purple_Discussion',
    'Red_Critiques_Refs',
    'Blue_Future',
    'Orange_Important',
    'Gray_Glossary',
    'Uncategorized'
]

# ───────────────────────────────────────────────────────────────────────────
# END OF USER CONFIGURATION
# (You shouldn't need to modify anything below this line)
# ───────────────────────────────────────────────────────────────────────────

print("=" * 80)
print("ZOTERO RESEARCH DASHBOARD GENERATOR")
print("=" * 80)
print(f"\nZotero database: {ZOTERO_DB_PATH}")
print(f"Output HTML: {OUTPUT_HTML_PATH}")
print(f"Categories configured: {len(CATEGORY_NAMES)}")
print()

# Validate configuration
if not os.path.exists(ZOTERO_DB_PATH):
    print(f"❌ ERROR: Zotero database not found at: {ZOTERO_DB_PATH}")
    print("\nPlease edit the ZOTERO_DB_PATH variable at the top of this script.")
    print("Common locations:")
    print("  - Windows: C:/Users/YourName/Zotero/zotero.sqlite")
    print("  - macOS: ~/Zotero/zotero.sqlite")
    print("  - Linux: ~/Zotero/zotero.sqlite")
    sys.exit(1)

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(os.path.dirname(OUTPUT_HTML_PATH), exist_ok=True)

# ─ 1. Paths ───────────────────────────────────────────────────────────
temp_db_path = os.path.join(TEMP_DIR, "zotero_temp.sqlite")

print("Copying Zotero database …")
shutil.copy2(ZOTERO_DB_PATH, temp_db_path)
conn = sqlite3.connect(temp_db_path)

# ─ 2. Query: Annotation Notes ───────────────────────────────────────
query_notes = """
              SELECT c.collectionName                                       AS Topic_Folder, \
                     MAX(CASE WHEN f.fieldName = 'title' THEN dv.value END) AS Title, \
                     MAX(CASE WHEN f.fieldName = 'date' THEN dv.value END) AS Year,
    MAX(CASE WHEN f.fieldName = 'publicationTitle' THEN dv.value END) AS Publication,
    (SELECT GROUP_CONCAT(cr.lastName, ', ')
       FROM itemCreators ic
       JOIN creators cr ON ic.creatorID = cr.creatorID
      WHERE ic.itemID = parent.itemID) AS Authors,
    ann.color,
    (SELECT GROUP_CONCAT(t.name, ', ')
       FROM itemTags it
       JOIN tags t ON it.tagID = t.tagID
      WHERE it.itemID IN (parent.itemID, ann.itemID)) AS Annotation_Tags,
    ann.text    AS Highlight,
    ann.comment AS My_Comment
              FROM items parent
                  JOIN itemAttachments att \
              ON parent.itemID = att.parentItemID
                  JOIN items attachItem ON att.itemID = attachItem.itemID
                  JOIN itemAnnotations ann ON attachItem.itemID = ann.parentItemID
                  LEFT JOIN collectionItems ci ON parent.itemID = ci.itemID
                  LEFT JOIN collections c ON ci.collectionID = c.collectionID
                  LEFT JOIN itemData pd ON parent.itemID = pd.itemID
                  LEFT JOIN fields f ON pd.fieldID = f.fieldID
                  LEFT JOIN itemDataValues dv ON pd.valueID = dv.valueID
              WHERE ann.text IS NOT NULL OR ann.comment IS NOT NULL
              GROUP BY parent.itemID, ann.itemID, c.collectionName \
              """

# ─ 3. Query: Abstracts ────────────────────────────────────────────────
query_abstracts = """
                  SELECT c.collectionName                                       AS Topic_Folder, \
                         MAX(CASE WHEN f.fieldName = 'title' THEN dv.value END) AS Title, \
                         MAX(CASE WHEN f.fieldName = 'date' THEN dv.value END) AS Year,
    MAX(CASE WHEN f.fieldName = 'publicationTitle' THEN dv.value END) AS Publication,
    (SELECT GROUP_CONCAT(cr.lastName, ', ')
       FROM itemCreators ic
       JOIN creators cr ON ic.creatorID = cr.creatorID
      WHERE ic.itemID = parent.itemID) AS Authors,
    MAX(CASE WHEN f.fieldName = 'abstractNote' THEN dv.value END) AS Abstract
                  FROM items parent
                      LEFT JOIN collectionItems ci \
                  ON parent.itemID = ci.itemID
                      LEFT JOIN collections c ON ci.collectionID = c.collectionID
                      LEFT JOIN itemData pd ON parent.itemID = pd.itemID
                      LEFT JOIN fields f ON pd.fieldID = f.fieldID
                      LEFT JOIN itemDataValues dv ON pd.valueID = dv.valueID
                  GROUP BY parent.itemID, c.collectionName
                  HAVING MAX (CASE WHEN f.fieldName = 'abstractNote' THEN dv.value END) IS NOT NULL \
                  """

print("Running SQL queries …")
df_notes = pd.read_sql_query(query_notes, conn)
df_abstracts = pd.read_sql_query(query_abstracts, conn)
conn.close()
os.remove(temp_db_path)

# ─ 4. Data normalisation ──────────────────────────────────────────────
df_notes["Year"] = df_notes["Year"].str.extract(r"(\d{4})").fillna("Unknown")
df_abstracts["Year"] = df_abstracts["Year"].str.extract(r"(\d{4})").fillna("Unknown")

# Apply user-configured color mapping
print(f"Applying color mapping ({len(COLOR_MAPPING)} colors configured)...")
df_notes["Category"] = (
    df_notes["color"]
    .str.strip()
    .str.lower()
    .map({k.lower(): v for k, v in COLOR_MAPPING.items()})
    .fillna("Uncategorized")
)

df_notes.fillna("", inplace=True)
df_abstracts.fillna("", inplace=True)

notes_json = json.dumps(df_notes.to_dict(orient="records"), ensure_ascii=False)
abstracts_json = json.dumps(df_abstracts.to_dict(orient="records"), ensure_ascii=False)

# ─ 5. Diagnostic summary ───────────────────────────────────────────────
print("\n📊 Category distribution 📊")
print(df_notes["Category"].value_counts().to_string())
print(f"\nTotal notes:     {len(df_notes)}")
print(f"Total abstracts: {len(df_abstracts)}")

# ─ 6. Generate HTML ────────────────────────────────────────────────────

# Convert configuration to JavaScript
cat_mapping_js = json.dumps(CATEGORY_NAMES)
cat_colors_js = json.dumps(CATEGORY_COLORS)
cat_order_js = json.dumps(CATEGORY_ORDER)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Comps Research Dashboard</title>
<style>
*{{box-sizing:border-box}}
body{{
  font-family:'Segoe UI',system-ui,-apple-system,sans-serif;
  background:#f0f2f5;margin:0;display:flex;height:100vh;overflow:hidden;color:#2c3e50;
}}

/* 📌 Sidebar ═══════════════════════════════════════════════ */
#sidebar{{
  flex:0 0 300px;background:#fff;padding:20px 18px;
  box-shadow:2px 0 8px rgba(0,0,0,.08);overflow-y:auto;z-index:10;
  border-right:1px solid #e0e0e0;
}}
#sidebar h2{{margin:0 0 16px;font-size:17px;letter-spacing:.3px;color:#34495e}}

.btn-group button{{
  display:block;width:100%;padding:10px 12px;margin-bottom:6px;
  background:#f5f6f8;border:1px solid #ddd;border-radius:6px;cursor:pointer;
  text-align:left;font-weight:600;font-size:13px;transition:.15s;color:#555;
}}
.btn-group button.active{{background:#2c3e50;color:#fff;border-color:#2c3e50}}
.btn-group button:hover:not(.active){{background:#ebeef2}}

.filter-group{{margin-top:12px}}
.filter-group label{{
  display:block;font-size:10px;font-weight:700;color:#7f8c8d;
  margin-bottom:4px;text-transform:uppercase;letter-spacing:.6px;
}}
.filter-group select,.filter-group input{{
  width:100%;padding:7px 8px;border-radius:5px;border:1px solid #ccc;
  font-size:12.5px;background:#fcfcfc;
}}
.filter-group select{{
  margin-top:4px;
}}

.filter-search-box{{
  width:100%;padding:5px 8px;border:1px solid #d0d0d0;border-radius:4px;
  font-size:11px;margin-bottom:4px;background:#fff;
  font-family:inherit;
}}
.filter-search-box::placeholder{{
  color:#999;font-style:italic;
}}
#tag-filter{{
  width:100%;padding:4px;border-radius:5px;border:1px solid #ccc;
  font-size:11.5px;background:#fcfcfc;max-height:300px;margin-top:4px;
}}
#tag-filter option{{
  padding:5px 8px;border-radius:3px;margin-bottom:2px;
}}
#tag-filter option:checked{{
  background:#2196f3;color:#fff;font-weight:600;
}}

.clear-btn{{
  margin-top:14px;width:100%;padding:8px;background:#e74c3c;color:#fff;
  border:none;border-radius:6px;cursor:pointer;font-weight:700;font-size:11px;
}}
.clear-btn:hover{{background:#c0392b}}

.export-btn{{
  margin-top:8px;width:100%;padding:8px;background:#3498db;color:#fff;
  border:none;border-radius:6px;cursor:pointer;font-weight:700;font-size:11px;
}}
.export-btn:hover{{background:#2980b9}}

#result-count{{
  margin-top:16px;font-size:11px;color:#95a5a6;text-align:center;font-weight:600;
}}

/* 📌 Main area ═════════════════════════════════════════════ */
#main{{flex:1;padding:24px 28px;overflow-y:auto}}

mark{{background:#fff176;color:#000;padding:0 2px;border-radius:2px;font-weight:700}}

/* 📌 Paper group ═══════════════════════════════════════════ */
.paper-group{{
  background:#fff;padding:22px;margin-bottom:26px;border-radius:10px;
  box-shadow:0 2px 6px rgba(0,0,0,.04);border-top:4px solid #34495e;
  min-width:min-content;position:relative;
}}
.paper-group h3{{margin:0 0 6px;font-size:16px;line-height:1.35;padding-right:80px;}}
.paper-meta{{
  font-size:.85em;color:#7f8c8d;margin-bottom:16px;
  border-bottom:1px solid #eee;padding-bottom:12px;line-height:1.45;
}}
.copy-citation-btn{{
  position:absolute;top:20px;right:20px;
  padding:6px 12px;background:#3498db;color:#fff;border:none;
  border-radius:4px;cursor:pointer;font-size:11px;font-weight:600;
  transition:.2s;
}}
.copy-citation-btn:hover{{background:#2980b9;transform:translateY(-1px);}}
.copy-citation-btn:active{{transform:translateY(0);}}

/* 📌 Kanban ═════════════════════════════════════════════════ */
.kanban-board{{
  display:flex;gap:16px;overflow-x:auto;padding-bottom:12px;align-items:flex-start;
}}
.kanban-column{{
  flex:0 0 360px;background:#f8f9fa;border-radius:8px;padding:14px;
  border-top:5px solid #ccc;max-height:720px;overflow-y:auto;
}}
.kanban-column h4{{
  border-bottom:1px solid #e0e0e0;padding-bottom:8px;margin:0 0 12px;
  font-size:13px;display:flex;justify-content:space-between;align-items:center;
}}
.col-count{{
  background:rgba(0,0,0,.06);padding:2px 8px;border-radius:10px;font-size:.7em;
}}

/* 📌 Note card ═════════════════════════════════════════════ */
.note-card{{
  background:#fff;border:1px solid #e8e8e8;border-left:5px solid #ccc;
  border-radius:7px;padding:13px;margin-bottom:12px;
  box-shadow:0 1px 3px rgba(0,0,0,.025);position:relative;
}}
.copy-note-btn{{
  position:absolute;top:8px;right:8px;
  padding:4px 8px;background:#95a5a6;color:#fff;border:none;
  border-radius:3px;cursor:pointer;font-size:10px;font-weight:600;
  opacity:0;transition:.2s;
}}
.note-card:hover .copy-note-btn{{opacity:1;}}
.copy-note-btn:hover{{background:#7f8c8d;}}
.tag{{
  display:inline-block;background:#e8eaed;padding:3px 9px;border-radius:10px;
  font-size:.78em;margin-bottom:8px;margin-right:4px;font-weight:500;
}}
.tag.highlighted{{background:#2196f3;color:#fff;font-weight:600}}
.tag-count{{
  background:#2196f3;color:#fff;padding:2px 6px;border-radius:8px;
  font-size:.75em;margin-left:4px;font-weight:700;
}}
.highlight-box{{
  background:#fdfbf7;padding:10px 12px;border:1px solid #e8e0d0;
  font-style:italic;color:#444;font-size:.92em;margin-bottom:8px;
  border-radius:4px;line-height:1.55;
}}
.comment-box{{
  background:#f0f7ff;padding:10px 12px;border:1px solid #c4ddf1;
  color:#2c3e50;font-size:.92em;border-radius:4px;
  border-left:3px solid #3498db;line-height:1.55;
}}

/* 📌 Table ══════════════════════════════════════════════════ */
table{{width:100%;border-collapse:collapse;background:#fff;border-radius:8px;overflow:hidden}}
th,td{{padding:10px 12px;text-align:left;border-bottom:1px solid #eee;font-size:.88em}}
th{{background:#34495e;color:#fff;font-size:.82em;text-transform:uppercase;letter-spacing:.4px}}
tr:hover{{background:#f9fafb}}
</style>
</head>
<body>

<div id="sidebar">
  <h2>Research Control</h2>
  <div class="btn-group">
    <button id="btn-notes" class="active" onclick="setView('notes')">📝 My Kanban Notes</button>
    <button id="btn-abstracts" onclick="setView('abstracts')">📄 Abstracts</button>
    <button id="btn-biblio" onclick="setView('biblio')">📚 Bibliography</button>
  </div>

  <div class="filter-group">
    <label>Folder</label>
    <input type="text" class="filter-search-box" id="folder-search" placeholder="🔍 Search folders..." onkeyup="filterDropdown('folder-filter', 'folder-search')">
    <select id="folder-filter" onchange="triggerRender()"></select>
  </div>
  <div class="filter-group">
    <label>Title</label>
    <input type="text" class="filter-search-box" id="title-search" placeholder="🔍 Search titles..." onkeyup="filterDropdown('title-filter', 'title-search')">
    <select id="title-filter" onchange="triggerRender()"></select>
  </div>
  <div class="filter-group">
    <label>Author</label>
    <input type="text" class="filter-search-box" id="author-search" placeholder="🔍 Search authors..." onkeyup="filterDropdown('author-filter', 'author-search')">
    <select id="author-filter" onchange="triggerRender()"></select>
  </div>
  <div class="filter-group">
    <label>Publication</label>
    <input type="text" class="filter-search-box" id="pub-search" placeholder="🔍 Search publications..." onkeyup="filterDropdown('pub-filter', 'pub-search')">
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
    <label>Tags (select multiple)</label>
    <input type="text" class="filter-search-box" id="tag-search" placeholder="🔍 Search tags..." onkeyup="filterTagDropdown()">
    <select id="tag-filter" multiple size="12" onchange="handleTagSelection()"></select>
  </div>
  <div class="filter-group"><label>Text Search</label><input type="text" id="search-box" placeholder="Highlight matches…" onkeyup="debounceSearch()"></div>

  <button class="clear-btn" onclick="resetFilters()">Reset All Filters</button>
  <button class="export-btn" onclick="exportFilteredNotes()">📄 Export Notes</button>
  <button class="export-btn" onclick="copyBibliography()">📋 Copy Citations</button>
  <button class="export-btn" onclick="toggleStats()">📊 Statistics</button>
  <div id="stats-panel" style="display:none;margin-top:12px;padding:12px;background:#f8f9fa;border-radius:6px;font-size:11px;"></div>
  <div id="result-count"></div>
</div>

<div id="main"><div id="content-area"></div></div>

<script>
// ══════════════════════════════════════════════════════════
// DATA (injected by Python)
// ══════════════════════════════════════════════════════════
const notes = {notes_json};
const abstracts = {abstracts_json};

// Build a de-duplicated papers list for Bibliography view
const paperMap = new Map();
[...abstracts, ...notes].forEach(item => {{
    if (!paperMap.has(item.Title) && item.Title) {{
        paperMap.set(item.Title, {{
            Title: item.Title, Year: item.Year, Authors: item.Authors,
            Folder: item.Topic_Folder, Publication: item.Publication || 'N/A'
        }});
    }}
}});
const papersList = Array.from(paperMap.values()).sort((a, b) => b.Year - a.Year);

// ══════════════════════════════════════════════════════════
// CATEGORY SYSTEM (from Python configuration)
// ══════════════════════════════════════════════════════════
const catMapping = {cat_mapping_js};
const catColors = {cat_colors_js};
const catOrder = {cat_order_js};

// ══════════════════════════════════════════════════════════
// UI STATE
// ══════════════════════════════════════════════════════════
let currentView = 'notes';
let searchTimeout = null;
let selectedTags = new Set();

function esc(s) {{ return s.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&'); }}

function applyHighlight(text, term) {{
    if (!term || term.length < 2) return text;
    return text.replace(new RegExp(`(${{esc(term)}})`, 'gi'), '<mark>$1</mark>');
}}

// Fix for apostrophes breaking HTML data attributes
function escapeHTML(str) {{
    return str.replace(/&/g, '&amp;')
              .replace(/</g, '&lt;')
              .replace(/>/g, '&gt;')
              .replace(/"/g, '&quot;')
              .replace(/'/g, '&#39;');
}}

// ══════════════════════════════════════════════════════════
// TAG MULTI-SELECT MANAGEMENT
// ══════════════════════════════════════════════════════════
let allAvailableTags = [];

function handleTagSelection() {{
    const select = document.getElementById('tag-filter');
    selectedTags = new Set(
        Array.from(select.selectedOptions).map(opt => opt.value)
    );
    triggerRender();
}}

function filterTagDropdown() {{
    const select = document.getElementById('tag-filter');
    const searchTerm = document.getElementById('tag-search').value.toLowerCase();

    Array.from(select.options).forEach(option => {{
        const text = option.text.toLowerCase();
        option.style.display = text.includes(searchTerm) ? '' : 'none';
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

    // Get available tags based on current filters
    const availableTags = new Set();
    notes.forEach(n => {{
        if (fFolder !== 'All' && n.Topic_Folder !== fFolder) return;
        if (fTitle  !== 'All' && n.Title !== fTitle) return;
        if (fYear   !== 'All' && n.Year  !== fYear)  return;
        if (fPub    !== 'All' && n.Publication !== fPub) return;
        if (fAuthor !== 'All' && !n.Authors.split(',').map(a => a.trim()).includes(fAuthor)) return;
        if (fCat    !== 'All' && n.Category !== fCat) return;

        if (n.Annotation_Tags) {{
            n.Annotation_Tags.split(',').forEach(t => {{
                const tag = t.trim();
                if (tag) availableTags.add(tag);
            }});
        }}
    }});

    allAvailableTags = Array.from(availableTags).sort();

    // Rebuild options
    select.innerHTML = '';
    allAvailableTags.forEach(tag => {{
        const option = document.createElement('option');
        option.value = tag;
        option.text = '#' + tag;
        if (selectedTags.has(tag)) {{
            option.selected = true;
        }}
        select.add(option);
    }});

    // Apply search filter if present
    const searchTerm = document.getElementById('tag-search')?.value || '';
    if (searchTerm) {{
        filterTagDropdown();
    }}
}}

// ══════════════════════════════════════════════════════════
// DROPDOWN SEARCH FILTERING
// ══════════════════════════════════════════════════════════
function filterDropdown(selectId, searchId) {{
    const select = document.getElementById(selectId);
    const search = document.getElementById(searchId);
    const searchTerm = search.value.toLowerCase();

    const options = Array.from(select.options);

    options.forEach(option => {{
        if (option.value === 'All') {{
            option.style.display = '';
            return;
        }}
        const text = option.text.toLowerCase();
        option.style.display = text.includes(searchTerm) ? '' : 'none';
    }});
}}

// ══════════════════════════════════════════════════════════
// CASCADING (FACETED) DROPDOWN LOGIC
// ══════════════════════════════════════════════════════════
function updateDropdowns() {{
    const fFolder = document.getElementById('folder-filter').value;
    const fTitle  = document.getElementById('title-filter').value;
    const fYear   = document.getElementById('year-filter').value;
    const fAuthor = document.getElementById('author-filter').value;
    const fPub    = document.getElementById('pub-filter').value;
    const fCat    = document.getElementById('cat-filter')?.value || 'All';

    const baseData = currentView === 'notes' ? notes
                   : currentView === 'abstracts' ? abstracts
                   : papersList;

    const getFilteredFor = (ignore) => {{
        return baseData.filter(item => {{
            const folder = item.Topic_Folder || item.Folder;
            if (ignore !== 'folder' && fFolder !== 'All' && folder !== fFolder) return false;
            if (ignore !== 'title'  && fTitle  !== 'All' && item.Title !== fTitle) return false;
            if (ignore !== 'year'   && fYear   !== 'All' && item.Year  !== fYear)  return false;
            if (ignore !== 'pub'    && fPub    !== 'All' && item.Publication !== fPub) return false;
            if (ignore !== 'author' && fAuthor !== 'All') {{
                if (!item.Authors.split(',').map(a => a.trim()).includes(fAuthor)) return false;
            }}
            if (currentView === 'notes') {{
                if (ignore !== 'cat' && fCat !== 'All' && item.Category !== fCat) return false;
                // Note: tag filtering is handled separately via selectedTags
            }}
            return true;
        }});
    }};

    const rebuild = (id, ignore, field, isArray = false) => {{
        const sel = document.getElementById(id);
        if (!sel) return;
        const prev = sel.value;
        const subset = getFilteredFor(ignore);
        const vals = new Set();
        subset.forEach(i => {{
            let v = i[field];
            if (field === 'Topic_Folder' && i.Folder) v = i.Folder;
            if (v) {{
                if (isArray) v.split(',').forEach(x => {{ if (x.trim()) vals.add(x.trim()); }});
                else vals.add(v);
            }}
        }});
        let sorted = [...vals].sort();
        if (field === 'Year') sorted.sort((a, b) => b - a);

        const label = id.split('-')[0];
        sel.innerHTML = `<option value="All">All ${{label}}s</option>`;
        sorted.forEach(v => {{
            const display = id === 'cat-filter' ? (catMapping[v] || v) : v;
            sel.add(new Option(display, v));
        }});
        if (prev !== 'All' && vals.has(prev)) sel.value = prev;
    }};

    rebuild('folder-filter', 'folder', 'Topic_Folder');
    rebuild('title-filter',  'title',  'Title');
    rebuild('year-filter',   'year',   'Year');
    rebuild('author-filter', 'author', 'Authors', true);
    rebuild('pub-filter',    'pub',    'Publication');
    if (currentView === 'notes') {{
        rebuild('cat-filter', 'cat', 'Category');
        updateTagDropdown();
    }}
}}

// ══════════════════════════════════════════════════════════
// CORE RENDER
// ══════════════════════════════════════════════════════════
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

    // ─ Notes (Kanban) view ─────────────────────────────────────────
    if (currentView === 'notes') {{
        const fCat = document.getElementById('cat-filter').value;

        const filtered = notes.filter(n => {{
            if (fFolder !== 'All' && n.Topic_Folder !== fFolder) return false;
            if (fTitle  !== 'All' && n.Title !== fTitle) return false;
            if (fYear   !== 'All' && n.Year  !== fYear)  return false;
            if (fPub    !== 'All' && n.Publication !== fPub) return false;
            if (fAuthor !== 'All' && !n.Authors.split(',').map(a => a.trim()).includes(fAuthor)) return false;
            if (fCat    !== 'All' && n.Category !== fCat) return false;

            // Multi-tag filter: note must have ALL selected tags
            if (selectedTags.size > 0) {{
                const noteTags = n.Annotation_Tags ? n.Annotation_Tags.split(',').map(t => t.trim()) : [];
                for (const tag of selectedTags) {{
                    if (!noteTags.includes(tag)) return false;
                }}
            }}

            if (term && !(n.Title + n.Highlight + n.My_Comment + n.Authors).toLowerCase().includes(term)) return false;
            return true;
        }});

        // Group by paper title
        const grouped = {{}};
        filtered.forEach(n => {{
            if (!grouped[n.Title]) grouped[n.Title] = [];
            grouped[n.Title].push(n);
        }});

        let html = '';
        for (const [title, group] of Object.entries(grouped)) {{
            const f = group[0];

            // Prepare APA citation for this paper
            const authors = f.Authors.split(',').map(a => a.trim());
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
            const citation = `${{authorString}}. (${{f.Year}}). ${{title}}. ${{f.Publication}}.`;

            html += `<div class="paper-group">`;
            html += `<button class="copy-citation-btn" onclick="copyCitation('${{citation.replace(/'/g, "\\\\'")}}')" title="Copy APA citation">📋 Copy Citation</button>`;
            html += `<h3>${{applyHighlight(title, term)}} (${{f.Year}})</h3>`;
            html += `<div class="paper-meta">📁 ${{f.Topic_Folder}} &nbsp;•&nbsp; 👥 ${{applyHighlight(f.Authors, term)}} &nbsp;•&nbsp; 📚 ${{applyHighlight(f.Publication, term)}}</div>`;
            html += `<div class="kanban-board">`;

            // Bucket notes by category
            const catGroups = {{}};
            group.forEach(n => {{
                if (!catGroups[n.Category]) catGroups[n.Category] = [];
                catGroups[n.Category].push(n);
            }});

            // Render each column in canonical order
            catOrder.forEach(cat => {{
                if (!catGroups[cat]) return;
                const color = catColors[cat] || '#ccc';
                const items = catGroups[cat];
                html += `<div class="kanban-column" style="border-top-color:${{color}}">`;
                html += `<h4><span>${{catMapping[cat]}}</span><span class="col-count" style="color:${{color}}">${{items.length}}</span></h4>`;
                items.forEach(n => {{
                    // Prepare note data for copying
                    const noteData = {{
                        title: title,
                        year: f.Year,
                        authors: f.Authors,
                        category: catMapping[cat],
                        tags: n.Annotation_Tags || '',
                        highlight: n.Highlight || '',
                        comment: n.My_Comment || ''
                    }};

                    html += `<div class="note-card" style="border-left-color:${{color}}" data-note="${{escapeHTML(JSON.stringify(noteData))}}">`;
                    html += `<button class="copy-note-btn" onclick="copyNoteFromCard(this)" title="Copy this note">📋 Copy</button>`;

                    // Enhanced tag display with highlighting
                    if (n.Annotation_Tags) {{
                        const rawTags = n.Annotation_Tags.split(',').map(t => t.trim()).filter(t => t);
                        const noteTags = [...new Set(rawTags)]; // Deduplicate paper and highlight tags
                        const matchCount = noteTags.filter(t => selectedTags.has(t)).length;

                        noteTags.forEach(tag => {{
                            const isHighlighted = selectedTags.has(tag);
                            const tagClass = isHighlighted ? 'tag highlighted' : 'tag';
                            html += `<div class="${{tagClass}}">#${{applyHighlight(tag, term)}}</div>`;
                        }});

                        if (matchCount > 1) {{
                            html += `<span class="tag-count">${{matchCount}} matching tags</span>`;
                        }}
                    }}

                    if (n.Highlight)   html += `<div class="highlight-box">${{applyHighlight(n.Highlight.replace(/\\n/g, '<br>'), term)}}</div>`;
                    if (n.My_Comment)  html += `<div class="comment-box">${{applyHighlight(n.My_Comment.replace(/\\n/g, '<br>'), term)}}</div>`;
                    html += `</div>`;
                }});
                html += `</div>`;
            }});

            html += `</div></div>`;
        }}

        el.innerHTML = html || '<p style="color:#999;text-align:center;margin-top:60px">No matching notes.</p>';

        const tagInfo = selectedTags.size > 0 ? ` with ${{selectedTags.size}} tag(s)` : '';
        counter.textContent = `${{filtered.length}} note(s) across ${{Object.keys(grouped).length}} paper(s)${{tagInfo}}`;

    // ─ Abstracts view ──────────────────────────────────────────────
    }} else if (currentView === 'abstracts') {{
        const filtered = abstracts.filter(a => {{
            if (fFolder !== 'All' && a.Topic_Folder !== fFolder) return false;
            if (fTitle  !== 'All' && a.Title !== fTitle)  return false;
            if (fYear   !== 'All' && a.Year  !== fYear)   return false;
            if (fPub    !== 'All' && a.Publication !== fPub) return false;
            if (fAuthor !== 'All' && !a.Authors.split(',').map(x => x.trim()).includes(fAuthor)) return false;
            if (term && !(a.Title + a.Abstract).toLowerCase().includes(term)) return false;
            return true;
        }});

        let html = '';
        filtered.forEach(a => {{
            // Prepare APA citation
            const authors = a.Authors.split(',').map(au => au.trim());
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
            const citation = `${{authorString}}. (${{a.Year}}). ${{a.Title}}. ${{a.Publication}}.`;

            html += `<div class="paper-group">`;
            html += `<button class="copy-citation-btn" onclick="copyCitation('${{citation.replace(/'/g, "\\\\'")}}')" title="Copy APA citation">📋 Copy Citation</button>`;
            html += `<h3>${{applyHighlight(a.Title, term)}} (${{a.Year}})</h3>`;
            html += `<div class="paper-meta">📁 ${{a.Topic_Folder}} &nbsp;•&nbsp; 👥 ${{a.Authors}}</div>`;
            html += `<div style="line-height:1.6;font-size:.93em">${{applyHighlight(a.Abstract.replace(/\\n/g, '<br><br>'), term)}}</div>`;
            html += `</div>`;
        }});
        el.innerHTML = html || '<p style="color:#999;text-align:center;margin-top:60px">No matching abstracts.</p>';
        counter.textContent = `${{filtered.length}} abstract(s)`;

    // ─ Bibliography view ───────────────────────────────────────────
    }} else {{
        const filtered = papersList.filter(p => {{
            if (fFolder !== 'All' && p.Folder !== fFolder) return false;
            if (fTitle  !== 'All' && p.Title  !== fTitle)  return false;
            if (fYear   !== 'All' && p.Year   !== fYear)   return false;
            if (fPub    !== 'All' && p.Publication !== fPub) return false;
            if (fAuthor !== 'All' && !p.Authors.split(',').map(x => x.trim()).includes(fAuthor)) return false;
            if (term && !(p.Title + p.Authors + p.Publication).toLowerCase().includes(term)) return false;
            return true;
        }});

        let html = '<table><thead><tr><th>Year</th><th>Authors</th><th>Title</th><th>Publication</th></tr></thead><tbody>';
        filtered.forEach(p => {{
            html += `<tr>`;
            html += `<td>${{p.Year}}</td>`;
            html += `<td>${{applyHighlight(p.Authors, term)}}</td>`;
            html += `<td>${{applyHighlight(p.Title, term)}}</td>`;
            html += `<td>${{applyHighlight(p.Publication, term)}}</td>`;
            html += `</tr>`;
        }});
        html += '</tbody></table>';
        el.innerHTML = html;
        counter.textContent = `${{filtered.length}} paper(s)`;
    }}
}}

// ══════════════════════════════════════════════════════════
// UI HELPERS
// ══════════════════════════════════════════════════════════
function resetFilters() {{
    ['folder-filter','title-filter','year-filter','author-filter',
     'pub-filter','cat-filter'].forEach(id => {{
        const el = document.getElementById(id);
        if (el) el.value = 'All';
    }});
    ['folder-search','title-search','author-search','pub-search','tag-search'].forEach(id => {{
        const el = document.getElementById(id);
        if (el) {{
            el.value = '';
            // Show all options
            const filterId = id.replace('-search', '-filter');
            const select = document.getElementById(filterId);
            if (select) {{
                Array.from(select.options).forEach(opt => opt.style.display = '');
            }}
        }}
    }});
    selectedTags.clear();
    const tagSelect = document.getElementById('tag-filter');
    if (tagSelect) {{
        Array.from(tagSelect.options).forEach(opt => opt.selected = false);
    }}
    document.getElementById('search-box').value = '';
    triggerRender();
}}

function debounceSearch() {{
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(triggerRender, 250);
}}

function setView(view) {{
    currentView = view;
    document.getElementById('btn-notes').className     = view === 'notes'     ? 'active' : '';
    document.getElementById('btn-abstracts').className  = view === 'abstracts' ? 'active' : '';
    document.getElementById('btn-biblio').className     = view === 'biblio'    ? 'active' : '';
    document.getElementById('cat-filter-container').style.display = view === 'notes' ? 'block' : 'none';
    document.getElementById('tag-filter-container').style.display = view === 'notes' ? 'block' : 'none';
    triggerRender();
}}

window.onload = function() {{
    updateDropdowns();
    triggerRender();
}};

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
            const noteTags = n.Annotation_Tags ? n.Annotation_Tags.split(',').map(t => t.trim()) : [];
            for (const tag of selectedTags) {{
                if (!noteTags.includes(tag)) return false;
            }}
        }}
        if (term && !(n.Title + n.Highlight + n.My_Comment + n.Authors).toLowerCase().includes(term)) return false;
        return true;
    }});

    // Group by paper
    const grouped = {{}};
    filtered.forEach(n => {{
        if (!grouped[n.Title]) grouped[n.Title] = [];
        grouped[n.Title].push(n);
    }});

    let exportText = `EXPORTED NOTES - ${{new Date().toLocaleDateString()}}\\n`;
    exportText += `Total: ${{filtered.length}} notes from ${{Object.keys(grouped).length}} papers\\n`;
    exportText += `${{selectedTags.size > 0 ? 'Tags: ' + Array.from(selectedTags).join(', ') : ''}}\\n`;
    exportText += '='.repeat(80) + '\\n\\n';

    for (const [title, group] of Object.entries(grouped)) {{
        const first = group[0];
        exportText += `${{title}} (${{first.Year}})\\n`;
        exportText += `Authors: ${{first.Authors}}\\n`;
        exportText += `Publication: ${{first.Publication}}\\n`;
        exportText += `Folder: ${{first.Topic_Folder}}\\n`;
        exportText += '-'.repeat(80) + '\\n\\n';

        // Group notes by category
        const byCategory = {{}};
        group.forEach(n => {{
            if (!byCategory[n.Category]) byCategory[n.Category] = [];
            byCategory[n.Category].push(n);
        }});

        catOrder.forEach(cat => {{
            if (!byCategory[cat]) return;
            exportText += `  [${{catMapping[cat]}}]\\n`;
            byCategory[cat].forEach(n => {{
                if (n.Annotation_Tags) exportText += `    Tags: ${{n.Annotation_Tags}}\\n`;
                if (n.Highlight) exportText += `    "${{n.Highlight}}"\\n`;
                if (n.My_Comment) exportText += `    📝 ${{n.My_Comment}}\\n`;
                exportText += '\\n';
            }});
        }});

        exportText += '\\n' + '='.repeat(80) + '\\n\\n';
    }}

    // Copy to clipboard
    navigator.clipboard.writeText(exportText).then(() => {{
        alert(`✅ Exported ${{filtered.length}} notes to clipboard!\\n\\nYou can now paste them into your essay document.`);
    }}).catch(() => {{
        // Fallback: download as file
        const blob = new Blob([exportText], {{ type: 'text/plain' }});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `notes_export_${{new Date().toISOString().split('T')[0]}}.txt`;
        a.click();
    }});
}}

function copyBibliography() {{
    const term    = document.getElementById('search-box').value.toLowerCase();
    const fFolder = document.getElementById('folder-filter').value;
    const fTitle  = document.getElementById('title-filter').value;
    const fYear   = document.getElementById('year-filter').value;
    const fAuthor = document.getElementById('author-filter').value;
    const fPub    = document.getElementById('pub-filter').value;

    // Get unique papers from filtered notes
    const paperTitles = new Set();
    const filtered = notes.filter(n => {{
        if (fFolder !== 'All' && n.Topic_Folder !== fFolder) return false;
        if (fTitle  !== 'All' && n.Title !== fTitle) return false;
        if (fYear   !== 'All' && n.Year  !== fYear)  return false;
        if (fPub    !== 'All' && n.Publication !== fPub) return false;
        if (fAuthor !== 'All' && !n.Authors.split(',').map(a => a.trim()).includes(fAuthor)) return false;
        if (selectedTags.size > 0) {{
            const noteTags = n.Annotation_Tags ? n.Annotation_Tags.split(',').map(t => t.trim()) : [];
            for (const tag of selectedTags) {{
                if (!noteTags.includes(tag)) return false;
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

    // APA 7 format citations
    let bibText = '';
    papers.forEach((p, index) => {{
        // Format authors in APA style (Last, F. M., & Last, F. M.)
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

        // APA 7 format: Author(s). (Year). Title. Publication.
        bibText += `${{authorString}}. (${{p.Year}}). ${{p.Title}}. ${{p.Publication}}.`;

        // Add blank line between entries except for the last one
        if (index < papers.length - 1) {{
            bibText += '\\n\\n';
        }}
    }});

    navigator.clipboard.writeText(bibText).then(() => {{
        alert(`✅ Copied ${{papers.length}} APA citations to clipboard!`);
    }}).catch(err => {{
        alert('Failed to copy to clipboard. Please try again.');
    }});
}}

function toggleStats() {{
    const panel = document.getElementById('stats-panel');
    if (panel.style.display === 'none') {{
        // Calculate statistics
        const totalPapers = new Set(notes.map(n => n.Title)).size;
        const totalNotes = notes.length;
        const avgNotesPerPaper = (totalNotes / totalPapers).toFixed(1);

        // Category breakdown
        const catCounts = {{}};
        notes.forEach(n => {{
            catCounts[n.Category] = (catCounts[n.Category] || 0) + 1;
        }});

        // Tag frequency
        const tagCounts = {{}};
        notes.forEach(n => {{
            if (n.Annotation_Tags) {{
                const uniqueTags = new Set(n.Annotation_Tags.split(',').map(t => t.trim()).filter(t => t));
                uniqueTags.forEach(tag => {{
                    tagCounts[tag] = (tagCounts[tag] || 0) + 1;
                }});
            }}
        }});
        const topTags = Object.entries(tagCounts)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5)
            .map(([tag, count]) => `#${{tag}} (${{count}})`);

        // Year distribution
        const yearCounts = {{}};
        notes.forEach(n => {{
            yearCounts[n.Year] = (yearCounts[n.Year] || 0) + 1;
        }});

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
        // Visual feedback - could enhance this with a tooltip
        const msg = document.createElement('div');
        msg.textContent = '✅ Citation copied!';
        msg.style.cssText = 'position:fixed;top:20px;right:20px;background:#27ae60;color:#fff;padding:12px 20px;border-radius:6px;font-weight:600;z-index:9999;box-shadow:0 4px 12px rgba(0,0,0,.15);';
        document.body.appendChild(msg);
        setTimeout(() => msg.remove(), 2000);
    }}).catch(() => {{
        alert('Failed to copy citation. Please try again.');
    }});
}}

function copyNoteFromCard(button) {{
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
        const msg = document.createElement('div');
        msg.textContent = '✅ Note copied!';
        msg.style.cssText = 'position:fixed;top:20px;right:20px;background:#27ae60;color:#fff;padding:12px 20px;border-radius:6px;font-weight:600;z-index:9999;box-shadow:0 4px 12px rgba(0,0,0,.15);';
        document.body.appendChild(msg);
        setTimeout(() => msg.remove(), 2000);
    }}).catch(() => {{
        alert('Failed to copy note. Please try again.');
    }});
}}
</script>
</body>
</html>"""

with open(OUTPUT_HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"\n✅ Dashboard written to: {OUTPUT_HTML_PATH}")
print("=" * 80)
print("\nCONFIGURATION SUMMARY:")
print(f"  • Categories: {list(CATEGORY_NAMES.keys())}")
print(f"  • Color mappings: {len(COLOR_MAPPING)}")
print(f"  • Display order: {len(CATEGORY_ORDER)} categories")
print("\nTo customize this dashboard:")
print("  1. Edit the configuration section at the top of this script")
print("  2. Run the script again")
print("=" * 80)