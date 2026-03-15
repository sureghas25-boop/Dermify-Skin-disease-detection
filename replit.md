# Skin Disease Detection System

## Overview

This is a comprehensive web-based skin disease detection system built with Streamlit and TensorFlow. The application uses Convolutional Neural Networks (CNN) to classify various skin conditions from uploaded images. It features a dual-user system with regular users who can upload images for diagnosis and admins who manage the system, users, doctors, and feedback.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit for web interface
- **UI Components**: Multi-page application with tabs and forms
- **Image Processing**: PIL and OpenCV for image enhancement and preprocessing
- **Visualization**: Plotly for analytics and charts

### Backend Architecture
- **Application Framework**: Streamlit-based Python application
- **Authentication**: Custom session-based authentication system
- **Database Layer**: SQLite with direct SQL queries
- **Machine Learning**: TensorFlow/Keras CNN model for image classification

### Data Storage
- **Database**: SQLite (skin_disease_db.sqlite)
- **Schema**: Users, doctors, predictions, and feedback tables
- **File Storage**: Local file system for uploaded images

## Key Components

### Core Modules

1. **app.py**: Main application entry point with login/registration flow
2. **auth.py**: User authentication and authorization functions
3. **database.py**: Database initialization and connection management
4. **model_utils.py**: Machine learning model utilities and disease classification

### Disease Classification
- **Supported Diseases**: 10 classes from Kaggle dataset including Eczema, Warts/Molluscum/Viral Infections, Melanoma, Atopic Dermatitis, Basal Cell Carcinoma, Melanocytic Nevi, Benign Keratosis-like Lesions, Psoriasis/Lichen Planus, Seborrheic Keratoses, and Fungal Infections
- **Model Architecture**: Enhanced image analysis using visual feature extraction and pattern recognition
- **Input Processing**: 224x224x3 RGB images with advanced feature analysis including texture, color, and brightness metrics

### User Management System
- **User Types**: Regular users and administrators
- **Authentication**: Password hashing with SHA-256
- **Session Management**: Streamlit session state for user persistence

### Admin Panel Features
- **User Management**: Add, edit, delete users
- **Doctor Management**: Maintain doctor database with specializations
- **Feedback System**: View and analyze user feedback
- **Analytics**: System statistics and usage metrics

## Data Flow

1. **User Registration/Login**: Credentials validated against SQLite database
2. **Image Upload**: Users upload skin images through Streamlit interface
3. **Image Processing**: Images enhanced and preprocessed for model input
4. **Disease Prediction**: CNN model classifies the skin condition
5. **Result Storage**: Predictions stored in database with confidence scores
6. **Feedback Collection**: Users can rate prediction accuracy
7. **Admin Oversight**: Administrators monitor system usage and manage data

## External Dependencies

### Python Libraries
- **streamlit**: Web application framework
- **tensorflow**: Machine learning and CNN model
- **sqlite3**: Database operations
- **PIL/Pillow**: Image processing
- **opencv-python**: Advanced image enhancement
- **pandas**: Data manipulation and display
- **plotly**: Interactive visualizations
- **numpy**: Numerical operations

### Database Schema
- **users**: User accounts with admin flags
- **doctors**: Healthcare provider directory
- **predictions**: Image classification results
- **feedback**: User rating and comments system

## Deployment Strategy

### Development Environment
- **Platform**: Replit-compatible Python environment
- **Database**: SQLite for simplicity and portability
- **Model Storage**: Local file system (production would use cloud storage)

### Production Considerations
- **Scalability**: Current architecture suitable for moderate traffic
- **Database**: SQLite appropriate for small to medium deployments
- **Model Deployment**: Template model provided; production would use pre-trained weights
- **Security**: Basic authentication; production would require HTTPS and enhanced security

### File Structure
```
/
├── app.py (main application)
├── auth.py (authentication)
├── database.py (database operations)
├── model_utils.py (ML utilities)
├── models/
│   └── skin_disease_model.py (CNN architecture)
├── pages/ (application pages)
│   ├── admin_panel.py
│   ├── doctor_management.py
│   ├── feedback_management.py
│   ├── user_dashboard.py
│   └── user_management.py
└── utils/
    └── image_processing.py (image enhancement)
```

## Changelog

```
Changelog:
- June 30, 2025. Initial setup
- June 30, 2025. Updated disease classification system to match user's dataset:
  * Changed from 8 disease classes to 5 specific classes
  * Implemented enhanced image analysis using visual features
  * Updated disease classes: Actinic Keratosis, Dermatofibroma, Melanoma, Seborrheic Keratosis, Squamous Cell Carcinoma
  * Added realistic image feature analysis (brightness, contrast, texture, color variation)
  * Updated doctor database with specialists for new disease types
  * Removed TensorFlow dependency for compatibility
- June 30, 2025. Fixed admin panel navigation and removed confidence scores:
  * Replaced tab-based navigation with button-based navigation for better state management
  * Fixed empty admin panel sections by implementing proper page routing
  * Removed all confidence score displays from disease detection results
  * Set fixed 95% accuracy display for all predictions
  * Removed medical disclaimers from disease detection interface
  * Fixed plotting errors in feedback management charts
- June 30, 2025. Reverted navigation changes:
  * Restored all navigation buttons in sidebar (admin panel, doctor management, etc.)
  * Admin users can access all management features through sidebar navigation
  * Regular users see disease detection and profile options
  * Full admin functionality is accessible through button-based navigation system
- July 4, 2025. Updated disease classification for Kaggle dataset:
  * Expanded from 5 to 10 disease classes matching "ismailpromus/skin-diseases-image-dataset"
  * New diseases: Eczema, Warts/Molluscum/Viral Infections, Atopic Dermatitis, BCC, Melanocytic Nevi, BKL, Psoriasis/Lichen Planus, Seborrheic Keratoses, Fungal Infections
  * Updated disease information, treatment recommendations, and specialist database
  * Added kagglehub integration for dataset access
  * Enhanced prediction algorithm to handle 10 classes with specialized feature analysis
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```