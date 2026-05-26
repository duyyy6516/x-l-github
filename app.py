import streamlit as st
import pandas as pd
import numpy as np
import json
import datetime
import time

# Cấu hình trang Streamlit
st.set_page_config(page_title="VPD Monitoring Tool", layout="wide")
st.title("🌱 Công Cụ Giám Sát & Phân Tích Chỉ Số VPD")

# --- HÀM TOÁN HỌC TÍNH VPD ---
def calculate_vpd(temp, humi):
    """
    Tính toán chỉ số VPD (Vapor Pressure Deficit) từ Nhiệt độ (°C) và Độ ẩm (%)
    """
    # Áp suất hơi bão hòa (SVP) tính bằng kPa
    svp = 0.61078 * np.exp((17.27 * temp) / (temp + 237.3))
    # Áp suất hơi thực tế (AVP) tính bằng kPa
    avp = svp * (humi / 100.0)
    # Thâm hụt áp suất hơi nước (VPD)
    vpd = svp - avp
    return round(vpd, 2)

# --- KHỐI CẤU HÌNH BAN ĐẦU (SIDEBAR) ---
st.sidebar.header("⚙️ Cấu Hình Hệ Thống")

# 1. Chọn loại cây
cay_trong = st.sidebar.selectbox(
    "Chọn Loại Cây Trồng:",
    ["Cà chua", "Dâu tây", "Ớt chuông", "Hoa cúc", "Hoa ly", "Dưa lưới", "Ớt chỉ thiên"]
)

# 2. Cài đặt ngưỡng động tự chọn theo khung giờ
st.sidebar.subheader("⏰ Tự Chọn Ngưỡng VPD Mục Tiêu")

with st.sidebar.expander("Khung Sáng (7h - 11h)", expanded=True):
    sang_min, sang_max = st.slider("Ngưỡng Sáng:", 0.0, 2.0, (0.8, 1.2), 0.1, key="sang")
with st.sidebar.expander("Khung Trưa (11h - 14h)"):
    trua_min, trua_max = st.slider("Ngưỡng Trưa:", 0.0, 2.0, (1.0, 1.5), 0.1, key="trua")
with st.sidebar.expander("Khung Chiều (14h - 18h)"):
    chieu_min, chieu_max = st.slider("Ngưỡng Chiều:", 0.0, 2.0, (0.9, 1.3), 0.1, key="chieu")
with st.sidebar.expander("Khung Tối (18h - 22h)"):
    toi_min, toi_max = st.slider("Ngưỡng Tối:", 0.0, 2.0, (0.5, 0.9), 0.1, key="toi")
with st.sidebar.expander("Khung Khuya (22h - 6h)"):
    khuya_min, khuya_max = st.slider("Ngưỡng Khuya:", 0.0, 2.0, (0.4, 0.7), 0.1, key="khuya")

# Gom cụm cấu hình ngưỡng để đối chiếu dữ liệu
nguong_cau_hinh = {
    "Sáng": (sang_min, sang_max),
    "Trưa": (trua_min, trua_max),
    "Chiều": (chieu_min, chieu_max),
    "Tối": (toi_min, toi_max),
    "Khuya": (khuya_min, khuya_max)
}

def lay_khung_gio_va_nguong(gio):
    if 7 <= gio < 11: return "Sáng", nguong_cau_hinh["Sáng"]
    elif 11 <= gio < 14: return "Trưa", nguong_cau_hinh["Trưa"]
    elif 14 <= gio < 18: return "Chiều", nguong_cau_hinh["Chiều"]
    elif 18 <= gio < 22: return "Tối", nguong_cau_hinh["Tối"]
    else: return "Khuya", nguong_cau_hinh["Khuya"]


# --- CHIA 2 TAGS (TABS) GIAO DIỆN ---
tab1, tab2 = st.tabs(["📊 Phân Tích VPD Thời Gian Thực", "📂 Phân Tích Lịch Sử (File JSON)"])

