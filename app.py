import streamlit as st
from PIL import Image
from cartoonify import cartoonify_image
import io

# Streamlit page setup
st.set_page_config(page_title="🎨 Cartoonify Pro", layout="wide")
st.title("🖼️ Cartoonify Pro – Turn Your Photos into Art!")
st.markdown("Upload an image, pick a style, and tweak sliders to make your photo look like a **cartoon, comic, or pencil sketch!** 🎨")

# Upload section
uploaded_file = st.file_uploader("📸 Upload Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)

    with st.sidebar:
        st.header("🎛️ Adjustments")

        style = st.radio("🖌️ Choose Style", ["Classic", "Comic", "Pencil", "Soft"])

        brightness = st.slider("Brightness", 0, 100, 50)
        contrast = st.slider("Contrast", 0, 100, 50)
        grayscale_strength = st.slider("Grayscale Intensity", 0, 100, 50)
        edge_strength = st.slider("Edge Strength", 5, 15, 9, step=2)
        color_smooth = st.slider("Color Smoothness", 5, 20, 9)

        st.markdown("✨ Tip: Increase **Color Smoothness** and **Contrast** for a stronger cartoon effect!")

    with st.spinner("🪄 Creating your cartoon masterpiece..."):
        cartoon_img = cartoonify_image(image, brightness, contrast, grayscale_strength, edge_strength, color_smooth, style)

    col1, col2 = st.columns(2)

    with col1:
        st.image(image, caption="Original Image", use_container_width=True)

    with col2:
        st.image(cartoon_img, caption=f"{style} Cartoonified Image", use_container_width=True)

        # Download option
        buf = io.BytesIO()
        Image.fromarray(cartoon_img).save(buf, format="PNG")
        byte_im = buf.getvalue()
        st.download_button(
            label="💾 Download Cartoon Image",
            data=byte_im,
            file_name=f"{style.lower()}_cartoon.png",
            mime="image/png"
        )

    # About section
    with st.expander("📘 About this Project"):
        st.markdown("""
        This project uses **OpenCV** and **Streamlit** to convert real images into cartoon-style artwork.
        - 🧩 Filters: Edge detection, bilateral filtering, k-means color clustering
        - 🎛️ Adjustable: Brightness, contrast, grayscale, smoothness
        - 🎨 Styles: Classic, Comic, Pencil, and Soft look
        - 🚀 Built using Python and deployed via Streamlit Cloud
        """)

else:
    st.info("Please upload an image to start cartoonifying!")
