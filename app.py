import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import time

# --- Cấu hình trang ---
st.set_page_config(page_title="VPD IoT Dashboard", layout="wide", page_icon="🌱")

st.title("🌱 Hệ Thống Giám Sát & Cảnh Báo Chỉ Số VPD (IoT)")
st.markdown("---")

# --- BANNER THÔNG TIN TRUYỀN THÔNG ---
st.sidebar.header("📡 Cấu Hình Truyền Thông (MQTT)")
mqtt_broker = st.sidebar.text_input("MQTT Broker", "broker.hivemq.com")
mqtt_topic_app = st.sidebar.text_input("App -> Topic (Update)", "dv/app/update")
mqtt_topic_esp = st.sidebar.text_input("ESP -> Topic (Data)", "dv/esp/data")

if st.sidebar.button("Kết nối Hệ thống"):
    st.sidebar.success(f"Đã kết nối Broker: {mqtt_broker}")

# --- MODULE I: QUẢN LÝ CÂY TRỒNG & VÙNG MIỀN ---
st.sidebar.header("📍 Cấu Hình Vùng & Cây Trồng")
region = st.sidebar.selectbox("Chọn Vùng Miền", ["Lâm Đồng", "Miền Trung", "Miền Tây", "Huế"])
plant_type = st.sidebar.selectbox("Chọn Loại Cây", ["Ớt chuông", "Cà chua", "Dâu tây", "Dưa lưới", "Dưa leo", "Hoa cúc", "Hoa Ly"])

# Nếu là ớt chuông, hiển thị phân loại theo bảng tiêu chuẩn (Loại A, B, C)
if plant_type == "Ớt chuông":
    st.sidebar.info("📋 Tiêu chuẩn phân loại Ớt chuông:\n- Loại A: 25\n- Loại B: 10\n- Loại C: 6")

# --- MODULE II: CẤU HÌNH NGƯỠNG VPD ---
st.sidebar.header("⚙️ Cấu Hình Ngưỡng VPD")
vpd_min = st.sidebar.slider("Cận dưới (Thấp)", 0.0, 1.0, 0.8, step=0.1)
vpd_max = st.sidebar.slider("Cận trên (Cao)", 1.0, 2.0, 1.2, step=0.1)

st.sidebar.caption(f"Khoảng tối ưu hiện tại: {vpd_min} - {vpd_max}")

# --- GIẢ LẬP DỮ LIỆU REALTIME & QUÁ KHỨ ---
# (Trong thực tế, bạn sẽ dùng thư viện paho-mqtt để subscribe dữ liệu từ ESP32)
@st.cache_data
def load_historical_data():
    # Tạo dữ liệu giả lập cho 3 mốc: Sáng, Trưa, Chiều tối
    times = pd.date_range(start="2026-05-26 06:00:00", end="2026-05-26 18:00:00", freq="15min")
    np.random.seed(42)
    # Giả lập VPD biến thiên (thấp buổi sáng, cao buổi trưa)
    vpd_values = 0.5 + np.sin(np.linspace(0, 3.14, len(times))) * 0.9 + np.random.normal(0, 0.05, len(times))
    temp_values = 22 + np.sin(np.linspace(0, 3.14, len(times))) * 8
    hum_values = 85 - np.sin(np.linspace(0, 3.14, len(times))) * 30
    
    df = pd.DataFrame({"Thời gian": times, "VPD": vpd_values, "Nhiệt độ": temp_values, "Độ ẩm": hum_values})
    return df

df_data = load_historical_data()
current_vpd = round(df_data["VPD"].iloc[-1], 2)

# --- MODULE III: HIỂN THỊ TRẠNG THÁI REALTIME ---
col1, col2, col3 = st.columns(3)

# Xác định trạng thái dựa trên cấu hình ngưỡng
if current_vpd < 0.5:
    status = "🔴 RẤT THẤP"
    color_metric = "inverse"
