# Slideshow App (Streamlit)

Simple Streamlit app to create and display a slideshow/video from images.

**Features:**
- Create slideshows from image sequences
- Export as video using FFmpeg via `moviepy`

**Quick Start (local)**
1. Create a virtual environment (recommended).
2. Install Python dependencies:

   pip install -r requirements.txt

3. Run the app locally:

   streamlit run app.py

**Streamlit Community Cloud Deployment**
1. Ensure your repo contains these files at the project root:
   - `app.py`
   - `requirements.txt` (Python deps)
   - `packages.txt` (system packages for Streamlit Cloud)

2. `requirements.txt` should include at least:

   streamlit
   moviepy
   pillow
   opencv-python-headless
   numpy

3. `packages.txt` should contain `ffmpeg` so the cloud instance can render videos.

4. Push your code to a GitHub repository, then on share.streamlit.io click **New app**, select your repo, branch `main`, and set the main file to `app.py`. Click **Deploy**.

**Notes**
- Use `opencv-python-headless` in cloud environments to avoid GUI dependencies.
- If your app needs extra system packages, add them to `packages.txt`.

**License & Contact**
Feel free to update this README with your name, license, and contact details.

