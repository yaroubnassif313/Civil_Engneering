# -*- coding: utf-8 -*-
import streamlit as st
import sqlite3

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="Civil Engineering Hub", layout="centered")

# --- 2. دالة التحقق من الطلاب ---
def check_user(name, serial):
    try:
        conn = sqlite3.connect("Engineering_Library.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM access_gate WHERE full_name=? AND serial_number=?", (name, serial))
        res = cursor.fetchone()
        conn.close()
        return res
    except:
        return None

# --- 3. إدارة الجلسة والوضع السري (المطور) ---
if 'page' not in st.session_state:
    st.session_state.page = 'welcome'
if 'admin_auth' not in st.session_state:
    st.session_state.admin_auth = False

# الطريقة الجديدة لقراءة الرابط السري (?admin=true)
is_admin_mode = st.query_params.get("admin") == "true"

# --- 4. الصفحة الرئيسية ---
if st.session_state.page == 'welcome':
    st.title("🏗️ Civil Engineering Hub")
    st.divider()
    
    # زر الطلاب (للجميع)
    if st.button("Student Access", use_container_width=True, type="primary"):
        st.session_state.page = 'login'
        st.rerun()
    
    # ظهور زر الأدمن "فقط" إذا كان الرابط ينتهي بـ ?admin=true
    if is_admin_mode:
        st.warning("🔐 Admin Access Detected")
        if st.button("Open Admin Dashboard", use_container_width=True):
            st.session_state.page = 'admin'
            st.rerun()

# --- 5. لوحة التحكم (الكاملة بالتبويبات الثلاثة) ---
elif st.session_state.page == 'admin':
    st.header("🛡️ Admin Panel")
    if not st.session_state.admin_auth:
        with st.form("admin_login"):
            pw = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                if pw == "yarub2024":
                    st.session_state.admin_auth = True
                    st.rerun()
                else:
                    st.error("Wrong Password")
    else:
        t1, t2, t3 = st.tabs(["📚 Lectures", "👥 Add Student", "⚙️ Manage Students"])
        
        with t1:
            st.subheader("Add Lecture")
            years = ["السنة الأولى", "السنة الثانية", "السنة الثالثة", "السنة الرابعة", "السنة الخامسة"]
            y = st.selectbox("Year:", years, key="adm_y")
            conn = sqlite3.connect("Engineering_Library.db"); c = conn.cursor()
            c.execute("SELECT subject_name FROM subjects WHERE academic_year=?", (y,))
            subs = [r[0] for r in c.fetchall()]; conn.close()
            if subs:
                s = st.selectbox("Subject:", subs, key="adm_s")
                title = st.text_input("Title")
                link = st.text_input("Link")
                if st.button("Save"):
                    conn = sqlite3.connect("Engineering_Library.db"); c = conn.cursor()
                    c.execute("INSERT INTO university_archive VALUES (?,?,?,?)", (y, s, title, link))
                    conn.commit(); conn.close(); st.success("Added!")

        with t2:
            st.subheader("Register Student")
            new_n = st.text_input("Name")
            new_s = st.text_input("Serial")
            if st.button("Register"):
                conn = sqlite3.connect("Engineering_Library.db"); c = conn.cursor()
                c.execute("INSERT INTO access_gate VALUES (?,?)", (new_n, new_s))
                conn.commit(); conn.close(); st.success(f"Registered: {new_n}")

        with t3:
            st.subheader("Delete Students")
            conn = sqlite3.connect("Engineering_Library.db"); c = conn.cursor()
            c.execute("SELECT full_name, serial_number FROM access_gate")
            all_st = c.fetchall(); conn.close()
            for name, serial in all_st:
                col1, col2 = st.columns([3, 1])
                col1.write(f"👤 {name} ({serial})")
                if col2.button("Delete", key=f"del_{serial}"):
                    conn = sqlite3.connect("Engineering_Library.db"); c = conn.cursor()
                    c.execute("DELETE FROM access_gate WHERE serial_number=?", (serial,))
                    conn.commit(); conn.close(); st.rerun()

    if st.button("Exit Admin"):
        st.session_state.admin_auth = False
        st.session_state.page = 'welcome'
        st.rerun()

# --- 6. صفحة الدخول للطلاب ---
elif st.session_state.page == 'login':
    st.header("🔑 Verification")
    n = st.text_input("Name")
    s = st.text_input("Serial")
    if st.button("Enter", use_container_width=True, type="primary"):
        if check_user(n, s):
            st.session_state.page = 'library'
            st.rerun()
        else: st.error("Not Found")
    if st.button("Back"):
        st.session_state.page = 'welcome'
        st.rerun()

# --- 7. صفحة المكتبة ---
elif st.session_state.page == 'library':
    st.title("📚 Archive")
    years = ["السنة الأولى", "السنة الثانية", "السنة الثالثة", "السنة الرابعة", "السنة الخامسة"]
    sy = st.sidebar.selectbox("Year:", years)
    conn = sqlite3.connect("Engineering_Library.db"); c = conn.cursor()
    c.execute("SELECT subject_name FROM subjects WHERE academic_year=?", (sy,))
    subs = [r[0] for r in c.fetchall()]; conn.close()
    if subs:
        ss = st.selectbox("Subject:", subs)
        conn = sqlite3.connect("Engineering_Library.db"); c = conn.cursor()
        c.execute("SELECT lecture_title, file_url FROM university_archive WHERE academic_year=? AND subject_name=?", (sy, ss))
        files = c.fetchall(); conn.close()
        for ft, fu in files:
            c1, c2 = st.columns([3, 1])
            c1.write(f"📄 {ft}")
            c2.link_button("View", fu)
    if st.sidebar.button("Logout"):
        st.session_state.page = 'welcome'
        st.rerun()
