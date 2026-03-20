import streamlit as st
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import pytesseract
from pytesseract import Output

# -----------------------------
# Tesseract Path (Windows)
# -----------------------------

# Windows my path
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Users\mujam\OneDrive\Documents\Luminar\Machine_Learning\Deep_Learning_Projects"
    r"\read_text\DL_Project\DL Project\OCR\Tesseract-OCR\tesseract.exe"
)
# import os
# import shutil

# # Try auto-detect first
# tesseract_path = shutil.which("tesseract")

# if tesseract_path:
#     pytesseract.pytesseract.tesseract_cmd = tesseract_path
# elif os.name == "nt":
#     # fallback for common Windows path
#     pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Visual Error Spotter",
    layout="centered"
)

st.title("📄 Visual Error Spotter")
st.caption("Detects visual formatting issues in document images")

# -----------------------------
# Contrast Detection (CORRECT)
# -----------------------------
def compute_text_contrast(gray_img, rgb_img):
    data = pytesseract.image_to_data(
        rgb_img, output_type=Output.DICT
    )

    contrasts = []

    for i in range(len(data["text"])):
        txt = data["text"][i].strip()
        x = data["left"][i]
        y = data["top"][i]
        w = data["width"][i]
        h = data["height"][i]

        if txt == "" or w < 10 or h < 10:
            continue

        roi = gray_img[y:y+h, x:x+w]
        if roi.size == 0:
            continue

        # Binarize ROI
        _, binary = cv2.threshold(
            roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        text_pixels = roi[binary == 0]
        bg_pixels   = roi[binary == 255]

        if len(text_pixels) < 10 or len(bg_pixels) < 10:
            continue

        contrast = abs(
            np.mean(text_pixels) - np.mean(bg_pixels)
        )

        contrasts.append(contrast)

    if not contrasts:
        return None

    return float(np.mean(contrasts))


def analyze_contrast_severity(score):
    if score > 120:
        return "Excellent Contrast"
    elif score > 70:
        return "Good Contrast"
    elif score > 40:
        return "Moderate Contrast"
    else:
        return "Poor Contrast"

# -----------------------------
# Skew Detection
# -----------------------------
def detect_skew_angle(gray):
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

    if lines is None:
        return 0.0

    angles = []
    for i in range(min(50, len(lines))):
        rho, theta = lines[i][0]
        angle = (theta - np.pi / 2) * 180 / np.pi
        angles.append(angle)

    return float(np.median(angles)) if angles else 0.0


def skew_severity(angle):
    angle = abs(angle)
    if angle < 1:
        return "Well Aligned"
    elif angle < 3:
        return "Slight Skew"
    else:
        return "Severe Skew"

# -----------------------------
# Font Size Variance
# -----------------------------
def estimate_font_variance(image):
    data = pytesseract.image_to_data(image, output_type=Output.DICT)

    heights = [
        h for txt, h in zip(data["text"], data["height"])
        if txt.strip() != "" and h > 10
    ]

    if len(heights) < 5:
        return None

    return float(np.var(heights))


def font_severity(var):
    if var < 20:
        return "Uniform Font"
    elif var < 80:
        return "Mixed Font Sizes"
    else:
        return "Highly Inconsistent Fonts"

# -----------------------------
# Line Spacing Variance
# -----------------------------
def estimate_line_spacing(image):
    data = pytesseract.image_to_data(image, output_type=Output.DICT)

    lines = {}

    for i in range(len(data["text"])):
        txt = data["text"][i].strip()
        y = data["top"][i]

        if txt == "":
            continue

        key = int(y / 15)

        if key not in lines:
            lines[key] = []
        lines[key].append(y)

    line_positions = sorted([int(np.mean(v)) for v in lines.values()])

    if len(line_positions) < 3:
        return 0.0

    spacings = np.diff(line_positions)

    # Remove extreme spacing (headings, sections)
    spacings = [s for s in spacings if s < np.percentile(spacings, 90)]

    if not spacings:
        return 0.0

    spacings = np.array(spacings)

    mean_spacing = np.mean(spacings)

    # Normalize variance (coefficient of variation)
    cv = np.std(spacings) / mean_spacing

    return float(cv * 100)

def line_spacing_severity(var):
    if var < 20:
        return "Consistent Spacing"
    elif var < 40:
        return "Moderate Variation"
    else:
        return "Erratic Spacing"
    
# -----------------------------
# Document Type Detection
# -----------------------------
def detect_document_type(image):
    data = pytesseract.image_to_data(image, output_type=Output.DICT)

    words = data["text"]
    confs = data["conf"]

    valid_words = []
    valid_conf = []

    for w, c in zip(words, confs):
        if w.strip() != "":
            valid_words.append(w)
            try:
                valid_conf.append(int(c))
            except:
                continue

    if len(valid_words) < 5:
        return "Handwritten / Low Text"

    avg_conf = np.mean(valid_conf) if valid_conf else 0

    if avg_conf < 50:
        return "Handwritten / Low OCR Confidence"
    else:
        return "Printed Document"
# -----------------------------
# Upload Section
# -----------------------------
uploaded = st.file_uploader(
    "Upload a document image (PNG / JPG)",
    type=["png", "jpg", "jpeg"]
)

if uploaded:
    image = Image.open(uploaded).convert("RGB")
    st.image(image, caption="Uploaded Image", use_container_width=True)

    img_np = np.array(image)
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

    # Detect document type
    doc_type = detect_document_type(img_np)

    st.subheader("📄 Document Type")
    st.info(doc_type)

    if "Handwritten" in doc_type:
        st.warning("⚠️ This system is optimized for printed documents. Results may be unreliable.")

        st.info("ℹ️ Font and spacing metrics may not apply to handwritten documents")
    # -----------------------------
    # Analysis
    # -----------------------------
    low_text_flag = False
    contrast_score = compute_text_contrast(gray, img_np)

    if contrast_score is None:
        st.warning("⚠️ Could not detect sufficient text for contrast analysis")
        contrast_level = "Unavailable"
        contrast_score = 0
        low_text_flag = True
    else:
        contrast_level = analyze_contrast_severity(contrast_score)

    skew_angle = detect_skew_angle(gray)
    skew_level = skew_severity(skew_angle)

    font_variance = estimate_font_variance(img_np)

    if font_variance is None:
        st.warning("⚠️ Not enough text detected for reliable font analysis")
        font_level = "Unavailable"
    else:
        font_level = font_severity(font_variance)

    line_variance = estimate_line_spacing(img_np)
    line_level = line_spacing_severity(line_variance)

    # -----------------------------
    # Summary Table
    # -----------------------------
    summary_df = pd.DataFrame([
        {
            "Metric": "Text Contrast",
            "Value": round(contrast_score, 2),
            "Severity / Interpretation": contrast_level
        },
        {
            "Metric": "Skew Angle (degrees)",
            "Value": round(skew_angle, 2),
            "Severity / Interpretation": skew_level
        },
        {
            "Metric": "Font Size Variance",
            "Value": round(font_variance, 2) if font_variance is not None else "N/A",
            "Severity / Interpretation": font_level
        },
        {
            "Metric": "Line Spacing Variance",
            "Value": round(line_variance, 2),
            "Severity / Interpretation": line_level
        }
    ])

    st.subheader("📊 Analysis Summary")
    st.dataframe(summary_df, use_container_width=True)

    # Final Decision
    # -----------------------------
# -----------------------------
# FINAL DECISION LOGIC (FIXED)
# -----------------------------

    score = 0

    # Skew (more realistic threshold)
    if abs(skew_angle) > 5 and contrast_score > 0:
        score += 3

    # Contrast
    if not low_text_flag and abs(skew_angle) > 5:
        score += 3

    # Line spacing
    if line_variance > 50:
        score += 2

    # Font variance
    if font_variance is not None and font_variance > 30:
        score += 1

    # Low text penalty (important)
    if low_text_flag:
        score += 2

    # Handwritten penalty (soft)
    if "Handwritten" in doc_type and not low_text_flag:
        score += 2


    # Final decision
    if score >= 6:
        final_decision = "REJECT"

    elif score >= 3:
        final_decision = "REVIEW"

    else:
        final_decision = "ACCEPTABLE"

    st.subheader("📌 Final Decision")

    if final_decision == "ACCEPTABLE":
        st.success("✅ ACCEPTABLE")

    elif final_decision == "REVIEW":
        st.warning("⚠️ REVIEW")

    else:
        st.error("❌ REJECT")

    st.caption(f"Decision Score: {score} (Higher = Worse Quality)")
    # -----------------------------
    # Download
    # -----------------------------
    st.download_button(
        "⬇️ Download CSV Report",
        summary_df.to_csv(index=False).encode("utf-8"),
        "visual_error_report.csv",
        "text/csv"
    )

else:
    st.info("Please upload an image to begin analysis.")
