# 📄 Document Quality Assessment System

An intelligent document analysis tool that evaluates the **visual quality of scanned or digital documents** using Computer Vision and OCR-based techniques.

---

## 🚀 Problem

Poor-quality documents (skewed, low contrast, inconsistent formatting) significantly reduce **OCR accuracy** and downstream data processing reliability.

Manual inspection is:

* Time-consuming
* Inconsistent
* Not scalable

---

## 💡 Solution

This project provides an automated system to assess document quality using **multi-dimensional analysis**:

* 📐 Skew Detection (alignment issues)
* 🔤 Font Consistency Analysis (formatting irregularities)
* 🎨 Text Contrast Evaluation (readability)
* 📏 Line Spacing Analysis (layout structure)
* 📄 Document Type Detection (Printed vs Handwritten)

---

## 🧠 Key Features

✔ Multi-metric document evaluation
✔ OCR-based structural analysis
✔ Normalized statistical scoring (robust to layout variations)
✔ Context-aware warnings for handwritten documents
✔ Final decision system: **Accept / Review / Reject**
✔ Exportable analysis report (CSV)
✔ Interactive UI using Streamlit

---

## 🖥️ Demo Workflow

1. Upload a document image (JPG/PNG)
2. System detects document type
3. Performs quality analysis
4. Displays structured report
5. Provides final decision
6. Allows CSV download

---

## 📊 Sample Output

| Metric        | Value  | Interpretation |
| ------------- | ------ | -------------- |
| Contrast      | 149.33 | Excellent      |
| Skew          | 0°     | Well Aligned   |
| Font Variance | 11.13  | Uniform        |
| Line Spacing  | 32.97  | Moderate       |

**Final Decision:** ✅ ACCEPTABLE

---

## ⚙️ Tech Stack

* Python
* OpenCV
* Tesseract OCR
* NumPy & Pandas
* Streamlit

---

## ▶️ How to Run

```bash
git clone https://github.com/your-username/document-quality-assessment.git
cd document-quality-assessment
pip install -r requirements.txt
streamlit run app.py
```

---

## ⚠️ Limitations

* Designed primarily for **printed documents**
* Handwritten text may produce unreliable metrics
* Heuristic thresholds (can be improved with labeled datasets)

---

## 🚀 Future Improvements

* ML-based document classification
* Confidence scoring system
* Layout-aware spacing detection
* API deployment for real-time processing

---

## 🧠 Key Insights

* Traditional document quality checks rely on raw metrics, which often fail on structured layouts (e.g., headings, bullet points).

* This system uses **normalized statistical measures (coefficient of variation)** to distinguish between natural layout variation and actual formatting issues.

* OCR-based region analysis enables extraction of structural features (font size, spacing, contrast) without relying on language understanding.

* Document type detection (Printed vs Handwritten) improves reliability by adapting interpretation logic based on OCR confidence.

* The system demonstrates how multiple weak signals (geometry, typography, clarity) can be combined into a **robust decision framework**.


⚠️ Note: This system is optimized for printed documents. Handwritten content may produce unreliable metrics.

---

## 👨‍💻 Author

Mujammil Ibrahim
