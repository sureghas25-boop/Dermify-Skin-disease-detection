import streamlit as st
from database import get_db_connection
import pandas as pd
import plotly.express as px

def show_feedback_management():
    """Feedback management interface"""
    st.title("💬 Feedback Management")
    
    tab1, tab2, tab3 = st.tabs(["All Feedback", "Analytics", "Export"])
    
    with tab1:
        show_all_feedback()
    
    with tab2:
        show_feedback_analytics()
    
    with tab3:
        show_export_options()

def show_all_feedback():
    """Display all feedback with filtering options"""
    st.subheader("User Feedback")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all feedback with user and prediction details
    cursor.execute('''
        SELECT f.*, u.username, p.predicted_disease, p.confidence_score
        FROM feedback f
        JOIN users u ON f.user_id = u.id
        JOIN predictions p ON f.prediction_id = p.id
        ORDER BY f.created_at DESC
    ''')
    
    feedback_data = cursor.fetchall()
    conn.close()
    
    if feedback_data:
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_rating = st.selectbox("Minimum Rating:", [1, 2, 3, 4, 5], index=0)
        
        with col2:
            diseases = list(set([fb['predicted_disease'] for fb in feedback_data]))
            selected_disease = st.selectbox("Filter by Disease:", ["All"] + diseases)
        
        with col3:
            # Date range filter could be added here
            st.write("") # Placeholder
        
        # Apply filters
        filtered_feedback = []
        for fb in feedback_data:
            if fb['rating'] >= min_rating:
                if selected_disease == "All" or fb['predicted_disease'] == selected_disease:
                    filtered_feedback.append(fb)
        
        st.write(f"Showing {len(filtered_feedback)} of {len(feedback_data)} feedback entries")
        
        # Display feedback
        for fb in filtered_feedback:
            with st.expander(f"Feedback by {fb['username']} - {fb['rating']}/5 stars - {fb['created_at'][:19]}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Prediction:** {fb['predicted_disease']}")
                    st.write(f"**Confidence:** {fb['confidence_score']:.2%}")
                    st.write(f"**Rating:** {'⭐' * fb['rating']} ({fb['rating']}/5)")
                    st.write(f"**Comments:** {fb['comments']}")
                
                with col2:
                    st.write(f"**User:** {fb['username']}")
                    st.write(f"**Date:** {fb['created_at'][:19]}")
                    
                    # Admin actions
                    if st.button(f"Mark as Reviewed", key=f"review_{fb['id']}"):
                        mark_feedback_reviewed(fb['id'])
                        st.success("Marked as reviewed")
    else:
        st.info("No feedback received yet.")

