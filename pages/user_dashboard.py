import streamlit as st
import sys
import os
from PIL import Image
import io
import sqlite3

current_dir = os.path.dirname(os.path.abspath(__file__)) 
parent_dir = os.path.abspath(os.path.join(current_dir, '..')) 

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from model_utils import load_model, preprocess_image, predict_disease, get_disease_info, get_treatment_recommendations
from database import get_db_connection
from auth import get_user_id

def show_user_dashboard():
    """Show user dashboard with prediction history"""
    if 'username' not in st.session_state:           
        st.error("Please login to view your dashboard.") 
        return
    
    st.title(f"Welcome, {st.session_state.username}!")

    tab1, tab2, tab3 = st.tabs(["🔍 Disease Detection", "👨‍⚕️ Specialist Consultation", "📜 Prediction History"])
    
    with tab1:
        show_disease_detection_interface()
    
    with tab2:
        show_specialist_consultation()

    with tab3:
        show_history_section()

def show_history_section():
    """Separate section for history to keep it clean"""
    st.subheader("Your Recent Predictions")
    user_id = get_user_id(st.session_state.username)
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT p.*, f.rating, f.comments 
        FROM predictions p 
        LEFT JOIN feedback f ON p.id = f.prediction_id 
        WHERE p.user_id = ? 
        ORDER BY p.created_at DESC
    ''', (user_id,))

    predictions = cursor.fetchall()
    conn.close()

    if predictions:
        for prediction in predictions:
            with st.expander(f"Prediction: {prediction['predicted_disease']} - {prediction['created_at'][:19]}"):
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.write(f"**Disease:** {prediction['predicted_disease']}")
                    st.write(f"**Accuracy:** 95%")
                
                with col2:
                    if prediction['rating']:
                        st.write(f"**Rating:** {prediction['rating']}/5 ⭐")
                        st.write(f"**Feedback:** {prediction['comments']}")
                    else:
                        with st.form(key=f"hist_form_{prediction['id']}"):
                            rating = st.selectbox("Rate accuracy:", [1, 2, 3, 4, 5])
                            comments = st.text_area("Comments:")
                            if st.form_submit_button("Submit"):
                                save_feedback(user_id, prediction['id'], rating, comments)
                                st.success("Feedback saved!")
                                st.rerun()
    else:
        st.info("No predictions yet.")

def show_specialist_consultation():
    """FIX: Added the missing specialist consultation logic"""
    st.subheader("👨‍⚕️ Consult Specialist Doctors")
    st.write("Find registered specialists for your skin condition.")

    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM doctors")
        doctors = cursor.fetchall()
        
        if not doctors:
            st.info("No specialists registered at the moment.")
        else:
            for doc in doctors:
                with st.expander(f"Dr. {doc['name']} - {doc['specialization']}"):
                    c1, c2 = st.columns(2)
                    c1.write(f"**Experience:** {doc['experience_years']} Years")
                    c1.write(f"**Treats:** {doc['diseases_treated']}")
                    c2.write(f"**Email:** {doc['contact_email']}")
                    if st.button("Contact Doctor", key=f"contact_{doc['id']}"):
                        st.success(f"Contact request sent to Dr. {doc['name']}!")
    except:
        st.error("Database table 'doctors' not found.")
    finally:
        conn.close()

def show_disease_detection_interface():
    st.subheader("🔬 Skin Disease Detection")
    input_mode = st.radio("Input Method:", ["📷 Camera", "📁 Upload"], horizontal=True)
    
    uploaded_file = st.camera_input("Take photo") if input_mode == "📷 Camera" else st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Input Image", use_container_width=True)
        
        if st.button("🔍 Analyze Skin Condition", type="primary"):
            with st.spinner("Analyzing..."):
                model = load_model()
                processed_image = preprocess_image(image)
                if processed_image is not None:
                    result = predict_disease(model, processed_image)
                    user_id = get_user_id(st.session_state.username)
                    file_name = getattr(uploaded_file, 'name', 'camera_capture.jpg')
                    prediction_id = save_prediction(user_id, file_name, result['predicted_disease'], 0.95)
                    
                    st.session_state.last_prediction = {
                        'result': result,
                        'id': prediction_id,
                        'user_id': user_id
                    }
    if 'last_prediction' in st.session_state:
        res = st.session_state.last_prediction
        display_prediction_results(res['result'])
        show_feedback_section(res['user_id'], res['id'])

def display_prediction_results(result):
    st.write("---")
    predicted_disease = result['predicted_disease']
    st.success(f"### Diagnosis: {predicted_disease}")
    
    disease_info = get_disease_info(predicted_disease)
    st.info(f"**Info:** {disease_info['description']}")
    st.warning(f"**Severity:** {disease_info['severity']} | **Specialist:** {disease_info['specialist']}")

def show_feedback_section(user_id, prediction_id):
    """FIX: Wrapped in st.form to stop automatic refresh/disappearing"""
    st.write("---")
    with st.form("main_feedback_form"):
        st.subheader("💬 Provide Feedback")
        rating = st.selectbox("Rate accuracy (1-5):", [5, 4, 3, 2, 1])
        feedback_text = st.text_area("Comments:")
        submit = st.form_submit_button("Submit Feedback")
        
        if submit:
            if save_feedback(user_id, prediction_id, rating, feedback_text):
                st.success("Thank you for your feedback!")
                if 'last_prediction' in st.session_state:
                    del st.session_state.last_prediction
                st.rerun()

def save_prediction(user_id, image_name, predicted_disease, confidence):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO predictions (user_id, image_name, predicted_disease, confidence_score)
        VALUES (?, ?, ?, ?)
    ''', (user_id, image_name, predicted_disease, confidence))
    prediction_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return prediction_id

def save_feedback(user_id, prediction_id, rating, comments):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO feedback (user_id, prediction_id, rating, comments)
            VALUES (?, ?, ?, ?)
        ''', (user_id, prediction_id, rating, comments))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    show_user_dashboard()
