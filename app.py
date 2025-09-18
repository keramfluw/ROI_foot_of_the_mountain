
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

st.set_page_config(page_title="PV Halter Wirtschaftlichkeit", layout="wide")
st.title("📊 Wirtschaftlichkeitsanalyse – PV-Modulhalter")

st.markdown("### 1. Detailkosten & Verkaufspreis-Konfiguration")

# Eingabevariablen: Detailpositionen
def kosten_eingabe(titel, prefix):
    with st.expander(f"{titel}"):
        col1, col2 = st.columns(2)
        with col1:
            material = st.number_input(f"{prefix} Materialkosten (€)", value=10.0)
            lohn = st.number_input(f"{prefix} Lohnkosten (€)", value=5.0)
            energie = st.number_input(f"{prefix} Energiekosten (€)", value=2.0)
        with col2:
            lager = st.number_input(f"{prefix} Lagerhaltungskosten (€)", value=2.0)
            transport = st.number_input(f"{prefix} Transportkosten (€)", value=3.0)
            hilfs = st.number_input(f"{prefix} Hilfsstoffkosten (€)", value=1.0)
    return material + lohn + energie + lager + transport + hilfs

# Variablen Kosten
st.subheader("Variable Kosten je Stück")
var_beton = kosten_eingabe("Betonfuß – Variable Kosten", "Beton")
var_recyc = kosten_eingabe("Recyclingfuß – Variable Kosten", "Recycling")

# Verkaufspreis-Kalkulation
def vk_kalkulation(prefix, var_kosten):
    with st.expander(f"{prefix} Verkaufspreis-Kalkulation"):
        aufschlag_prozent = st.number_input(f"{prefix} Aufschlag (%)", value=25.0)
        vertrieb = st.number_input(f"{prefix} Vertriebskosten (€)", value=2.0)
        skonto = st.number_input(f"{prefix} Skonto (€)", value=1.0)
        marketing = st.number_input(f"{prefix} Marketingkosten (€)", value=2.0)
        vk = var_kosten * (1 + aufschlag_prozent / 100) + vertrieb + skonto + marketing
    return vk

st.subheader("Verkaufspreise je Stück")
vk_beton = vk_kalkulation("Beton", var_beton)
vk_recyc = vk_kalkulation("Recycling", var_recyc)

# Fixkosten
st.markdown("### 2. Fixkosten")
col1, col2 = st.columns(2)
with col1:
    fix_beton = st.number_input("Fixkosten Beton (€)", value=23000.0)
with col2:
    fix_recyc = st.number_input("Fixkosten Recycling (€)", value=26000.0)

# Stückzahlen
max_stück = st.slider("Maximale Stückzahl", 100, 5000, 2000, step=100)
stückzahlen = np.arange(1, max_stück + 1)

# Wirtschaftlichkeitsberechnung
erlös_beton = stückzahlen * vk_beton
erlös_recyc = stückzahlen * vk_recyc
aufwand_beton = fix_beton + stückzahlen * var_beton
aufwand_recyc = fix_recyc + stückzahlen * var_recyc
gewinn_beton = erlös_beton - aufwand_beton
gewinn_recyc = erlös_recyc - aufwand_recyc
roi_beton = (gewinn_beton) / np.where(aufwand_beton != 0, aufwand_beton, np.nan)
roi_recyc = (gewinn_recyc) / np.where(aufwand_recyc != 0, aufwand_recyc, np.nan)

def find_zero_crossing_x(x, y):
    \"\"\"Linear interpolated x where curve y crosses 0. Returns None if no crossing.\"\"\"
    sign = np.sign(y)
    idx = np.where(np.diff(sign) != 0)[0]
    if len(idx) == 0:
        return None
    i = idx[0]
    x0, x1 = x[i], x[i+1]
    y0, y1 = y[i], y[i+1]
    if (y1 - y0) == 0:
        return float(x0)
    xz = x0 - y0 * (x1 - x0) / (y1 - y0)
    return float(xz)

def find_intersection_x(x, y1, y2):
    \"\"\"Linear interpolated x where y1-y2 crosses 0.\"\"\"
    diff = y1 - y2
    return find_zero_crossing_x(x, diff)

# Schnittpunkte berechnen
be_beton_x = find_zero_crossing_x(stückzahlen, gewinn_beton)
be_recyc_x = find_zero_crossing_x(stückzahlen, gewinn_recyc)
gain_intersect_x = find_intersection_x(stückzahlen, gewinn_beton, gewinn_recyc)

