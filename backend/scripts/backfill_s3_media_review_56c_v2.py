#!/usr/bin/env python3
"""Batch 56C — Products/Brands S3 media backfill review workbook generator.

Generates an XLSX review file (v2 fixed Excel theme issue) for existing Products and Brands image/logo paths.
It does not upload files and does not modify DynamoDB.

Run from project root or backend folder with backend venv activated.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import mimetypes
import os
import posixpath
import re
import sys
import zipfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import unquote, urlparse

import csv

import boto3
import botocore

DEFAULT_BUCKET = "rsa-cms-media-537765358118-ap-southeast-1"
SKIP_DIRS = {
    ".git", ".idea", ".vscode", "venv", ".venv", "node_modules", "__pycache__",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", "dist", "build", ".next",
}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"}

HEADERS = [
    "Review Decision",
    "Type",
    "Record ID",
    "Record Name",
    "Public Visibility",
    "Brand/Category",
    "Current Local Filename",
    "To-be Filename",
    "Current Project Path",
    "To-be Project Path",
    "S3 Key",
    "Local Match Status",
    "S3 Status",
    "Planned Action",
    "Local File Match Count",
    "Matched Local Source Path",
    "File Size KB",
    "Content Type",
    "DynamoDB Table",
    "Image Field",
    "Notes",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Batch 56C Products/Brands S3 media backfill review XLSX.")
    parser.add_argument("--project-root", required=True, help="Project root folder, e.g. C:\\...\\cctv-crm-project")
    parser.add_argument("--out", default=None, help="Output .xlsx path. Default: <project-root>/docs/review/batch56c_products_brands_s3_backfill_review.xlsx")
    parser.add_argument("--region", default=os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "ap-southeast-1")
    parser.add_argument("--bucket", default=os.getenv("RSA_MEDIA_S3_BUCKET") or DEFAULT_BUCKET)
    parser.add_argument("--table-prefix", default="rsa_")
    parser.add_argument("--year", default=str(dt.datetime.utcnow().year))
    parser.add_argument("--month", default=f"{dt.datetime.utcnow().month:02d}")
    return parser.parse_args()


def scan_table(ddb: Any, table_name: str) -> List[Dict[str, Any]]:
    table = ddb.Table(table_name)
    items: List[Dict[str, Any]] = []
    kwargs: Dict[str, Any] = {}
    while True:
        response = table.scan(**kwargs)
        items.extend(response.get("Items", []))
        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            break
        kwargs["ExclusiveStartKey"] = last_key
    return items


def first_value(item: Dict[str, Any], keys: Iterable[str]) -> str:
    for key in keys:
        value = item.get(key)
        if value not in (None, ""):
            return str(value)
    return ""


def normalize_media_path(path: str) -> str:
    path = (path or "").strip()
    if not path:
        return ""
    # Strip quotes and URL fragments/query strings where possible.
    path = path.strip("'\"")
    parsed = urlparse(path)
    if parsed.scheme and parsed.netloc:
        path = parsed.path
    else:
        path = path.split("?", 1)[0].split("#", 1)[0]
    path = unquote(path).replace("\\", "/")
    return path


def extract_filename(path: str) -> str:
    norm = normalize_media_path(path)
    if not norm:
        return ""
    return posixpath.basename(norm.rstrip("/"))


def sanitize_filename(filename: str) -> str:
    filename = filename.strip().replace(" ", "-")
    filename = re.sub(r"[^A-Za-z0-9._-]", "-", filename)
    filename = re.sub(r"-+", "-", filename)
    return filename.lower()


def current_path_to_target(record_type: str, current_path: str, year: str, month: str) -> Dict[str, str]:
    norm = normalize_media_path(current_path)
    filename = extract_filename(norm)
    to_be_filename = sanitize_filename(filename) if filename else ""

    if norm.startswith("/api/media/"):
        s3_key = norm[len("/api/media/"):]
        return {
            "current_filename": filename,
            "to_be_filename": posixpath.basename(s3_key),
            "current_project_path": norm,
            "to_be_project_path": norm,
            "s3_key": s3_key,
            "path_mode": "api_media_existing",
        }

    # For old static paths, stage into the current approved media folder naming.
    media_folder = "products" if record_type == "product" else "brands"
    s3_key = f"{media_folder}/{year}/{month}/{to_be_filename}" if to_be_filename else ""
    return {
        "current_filename": filename,
        "to_be_filename": to_be_filename,
        "current_project_path": norm,
        "to_be_project_path": f"/api/media/{s3_key}" if s3_key else "",
        "s3_key": s3_key,
        "path_mode": "static_path_needs_record_update",
    }


def build_filename_index(project_root: Path) -> Dict[str, List[Path]]:
    index: Dict[str, List[Path]] = {}
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for name in files:
            suffix = Path(name).suffix.lower()
            if suffix not in IMAGE_EXTS:
                continue
            index.setdefault(name.lower(), []).append(Path(root) / name)
    return index


def choose_local_match(filename_index: Dict[str, List[Path]], current_filename: str, to_be_filename: str) -> Dict[str, Any]:
    names = []
    if current_filename:
        names.append(current_filename.lower())
    if to_be_filename and to_be_filename.lower() not in names:
        names.append(to_be_filename.lower())

    matches: List[Path] = []
    for name in names:
        matches.extend(filename_index.get(name, []))

    # De-duplicate while preserving order.
    seen = set()
    unique_matches = []
    for p in matches:
        key = str(p).lower()
        if key not in seen:
            seen.add(key)
            unique_matches.append(p)

    if len(unique_matches) == 1:
        p = unique_matches[0]
        return {
            "status": "FOUND",
            "count": 1,
            "path": str(p),
            "size_kb": round(p.stat().st_size / 1024, 1),
            "content_type": mimetypes.guess_type(p.name)[0] or "application/octet-stream",
        }
    if len(unique_matches) == 0:
        return {"status": "MISSING", "count": 0, "path": "", "size_kb": "", "content_type": ""}
    return {
        "status": "AMBIGUOUS",
        "count": len(unique_matches),
        "path": " | ".join(str(p) for p in unique_matches[:5]),
        "size_kb": "",
        "content_type": "",
    }


def check_s3_object(s3: Any, bucket: str, key: str) -> str:
    if not key:
        return "NOT_CHECKED"
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return "ALREADY_IN_S3"
    except botocore.exceptions.ClientError as exc:
        code = str(exc.response.get("Error", {}).get("Code", ""))
        if code in {"404", "NoSuchKey", "NotFound"}:
            return "MISSING_IN_S3"
        if code in {"403", "AccessDenied"}:
            return "S3_ACCESS_DENIED"
        return f"S3_ERROR_{code or 'UNKNOWN'}"


def planned_action(path_mode: str, local_status: str, s3_status: str) -> str:
    if s3_status == "ALREADY_IN_S3":
        return "NO_ACTION_ALREADY_IN_S3"
    if local_status != "FOUND":
        return "REVIEW_LOCAL_FILE"
    if path_mode == "api_media_existing":
        return "UPLOAD_ONLY"
    if path_mode == "static_path_needs_record_update":
        return "UPLOAD_AND_UPDATE_RECORD_REVIEW"
    return "REVIEW"


def collect_rows(args: argparse.Namespace) -> List[List[Any]]:
    project_root = Path(args.project_root).resolve()
    print(f"Indexing local image files under: {project_root}")
    filename_index = build_filename_index(project_root)
    print(f"Indexed unique image filenames: {len(filename_index)}")

    ddb = boto3.resource("dynamodb", region_name=args.region)
    s3 = boto3.client("s3", region_name=args.region)

    configs = [
        {
            "type": "product",
            "table": f"{args.table_prefix}products",
            "id_keys": ["product_id", "id", "product_key", "sku"],
            "name_keys": ["product_name", "name", "title"],
            "path_keys": ["image_path", "product_image_path", "image_url"],
            "visibility_keys": ["show_flag", "visible", "public_visibility"],
            "group_keys": ["category_name", "category_key", "product_brand_name", "brand_name"],
        },
        {
            "type": "brand",
            "table": f"{args.table_prefix}brands",
            "id_keys": ["product_brand_key", "brand_key", "brand_id", "id"],
            "name_keys": ["product_brand_name", "brand_name", "name"],
            "path_keys": ["brand_logo_path", "logo_path", "image_path", "brand_image_path"],
            "visibility_keys": ["show_flag", "visible", "public_visibility"],
            "group_keys": ["brand_type", "category_name"],
        },
    ]

    rows: List[List[Any]] = []
    for cfg in configs:
        print(f"Scanning DynamoDB table: {cfg['table']}")
        items = scan_table(ddb, cfg["table"])
        print(f"  Records: {len(items)}")
        for item in items:
            current_path = first_value(item, cfg["path_keys"])
            if not current_path:
                continue
            image_field = next((k for k in cfg["path_keys"] if item.get(k) not in (None, "")), "")
            target = current_path_to_target(cfg["type"], current_path, args.year, args.month)
            local = choose_local_match(filename_index, target["current_filename"], target["to_be_filename"])
            s3_status = check_s3_object(s3, args.bucket, target["s3_key"])
            action = planned_action(target["path_mode"], local["status"], s3_status)
            decision = "Review"
            notes = ""
            if action == "NO_ACTION_ALREADY_IN_S3":
                decision = "Done"
                notes = "S3 object already exists."
            elif action == "UPLOAD_ONLY":
                notes = "Record already points to /api/media; upload missing local file to S3 using S3 Key."
            elif action == "UPLOAD_AND_UPDATE_RECORD_REVIEW":
                notes = "Old static path found; review before changing DynamoDB path to To-be Project Path."

            rows.append([
                decision,
                cfg["type"],
                first_value(item, cfg["id_keys"]),
                first_value(item, cfg["name_keys"]),
                first_value(item, cfg["visibility_keys"]),
                first_value(item, cfg["group_keys"]),
                target["current_filename"],
                target["to_be_filename"],
                target["current_project_path"],
                target["to_be_project_path"],
                target["s3_key"],
                local["status"],
                s3_status,
                action,
                local["count"],
                local["path"],
                local["size_kb"],
                local["content_type"],
                cfg["table"],
                image_field,
                notes,
            ])
    return rows


def col_letter(n: int) -> str:
    result = ""
    while n:
        n, rem = divmod(n - 1, 26)
        result = chr(65 + rem) + result
    return result


def xlsx_cell(value: Any, row: int, col: int, style: int = 0) -> str:
    ref = f"{col_letter(col)}{row}"
    s_attr = f' s="{style}"' if style else ""
    if value is None or value == "":
        return f'<c r="{ref}"{s_attr}/>'
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f'<c r="{ref}"{s_attr}><v>{value}</v></c>'
    text = html.escape(str(value), quote=False)
    return f'<c r="{ref}" t="inlineStr"{s_attr}><is><t>{text}</t></is></c>'


def xlsx_sheet_xml(rows: List[List[Any]], header_style: int = 1) -> str:
    out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>']
    out.append('<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">')
    out.append('<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>')
    out.append('<cols>')
    widths = [16,12,18,30,14,24,28,28,45,45,38,20,22,32,14,55,12,16,18,18,48]
    for i, width in enumerate(widths, 1):
        out.append(f'<col min="{i}" max="{i}" width="{width}" customWidth="1"/>')
    out.append('</cols>')
    out.append('<sheetData>')
    for r_idx, row_values in enumerate(rows, 1):
        out.append(f'<row r="{r_idx}">')
        for c_idx, value in enumerate(row_values, 1):
            out.append(xlsx_cell(value, r_idx, c_idx, header_style if r_idx == 1 else 0))
        out.append('</row>')
    out.append('</sheetData>')
    last_row = max(len(rows), 1)
    last_col = col_letter(len(rows[0]) if rows else 1)
    out.append(f'<autoFilter ref="A1:{last_col}{last_row}"/>')
    out.append('</worksheet>')
    return "".join(out)


def write_xlsx(path: Path, data_rows: List[List[Any]]) -> None:
    rows = [HEADERS] + data_rows
    legend_rows = [
        ["Batch 56C — Backfill Existing Product/Brand Images to S3", ""],
        ["Purpose", "Review product/brand image paths and local file matches before uploading missing files to S3."],
        ["Scope", "Products and Brands only. Project Gallery and Contact Persons are intentionally skipped."],
        ["Safe default", "This script only generates the review workbook. It does not upload files and does not update DynamoDB."],
        ["Recommended next step", "Review rows with MISSING_IN_S3 + FOUND local match. Approve before execute script is prepared."],
        ["UPLOAD_ONLY", "DynamoDB path already starts with /api/media/. Only the missing S3 object must be uploaded."],
        ["UPLOAD_AND_UPDATE_RECORD_REVIEW", "Current path is old static path. Upload and DynamoDB path update should be reviewed before execution."],
        ["AMBIGUOUS", "Multiple local files have the same filename. Choose manually before upload."],
        ["MISSING", "No local file with the same filename was found under project root."],
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    created = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    workbook_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Batch56C Review" sheetId="1" r:id="rId1"/><sheet name="Status Legend" sheetId="2" r:id="rId2"/></sheets></workbook>'''
    rels_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>'''
    root_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/></Relationships>'''
    content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/><Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/><Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/></Types>'''
    styles = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><color rgb="FFFFFFFF"/><sz val="11"/><name val="Calibri"/></font></fonts><fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF7F1D1D"/><bgColor indexed="64"/></patternFill></fill></fills><borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf><xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFill="1" applyFont="1" applyAlignment="1"><alignment horizontal="center" vertical="center" wrapText="1"/></xf></cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>'''
    theme = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Office Theme"><a:themeElements><a:clrScheme name="Office"><a:dk1><a:sysClr val="windowText" lastClr="000000"/></a:dk1><a:lt1><a:sysClr val="window" lastClr="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="1F2937"/></a:dk2><a:lt2><a:srgbClr val="F9FAFB"/></a:lt2><a:accent1><a:srgbClr val="7F1D1D"/></a:accent1><a:accent2><a:srgbClr val="B91C1C"/></a:accent2><a:accent3><a:srgbClr val="F59E0B"/></a:accent3><a:accent4><a:srgbClr val="059669"/></a:accent4><a:accent5><a:srgbClr val="2563EB"/></a:accent5><a:accent6><a:srgbClr val="6B7280"/></a:accent6><a:hlink><a:srgbClr val="2563EB"/></a:hlink><a:folHlink><a:srgbClr val="7C3AED"/></a:folHlink></a:clrScheme><a:fontScheme name="Office"><a:majorFont><a:latin typeface="Calibri"/></a:majorFont><a:minorFont><a:latin typeface="Calibri"/></a:minorFont></a:fontScheme><a:fmtScheme name="Office"/></a:themeElements></a:theme>'''
    core = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>Batch 56C S3 Media Backfill Review</dc:title><dc:creator>RSA CMS script</dc:creator><cp:lastModifiedBy>RSA CMS script</cp:lastModifiedBy><dcterms:created xsi:type="dcterms:W3CDTF">{created}</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">{created}</dcterms:modified></cp:coreProperties>'''
    app = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"><Application>RSA CMS</Application></Properties>'''

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", root_rels)
        z.writestr("docProps/core.xml", core)
        z.writestr("docProps/app.xml", app)
        z.writestr("xl/workbook.xml", workbook_xml)
        z.writestr("xl/_rels/workbook.xml.rels", rels_xml)
        z.writestr("xl/styles.xml", styles)
        z.writestr("xl/worksheets/sheet1.xml", xlsx_sheet_xml(rows))
        z.writestr("xl/worksheets/sheet2.xml", xlsx_sheet_xml(legend_rows))


def write_csv(path: Path, data_rows: List[List[Any]]) -> None:
    csv_path = path.with_suffix(".csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)
        writer.writerows(data_rows)


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    if not project_root.exists():
        print(f"ERROR project root does not exist: {project_root}", file=sys.stderr)
        return 2
    out = Path(args.out) if args.out else project_root / "docs" / "review" / "batch56c_products_brands_s3_backfill_review.xlsx"

    print("Batch 56C review workbook generator")
    print(f"Region: {args.region}")
    print(f"Bucket: {args.bucket}")
    rows = collect_rows(args)
    rows.sort(key=lambda r: (str(r[1]), str(r[3]).lower(), str(r[2])))
    write_xlsx(out, rows)
    write_csv(out, rows)

    print("DONE")
    print(f"Rows written: {len(rows)}")
    print(f"Workbook: {out}")
    print(f"CSV fallback: {out.with_suffix('.csv')}")
    print("No files uploaded. No DynamoDB records modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
