import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import unicodedata
import re
from datetime import datetime, timedelta

# --- 1. CẤU HÌNH & CSS GIAO DIỆN ---
st.set_page_config(
    page_title="CỔNG THÔNG TIN CÔNG TÁC DOANH NGHIỆP",
    page_icon="🔮",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Biến cấu hình
APP_URL = "https://share.streamlit.io/..." 
ADMIN_ZALO = "0909000xxx" 
ADMIN_EMAIL = "admin@tna.com"
ADMIN_PHONE = "0909.000.xxx HOÀNG TÚ "

# CSS tùy chỉnh
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    .result-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #ff4b4b;
        text-align: center;
        margin-bottom: 20px;
    }
    .big-number {
        font-size: 3rem;
        font-weight: bold;
        color: #ff4b4b;
    }
    .label-text {
        font-size: 1.2rem;
        font-weight: 500;
        color: #31333F;
    }
    
    [data-testid="stToolbar"] {display: none;}
    [data-testid="stDecoration"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. HÀM XỬ LÝ DỮ LIỆU ---
def clean_id(text):
    if not text or str(text) == "nan": return ""
    s = str(text).split('.')[0].strip()
    s = unicodedata.normalize('NFD', s)
    s = ''.join([c for c in s if unicodedata.category(c) != 'Mn'])
    s = s.replace('đ', 'd').replace('Đ', 'D')
    s = re.sub(r'[^a-zA-Z0-9]', '', s).lower()
    if s.isdigit() and len(s) == 7:
        s = "0" + s
    return s

# --- 3. SIDEBAR (ĐÃ RÚT GỌN) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712009.png", width=100)
    st.title("Trung Tâm Hỗ Trợ")
    
    if "client_auth" in st.session_state and st.session_state["client_auth"]:
        st.success("✅ Đang đăng nhập")
        if st.button("Đăng xuất"):
            st.session_state["client_auth"] = False
            st.rerun()
    else:
        st.info("🔒 Chưa đăng nhập")

# --- 4. MÀN HÌNH ĐĂNG NHẬP ---
if "client_auth" not in st.session_state:
    st.session_state["client_auth"] = False

if not st.session_state["client_auth"]:
    st.markdown("<h1 style='text-align: center;'>🔮 Cổng Tra Cứu </h1>", unsafe_allow_html=True)
    st.write("---")
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        pwd = st.text_input("Nhập mật khẩu truy cập:", type="password")
        if st.button("Truy cập hệ thống", use_container_width=True):
            if pwd == "nhanvien2026":
                st.session_state["client_auth"] = True
                st.rerun()
            else:
                st.error("Mật khẩu không đúng, vui lòng liên hệ Admin.")
    st.stop()

# --- 5. CHƯƠNG TRÌNH CHÍNH: TRA CỨU ---
st.markdown("<h1 style='text-align: center; color: #ff4b4b;'>✨ Tra Cứu Thần Số Học ✨</h1>", unsafe_allow_html=True)
st.write("Nhập thông tin của bạn để khám phá những con số bí ẩn.")

conn = st.connection("gsheets", type=GSheetsConnection)

with st.container(border=True):
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        name_in = st.text_input("Họ và Tên (viết thường,VD : luu xuan quang):", placeholder="Nguyen Van A")
    with col_input2:
        dob_in = st.text_input("Mã Ngày Sinh (Ví dụ: 01101972):", placeholder="ddmmyyyy")
    
    btn_search = st.button("🔍 Tra cứu ngay", type="primary", use_container_width=True)

if btn_search:
    if name_in and dob_in:
        try:
            with st.spinner("Đang kết nối với vũ trụ..."):
                df = conn.read(ttl=0)
                df['n_match'] = df.iloc[:, 0].apply(clean_id)
                df['d_match'] = df.iloc[:, 1].apply(clean_id)
                
                s_name = clean_id(name_in)
                s_dob = clean_id(dob_in)
                
                match = df[(df['n_match'] == s_name) & (df['d_match'] == s_dob)]
                
                if not match.empty:
                    res_full_name = match.iloc[0, 0]
                    scd = str(match.iloc[0, 3]).split('.')[0]
                    sdm = str(match.iloc[0, 4]).split('.')[0]
                    
                    st.markdown("---")
                    st.success(f"🎉 Chào mừng bạn **{res_full_name.upper()}**!")
                    
                    col_res1, col_res2 = st.columns(2)
                    with col_res1:
                        st.markdown(f'<div class="result-card"><div class="label-text">Số Chủ Đạo</div><div class="big-number">{scd}</div></div>', unsafe_allow_html=True)
                    with col_res2:
                        st.markdown(f'<div class="result-card"><div class="label-text">Số Định Mệnh</div><div class="big-number">{sdm}</div></div>', unsafe_allow_html=True)

                    st.markdown("### 💖 Bạn cảm thấy thế nào?")
                    c_like, c_share_fb, c_copy = st.columns([1, 1, 1])
                    with c_like:
                        if st.button("❤️ Yêu thích"):
                            st.balloons()
                            st.toast("Cảm ơn bạn đã yêu thích!", icon="😍")
                    with c_share_fb:
                        fb_share_url = f"https://www.facebook.com/sharer/sharer.php?u={APP_URL}"
                        st.link_button("Chia sẻ Facebook", fb_share_url)
                    with c_copy:
                         st.link_button("Gửi Zalo cho bạn bè", f"https://zalo.me/share/?url={APP_URL}")

                    # --- PHẦN GHI LỊCH SỬ ---
                    try:
                        now_vn = (datetime.now() + timedelta(hours=7)).strftime("%d/%m/%Y %H:%M:%S")
                        new_log = pd.DataFrame([{"Thời Gian Tra Cứu": now_vn, "Họ Và Tên": res_full_name, "Ngày Sinh": f"'{s_dob}", "Trạng Thái": "Thành công"}])
                        history_df = conn.read(worksheet="History", ttl=0)
                        updated_history = pd.concat([history_df, new_log], ignore_index=True)
                        conn.update(worksheet="History", data=updated_history)
                    except Exception as log_err:
                        print(f"Log error: {log_err}")
                else:
                    st.error("❌ Không tìm thấy thông tin phù hợp.")
        except Exception as e:
            st.error(f"Lỗi hệ thống: {e}")
    else:
        st.warning("Vui lòng nhập đầy đủ thông tin.")

# --- 6. PHẦN THÔNG TIN LIÊN HỆ (FOOTER MỚI) ---
st.markdown("<br><br>", unsafe_allow_html=True) # Tạo khoảng cách
st.markdown("---")
f_col1, f_col2 = st.columns([2, 1])

with f_col1:
    st.markdown("### 📞 Liên hệ Quản Trị")
    st.write(f"**Hotline:** {ADMIN_PHONE}")
    st.write(f"**Email:** {ADMIN_EMAIL}")

with f_col2:
    st.markdown("### Kết nối nhanh")
    st.link_button("💬 Chat Zalo Admin", f"https://zalo.me/{ADMIN_ZALO}", use_container_width=True)
    st.link_button("🌐 Fanpage Facebook", "https://facebook.com", use_container_width=True)

st.caption("© 2026 Tra Cứu Thông Tin | Phát triển bởi Team Admin")

