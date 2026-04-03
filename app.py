# -*- coding: utf-8 -*-
import streamlit as st
import sqlite3

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="Civil Engineering Hub", layout="centered")

# --- 2. دالات قاعدة البيانات ---
def get_db():
    return sqlite3.connect("Engineering_Library.db")

def check_user(name, serial):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM access_gate WHERE full_name=? AND serial_number=?", (name, serial))
        res = cursor.fetchone()
        conn.close()
        return res
    except:
        return None

# --- 3. إدارة الجلسة والوضع السري ---
# التحقق من وجود ?role=admin في الرابط لإظهار لوحة التحكم
query_params = st.query_params
is_admin_mode = query_params.get("role") == "admin"

if 'page' not in st.session_state:
    st.session_state.page = 'welcome'
if 'admin_auth' not in st.session_state:
    st.session_state.admin_auth = False

# --- 4. الصفحة الرئيسية ---
if st.session_state.page == 'welcome':
    st.title("🏗️ Civil Engineering Hub")
    st.divider()
    
    # دخول الطلاب (يظهر دائماً)
    if st.button("Student Access", use_container_width=True, type="primary"):
        st.session_state.page = 'login'
        st.rerun()
    
    # دخول المسؤول (يظهر فقط بالرابط السري)
    if is_admin_mode:
        st.info("🔐 Admin Mode Active")
        if st.button("Open Admin Dashboard", use_container_width=True):
            st.session_state.page = 'admin'
            st.rerun()

# --- 5. صفحة التحقق للطلاب ---
elif st.session_state.page == 'login':
    st.header("🔑 Student Verification")
    u_name = st.text_input("Full Name")
    u_serial = st.text_input("Serial Number")
    
    if st.button("Verify & Enter", use_container_width=True, type="primary"):
        if check_user(u_name, u_serial):
            st.session_state.page = 'library'
            st.rerun()
        else:
            st.error("Student Not Found in Records.")
            
    if st.button("Back to Home"):
        st.session_state.page = 'welcome'
        st.rerun()

# --- 6. لوحة تحكم المسؤول الشاملة ---
elif st.session_state.page == 'admin':
    st.header("🛡️ Admin Panel")
    if not st.session_state.admin_auth:
        with st.form("admin_login"):
            pw = st.text_input("Admin Password", type="password")
            if st.form_submit_button("Login"):
                if pw == "yarub2024":
                    st.session_state.admin_auth = True
                    st.rerun()
                else:
                    st.error("Wrong Password")
    else:
        # التبويبات الثلاثة (إدارة المحاضرات، إضافة طلاب، حذف/تعديل طلاب)
        t1, t2, t3 = st.tabs(["📚 Lectures", "👥 Add Student", "⚙️ Manage Students"])
        
        with t1:
            st.subheader("Add Lecture")
            years = ["السنة الأولى", "السنة الثانية", "السنة الثالثة", "السنة الرابعة", "السنة الخامسة"]
            y = st.selectbox("Year:", years, key="adm_y")
            
            conn = get_db(); c = conn.cursor()
            c.execute("SELECT subject_name FROM subjects WHERE academic_year=?", (y,))
            subs = [r[0] for r in c.fetchall()]
            conn.close()
            
            if subs:
                s = st.selectbox("Subject:", subs, key="adm_s")
                title = st.text_input("Lecture Title")
                link = st.text_input("Drive Link")
                if st.button("Save Lecture"):
                    if title and link:
                        conn = get_db(); c = conn.cursor()
                        c.execute("INSERT INTO university_archive (academic_year, subject_name, lecture_title, file_url) VALUES (?,?,?,?)", (y, s, title, link))
                        conn.commit(); conn.close()
                        st.success(f"Added: {title}")

        with t2:
            st.subheader("Add New Student")
            new_n = st.text_input("Full Name", key="new_n")
            new_s = st.text_input("Serial Number", key="new_s")
            if st.button("Register Student"):
                if new_n and new_s:
                    conn = get_db(); c = conn.cursor()
                    c.execute("INSERT INTO access_gate (full_name, serial_number) VALUES (?,?)", (new_n, new_s))
                    conn.commit(); conn.close()
                    st.success(f"Student {new_n} Registered!")

        with t3:
            st.subheader("Current Students List")
            conn = get_db(); c = conn.cursor()
            c.execute("SELECT full_name, serial_number FROM access_gate")
            students = c.fetchall()
            conn.close()
            
            for name, serial in students:
                col1, col2 = st.columns([3, 1])
                col1.write(f"👤 {name} ({serial})")
                if col2.button("Delete", key=f"del_{serial}"):
                    conn = get_db(); c = conn.cursor()
                    c.execute("DELETE FROM access_gate WHERE serial_number=?", (serial,))
                    conn.commit(); conn.close()
                    st.rerun()

    if st.button("Exit Admin"):
        st.session_state.admin_auth = False
        st.session_state.page = 'welcome'
        st.rerun()

# --- 7. صفحة أرشيف المواد ---
elif st.session_state.page == 'library':
    st.title("📚 Academic Archive")
    years = ["السنة الأولى", "السنة الثانية", "السنة الثالثة", "السنة الرابعة", "السنة الخامسة"]
    sy = st.sidebar.selectbox("Select Year:", years)
    
    conn = get_db(); c = conn.cursor()
    c.execute("SELECT subject_name FROM subjects WHERE academic_year=?", (sy,))
    subs = [r[0] for r in c.fetchall()]
    conn.close()
    
    if subs:
        ss = st.selectbox("Choose Subject:", subs)
        st.divider()
        conn = get_db(); c = conn.cursor()
        c.execute("SELECT lecture_title, file_url FROM university_archive WHERE academic_year=? AND subject_name=?", (sy, ss))
        files = c.fetchall()
        conn.close()
        
        if files:
            for f_t, f_u in files:
                c1, c2 = st.columns([3, 1])
                c1.write(f"📄 {f_t}")
                c2.link_button("View", f_u)
        else:
            st.info("No files uploaded for this subject.")
            
    if st.sidebar.button("Log Out"):
        st.session_state.page = 'welcome'
        st.rerun()
