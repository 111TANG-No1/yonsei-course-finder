# Yonsei Course Finder (OCR Demo)

A small demo that turns Yonsei course “plan” screenshots into a structured grading table (midterm/final/assignment/attendance/etc.), and provides a simple web UI for filtering.

## What it does
- OCR course plan images into text
- Parse grading percentages from OCR text
- Merge pages into one file per course (`data/merged/course_*.txt`)
- Output a structured CSV (`data/course_grading.csv`)
- Web UI to filter by assessment item & threshold
- Fallback override when OCR cannot reliably extract percentages (`data/override.csv`)

## Project structure (key files)
- `ocr_plans_pages.py`  
  OCR images under `data/plans_pages/*.png` → text in `data/plans_pages_ocr/*.txt`
- `parse_ocr_pages.py`  
  Parse each OCR page → `data/plans_pages_parsed.csv`
- `parse_merged.py`  
  Merge pages & parse into course-level results → `data/course_grading.csv`
- `web.html`  
  Local web UI (reads `data/course_grading.csv` + optional `data/override.csv`)

## How to run (local)
### 1) Activate env
```bash
conda activate ocr
