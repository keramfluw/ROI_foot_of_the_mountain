
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF
from openpyxl import Workbook

st.set_page_config(page_title="PV Halter Wirtschaftlichkeit", layout="wide")
st.title("📊 Wirtschaftlichkeitsanalyse für PV-Modulhalter")

col1, col2 = st.columns(2)
with col1:
    st.header("Betonvariante")
    vk_beton = st.number_input("Verkaufspreis Beton (€)", value=30.0)
    fixkosten_beton = st.number_input("Fixkosten Beton (€)", value=23000.0)
    variable_beton = st.number_input("Variable Kosten pro Stück Beton (€)", value=23.0)

with col2:
    st.header("Recyclingvariante")
    vk_recyc = st.number_input("Verkaufspreis Recycling (€)", value=40.0)
    fixkosten_recyc = st.number_input("Fixkosten Recycling (€)", value=26000.0)
    variable_recyc = st.number_input("Variable Kosten pro Stück Recycling (€)", value=26.5)

max_stück = st.slider("Maximale Stückzahl", min_value=100, max_value=5000, value=2000, step=100)
stückzahlen = np.arange(1, max_stück + 1)

erlös_beton = stückzahlen * vk_beton
erlös_recyc = stückzahlen * vk_recyc

aufwand_beton = fixkosten_beton + stückzahlen * variable_beton
aufwand_recyc = fixkosten_recyc + stückzahlen * variable_recyc

gewinn_beton = erlös_beton - aufwand_beton
gewinn_recyc = erlös_recyc - aufwand_recyc

roi_beton = (gewinn_beton) / np.where(aufwand_beton != 0, aufwand_beton, np.nan)
roi_recyc = (gewinn_recyc) / np.where(aufwand_recyc != 0, aufwand_recyc, np.nan)

st.subheader("Break-Even & Gewinnvergleich")
fig1, ax1 = plt.subplots()
ax1.plot(stückzahlen, gewinn_beton, label="Gewinn Beton")
ax1.plot(stückzahlen, gewinn_recyc, label="Gewinn Recycling")
ax1.axhline(0, color="black", linestyle="--", linewidth=0.8)
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
ax2.axhline(0, color="black", linestyle="--", linewidth=0.8)
ax2.set_xlabel("Stückzahl")
ax2.set_ylabel("ROI")
ax2.set_title("ROI Verlauf")
ax2.legend()
ax2.grid(True)
st.pyplot(fig2)

df = pd.DataFrame({
    "Stückzahl": stückzahlen,
    "Gewinn Beton (€)": gewinn_beton,
    "Gewinn Recycling (€)": gewinn_recyc,
    "ROI Beton": roi_beton,
    "ROI Recycling": roi_recyc
})

if st.checkbox("Tabelle anzeigen"):
    st.dataframe(df)

# Export Excel
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

# Export PDF
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
    for index, row in df.iterrows():
        for item in row:
            pdf.cell(col_width, 8, f"{item:.2f}", border=1)
        pdf.ln()
    bio = BytesIO()
    pdf.output(bio)
    bio.seek(0)
    return bio

st.subheader("📤 Export Optionen")
col3, col4 = st.columns(2)
with col3:
    excel_bytes = to_excel(df)
    st.download_button("📥 Excel herunterladen", data=excel_bytes, file_name="wirtschaftlichkeit_pvhalter.xlsx")

with col4:
    pdf_bytes = to_pdf(df)
    st.download_button("📥 PDF herunterladen", data=pdf_bytes, file_name="wirtschaftlichkeit_pvhalter.pdf")
