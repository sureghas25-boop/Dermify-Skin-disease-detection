import streamlit as st
from database import get_db_connection, hash_password
import pandas as pd

def show_user_management():
    """User management interface"""
    st.title("👥 User Management")
    
    tab1, tab2 = st.tabs(["View Users", "Add User"])
    
    with tab1:
        show_users_list()
    
    with tab2:
        show_add_user_form()

def show_users_list():
    """Display list of all users with management options"""
    st.subheader("Registered Users")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT u.*, 
               COUNT(p.id) as prediction_count,
               MAX(p.created_at) as last_prediction
        FROM users u
        LEFT JOIN predictions p ON u.id = p.user_id
        WHERE u.is_admin = 0
        GROUP BY u.id
        ORDER BY u.created_at DESC
    ''')
    
    users = cursor.fetchall()
    conn.close()
    
    if users:
        # Convert to DataFrame for better display
        users_data = []
        for user in users:
            users_data.append({
                'ID': user['id'],
                'Username': user['username'],
                'Email': user['email'],
                'Joined': user['created_at'][:10],
                'Predictions': user['prediction_count'] or 0,
                'Last Active': user['last_prediction'][:10] if user['last_prediction'] else 'Never'
            })
        
        df = pd.DataFrame(users_data)
        st.dataframe(df, use_container_width=True)
        
        # User statistics
        st.write("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Users", len(users))
        
        with col2:
            active_users = sum(1 for user in users if user['prediction_count'] > 0)
            st.metric("Active Users", active_users)
        
        with col3:
            total_predictions = sum(user['prediction_count'] or 0 for user in users)
            st.metric("Total Predictions", total_predictions)
        
        # User management actions
        st.write("---")
        st.subheader("User Actions")
        
        user_options = [f"{user['id']} - {user['username']} ({user['email']})" for user in users]
        selected_user = st.selectbox("Select user to manage:", [""] + user_options)
        
        if selected_user:
            user_id = int(selected_user.split(" - ")[0])
            selected_user_data = next(user for user in users if user['id'] == user_id)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("👁️ View Details", use_container_width=True):
                    show_user_details(user_id)
            
            with col2:
                if st.button("🔄 Reset Password", use_container_width=True):
                    show_reset_password_form(user_id, selected_user_data['username'])
            
            with col3:
                if st.button("🗑️ Delete User", use_container_width=True, type="secondary"):
                    if st.session_state.get('confirm_delete_user') == user_id:
                        delete_user(user_id)
                        st.success("User deleted successfully!")
                        st.rerun()
                    else:
                        st.session_state.confirm_delete_user = user_id
                        st.warning("Click again to confirm deletion")
    else:
        st.info("No users registered yet.")

def show_user_details(user_id):
    """Show detailed information about a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get user info
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    
    # Get user's predictions
    cursor.execute('''
        SELECT * FROM predictions 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    ''', (user_id,))
    predictions = cursor.fetchall()
    
    # Get user's feedback
    cursor.execute('''
        SELECT f.*, p.predicted_disease 
        FROM feedback f
        JOIN predictions p ON f.prediction_id = p.id
        WHERE f.user_id = ?
        ORDER BY f.created_at DESC
    ''', (user_id,))
    feedback = cursor.fetchall()
    
    conn.close()
    
    with st.expander(f"User Details: {user['username']}", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Username:** {user['username']}")
            st.write(f"**Email:** {user['email']}")
            st.write(f"**Joined:** {user['created_at']}")
            st.write(f"**Total Predictions:** {len(predictions)}")
        
        with col2:
            st.write(f"**Total Feedback:** {len(feedback)}")
            if feedback:
                avg_rating = sum(f['rating'] for f in feedback) / len(feedback)
                st.write(f"**Average Rating Given:** {avg_rating:.1f}/5")
        
        if predictions:
            st.write("**Recent Predictions:**")
            for pred in predictions[:5]:
                st.write(f"• {pred['predicted_disease']} ({pred['confidence_score']:.2%}) - {pred['created_at'][:19]}")
        
        if feedback:
            st.write("**Recent Feedback:**")
            for fb in feedback[:3]:
                st.write(f"• {fb['predicted_disease']}: {fb['rating']}/5 - \"{fb['comments'][:50]}...\"")

def show_reset_password_form(user_id, username):
    """Show form to reset user password"""
    with st.expander(f"Reset Password for {username}", expanded=True):
        new_password = st.text_input("New Password", type="password", key=f"new_pass_{user_id}")
        confirm_password = st.text_input("Confirm Password", type="password", key=f"confirm_pass_{user_id}")
        
        if st.button(f"Reset Password for {username}", key=f"reset_{user_id}"):
            if new_password and confirm_password:
                if new_password == confirm_password:
                    if reset_user_password(user_id, new_password):
                        st.success("Password reset successfully!")
                    else:
                        st.error("Error resetting password")
                else:
                    st.error("Passwords do not match")
            else:
                st.error("Please enter both password fields")

def show_add_user_form():
    """Show form to add new user"""
    st.subheader("Add New User")
    
    with st.form("add_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Username*")
            email = st.text_input("Email*")
        
        with col2:
            password = st.text_input("Password*", type="password")
            is_admin = st.checkbox("Admin User")
        
        submitted = st.form_submit_button("Add User", type="primary")
        
        if submitted:
            if username and email and password:
                success = add_user(username, email, password, is_admin)
                if success:
                    st.success("User added successfully!")
                else:
                    st.error("Error adding user. Username or email might already exist.")
            else:
                st.error("Please fill all required fields")

def add_user(username, email, password, is_admin=False):
    """Add new user to database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        password_hash = hash_password(password)
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, is_admin)
            VALUES (?, ?, ?, ?)
        ''', (username, email, password_hash, is_admin))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error adding user: {str(e)}")
        return False

def reset_user_password(user_id, new_password):
    """Reset user password"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        password_hash = hash_password(new_password)
        cursor.execute('''
            UPDATE users SET password_hash = ? WHERE id = ?
        ''', (password_hash, user_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error resetting password: {str(e)}")
        return False

def delete_user(user_id):
    """Delete user and all associated data"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Delete associated feedback first
        cursor.execute("DELETE FROM feedback WHERE user_id = ?", (user_id,))
        
        # Delete associated predictions
        cursor.execute("DELETE FROM predictions WHERE user_id = ?", (user_id,))
        
        # Delete user
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error deleting user: {str(e)}")
        return False