roi_beton_zero_x = find_zero_crossing_x(stückzahlen, roi_beton)
roi_recyc_zero_x = find_zero_crossing_x(stückzahlen, roi_recyc)

# Diagramme
st.markdown("### 3. Ergebnisse & Diagramme")
st.subheader("Break-Even & Gewinnvergleich")
fig1, ax1 = plt.subplots()
ax1.plot(stückzahlen, gewinn_beton, label="Gewinn Beton")
ax1.plot(stückzahlen, gewinn_recyc, label="Gewinn Recycling")
ax1.axhline(0, linestyle="--", linewidth=0.8)

# Schnittpunkte markieren & beschriften
def annotate_point(ax, x_val, y_func, label):
    if x_val is not None and x_val >= stückzahlen[0] and x_val <= stückzahlen[-1]:
        y_val = np.interp(x_val, stückzahlen, y_func)
        ax.scatter([x_val], [y_val])
        ax.annotate(f\"{label}\nStk≈{x_val:.0f}, Wert≈{y_val:.0f} €\",
                    xy=(x_val, y_val),
                    xytext=(10, 15),
                    textcoords=\"offset points\",
                    arrowprops=dict(arrowstyle=\"->\"))

annotate_point(ax1, be_beton_x, gewinn_beton, "Break-Even Beton")
annotate_point(ax1, be_recyc_x, gewinn_recyc, "Break-Even Recycling")
annotate_point(ax1, gain_intersect_x, gewinn_beton, "Schnitt Gewinnkurven")

ax1.set_xlabel("Stückzahl")
ax1.set_ylabel("Gewinn (€)")
ax1.set_title("Break-Even Kurve")
ax1.legend()
ax1.grid(True)
st.pyplot(fig1)

st.subheader("ROI Vergleich")
fig2, ax2 = plt.subplots()
ax2.plot(stückzahlen, roi_beton, label="ROI Beton")
ax2.plot(stückzahlen, roi_recyc, label="ROI Recycling")
ax2.axhline(0, linestyle="--", linewidth=0.8)

annotate_point(ax2, roi_beton_zero_x, roi_beton, "ROI=0 Beton")
annotate_point(ax2, roi_recyc_zero_x, roi_recyc, "ROI=0 Recycling")

ax2.set_xlabel("Stückzahl")
ax2.set_ylabel("ROI")
ax2.set_title("ROI Verlauf")
ax2.legend()
ax2.grid(True)
st.pyplot(fig2)

# Tabelle
df = pd.DataFrame({
    "Stückzahl": stückzahlen,
    "Gewinn Beton (€)": gewinn_beton,
    "Gewinn Recycling (€)": gewinn_recyc,
    "ROI Beton": roi_beton,
    "ROI Recycling": roi_recyc
})
if st.checkbox("📋 Tabelle anzeigen"):
    st.dataframe(df)

# Exportfunktionen
def to_excel(df):
    wb = Workbook()
    ws = wb.active
    ws.title = "Wirtschaftlichkeit"
    for r in dataframe_to_rows(df, index=False, header=True):
        ws.append(r)
    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)
    return bio

def to_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt="Wirtschaftlichkeitsanalyse PV Modulhalter", ln=1, align="C")
    pdf.set_font("Arial", size=8)
    col_names = list(df.columns)
    col_width = 200 / len(col_names)
    for col in col_names:
        pdf.cell(col_width, 8, col, border=1)
    pdf.ln()
    max_rows = min(len(df), 50)
    for index, row in df.head(max_rows).iterrows():
        for item in row:
            try:
                pdf.cell(col_width, 8, f"{float(item):.2f}", border=1)
            except:
                pdf.cell(col_width, 8, str(item), border=1)
        pdf.ln()
    bio = BytesIO()
    pdf.output(bio)
    bio.seek(0)
    return bio

st.markdown("### 4. 📤 Export")
col3, col4 = st.columns(2)
with col3:
    excel_bytes = to_excel(df)
    st.download_button("📥 Excel herunterladen", data=excel_bytes, file_name="wirtschaftlichkeit_pvhalter.xlsx")

with col4:
    pdf_bytes = to_pdf(df)
    st.download_button("📥 PDF herunterladen", data=pdf_bytes, file_name="wirtschaftlichkeit_pvhalter.pdf")