def show_feedback_analytics():
    """Show feedback analytics and insights"""
    st.subheader("Feedback Analytics")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Overall statistics
    cursor.execute('''
        SELECT 
            AVG(rating) as avg_rating,
            COUNT(*) as total_feedback,
            COUNT(CASE WHEN rating >= 4 THEN 1 END) as positive_feedback,
            COUNT(CASE WHEN rating <= 2 THEN 1 END) as negative_feedback
        FROM feedback
    ''')
    
    stats = cursor.fetchone()
    
    if stats and stats['total_feedback'] > 0:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Average Rating", f"{stats['avg_rating']:.2f}/5")
        
        with col2:
            st.metric("Total Feedback", stats['total_feedback'])
        
        with col3:
            positive_percent = (stats['positive_feedback'] / stats['total_feedback']) * 100
            st.metric("Positive (4-5⭐)", f"{positive_percent:.1f}%")
        
        with col4:
            negative_percent = (stats['negative_feedback'] / stats['total_feedback']) * 100
            st.metric("Negative (1-2⭐)", f"{negative_percent:.1f}%")
        
        # Rating distribution
        cursor.execute('''
            SELECT rating, COUNT(*) as count
            FROM feedback
            GROUP BY rating
            ORDER BY rating
        ''')
        
        rating_dist = cursor.fetchall()
        
        if rating_dist:
            st.subheader("Rating Distribution")
            rating_df = pd.DataFrame(rating_dist, columns=['Rating', 'Count'])
            fig = px.bar(rating_df, x='Rating', y='Count', title="Distribution of Ratings")
            st.plotly_chart(fig, use_container_width=True)
        
        # Feedback by disease
        cursor.execute('''
            SELECT p.predicted_disease, AVG(f.rating) as avg_rating, COUNT(f.id) as feedback_count
            FROM feedback f
            JOIN predictions p ON f.prediction_id = p.id
            GROUP BY p.predicted_disease
            ORDER BY feedback_count DESC
        ''')
        
        disease_feedback = cursor.fetchall()
        
        if disease_feedback:
            st.subheader("Average Rating by Disease")
            disease_df = pd.DataFrame(disease_feedback, columns=['Disease', 'Avg Rating', 'Count'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(disease_df, x='Disease', y='Avg Rating', 
                           title="Average Rating by Disease Type")
                fig.update_layout(xaxis={'tickangle': 45})
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(disease_df, x='Disease', y='Count', 
                           title="Feedback Count by Disease Type")
                fig.update_layout(xaxis={'tickangle': 45})
                st.plotly_chart(fig, use_container_width=True)
        
        # Recent trends
        cursor.execute('''
            SELECT DATE(created_at) as date, AVG(rating) as avg_rating, COUNT(*) as count
            FROM feedback
            WHERE created_at >= datetime('now', '-30 days')
            GROUP BY DATE(created_at)
            ORDER BY date
        ''')
        
        trends = cursor.fetchall()
        
        if trends:
            st.subheader("Rating Trends (Last 30 Days)")
            trends_df = pd.DataFrame(trends, columns=['Date', 'Avg Rating', 'Count'])
            
            fig = px.line(trends_df, x='Date', y='Avg Rating', 
                         title="Average Rating Trend Over Time")
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("No feedback data available for analytics.")
    
    conn.close()

def show_export_options():
    """Show options to export feedback data"""
    st.subheader("Export Feedback Data")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT f.*, u.username, p.predicted_disease, p.confidence_score
        FROM feedback f
        JOIN users u ON f.user_id = u.id
        JOIN predictions p ON f.prediction_id = p.id
        ORDER BY f.created_at DESC
    ''')
    
    feedback_data = cursor.fetchall()
    conn.close()
    
    if feedback_data:
        # Convert to DataFrame
        export_data = []
        for fb in feedback_data:
            export_data.append({
                'Feedback ID': fb['id'],
                'Username': fb['username'],
                'Predicted Disease': fb['predicted_disease'],
                'Model Confidence': fb['confidence_score'],
                'User Rating': fb['rating'],
                'Comments': fb['comments'],
                'Date': fb['created_at']
            })
        
        df = pd.DataFrame(export_data)
        
        # Display summary
        st.write(f"Total records to export: {len(df)}")
        
        # Preview data
        st.subheader("Data Preview")
        st.dataframe(df.head(10), use_container_width=True)
        
        # Export options
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Download as CSV", use_container_width=True):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Click to Download CSV",
                    data=csv,
                    file_name=f"feedback_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("📋 Generate Summary Report", use_container_width=True):
                generate_summary_report(df)
    
    else:
        st.info("No feedback data available to export.")

def generate_summary_report(df):
    """Generate a summary report of the feedback"""
    st.subheader("📋 Feedback Summary Report")
    
    total_feedback = len(df)
    avg_rating = df['User Rating'].mean()
    
    # Rating distribution
    rating_counts = df['User Rating'].value_counts().sort_index()
    
    # Most common diseases in feedback
    disease_counts = df['Predicted Disease'].value_counts()
    
    # Generate report text
    report = f"""
    ## Feedback Summary Report
    Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    ### Overview
    - Total Feedback Entries: {total_feedback}
    - Average Rating: {avg_rating:.2f}/5.0
    
    ### Rating Distribution
    """
    
    for rating in range(1, 6):
        count = rating_counts.get(rating, 0)
        percentage = (count / total_feedback) * 100 if total_feedback > 0 else 0
        report += f"- {rating} Stars: {count} ({percentage:.1f}%)\n"
    
    report += f"""
    
    ### Most Frequently Rated Diseases
    """
    
    for disease, count in disease_counts.head(5).items():
        percentage = (count / total_feedback) * 100
        report += f"- {disease}: {count} ({percentage:.1f}%)\n"
    
    st.markdown(report)
    
    # Download report
    if st.button("📄 Download Report as Text"):
        st.download_button(
            label="Click to Download Report",
            data=report,
            file_name=f"feedback_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

def mark_feedback_reviewed(feedback_id):
    """Mark feedback as reviewed (could add a reviewed column to database)"""
    # This is a placeholder function
    # In a real implementation, you might add a 'reviewed' column to the feedback table
    pass
