
import json, os, datetime, re, pathlib
from typing import Dict, Any, List, Optional
from xml.etree.ElementTree import Element, SubElement, tostring

def _get_in(data: dict, path: str) -> Optional[str]:
    # simple dot/bracket path extractor; supports [] at leaf
    try:
        parts = re.split(r"\.(?![^\[]*\])", path)
        cur = data
        for p in parts:
            if p.endswith("[]"):
                p = p[:-2]
                arr = cur.get(p, [])
                return "; ".join(str(x) for x in arr if x is not None)
            elif '[' in p and ']' in p:
                # not fully general; skip complex cases in v1
                key = p.split('[')[0]
                cur = cur.get(key, {})
            else:
                cur = cur.get(p)
            if cur is None:
                return None
        return str(cur) if cur is not None else None
    except Exception:
        return None

def to_ris(work: dict, mapping_path: str, attach_mode: str = "url", attachments: Optional[List[str]] = None) -> str:
    with open(mapping_path, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    xform = mapping['transform']
    lines = ["TY  - PAT"]  # Patent reference
    # Core fields
    for ris_tag, field_path in [
        ("TI", xform.get("Title")),
        ("AN", xform.get("Application Number")),
        ("PN", xform.get("Patent Number")),
        ("AU", xform.get("Inventors")),
    ]:
        if not field_path:
            continue
        if isinstance(field_path, list):
            values = []
            for p in field_path:
                val = _get_in(work, p) if isinstance(p, str) else None
                if val:
                    values.append(val)
            if not values:
                continue
            if ris_tag == "AU":
                for v in "; ".join(values).split("; "):
                    lines.append(f"{ris_tag}  - {v}")
            else:
                lines.append(f"{ris_tag}  - {'; '.join(values)}")
        else:
            val = _get_in(work, field_path)
            if val:
                if ris_tag == "AU" and "; " in val:
                    for v in val.split("; "):
                        lines.append(f"{ris_tag}  - {v}")
                else:
                    lines.append(f"{ris_tag}  - {val}")
    # Dates
    for ris_tag, fld in [("FD", xform.get("Filing Date")), ("PY", xform.get("Issue Date"))]:
        val = _get_in(work, fld) if fld else None
        if val:
            lines.append(f"{ris_tag}  - {val}")
    # Examiner, Art Unit, etc. as notes
    notes = []
    for label in ["Examiner", "Art Unit", "Docket Number", "CPC", "USPC", "Primary Class", "Subclass", "Priority Data", "Continuity - Parent", "Continuity - Child"]:
        fld = xform.get(label)
        if not fld:
            continue
        if isinstance(fld, list):
            vals = [ _get_in(work, p) for p in fld ]
            vals = [ v for v in vals if v ]
            if vals:
                notes.append(f"{label}: {'; '.join(vals)}")
        else:
            val = _get_in(work, fld)
            if val:
                notes.append(f"{label}: {val}")
    # Attorneys & correspondence extras (v2)
    att = work.get("recordAttorney") or {}
    if att:
        # flatten some common fields
        regnums = []
        for bag_name in ("attorneyBag", "powerOfAttorneyBag"):
            for ent in att.get(bag_name, []) or []:
                rn = ent.get("registrationNumber")
                nm = " ".join(filter(None, [ent.get("firstName"), ent.get("lastName")]))
                if rn or nm:
                    regnums.append(f"{nm} ({rn})" if rn else nm)
        if regnums:
            notes.append("Attorneys: " + "; ".join(regnums))
    corr = work.get("correspondenceAddressBag") or []
    if corr:
        lab = []
        for c in corr:
            line = ", ".join(filter(None, [c.get("nameLineOneText"), c.get("addressLineOneText"), c.get("cityName"), c.get("geographicRegionCode"), c.get("postalCode"), c.get("countryName")]))
            if line:
                lab.append(line)
        if lab:
            notes.append("Correspondence: " + "; ".join(lab))

    if notes:
        for n in notes:
            lines.append(f"N1  - {n}")

    # URL
    url = _get_in(work, xform.get("URL")) if xform.get("URL") else None
    if url:
        lines.append(f"UR  - {url}")

    # Attachments
    atts = attachments or []
    if attach_mode == "url" and not atts:
        # pull from mapping if present
        for f in xform.get("File Attachments", []) or []:
            v = _get_in(work, f)
            if v:
                atts.extend([u for u in v.split("; ") if u])
    for a in atts:
        lines.append(f"L1  - {a}")

    lines.append("ER  - ")
    return "\n".join(lines)
