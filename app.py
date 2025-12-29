import streamlit as st
from moviepy.editor import ImageClip, CompositeVideoClip, VideoClip, ColorClip
from moviepy.video.fx.all import resize
import cv2
import numpy as np
from PIL import Image, ImageFilter
import tempfile
import os

# --- UI CONFIGURATION ---
st.set_page_config(page_title="Cinematic Slideshow Engine", layout="wide")

def apply_custom_style():
    st.markdown("""
        <style>
        .main { background-color: #0e1117; color: #ffffff; }
        .stButton>button { width: 100%; border-radius: 5px; background-color: #ff4b4b; color: white; }
        .stSlider { color: #ff4b4b; }
        </style>
    """, unsafe_allow_html=True)

class VideoEngine:
    """Handles the heavy lifting of image transformation and video assembly."""
    
    @staticmethod
    def create_blurred_background(pil_img, target_w, target_h):
        """Creates a blurred, scaled-to-fill background to eliminate black bars."""
        # Scale to fill the entire frame
        img_w, img_h = pil_img.size
        aspect_ratio = img_w / img_h
        target_ratio = target_w / target_h

        if aspect_ratio > target_ratio:
            # Image is wider than target
            new_h = target_h
            new_w = int(target_h * aspect_ratio)
        else:
            # Image is taller than target
            new_w = target_w
            new_h = int(target_w / aspect_ratio)

        # Create background: Resize -> Blur
        bg = pil_img.resize((new_w, new_h), Image.LANCZOS)
        bg = bg.filter(ImageFilter.GaussianBlur(radius=20))
        
        # Center crop the background to target size
        left = (new_w - target_w) / 2
        top = (new_h - target_h) / 2
        bg = bg.crop((left, top, left + target_w, top + target_h))
        return bg

    @staticmethod
    def process_foreground(pil_img, target_w, target_h):
        """Scales image to fit within the frame while maintaining aspect ratio."""
        pil_img.thumbnail((target_w, target_h), Image.LANCZOS)
        return pil_img

    @staticmethod
    def apply_motion(clip, effect, duration):
        """Applies dynamic transforms using MoviePy's coordinate system."""
        if effect == "Zoom In":
            return clip.resize(lambda t: 1 + 0.04 * t)
        elif effect == "Zoom Out":
            return clip.resize(lambda t: 1.2 - 0.04 * t)
        elif effect == "Slide Left":
            return clip.set_position(lambda t: (int(0 - (20 * t)), 'center'))
        return clip

def main():
    apply_custom_style()
    st.title("🎬 Cinematic Slideshow Engine")
    st.subheader("Professional Multimedia Pipeline")

    # --- SIDEBAR SETTINGS ---
    with st.sidebar:
        st.header("⚙️ Global Settings")
        ratio_label = st.selectbox("Aspect Ratio", ["16:9 (Landscape)", "9:16 (Portrait)", "1:1 (Square)"])
        duration = st.slider("Duration per Image (s)", 1, 10, 5)
        motion_effect = st.selectbox("Motion Effect", ["None", "Zoom In", "Zoom Out", "Slide Left"])
        
        # Map ratio
        ratios = {"16:9 (Landscape)": (1920, 1080), "9:16 (Portrait)": (1080, 1920), "1:1 (Square)": (1080, 1080)}
        W, H = ratios[ratio_label]

    # --- UPLOAD SECTION ---
    uploaded_files = st.file_uploader("Upload Images", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

    if uploaded_files:
        st.success(f"{len(uploaded_files)} images loaded.")
        
        if st.button("Generate Video"):
            clips = []
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                for idx, file in enumerate(uploaded_files):
                    status_text.text(f"Processing image {idx+1}/{len(uploaded_files)}...")
                    
                    # 1. Load and process images
                    raw_img = Image.open(file).convert("RGB")
                    
                    # Create Background (Blurred & Scaled)
                    bg_pil = VideoEngine.create_blurred_background(raw_img, W, H)
                    fg_pil = VideoEngine.process_foreground(raw_img, W, H)
                    
                    # Convert to MoviePy clips
                    bg_clip = ImageClip(np.array(bg_pil)).set_duration(duration)
                    fg_clip = ImageClip(np.array(fg_pil)).set_duration(duration).set_position('center')
                    
                    # 2. Layering
                    combined = CompositeVideoClip([bg_clip, fg_clip], size=(W, H))
                    
                    # 3. Apply Motion
                    if motion_effect != "None":
                        combined = VideoEngine.apply_motion(combined, motion_effect, duration)
                    
                    clips.append(combined)
                    progress_bar.progress((idx + 1) / len(uploaded_files))

                # 4. Concatenate and Render
                status_text.text("Finalizing render... This may take a moment.")
                final_video = CompositeVideoClip([VideoClip.set_start(c, i * duration) for i, c in enumerate(clips)])
                final_video.duration = len(clips) * duration

                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmpfile:
                    final_video.write_videofile(
                        tmpfile.name, 
                        fps=24, 
                        codec="libx264", 
                        audio=False, 
                        threads=4, 
                        preset="medium"
                    )
                    
                    st.video(tmpfile.name)
                    
                    with open(tmpfile.name, "rb") as f:
                        st.download_button("Download MP4", f, file_name="slideshow.mp4", mime="video/mp4")
                
                status_text.text("Render Complete!")

            except Exception as e:
                st.error(f"An error occurred: {e}")
            finally:
                # Cleanup logic would go here in a production env
                pass

if __name__ == "__main__":
    main()