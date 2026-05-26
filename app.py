import streamlit as st
import pandas as pd
import numpy as np
import json
import datetime

st.set_page_config(page_title="VPD Tool", layout="wide")

# --- HÀM TÍNH VPD ---
def calculate_vpd(temp, humi):
    svp = 0.61078 * np.exp((17.27 * temp) / (temp + 237.3))
    return round(svp * (1 - humi / 100.0), 2)

tab1, tab2 = st.tabs(["📊 PHÂN TÍCH REALTIME", "📂 PHÂN TÍCH LỊCH SỬ (JSON)"])

# =================================================================
# TAB 1: DỮ LIỆU MÔ PHỎNG RANDOM (ĐỘC LẬP)
# =================================================================
with tab1:
    st.header("📊 Phân tích VPD thời gian thực")
    if st.button("Chạy dữ liệu mô phỏng"):
        # Chỉ tạo dữ liệu ngẫu nhiên cho Tab 1
        t = np.random.uniform(15, 30)
        h = np.random.uniform(50, 90)
        vpd = calculate_vpd(t, h)
        
        st.metric("VPD Realtime", f"{vpd} kPa")
        st.write(f"Nhiệt độ mô phỏng: {t:.1f}°C | Độ ẩm: {h:.1f}%")
        st.line_chart(pd.DataFrame({'VPD': [vpd]}))

# =================================================================
# TAB 2: DỮ LIỆU TỪ FILE JSON (ĐỘC LẬP)
# =================================================================
with tab2:
    st.header("📂 Phân tích file JSON")
    uploaded_file = st.file_uploader("Tải file JSON:", type=["json"])
    
    if uploaded_file is not None:
        raw_data = json.load(uploaded_file)
        
        # Chỉ trích xuất đúng 2 key: tempkk và humikk từ file
        df = pd.DataFrame(raw_data)
        if {'tempkk', 'humikk'}.issubset(df.columns):
            df_filtered = df[['tempkk', 'humikk']]
            
            # Tính VPD dựa trên dữ liệu file
            df_filtered['VPD'] = df_filtered.apply(lambda x: calculate_vpd(x['tempkk'], x['humikk']), axis=1)
            
            st.write("Dữ liệu trích xuất từ file (Độc lập với Tab 1):")
            st.dataframe(df_filtered)
            
            # Biểu đồ 1: VPD
            st.subheader("Biểu đồ VPD từ file")
            st.line_chart(df_filtered['VPD'])
            
            # Biểu đồ 2: Temp & Humi
            st.subheader("Biểu đồ Temp & Humi từ file")
            st.line_chart(df_filtered[['tempkk', 'humikk']])
        else:
            st.error("File không chứa key 'tempkk' hoặc 'humikk'.")
