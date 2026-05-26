import streamlit as st
import pandas as pd
import numpy as np
import datetime
import time

st.set_page_config(page_title="VPD Monitoring System", layout="wide")
st.title("🌱 HỆ THỐNG GIÁM SÁT VÀ XỬ LÝ VPD THÔNG MINH")

# --- HÀM TÍNH VPD ---
def calculate_vpd(temp, humi):
    svp = 0.61078 * np.exp((17.27 * temp) / (temp + 237.3))
    avp = svp * (humi / 100.0)
    return round(svp - avp, 2)

# --- TAB 1: GIAO DIỆN NHƯ ẢNH MÔ PHỎNG ---
tab1, tab2 = st.tabs(["📊 PHÂN TÍCH REALTIME", "📂 PHÂN TÍCH LỊCH SỬ (JSON)"])

with tab1:
    col_left, col_right = st.columns([1, 3])
    
    with col_left:
        st.subheader("⚙️ Cấu hình ngưỡng VPD")
        cay_trong = st.selectbox("Giống cây:", ["Dâu tây Đà Lạt", "Cà chua", "Ớt chuông"])
        # Cấu hình slider tương tự ảnh
        sang = st.slider("Sáng (05h-10h):", 0.0, 2.0, (0.5, 0.9))
        trua = st.slider("Trưa (10h-15h):", 0.0, 2.0, (0.7, 1.2))
        chieu = st.slider("Chiều (15h-19h):", 0.0, 2.0, (0.6, 1.0))
        toi = st.slider("Tối (19h-23h):", 0.0, 2.0, (0.4, 0.8))
        khuya = st.slider("Khuya (23h-05h):", 0.0, 2.0, (0.3, 0.7))
        
        btn_start = st.button("▶ Khởi chạy trạm", use_container_width=True)
        st.button("⏹ Tạm dừng trạm", use_container_width=True)
        st.button("🔄 Reset dữ liệu", use_container_width=True)

    with col_right:
        if btn_start:
            # Mô phỏng dữ liệu realtime
            t = round(np.random.uniform(14, 30), 1)
            h = round(np.random.uniform(45, 95), 1)
            vpd = calculate_vpd(t, h)
            
            # Khung hiển thị thông số realtime
            st.info(f"🕒 Thời gian: {datetime.datetime.now().strftime('%H:%M:%S')}")
            c1, c2, c3 = st.columns(3)
            c1.metric("VPD thực tế", f"{vpd} kPa")
            c2.metric("Nhiệt độ", f"{t}°C")
            c3.metric("Độ ẩm", f"{h}%")
            
            # Biểu đồ mô phỏng
            data = pd.DataFrame({'VPD': [vpd], 'Temp': [t], 'Humi': [h]})
            st.line_chart(data)
            
            # Khối cảnh báo kỹ thuật như yêu cầu
            if vpd < 0.5:
                st.error("⚠️ SẮP QUÁ ẨM: Bật toàn bộ quạt hút cường độ cao!")
            elif vpd > 1.2:
                st.warning("⚠️ SẮP QUÁ KHÔ: Kích hoạt hệ thống phun sương!")
            else:
                st.success("✅ Chỉ số VPD đang trong ngưỡng an toàn.")

with tab2:
    st.header("📂 Phân tích file JSON")
    uploaded_file = st.file_uploader("Tải file dữ liệu:", type=["json"])
    if uploaded_file:
        import json
        data = json.load(uploaded_file)
        # Chỉ trích xuất tempkk và humikk
        df = pd.DataFrame(data)[['tempkk', 'humikk']]
        st.write("Dữ liệu đã lọc:", df.head())
        st.line_chart(df)
