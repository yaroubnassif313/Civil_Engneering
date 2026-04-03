# -*- coding: utf-8 -*-
import streamlit as st
import sqlite3

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Civil Engineering Hub", layout="centered")

# --- دالة التحقق من الطلاب ---
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

# --- إدارة الجلسة ---
if 'page' not in st.session_state:
    st.session_state.page = 'welcome'
if 'admin_auth' not in st.session_state:
    st.session_state.admin_auth = False

# --- 1. صفحة الترحيب ---
if st.session_state.page == 'welcome':
    st.title("🏗️ Civil Engineering Hub")
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Student Access", use_container_width=True, type="primary"):
            st.session_state.page = 'login'
            st.rerun()
    with c2:
        if st.button("Admin Dashboard", use_container_width=True):
            st.session_state.page = 'admin'
            st.rerun()

# --- 2. صفحة الدخول ---
elif st.session_state.page == 'login':
    st.header("🔑 Student Verification")
    u_name = st.text_input("Full Name")
    u_serial = st.text_input("Serial Number")
    if st.button("Verify", use_container_width=True, type="primary"):
        if check_user(u_name, u_serial):
            st.session_state.page = 'library'
            st.rerun()
        else:
            st.error("Student Not Found")
    if st.button("Back"):
        st.session_state.page = 'welcome'
        st.rerun()

# --- 3. لوحة التحكم (المعدلة بالتبويبات) ---
elif st.session_state.page == 'admin':
    st.header("🛡️ Admin Panel")
    if not st.session_state.admin_auth:
        with st.form("login_form"):
            pw = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                if pw == "yarub2024":
                    st.session_state.admin_auth = True
                    st.rerun()
                else:
                    st.error("Wrong Password")
    else:
        # التبويبات التي طلبتها
        t1, t2 = st.tabs(["📚 Lectures", "👥 Students"])
        
        with t1:
            st.subheader("Add Lecture")
            years = ["السنة الأولى", "السنة الثانية", "السنة الثالثة", "السنة الرابعة", "السنة الخامسة"]
            y = st.selectbox("Year:", years, key="y1")
            
            conn = sqlite3.connect("Engineering_Library.db")
            cursor = conn.cursor()
            cursor.execute("SELECT subject_name FROM subjects WHERE academic_year=?", (y,))
            subs = [r[0] for r in cursor.fetchall()] # جلب النص الصافي
            conn.close()
            
            if subs:
                s = st.selectbox("Subject:", subs, key="s1")
                title = st.text_input("Title")
                link = st.text_input("Drive Link")
                if st.button("Save Lecture"):
                    conn = sqlite3.connect("Engineering_Library.db")
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO university_archive (academic_year, subject_name, lecture_title, file_url) VALUES (?,?,?,?)", (y, s, title, link))
                    conn.commit()
                    conn.close()
                    st.success("Done!")

        with t2:
            st.subheader("Add Student")
            sn = st.text_input("Name")
            sr = st.text_input("Serial")
            if st.button("Register"):
                conn = sqlite3.connect("Engineering_Library.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO access_gate (full_name, serial_number) VALUES (?,?)", (sn, sr))
                conn.commit()
                conn.close()
                st.success("Registered!")

    if st.button("Logout"):
        st.session_state.admin_auth = False
        st.session_state.page = 'welcome'
        st.rerun()

# --- 4. صفحة المكتبة ---
elif st.session_state.page == 'library':
    st.title("📚 Archive")
    years = ["السنة الأولى", "السنة الثانية", "السنة الثالثة", "السنة الرابعة", "السنة الخامسة"]
    sy = st.sidebar.selectbox("Year:", years)
    
    conn = sqlite3.connect("Engineering_Library.db")
    cursor = conn.cursor()
    cursor.execute("SELECT subject_name FROM subjects WHERE academic_year=?", (sy,))
    subs = [r[0] for r in cursor.fetchall()]
    conn.close()
    
    if subs:
        ss = st.selectbox("Subject:", subs)
        conn = sqlite3.connect("Engineering_Library.db")
        cursor = conn.cursor()
        cursor.execute("SELECT lecture_title, file_url FROM university_archive WHERE academic_year=? AND subject_name=?", (sy, ss))
        files = cursor.fetchall()
        conn.close()
        for f in files:
            c1, c2 = st.columns([3, 1])
            c1.write(f"📄 {f[0]}")
            c2.link_button("View", f[1])
            
    if st.sidebar.button("Logout"):
        st.session_state.page = 'welcome'
        st.rerun()