# =====================================================================
# TAB 1: PHÂN TÍCH VPD THEO THỜI GIAN THỰC (REALTIME)
# =====================================================================
with tab1:
    st.header(f"📈 Mô phỏng dữ liệu Realtime cho cây: {cay_trong}")
    
    # Nút bấm kích hoạt luồng chạy realtime
    run_realtime = st.checkbox("Kích hoạt chạy luồng giả lập Realtime")
    
    # Vùng chứa đồ thị động
    placeholder_charts = st.empty()
    placeholder_actions = st.empty()
    
    # Khởi tạo hoặc lấy lại session state lưu trữ mảng dữ liệu realtime
    if 'realtime_data' not in st.session_state:
        st.session_state.realtime_data = pd.DataFrame(columns=["Time", "Nhiệt độ", "Độ ẩm", "VPD", "Cận Dưới", "Cận Trên"])

    if run_realtime:
        while run_realtime:
            now = datetime.datetime.now()
            current_time_str = now.strftime("%H:%M:%S")
            current_hour = now.hour
            
            # Khối xử lý mô phỏng hàm ngẫu nhiên sinh dữ liệu theo khung giờ thực tế
            ten_khung, (c_duoi, c_tren) = lay_khung_gio_va_nguong(current_hour)
            
            if ten_khung == "Sáng":
                temp = round(np.random.uniform(20.0, 26.0), 1)
                humi = round(np.random.uniform(65.0, 95.0), 1)
            elif ten_khung == "Trưa":
                temp = round(np.random.uniform(27.0, 32.0), 1)
                humi = round(np.random.uniform(45.0, 55.0), 1)
            elif ten_khung == "Chiều":
                temp = round(np.random.uniform(22.0, 25.0), 1)
                humi = round(np.random.uniform(65.0, 75.0), 1)
            elif ten_khung == "Tối":
                temp = round(np.random.uniform(17.0, 19.0), 1)
                humi = round(np.random.uniform(80.0, 90.0), 1)
            else: # Khuya
                temp = round(np.random.uniform(14.0, 16.0), 1)
                humi = round(np.random.uniform(90.0, 98.0), 1)
                
            vpd = calculate_vpd(temp, humi)
            
            # Cập nhật mảng dữ liệu vào DataFrame (giới hạn 30 bản ghi gần nhất để tránh lag biểu đồ)
            new_row = {
                "Time": current_time_str, "Nhiệt độ": temp, "Độ ẩm": humi, 
                "VPD": vpd, "Cận Dưới": c_duoi, "Cận Trên": c_tren
            }
            st.session_state.realtime_data = pd.concat([st.session_state.realtime_data, pd.DataFrame([new_row])], ignore_index=True)
            if len(st.session_state.realtime_data) > 30:
                st.session_state.realtime_data = st.session_state.realtime_data.iloc[1:]
                
            # Đổ dữ liệu ra 2 biểu đồ
            df_chart = st.session_state.realtime_data.set_index("Time")
            with placeholder_charts.container():
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Biểu đồ 1: Chỉ số VPD Realtime")
                    st.line_chart(df_chart[["VPD", "Cận Dưới", "Cận Trên"]], color=["#FF4B4B", "#0000FF", "#0000FF"])
                with col2:
                    st.subheader("Biểu đồ 2: Môi trường (Nhiệt độ & Độ ẩm)")
                    st.line_chart(df_chart[["Nhiệt độ", "Độ ẩm"]])
                    
            # Xử lý kịch bản kích hoạt thiết bị tự động (Logic hình 1)
            with placeholder_actions.container():
                st.subheader("🚨 Trạng Thái Điều Khiển Thiết Bị IoT Hệ Thống")
                metrics_cols = st.columns(4)
                metrics_cols[0].metric("Khí Độc", "An Toàn")
                metrics_cols[1].metric("Điện Năng Tiêu Thụ", "1.2 kWh")
                
                if vpd < c_duoi:
                    st.error(f"❌ CẢNH BÁO: Hiện tại đang THIẾU VPD ({vpd} < {c_duoi}) vào khung giờ {ten_khung}!")
                    st.warning("⚙️ [KỊCH BẢN XỬ LÝ NÓNG 1]: Tự động bật Hệ thống Quạt đối lưu / Quạt thông gió để hạ độ ẩm.")
                    metrics_cols[2].metric("Trạng thái Quạt", "ON (100% Công suất)", delta="Xử lý ẩm")
                    metrics_cols[3].metric("Trạng thái Lưới/Phun sương", "OFF")
                elif vpd > c_tren:
                    st.error(f"❌ CẢNH BÁO: Hiện tại đang THỪA VPD ({vpd} > {c_tren}) vào khung giờ {ten_khung}!")
                    st.warning("⚙️ [KỊCH BẢN HẠ NHIỆT MỞ RỘNG 4]: Tự động kích hoạt Bơm Phun Sương mịn + Kéo rèm Lưới che nắng.")
                    metrics_cols[2].metric("Trạng thái Quạt", "OFF")
                    metrics_cols[3].metric("Trạng thái Lưới/Phun sương", "ON (Đang hoạt động)", delta="-3°C Hạ nhiệt")
                else:
                    st.success(f"✅ Chỉ số VPD đạt mức tối ưu lý tưởng ({vpd}) cho cây {cay_trong} vào khung giờ {ten_khung}.")
                    metrics_cols[2].metric("Trạng thái Quạt", "OFF")
                    metrics_cols[3].metric("Trạng thái Lưới/Phun sương", "OFF")
                    
            time.sleep(2) # Cập nhật sau mỗi 2 giây
    else:
        st.info("Nhấn chọn hộp kiểm ở trên để bắt đầu giả lập chạy Realtime.")

