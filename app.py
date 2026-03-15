import streamlit as st
import sqlite3
from auth import authenticate_user, register_user, is_admin
from database import init_database
import os

# Initialize database
init_database()

# Set page config
st.set_page_config(
    page_title="Skin Disease Detection System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_type" not in st.session_state:
    st.session_state.user_type = ""

def main():
    st.title("🏥 Skin Disease Detection System")
    
    if not st.session_state.logged_in:
        show_login_page()
    else:
        show_main_app()

def show_login_page():
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login to Your Account")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", key="login_btn"):
            if username and password:
                user_data = authenticate_user(username, password)
                if user_data:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.user_type = "admin" if is_admin(username) else "user"
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.error("Please enter both username and password")
    
    with tab2:
        st.subheader("Create New Account")
        new_username = st.text_input("Username", key="reg_username")
        new_email = st.text_input("Email", key="reg_email")
        new_password = st.text_input("Password", type="password", key="reg_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_password")
        
        if st.button("Register", key="register_btn"):
            if new_username and new_email and new_password and confirm_password:
                if new_password == confirm_password:
                    if register_user(new_username, new_email, new_password):
                        st.success("Account created successfully! Please login.")
                    else:
                        st.error("Username already exists")
                else:
                    st.error("Passwords do not match")
            else:
                st.error("Please fill all fields")

def show_main_app():
    # Initialize navigation state
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Disease Detection"
    
    # Sidebar navigation
    with st.sidebar:
        st.write(f"Welcome, {st.session_state.username}!")
        st.write(f"Role: {st.session_state.user_type.title()}")
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.user_type = ""
            st.session_state.current_page = "Disease Detection"
            st.rerun()
        
        st.divider()
        
        # Navigation menu with buttons instead of selectbox
        st.subheader("Navigation")
        
        if st.button("🔬 Disease Detection", use_container_width=True):
            st.session_state.current_page = "Disease Detection"
            st.rerun()
        
        if st.session_state.user_type == "admin":
            if st.button("👤 Admin Panel", use_container_width=True):
                st.session_state.current_page = "Admin Panel"
                st.rerun()
            
            if st.button("👥 User Management", use_container_width=True):
                st.session_state.current_page = "User Management"
                st.rerun()
            
            if st.button("👨‍⚕️ Doctor Management", use_container_width=True):
                st.session_state.current_page = "Doctor Management"
                st.rerun()
            
            if st.button("💬 Feedback Management", use_container_width=True):
                st.session_state.current_page = "Feedback Management"
                st.rerun()
        else:
            if st.button("📊 My Profile", use_container_width=True):
                st.session_state.current_page = "My Profile"
                st.rerun()
    
    # Main content area based on current page
    page = st.session_state.current_page
    
    if page == "Disease Detection":
        show_disease_detection()
    elif page == "Admin Panel" and st.session_state.user_type == "admin":
        from pages.admin_panel import show_admin_panel
        show_admin_panel()
    elif page == "User Management" and st.session_state.user_type == "admin":
        from pages.user_management import show_user_management
        show_user_management()
    elif page == "Doctor Management" and st.session_state.user_type == "admin":
        from pages.doctor_management import show_doctor_management
        show_doctor_management()
    elif page == "Feedback Management" and st.session_state.user_type == "admin":
        from pages.feedback_management import show_feedback_management
        show_feedback_management()
    elif page == "My Profile":
        from pages.user_dashboard import show_user_dashboard
        show_user_dashboard()
    else:
        # Default to disease detection
        show_disease_detection()

def show_disease_detection():
    from pages.user_dashboard import show_disease_detection_interface
    show_disease_detection_interface()

if __name__ == "__main__":
    main()