elif current_vpd < vpd_min:
    status = "🟡 THẤP"
    color_metric = "normal"
elif current_vpd <= vpd_max:
    status = "🟢 TỐT (TỐI ƯU)"
    color_metric = "normal"
elif current_vpd <= 1.5:
    status = "🟡 CAO"
    color_metric = "normal"
else:
    status = "🔴 RẤT CAO"
    color_metric = "inverse"

with col1:
    st.metric(label=f"Chỉ số VPD Hiện Tại ({plant_type} - {region})", value=f"{current_vpd} kPa", delta=status)
with col2:
    st.metric(label="Nhiệt độ Hiện Tại", value=f"{round(df_data['Nhiệt độ'].iloc[-1], 1)} °C")
with col3:
    st.metric(label="Độ ẩm Hiện Tại", value=f"{round(df_data['Độ ẩm'].iloc[-1], 1)} %")

# --- MODULE IV: KỊCH BẢN XỬ LÝ SỰ CỐ & THIẾT BỊ CHẤP HÀNH ---
st.subheader("🚨 Trạng Thái Điều Khiển Thiết Bị Khí Cụ (Hệ thống IoT mở rộng)")
c_fan, c_lamp, c_net = st.columns(3)

# Logic tự động điều khiển thiết bị giả lập dựa trên trạng thái
if current_vpd < vpd_min:
    c_fan.error("Quạt: ĐANG TẮT (Tránh giảm ẩm)")
    c_lamp.success("Đèn sưởi: ĐANG BẬT")
    c_net.error("Lưới cắt nắng: ĐANG THU LẠI")
    st.warning("⚠️ Hệ thống đang tự động xử lý sự cố: **Thiếu VPD (VPD Thấp)** -> Thực hiện kích hoạt Vòng xử lý 1 & 2.")
elif current_vpd > vpd_max:
    c_fan.success("Quạt đối lưu: ĐANG BẬT")
    c_lamp.error("Đèn sưởi: ĐANG TẮT")
    c_net.success("Lưới cắt nắng: ĐANG KÉO (Giảm nhiệt)")
    st.error("🚨 Cảnh báo mức độ CAO: **Vượt ngưỡng VPD** -> Kích hoạt kịch bản xử lý khẩn cấp 3 & 4.")
else:
    c_fan.info("Quạt: TỰ ĐỘNG")
    c_lamp.info("Đèn: TỰ ĐỘNG")
    c_net.info("Lưới: TỰ ĐỘNG")
    st.success("✅ Chỉ số ổn định. Hệ thống chấp hành hoạt động ở chế độ duy trì.")

# --- MODULE V: ĐỒ THỊ BIỂU ĐỒ (FULL CHART) ---
st.subheader("📊 Biểu Đồ Phân Tích Dữ Liệu Thời Gian Thực")

# Vẽ biểu đồ VPD bằng Plotly (đẹp và tương tác tốt hơn biểu đồ mặc định)
fig = go.Figure()
fig.add_trace(go.Scatter(x=df_data["Thời gian"], y=df_data["VPD"], mode='lines+markers', name='Chỉ số VPD', line=dict(color='blue', width=2)))

# Thêm các đường giới hạn ngưỡng (Min/Max định cấu hình)
fig.add_hline(y=vpd_min, line_dash="dash", line_color="orange", annotation_text="Cận dưới tối ưu")
fig.add_hline(y=vpd_max, line_dash="dash", line_color="red", annotation_text="Cận trên tối ưu")

fig.update_layout(title="Biểu đồ biến thiên VPD trong ngày", xaxis_title="Thời gian", yaxis_title="VPD (kPa)", template="streamlit")
st.plotly_chart(fig, use_container_width=True)

# Hiển thị bảng dữ liệu thô khi cần phân tích
if st.checkbox("Hiển thị bảng dữ liệu chi tiết (3 Chart đầu ngày/cuối ngày)"):
    st.dataframe(df_data)
