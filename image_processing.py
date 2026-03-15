import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import streamlit as st

def enhance_image_quality(image):
    """Enhance image quality for better model prediction"""
    try:
        # Convert PIL image to numpy array
        img_array = np.array(image)
        
        # Apply various enhancement techniques
        enhanced_image = apply_image_enhancements(img_array)
        
        # Convert back to PIL Image
        return Image.fromarray(enhanced_image)
    
    except Exception as e:
        st.error(f"Error enhancing image: {str(e)}")
        return image

def apply_image_enhancements(img_array):
    """Apply various image enhancement techniques"""
    # Convert to BGR for OpenCV processing
    if len(img_array.shape) == 3 and img_array.shape[2] == 3:
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    else:
        img_bgr = img_array
    
    # 1. Noise reduction
    denoised = cv2.bilateralFilter(img_bgr, 9, 75, 75)
    
    # 2. Contrast enhancement using CLAHE
    lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    l = clahe.apply(l)
    
    enhanced = cv2.merge([l, a, b])
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
    
    # 3. Sharpening
    kernel = np.array([[-1,-1,-1],
                      [-1, 9,-1],
                      [-1,-1,-1]])
    sharpened = cv2.filter2D(enhanced, -1, kernel)
    
    # Convert back to RGB
    result = cv2.cvtColor(sharpened, cv2.COLOR_BGR2RGB)
    
    return result

def validate_image(image):
    """Validate uploaded image for skin disease detection"""
    try:
        # Check image size
        width, height = image.size
        
        if width < 100 or height < 100:
            return False, "Image is too small. Please upload an image at least 100x100 pixels."
        
        if width > 4000 or height > 4000:
            return False, "Image is too large. Please upload an image smaller than 4000x4000 pixels."
        
        # Check image format
        if image.format not in ['JPEG', 'JPG', 'PNG']:
            return False, "Unsupported image format. Please upload JPEG or PNG images."
        
        # Check if image has content (not completely black or white)
        img_array = np.array(image.convert('L'))  # Convert to grayscale
        mean_brightness = np.mean(img_array)
        
        if mean_brightness < 10 or mean_brightness > 245:
            return False, "Image appears to be too dark or too bright. Please upload a clearer image."
        
        return True, "Image validation passed."
    
    except Exception as e:
        return False, f"Error validating image: {str(e)}"

def resize_image_for_display(image, max_width=800, max_height=600):
    """Resize image for display purposes while maintaining aspect ratio"""
    try:
        width, height = image.size
        
        # Calculate scaling factor
        scale = min(max_width / width, max_height / height, 1.0)
        
        if scale < 1.0:
            new_width = int(width * scale)
            new_height = int(height * scale)
            return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image
    
    except Exception as e:
        st.error(f"Error resizing image: {str(e)}")
        return image

def extract_skin_region(image):
    """Extract skin region from image using color-based segmentation"""
    try:
        # Convert to numpy array
        img_array = np.array(image)
        
        # Convert to HSV color space
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        
        # Define skin color range in HSV
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        
        # Create mask for skin pixels
        mask = cv2.inRange(hsv, lower_skin, upper_skin)
        
        # Apply morphological operations to clean up the mask
        kernel = np.ones((3,3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Apply mask to original image
        result = cv2.bitwise_and(img_array, img_array, mask=mask)
        
        return Image.fromarray(result)
    
    except Exception as e:
        st.error(f"Error extracting skin region: {str(e)}")
        return image

def analyze_image_properties(image):
    """Analyze various properties of the uploaded image"""
    try:
        # Basic properties
        width, height = image.size
        format_type = image.format
        mode = image.mode
        
        # Convert to numpy for analysis
        img_array = np.array(image)
        
        # Color analysis
        if len(img_array.shape) == 3:
            mean_color = np.mean(img_array, axis=(0, 1))
            color_std = np.std(img_array, axis=(0, 1))
        else:
            mean_color = np.mean(img_array)
            color_std = np.std(img_array)
        
        # Brightness analysis
        gray = np.array(image.convert('L'))
        brightness = np.mean(gray)
        contrast = np.std(gray)
        
        # Sharpness analysis (using Laplacian variance)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        analysis = {
            'dimensions': f"{width} x {height}",
            'format': format_type,
            'mode': mode,
            'brightness': brightness,
            'contrast': contrast,
            'sharpness': laplacian_var,
            'mean_color': mean_color,
            'color_std': color_std
        }
        
        return analysis
    
    except Exception as e:
        st.error(f"Error analyzing image properties: {str(e)}")
        return {}

def suggest_image_improvements(analysis):
    """Suggest improvements based on image analysis"""
    suggestions = []
    
    if 'brightness' in analysis:
        brightness = analysis['brightness']
        if brightness < 50:
            suggestions.append("Image appears too dark. Try taking the photo in better lighting.")
        elif brightness > 200:
            suggestions.append("Image appears overexposed. Reduce lighting or camera flash.")
    
    if 'contrast' in analysis:
        contrast = analysis['contrast']
        if contrast < 30:
            suggestions.append("Image has low contrast. Ensure good lighting and focus.")
    
    if 'sharpness' in analysis:
        sharpness = analysis['sharpness']
        if sharpness < 100:
            suggestions.append("Image appears blurry. Hold the camera steady and ensure proper focus.")
    
    if 'dimensions' in analysis:
        width, height = map(int, analysis['dimensions'].split(' x '))
        if width < 300 or height < 300:
            suggestions.append("Image resolution is low. Try capturing a higher resolution image.")
    
    return suggestions
