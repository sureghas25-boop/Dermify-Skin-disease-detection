import streamlit as st
from database import get_db_connection
import pandas as pd

def show_doctor_management():
    """Doctor management interface"""
    st.title("👨‍⚕️ Doctor Management")
    
    tab1, tab2 = st.tabs(["View Doctors", "Add/Edit Doctor"])
    
    with tab1:
        show_doctors_list()
    
    with tab2:
        show_doctor_form()

def show_doctors_list():
    """Display list of all doctors with edit/delete options"""
    st.subheader("Registered Doctors")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM doctors ORDER BY name")
    doctors = cursor.fetchall()
    conn.close()
    
    if doctors:
        # Convert to DataFrame for better display
        doctors_data = []
        for doctor in doctors:
            doctors_data.append({
                'ID': doctor['id'],
                'Name': doctor['name'],
                'Specialization': doctor['specialization'],
                'Email': doctor['contact_email'],
                'Phone': doctor['contact_phone'],
                'Experience': f"{doctor['experience_years']} years",
                'Diseases Treated': doctor['diseases_treated'][:50] + "..." if len(doctor['diseases_treated']) > 50 else doctor['diseases_treated']
            })
        
        df = pd.DataFrame(doctors_data)
        st.dataframe(df, use_container_width=True)
        
        # Edit/Delete section
        st.write("---")
        st.subheader("Edit or Delete Doctor")
        
        doctor_options = [f"{doctor['id']} - {doctor['name']}" for doctor in doctors]
        selected_doctor = st.selectbox("Select doctor to modify:", [""] + doctor_options)
        
        if selected_doctor:
            doctor_id = int(selected_doctor.split(" - ")[0])
            selected_doctor_data = next(doctor for doctor in doctors if doctor['id'] == doctor_id)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✏️ Edit Doctor", use_container_width=True):
                    st.session_state.edit_doctor_id = doctor_id
                    st.rerun()
            
            with col2:
                if st.button("🗑️ Delete Doctor", use_container_width=True, type="secondary"):
                    if st.session_state.get('confirm_delete') == doctor_id:
                        delete_doctor(doctor_id)
                        st.success("Doctor deleted successfully!")
                        st.rerun()
                    else:
                        st.session_state.confirm_delete = doctor_id
                        st.warning("Click again to confirm deletion")
    else:
        st.info("No doctors registered yet.")

def show_doctor_form():
    """Show form to add or edit doctor"""
    edit_mode = 'edit_doctor_id' in st.session_state
    
    if edit_mode:
        st.subheader("Edit Doctor")
        doctor_id = st.session_state.edit_doctor_id
        
        # Get doctor data
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM doctors WHERE id = ?", (doctor_id,))
        doctor = cursor.fetchone()
        conn.close()
        
        if not doctor:
            st.error("Doctor not found!")
            del st.session_state.edit_doctor_id
            st.rerun()
    else:
        st.subheader("Add New Doctor")
        doctor = None
    
    # Doctor form
    with st.form("doctor_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Doctor Name*", 
                value=doctor['name'] if doctor else ""
            )
            specialization = st.text_input(
                "Specialization*", 
                value=doctor['specialization'] if doctor else ""
            )
            contact_email = st.text_input(
                "Contact Email", 
                value=doctor['contact_email'] if doctor else ""
            )
        
        with col2:
            contact_phone = st.text_input(
                "Contact Phone", 
                value=doctor['contact_phone'] if doctor else ""
            )
            experience_years = st.number_input(
                "Years of Experience", 
                min_value=0, 
                max_value=50, 
                value=int(doctor['experience_years']) if doctor else 0
            )
            address = st.text_input(
                "Address", 
                value=doctor['address'] if doctor else ""
            )
        
        diseases_treated = st.text_area(
            "Diseases/Conditions Treated (comma-separated)*", 
            value=doctor['diseases_treated'] if doctor else "",
            help="e.g., Acne, Eczema, Psoriasis, Melanoma"
        )
        
        submitted = st.form_submit_button(
            "Update Doctor" if edit_mode else "Add Doctor",
            type="primary"
        )
        
        if submitted:
            if name and specialization and diseases_treated:
                if edit_mode:
                    success = update_doctor(
                        doctor_id, name, specialization, contact_email, 
                        contact_phone, address, experience_years, diseases_treated
                    )
                    if success:
                        st.success("Doctor updated successfully!")
                        del st.session_state.edit_doctor_id
                        st.rerun()
                else:
                    success = add_doctor(
                        name, specialization, contact_email, 
                        contact_phone, address, experience_years, diseases_treated
                    )
                    if success:
                        st.success("Doctor added successfully!")
                        st.rerun()
            else:
                st.error("Please fill in all required fields (marked with *)")
    
    if edit_mode:
        if st.button("Cancel Edit"):
            del st.session_state.edit_doctor_id
            st.rerun()

def add_doctor(name, specialization, contact_email, contact_phone, address, experience_years, diseases_treated):
    """Add new doctor to database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO doctors (name, specialization, contact_email, contact_phone, address, experience_years, diseases_treated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, specialization, contact_email, contact_phone, address, experience_years, diseases_treated))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error adding doctor: {str(e)}")
        return False

def update_doctor(doctor_id, name, specialization, contact_email, contact_phone, address, experience_years, diseases_treated):
    """Update existing doctor"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE doctors 
            SET name=?, specialization=?, contact_email=?, contact_phone=?, address=?, experience_years=?, diseases_treated=?
            WHERE id=?
        ''', (name, specialization, contact_email, contact_phone, address, experience_years, diseases_treated, doctor_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error updating doctor: {str(e)}")
        return False

def delete_doctor(doctor_id):
    """Delete doctor from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM doctors WHERE id = ?", (doctor_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error deleting doctor: {str(e)}")
        return False
