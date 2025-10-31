# pdf_exporter.py — Minimal PDF report without external libraries (E5)
    # Creates a single-page PDF with Monthly Summary (Ozet_Aylik) and Branch Breakdown (Sube_Kirilim).
    from __future__ import annotations
    import sqlite3, pathlib
    from typing import List, Tuple

    def _connect(db_path: str) -> sqlite3.Connection:
        con = sqlite3.connect(db_path, timeout=15, isolation_level=None)
        con.execute("PRAGMA foreign_keys=ON;")
        con.execute("PRAGMA journal_mode=WAL;")
        con.execute("PRAGMA synchronous=NORMAL;")
        return con

    def _monthly(con: sqlite3.Connection, ym: str):
        cur = con.execute("SELECT COALESCE(SUM(amount),0) FROM incomes WHERE substr(date,1,7)=?", (ym,))
        inc = float(cur.fetchone()[0] or 0.0)
        cur = con.execute("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE substr(date,1,7)=?", (ym,))
        exp = float(cur.fetchone()[0] or 0.0)
        cur = con.execute("SELECT COALESCE(SUM(amount),0) FROM advances WHERE substr(date,1,7)=?", (ym,))
        adv = float(cur.fetchone()[0] or 0.0)
        net = inc - exp - adv
        return round(inc,2), round(exp,2), round(adv,2), round(net,2)

    def _branch(con: sqlite3.Connection, ym: str) -> List[Tuple[str, float, float]]:
        cur = con.execute(
            """WITH branches AS (
                   SELECT DISTINCT COALESCE(branch,'') AS b FROM incomes WHERE substr(date,1,7)=?
                   UNION
                   SELECT DISTINCT COALESCE(branch,'') AS b FROM expenses WHERE substr(date,1,7)=?
               )
               SELECT b as branch,
                      ROUND(COALESCE((SELECT SUM(amount) FROM incomes  WHERE substr(date,1,7)=? AND COALESCE(branch,'')=b),0),2) AS inc_total,
                      ROUND(COALESCE((SELECT SUM(amount) FROM expenses WHERE substr(date,1,7)=? AND COALESCE(branch,'')=b),0),2) AS exp_total
               FROM branches
               ORDER BY branch COLLATE NOCASE ASC""",
            (ym, ym, ym, ym)
        )
        return [(r[0], float(r[1] or 0.0), float(r[2] or 0.0)) for r in cur.fetchall()]

    def _pdf_escape(text: str) -> str:
        return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    def export_pdf(db_path: str, out_path: str, ym: str = "2025-10") -> str:
        out = pathlib.Path(out_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        con = _connect(db_path)
        try:
            inc, exp, adv, net = _monthly(con, ym)
            branches = _branch(con, ym)
        finally:
            con.close()

        # Build simple text content
        lines = []
        lines.append(f"GUNSONU RAPORU — {ym}")
        lines.append("")
        lines.append("Ozet_Aylik:")
        lines.append(f"  Gelir   : {inc}")
        lines.append(f"  Gider   : {exp}")
        lines.append(f"  Avans   : {adv}")
        lines.append(f"  Net     : {net}")
        lines.append("")
        lines.append("Sube_Kirilim (Gelir | Gider):")
        for b, i, e in branches:
            name = b if b else "(bos)"
            lines.append(f"  {name}: {i} | {e}")

        # Minimal PDF (single page, Helvetica, 12pt)
        # Reference: simple PDF objects: catalog -> pages -> page -> content stream
        text_lines = lines

        # Create text stream commands
        y = 800  # start from top of page
        leading = 16
        content_cmds = ["BT", "/F1 12 Tf", "1 0 0 1 50 %d Tm" % y]
        for ln in text_lines:
            safe = _pdf_escape(ln)
            content_cmds.append(f"({safe}) Tj")
            y -= leading
            content_cmds.append("0 -16 Td")
        content_cmds.append("ET")
        stream_data = ("\n".join(content_cmds)).encode("utf-8")
        stream_len = len(stream_data)

        # Assemble PDF objects
        objects = []
        xref = []
        def add_object(obj_str: bytes) -> None:
            offset = sum(len(o) for o in objects) + len(header)
            xref.append(offset)
            objects.append(obj_str)

        header = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"

        # 1) Font object
        font_obj_num = 1
        font_obj = f"""{font_obj_num} 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
""".encode("utf-8")
        add_object(font_obj)

        # 2) Content stream
        contents_obj_num = 2
        contents_obj = (f"""{contents_obj_num} 0 obj
<< /Length {stream_len} >>
stream
""".encode("utf-8") + stream_data + b"\nendstream\nendobj\n" )
        add_object(contents_obj)

        # 3) Page object
        page_obj_num = 3
        page_obj = f"""{page_obj_num} 0 obj
<< /Type /Page /Parent 4 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 {font_obj_num} 0 R >> >> /Contents {contents_obj_num} 0 R >>
endobj
""".encode("utf-8")
        add_object(page_obj)

        # 4) Pages object
        pages_obj_num = 4
        pages_obj = f"""{pages_obj_num} 0 obj
<< /Type /Pages /Kids [ {page_obj_num} 0 R ] /Count 1 >>
endobj
""".encode("utf-8")
        add_object(pages_obj)

        # 5) Catalog
        catalog_obj_num = 5
        catalog_obj = f"""{catalog_obj_num} 0 obj
<< /Type /Catalog /Pages {pages_obj_num} 0 R >>
endobj
""".encode("utf-8")
        add_object(catalog_obj)

        # Build xref
        xref_offset = sum(len(o) for o in objects) + len(header)
        xref_table = ["xref", f"0 {len(objects)+1}", "0000000000 65535 f "]
        for off in xref:
            xref_table.append(f"{off:010d} 00000 n ")
        xref_bytes = ("\n".join(xref_table) + "\n").encode("utf-8")

        trailer = f"""trailer
<< /Size {len(objects)+1} /Root {catalog_obj_num} 0 R >>
startxref
{xref_offset}
%%EOF
""".encode("utf-8")

        with open(out, "wb") as f:
            f.write(header)
            for o in objects:
                f.write(o)
            f.write(xref_bytes)
            f.write(trailer)

        return str(out)