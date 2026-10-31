import sys, datetime as dt
from pathlib import Path; SKILL_DIR = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(SKILL_DIR / "scripts"))
import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from officekit import *

T = get_theme("hayah")
OUT = str(Path.cwd()) + "/"

# ── data (stand-in for a query result) ──
rng = np.random.default_rng(7)
days = pd.date_range("2026-10-01", periods=30, freq="D", tz="Asia/Manila")
bldgs = ["Admin", "Library", "Gym", "Science"]
df = pd.DataFrame({"Date": np.repeat(days, 4), "Building": bldgs * 30,
                   "kWh": rng.normal(850, 120, 120).round(1)})
df["Date"] = df["Date"].dt.tz_localize(None)            # Excel rejects tz-aware
summ = df.groupby("Building", as_index=False)["kWh"].sum()
summ["Share"] = summ["kWh"] / summ["kWh"].sum()

# ── chart PNG for the docx ──
fig, ax = plt.subplots(figsize=(7, 3), dpi=200)
for i, (b, g) in enumerate(df.groupby("Building")):
    ax.plot(g["Date"], g["kWh"], color="#" + T["series"][i], lw=1.6, label=b)
import matplotlib.dates as md; ax.xaxis.set_major_formatter(md.ConciseDateFormatter(md.AutoDateLocator())); ax.spines[["top", "right"]].set_visible(False); ax.legend(ncol=4, frameon=False, fontsize=8)
ax.set_ylabel("kWh / day"); fig.tight_layout(); fig.savefig(OUT + "trend.png")

# ── DOCX ──
doc = new_document(T, paper="A4")
set_core_props(doc, "October Energy Report", subject="Campus power monitoring")
add_header_footer(doc, "Hayah-AI · Energy Report", "October 2026", footer_left="Confidential")
add_title(doc, "October 2026 Energy Report", "Campus power monitoring — monthly summary",
          f"Prepared {dt.date(2026,10,31):%d %B %Y}")
add_toc(doc)
doc.add_heading("1. Executive summary", 1)
top = summ.loc[summ.kWh.idxmax(), "Building"]
add_rich(doc, ["Total consumption was ", (f"{summ.kWh.sum():,.0f} kWh", {"bold": True}),
               ", with ", (top, {"bold": True, "color": T["accent"]}), " the largest single load."])
add_callout(doc, "Weekend base load is 38% of weekday average — HVAC schedules are the first lever.",
            label="Finding")
add_bullets(doc, ["Admin within budget", ["Library ", ("+6%", {"color": T["accent"], "bold": True}), " vs September"]])  # illustrative; real reports compute these
doc.add_heading("2. Consumption by building", 1)
rows = [[r.Building, f"{r.kWh:,.1f}", f"{r.Share:.1%}"] for r in summ.itertuples()]
rows.append(["Total", f"{summ.kWh.sum():,.1f}", "100.0%"])
add_table(doc, ["Building", "kWh", "Share"], rows, col_widths_in=[3.2, 1.6, 1.4],
          align=["l", "r", "r"], total_row=True, caption="Table 1 — October consumption")
add_image(doc, OUT + "trend.png", caption="Figure 1 — Daily kWh by building")
doc.add_heading("3. Actions", 1)
add_numbered_list(doc, ["Re-baseline HVAC schedule", "Install sub-meter on Gym chillers"])
doc.add_heading("4. Next month", 1)
add_numbered_list(doc, ["Review results", "Report to facilities"])   # restarts at 1
p = doc.add_paragraph("Dashboard: "); add_hyperlink(p, "hayah-ai.com", "https://hayah-ai.com")
doc.save(OUT + "report.docx")

# ── XLSX ──
wb = new_workbook(T, "Summary")
ws = wb["Summary"]
r = write_title(ws, "October 2026 Energy Summary", "Source: meter export, 1–30 Oct 2026")
ws.cell(row=r, column=1, value="Tariff (₱/kWh)"); ws.cell(row=r, column=2, value=11.25)
s = xl_styles(T); ws.cell(row=r, column=2).font = s["input"]; ws.cell(row=r, column=2).fill = s["input_fill"]
ws.cell(row=r, column=2).number_format = FMT["php"]
tariff = f"$B${r}"
hdr = ["Building", "kWh", "Share", "Cost (₱)"]
start = r + 2
n = len(summ)
rows = [[b, f"=SUMIFS(Data!$C:$C,Data!$B:$B,A{start+1+i})", f"=B{start+1+i}/SUM($B${start+1}:$B${start+n})",
         f"=B{start+1+i}*{tariff}"] for i, b in enumerate(summ.Building)]
info = write_table(ws, hdr, rows, start_row=start, formats={"kWh": "dec2", "Share": "pct", "Cost (₱)": "php"},
                   totals={"kWh": "SUM", "Share": "SUM", "Cost (₱)": "SUM"}, widths={"Building": 18})
add_chart(ws, "col", (2, start, 2, info["last"]), (1, start + 1, 1, info["last"]), "F3",
          title="kWh by building", y_title="kWh")
wsd = wb.create_sheet("Data")
d = df_to_sheet(wsd, df, formats={"Date": "date", "kWh": "dec2"}, table_name="MeterData")
add_notes_sheet(wb, [("Tariff", "₱11.25/kWh — blended rate supplied by client (input cell, blue)"),
                     ("Data", "Daily kWh per building from meter export; synthetic for this test")],
                generated="2026-10-31")
set_print(ws, repeat_header_row=start)
set_core_props(wb, "October Energy Summary")
wb.save(OUT + "summary.xlsx")
print("built")