# =====================================================================
# TAB 2: PHÂN TÍCH FILE DỮ LIỆU CŨ (IMPORT JSON / LOG FILE)
# =====================================================================
with tab2:
    st.header(f"🔍 Trích xuất và phân tích file dữ liệu cũ cho cây: {cay_trong}")
    
    uploaded_file = st.file_uploader("Tải lên file nhật ký hệ thống (Định dạng .json):", type=["json"])
    
    if uploaded_file is not None:
        try:
            # Đọc file json thô dữ liệu tải lên
            raw_data = json.load(uploaded_file)
            
            # Tiến hành chuyển đổi dữ liệu, CHỈ lọc trích xuất 2 key: tempkk và humikk
            parsed_records = []
            
            # Hỗ trợ cấu trúc file json dạng danh sách các bản ghi (Array of Objects)
            for index, record in enumerate(raw_data):
                # Ép lấy mốc thời gian, nếu file không có key time sẽ tự tạo mốc tăng dần theo giờ
                timestamp = record.get("time", f"{index:02d}:00:00")
                
                # BỘ LỌC CHỈ TRÍCH XUẤT ĐÚNG 2 KEY THEO YÊU CẦU
                if "tempkk" in record and "humikk" in record:
                    t_val = float(record["tempkk"])
                    h_val = float(record["humikk"])
                    vpd_val = calculate_vpd(t_val, h_val)
                    
                    # Lấy khung giờ từ chuỗi thời gian để tính toán ngưỡng động đối chiếu
                    try:
                        hour_part = int(timestamp.split(":")[0])
                    except:
                        hour_part = 12 # mặc định nếu lỗi chuỗi chu kỳ
                        
                    ten_khung, (c_duoi, c_tren) = lay_khung_gio_va_nguong(hour_part)
                    
                    parsed_records.append({
                        "Time": timestamp,
                        "tempkk (Nhiệt độ)": t_val,
                        "humikk (Độ ẩm)": h_val,
                        "VPD": vpd_val,
                        "Cận Dưới Ngưỡng": c_duoi,
                        "Cận Trên Ngưỡng": c_tren,
                        "Khung Giờ": ten_khung
                    })
            
            if len(parsed_records) > 0:
                df_history = pd.DataFrame(parsed_records)
                st.success(f"🎉 Tải file thành công! Đã trích xuất xong chuỗi dữ liệu từ 2 trường 'tempkk' và 'humikk'.")
                
                # Hiển thị biểu đồ lịch sử 2 đồ thị song song
                col1_h, col2_h = st.columns(2)
                with col1_h:
                    st.subheader("Biểu đồ 1: Lịch sử biến thiên chỉ số VPD tổng quan cả ngày")
                    st.line_chart(df_history.set_index("Time")[["VPD", "Cận Dưới Ngưỡng", "Cận Trên Ngưỡng"]], color=["#FF4B4B", "#0000FF", "#0000FF"])
                with col2_h:
                    st.subheader("Biểu đồ 2: Lịch sử dữ liệu môi trường (tempkk & humikk)")
                    st.line_chart(df_history.set_index("Time")[["tempkk (Nhiệt độ)", "humikk (Độ ẩm)"]])
                
                # Khối quét lọc lỗi hệ thống và phân tích khung giờ
                st.subheader("📋 Báo Cáo Phân Tích Lỗi Hệ Thống Theo Khung Giờ")
                
                loi_thieu_vpd = df_history[df_history["VPD"] < df_history["Cận Dưới Ngưỡng"]]
                loi_thua_vpd = df_history[df_history["VPD"] > df_history["Cận Trên Ngưỡng"]]
                
                col_err1, col_err2 = st.columns(2)
                
                with col_err1:
                    st.markdown("🔴 **Các mốc thời gian phát hiện hiện tượng THIẾU VPD:**")
                    if not loi_thieu_vpd.empty:
                        for _, row in loi_thieu_vpd.iterrows():
                            st.write(f"- Mốc `{row['Time']}` ({row['Khung Giờ']}): VPD đạt `{row['VPD']}` (Ngưỡng tối thiểu yêu cầu `{row['Cận Dưới Ngưỡng']}`). **Nguyên nhân:** Do trường dữ liệu độ ẩm `humikk` quá cao (`{row['humikk (Độ ẩm)']}%`).")
                    else:
                        st.write("Không phát hiện lỗi thiếu VPD.")
                        
                with col_err2:
                    st.markdown("🟠 **Các mốc thời gian phát hiện hiện tượng THỪA VPD (Quá khô nóng):**")
                    if not loi_thua_vpd.empty:
                        for _, row in loi_thua_vpd.iterrows():
                            st.write(f"- Mốc `{row['Time']}` ({row['Khung Giờ']}): VPD đạt `{row['VPD']}` (Ngưỡng tối đa yêu cầu `{row['Cận Trên Ngưỡng']}`). **Nguyên nhân:** Do nhiệt độ không khí `tempkk` quá cao (`{row['tempkk (Nhiệt độ)']}°C`) hoặc độ ẩm quá thấp.")
                    else:
                        st.write("Không phát hiện lỗi thừa VPD.")
            else:
                st.error("File JSON hợp lệ nhưng không tìm thấy dữ liệu chứa đồng thời 2 key 'tempkk' và 'humikk'.")
        except Exception as e:
            st.error(f"Lỗi cấu trúc khi đọc file định dạng JSON: {e}")
