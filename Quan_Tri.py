import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import unicodedata
import re
from datetime import datetime, timedelta

# --- 1. CẤU HÌNH ---
st.set_page_config(page_title="Thần Số Học 2026", page_icon="🔮", layout="wide")

# --- 2. HÀM CHUYỂN TIẾNG VIỆT THÀNH KHÔNG DẤU LATINH ---
def to_latinh(text):
    if text is None or str(text).lower() == "nan": return ""
    s = str(text).strip()
    if s.startswith("'"): s = s[1:] # Bỏ dấu nháy của Sheets
    # Phân tách các dấu ra khỏi chữ cái
    s = unicodedata.normalize('NFD', s)
    s = ''.join([c for c in s if unicodedata.category(c) != 'Mn'])
    # Thay thế chữ đ/Đ thành d/D
    s = s.replace('đ', 'd').replace('Đ', 'D')
    # Chuyển về chữ thường và xóa khoảng trắng thừa
    s = ' '.join(s.lower().split())
    return s

# --- 3. KẾT NỐI ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 4. PHÂN QUYỀN ---
if "role" not in st.session_state:
    st.session_state["role"] = None

with st.sidebar:
    if st.session_state["role"] == "admin":
        st.header("⚡ QUẢN TRỊ")
        menu = st.radio("Chức năng:", ["Tra cứu", "Quản lý Up_DaTa", "Nhật ký History"])
        if st.button("Đăng xuất Admin"):
            st.session_state["role"] = None
            st.rerun()
    else:
        menu = "Tra cứu"

# --- 5. TRANG TRA CỨU ---
if menu == "Tra cứu":
    st.title("🔍 Tra Cứu Kết Quả")
    if st.session_state["role"] is None:
        pwd = st.text_input("Nhập mật khẩu:", type="password")
        if st.button("Vào hệ thống"):
            if pwd == "khachhang2026": st.session_state["role"] = "user"; st.rerun()
            elif pwd == "admin2026": st.session_state["role"] = "admin"; st.rerun()
            else: st.error("Sai mật khẩu!")
        st.stop()

    n_in = st.text_input("Họ và Tên (Có dấu hoặc không đều được):")
    d_in = st.text_input("Ngày sinh (Đủ 8 số, ví dụ: 26031990):")
    
    if st.button("Tra cứu ngay"):
        if n_in and d_in:
            try:
                # Đọc dữ liệu từ sheet Up_DaTa (Lưu ý chữ T viết hoa)
                df = conn.read(worksheet="Up_DaTa", ttl=0).astype(str)
                
                # Chuẩn hóa thông tin người dùng nhập
                user_name = to_latinh(n_in)
                user_dob = d_in.strip()
                
                # Tìm kiếm thủ công để đảm bảo độ chính xác
                found_row = None
                for _, row in df.iterrows():
                    sheet_name = to_latinh(row.iloc[0]) # Cột Họ Tên
                    sheet_dob = str(row.iloc[1]).strip().replace("'", "") # Cột Ngày Sinh
                    
                    if sheet_name == user_name and sheet_dob == user_dob:
                        found_row = row
                        break
                
                if found_row is not None:
                    st.success(f"Chào bạn **{found_row.iloc[0]}**!")
                    c1, c2 = st.columns(2)
                    # Lấy Số Chủ Đạo và Số Định Mệnh
                    scd = str(found_row.iloc[3]).split('.')[0]
                    sdm = str(found_row.iloc[4]).split('.')[0]
                    c1.metric("Số Chủ Đạo", scd)
                    c2.metric("Số Định Mệnh", sdm)
                    
                    # Ghi nhật ký History
                    try:
                        hist_df = conn.read(worksheet="History", ttl=0)
                        new_log = pd.DataFrame([{
                            "Thời Gian Tra Cứu": (datetime.now() + timedelta(hours=7)).strftime("%d/%m/%Y %H:%M:%S"),
                            "Họ Và Tên": found_row.iloc[0],
                            "Ngày Sinh": f"'{d_in}",
                            "Trạng Thái": "Thành công"
                        }])
                        conn.update(worksheet="History", data=pd.concat([hist_df, new_log], ignore_index=True))
                    except: pass
                else:
                    st.error("Không tìm thấy kết quả. Vui lòng kiểm tra lại thông tin.")
            except Exception as e:
                st.error(f"Lỗi truy xuất dữ liệu: {e}")
        else:
            st.warning("Vui lòng điền đầy đủ thông tin.")

# --- 6. QUẢN LÝ DỮ LIỆU ---
elif menu == "Quản lý Up_DaTa":
    st.title("📂 Cập Nhật Dữ Liệu Nguồn")
    with st.expander("➕ Thêm khách hàng mới", expanded=True):
        with st.form("add_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Họ Tên:")
            dob = c2.text_input("Ngày sinh (8 số):")
            phone = c1.text_input("Số Điện Thoại:")
            scd = c2.text_input("Số Chủ Đạo:")
            sdm = st.text_input("Số Định Mệnh:")
            if st.form_submit_button("Lưu dữ liệu"):
                if name and dob:
                    try:
                        df_old = conn.read(worksheet="Up_DaTa", ttl=0)
                        new_row = pd.DataFrame([{"Họ Tên": name, "Ngày Sinh": f"'{dob}", "Số Điện Thoại": phone, "Số Chủ Đạo": scd, "Số Định Mệnh": sdm}])
                        conn.update(worksheet="Up_DaTa", data=pd.concat([df_old, new_row], ignore_index=True))
                        st.success("Đã lưu thành công!")
                        st.rerun()
                    except Exception as e: st.error(e)

    st.dataframe(conn.read(worksheet="Up_DaTa", ttl=0), use_container_width=True)

# --- 7. NHẬT KÝ ---
elif menu == "Nhật ký History":
    st.title("📋 Lịch Sử Hệ Thống")
    try:
        st.dataframe(conn.read(worksheet="History", ttl=0).sort_index(ascending=False), use_container_width=True)
    except: st.info("Chưa có lịch sử.")

