
import os, json, xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Iterable

def _get_in(obj: dict, path: str):
    # Minimal JSONPath-ish getter supporting []. and simple '+' concat rule
    parts = [p.strip() for p in path.split('+')]
    values = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if p.startswith("concat(") and p.endswith(")"):
            # Not implemented fully; just return empty for now
            continue
        sub = _extract(obj, p)
        if isinstance(sub, list):
            sub = "; ".join(str(x) for x in sub if x is not None)
        values.append("" if sub is None else str(sub))
    return " ".join(values).strip()

def _extract(obj, path: str):
    # Support simple dotted path and [] array expansion
    segs = path.split('.')
    cur = [obj]
    for seg in segs:
        next_items = []
        array = False
        if seg.endswith("[]"):
            seg = seg[:-2]
            array = True
        for item in cur:
            if isinstance(item, dict) and seg in item:
                val = item[seg]
                if array and isinstance(val, list):
                    next_items.extend(val)
                else:
                    next_items.append(val)
        cur = next_items
    if not cur:
        return None
    if len(cur) == 1:
        return cur[0]
    return cur

def map_to_endnote_fields(record: dict, mapping: dict) -> dict:
    out = {}
    for k, spec in mapping.items():
        if spec is None:
            out[k] = ""
        elif isinstance(spec, str):
            out[k] = _get_in(record, spec)
        elif isinstance(spec, list):
            vals = []
            for s in spec:
                v = _get_in(record, s)
                if v:
                    vals.append(v)
            out[k] = "; ".join(x for x in vals if x)
        else:
            out[k] = ""
    return out

def export_endnote_xml(records: list[dict], mapping_file: str, ref_type: str="Patent",
                       attach_policy: str="url", attachment_urls: dict|None=None) -> str:
    with open(mapping_file, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    mapping = cfg["transform"]
    root = ET.Element("xml")
    for rec in records:
        m = map_to_endnote_fields(rec, mapping)
        rec_el = ET.SubElement(root, "record")
        ET.SubElement(rec_el, "ref-type", {"name": ref_type}).text = ref_type
        for k,v in m.items():
            if not v:
                continue
            f_el = ET.SubElement(rec_el, "titles" if k.lower()=="title" else "custom", {"name": k})
            f_el.text = v
        # Attachments
        if attach_policy and attach_policy != "none":
            att = ET.SubElement(rec_el, "attachments")
            if attach_policy == "url":
                url = m.get("URL")
                if url:
                    a = ET.SubElement(att, "url")
                    a.text = url
            elif attach_policy == "file" and attachment_urls:
                # Map app number to path
                app = m.get("Application Number")
                path = attachment_urls.get(app) if app and attachment_urls else None
                if path:
                    a = ET.SubElement(att, "file")
                    a.text = path
    path = str(Path.cwd() / "endnote_export.xml")
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    return path

def export_ris(records: list[dict], mapping_file: str) -> str:
    with open(mapping_file, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    mapping = cfg["transform"]
    lines = []
    for rec in records:
        m = map_to_endnote_fields(rec, mapping)
        lines.append("TY  - PAT")
        if m.get("Title"):
            lines.append(f"TI  - {m['Title']}")
        if m.get("Patent Number"):
            lines.append(f"AN  - {m['Patent Number']}")
        if m.get("Application Number"):
            lines.append(f"AU  - {m['Application Number']}")  # Note: AU is authors; here we include application # for tools
        if m.get("Inventors"):
            for inv in m["Inventors"].split('; '):
                lines.append(f"AU  - {inv}")
        if m.get("Assignee/Applicant"):
            lines.append(f"PB  - {m['Assignee/Applicant']}")
        if m.get("Filing Date"):
            lines.append(f"DA  - {m['Filing Date']}")
        if m.get("Issue Date"):
            lines.append(f"PY  - {m['Issue Date']}")
        if m.get("URL"):
            lines.append(f"UR  - {m['URL']}")
        # Attorneys/Correspondence - v2 draft fields in RIS NOTE fields
        if m.get("Docket Number"):
            lines.append(f"N1  - Docket: {m['Docket Number']}")
        lines.append("ER  - ")
    path = str(Path.cwd() / "export.ris")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path
