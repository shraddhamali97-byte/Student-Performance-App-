# =========================================================
# IMPORT LIBRARIES
# =========================================================

import streamlit as st
import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import sqlite3

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.pagesizes import letter

from datetime import datetime

# =========================================================
# DATABASE CONNECTION
# =========================================================

conn = sqlite3.connect(
    'student_database.db',
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    predicted_sgpa REAL,
    prediction_date TEXT
)
""")
conn.commit()
# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(

    page_title="Student Performance Dashboard",
    page_icon="🎓",
    layout="wide"

)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

/* Main Background */

.stApp {

    background: linear-gradient(
        to right,
        #F8FAFC,
        #E0F2FE
    );

}

/* Sidebar */

[data-testid="stSidebar"] {

    background: linear-gradient(
        to bottom,
        #F0F9FF,
        #DBEAFE
    );

    border-right: 2px solid #BFDBFE;
}

/* Sidebar Text */

.sidebar-title {

    text-align:center;
    color:#1E3A8A;
    font-size:28px;
    font-weight:bold;

}

.sidebar-text {

    color:#111827;
    text-align:center;
    font-size:15px;
    font-weight:500;

}

/* Cards */

.metric-card {

    background:white;
    padding:25px;
    border-radius:20px;
    box-shadow:0px 4px 15px rgba(0,0,0,0.1);
    text-align:center;
    transition:0.3s;

}

.metric-card:hover {

    transform:scale(1.03);

}

/* Buttons */

.stButton>button {

    background: linear-gradient(
        to right,
        #2563EB,
        #1D4ED8
    );

    color:white;
    border-radius:12px;
    height:3em;
    width:100%;
    font-size:18px;
    border:none;
    font-weight:bold;

}

/* Metrics */

[data-testid="metric-container"] {

    background:white;
    border-radius:15px;
    padding:15px;
    box-shadow:0px 4px 10px rgba(0,0,0,0.08);

}

</style>
""", unsafe_allow_html=True)

# =========================================================
# LOAD MODEL
# =========================================================

model = joblib.load(
    "student_performance_model.pkl"
)

# =========================================================
# FEATURE NAMES
# =========================================================

feature_names = [

    'Semester',
    'Internal_Marks',
    'External_Marks',
    'Assignment_Score',
    'Attendance_Percentage',
    'Study_Hours_Per_Day',
    'Assignment_Submission_Rate',
    'Notes_Completion_Rate',
    'Core_Subject_Avg',
    'Technical_Subject_Avg',
    'Practical_Score',
    'Project_Score',
    'Communication_Score',
    'Gender',
    'Branch'

]

# =========================================================
# PDF REPORT FUNCTION
# =========================================================

def create_pdf(student_name, prediction):

    pdf_file = "student_report.pdf"

    c = canvas.Canvas(
        pdf_file,
        pagesize=letter
    )

    width, height = letter

    current_date = datetime.now().strftime(
        "%d-%m-%Y %H:%M"
    )

    # =====================================================
    # TITLE
    # =====================================================

    c.setFont(
        "Helvetica-Bold",
        24
    )

    c.setFillColor(
        colors.HexColor("#1E3A8A")
    )

    c.drawString(
        120,
        height - 80,
        "Student Performance Report"
    )

    # =====================================================
    # DATE
    # =====================================================

    c.setFont(
        "Helvetica",
        12
    )

    c.setFillColor(colors.black)

    c.drawString(
        50,
        height - 120,
        f"Generated On: {current_date}"
    )

    # =====================================================
    # PERFORMANCE LEVEL
    # =====================================================

    if prediction >= 9:

        performance = "Excellent"

    elif prediction >= 7:

        performance = "Good"

    elif prediction >= 5:

        performance = "Average"

    else:

        performance = "Needs Improvement"

    # =====================================================
    # TABLE
    # =====================================================

    data = [

        ["Student Name", student_name],

        ["Predicted SGPA", f"{prediction:.2f}"],

        ["Performance Level", performance]

    ]

    table = Table(
        data,
        colWidths=[220, 220]
    )

    style = TableStyle([

        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2563EB")),

        ('TEXTCOLOR', (0,0), (-1,0), colors.white),

        ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),

        ('GRID', (0,0), (-1,-1), 1, colors.grey),

        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),

        ('FONTSIZE', (0,0), (-1,-1), 12),

        ('BOTTOMPADDING', (0,0), (-1,0), 10)

    ])

    table.setStyle(style)

    table.wrapOn(c, width, height)

    table.drawOn(
        c,
        80,
        height - 250
    )

    # =====================================================
    # AI SUGGESTIONS
    # =====================================================

    c.setFont(
        "Helvetica-Bold",
        18
    )

    c.setFillColor(
        colors.HexColor("#1E3A8A")
    )

    c.drawString(
        50,
        height - 340,
        "AI Suggestions"
    )

    c.setFont(
        "Helvetica",
        12
    )

    c.setFillColor(colors.black)

    if prediction < 5:

        suggestions = [

            "Increase study hours daily",
            "Improve attendance percentage",
            "Focus on assignments and projects",
            "Take help from teachers"

        ]

    elif prediction < 8:

        suggestions = [

            "Maintain consistent study habits",
            "Focus on practical learning",
            "Improve weak subjects"

        ]

    else:

        suggestions = [

            "Excellent performance maintained",
            "Participate in advanced activities",
            "Continue smart learning"

        ]

    y = height - 380

    for suggestion in suggestions:

        c.drawString(
            70,
            y,
            f"• {suggestion}"
        )

        y -= 25

    # =====================================================
    # FOOTER
    # =====================================================

    c.setFillColor(colors.grey)

    c.line(
        50,
        80,
        width - 50,
        80
    )

    c.setFont(
        "Helvetica-Oblique",
        10
    )

    c.drawString(
        50,
        60,
        "Generated by AI Student Performance Prediction System"
    )

    c.drawRightString(
        width - 50,
        60,
        "Developed by Shraddha Mali"
    )

    c.save()



# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.image(
    "https://cdn-icons-png.flaticon.com/512/3135/3135755.png",
    width=120
)

st.sidebar.markdown("""

<div class='sidebar-title'>
🎓 AI Dashboard
</div>

""", unsafe_allow_html=True)

menu = st.sidebar.radio(

    "📌 Navigation",

    [

        "🏠 Dashboard Home",
        "🤖 AI Prediction",
        "📊 Analytics Dashboard",
        "📂 Bulk CSV Prediction",
        "📁 Dataset Explorer",
        "🗂 Prediction History",
        "ℹ️ About Project"

    ]

)

# =========================================================
# HOME PAGE
# =========================================================

if menu == "🏠 Dashboard Home":

    st.markdown("""

    <h1 style='text-align:center; color:#1E3A8A;'>

    🎓 Student Performance Prediction System

    </h1>

    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""

    <div style="
        background: linear-gradient(to right, #2563EB, #1E40AF);
        padding:40px;
        border-radius:25px;
        color:white;
        text-align:center;
        box-shadow:0px 6px 20px rgba(0,0,0,0.2);
    ">

    <h1>🚀 AI-Powered Academic Analytics</h1>

    <p style='font-size:18px;'>

    Predict student academic performance using
    Machine Learning and advanced analytics.

    </p>

    </div>

    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown("""

        <div class="metric-card">

        <img src="https://cdn-icons-png.flaticon.com/512/2103/2103633.png"
        width="80">

        <h3 style='color:#1E3A8A;'>
        🤖 Machine Learning
        </h3>

        <p>AI-based SGPA prediction system.</p>

        </div>

        """, unsafe_allow_html=True)

    with col2:

        st.markdown("""

        <div class="metric-card">

        <img src="https://cdn-icons-png.flaticon.com/512/4149/4149675.png"
        width="80">

        <h3 style='color:#1E3A8A;'>
        📊 Analytics
        </h3>

        <p>Interactive dashboards and insights.</p>

        </div>

        """, unsafe_allow_html=True)

    with col3:

        st.markdown("""

        <div class="metric-card">

        <img src="https://cdn-icons-png.flaticon.com/512/2721/2721297.png"
        width="80">

        <h3 style='color:#1E3A8A;'>
        ☁️ Cloud Ready
        </h3>

        <p>Deployable on Streamlit Cloud and AWS.</p>

        </div>

        """, unsafe_allow_html=True)

# =========================================================
# PREDICTION PAGE
# =========================================================

elif menu == "🤖 AI Prediction":

    st.title("📊 Student Performance Prediction")

    student_name = st.text_input(
        "👨‍🎓 Student Name"
    )

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:

        semester = st.slider("📘 Semester", 1, 8)
        internal_marks = st.slider("📝 Internal Marks", 0, 30)
        external_marks = st.slider("📚 External Marks", 0, 70)
        assignment_score = st.slider("📑 Assignment Score", 0, 20)
        attendance_percentage = st.slider("📅 Attendance %", 0, 100)

    with col2:

        study_hours = st.slider("⏰ Study Hours", 0, 12)
        assignment_rate = st.slider("📂 Assignment Submission Rate", 0, 100)
        notes_completion = st.slider("📒 Notes Completion Rate", 0, 100)
        core_avg = st.slider("📖 Core Subject Average", 0, 100)
        technical_avg = st.slider("💻 Technical Subject Average", 0, 100)

    with col3:

        practical_score = st.slider("🔬 Practical Score", 0, 100)
        project_score = st.slider("📊 Project Score", 0, 100)
        communication_score = st.slider("🗣 Communication Score", 0, 100)

        gender = st.selectbox(
            "👩 Gender",
            ["Female", "Male"]
        )

        branch = st.selectbox(
            "🏫 Branch",
            ["CSE", "IT", "ENTC", "Mechanical", "Civil", "AI&DS"]
        )

    # =====================================================
    # ENCODING
    # =====================================================

    gender = 1 if gender == "Male" else 0

    branch_mapping = {

        "CSE": 0,
        "IT": 1,
        "ENTC": 2,
        "Mechanical": 3,
        "Civil": 4,
        "AI&DS": 5

    }

    branch = branch_mapping[branch]

    # =====================================================
    # PREDICTION BUTTON
    # =====================================================

    if st.button("🔍 Predict Performance"):

        input_data = np.array([[

            semester,
            internal_marks,
            external_marks,
            assignment_score,
            attendance_percentage,
            study_hours,
            assignment_rate,
            notes_completion,
            core_avg,
            technical_avg,
            practical_score,
            project_score,
            communication_score,
            gender,
            branch

        ]])

        # ✅ ADD THIS HERE (IMPORTANT)
        if len(input_data[0]) != len(feature_names):
            st.error("Feature mismatch with model input!")
            st.stop()

        prediction = model.predict(input_data)[0]

        current_date = datetime.now().isoformat()

        cursor.execute("""
        INSERT INTO predictions (
            student_name,
            predicted_sgpa,
            prediction_date
        )
        VALUES (?, ?, ?)
        """, (student_name, prediction, current_date))

        conn.commit()

        # =================================================
        # STORE SESSION VALUES
        # =================================================

        st.session_state.prediction_value = prediction
        st.session_state.study_hours = study_hours
        st.session_state.attendance = attendance_percentage
        st.session_state.internal_marks = internal_marks
        st.session_state.external_marks = external_marks

        # =================================================
        # PDF CREATION
        # =================================================

        create_pdf(
            student_name,
            prediction
        )

        # =================================================
        # RESULT
        # =================================================

        st.success(
            f"🎯 Predicted SGPA: {prediction:.2f}"
        )

        if prediction >= 9:

            st.success("🌟 Excellent Performance")

            st.markdown("""

            <div style='text-align:center; font-size:60px;'>

            ⭐ ⭐ ⭐ ⭐ ⭐

            </div>

            """, unsafe_allow_html=True)

        elif prediction >= 7:

            st.info("👍 Good Performance")

        elif prediction >= 5:

            st.warning("⚠️ Average Performance")

        else:

            st.error("❌ Needs Improvement")

        # =================================================
        # PROGRESS BAR
        # =================================================

        st.subheader("📈 Performance Meter")

        st.progress(
            int(prediction * 10)
        )

        # =================================================
        # FEATURE IMPORTANCE
        # =================================================

        st.subheader("📊 Important Factors")

        if hasattr(model, "feature_importances_"):

            importance = model.feature_importances_

            imp_df = pd.DataFrame({

                'Feature': feature_names,
                'Importance': importance

            })

            imp_df = imp_df.sort_values(
                by='Importance',
                ascending=False
            )

            st.bar_chart(
                imp_df.set_index('Feature')
            )

        # =================================================
        # DOWNLOAD PDF
        # =================================================

        with open(
            "student_report.pdf",
            "rb"
        ) as pdf_file:

            st.download_button(

                label="📥 Download PDF Report",

                data=pdf_file,

                file_name="student_report.pdf",

                mime="application/pdf"

            )

# =========================================================
# ANALYTICS DASHBOARD
# =========================================================

elif menu == "📊 Analytics Dashboard":

    st.title("📈 Advanced Analytics Dashboard")

    st.markdown("---")

    if 'prediction_value' in st.session_state:

        prediction = st.session_state.prediction_value

        study_hours = st.session_state.study_hours
        attendance = st.session_state.attendance
        internal_marks = st.session_state.internal_marks
        external_marks = st.session_state.external_marks

        # =================================================
        # METRICS
        # =================================================

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "🎯 Predicted SGPA",
                f"{prediction:.2f}"
            )

        with col2:
            st.metric(
                "📚 Study Hours",
                f"{study_hours} hrs"
            )

        with col3:
            st.metric(
                "📅 Attendance",
                f"{attendance}%"
            )

        with col4:
            st.metric(
                "📝 Internal Marks",
                internal_marks
            )

        st.markdown("---")

        # =================================================
        # BAR CHART
        # =================================================

        st.subheader("📊 Academic Performance Analysis")

        labels = [

            "Study Hours",
            "Attendance",
            "Internal",
            "External"

        ]

        values = [

            study_hours,
            attendance / 10,
            internal_marks,
            external_marks / 5

        ]

        fig1, ax1 = plt.subplots(figsize=(8,5))

        ax1.bar(labels, values)

        ax1.set_title("Academic Analysis")

        st.pyplot(fig1)

        # =================================================
        # PIE CHART
        # =================================================

        st.subheader("🥧 Performance Distribution")

        fig2, ax2 = plt.subplots(figsize=(6,6))

        ax2.pie(

            [prediction, 10-prediction],

            labels=["Achieved", "Remaining"],

            autopct='%1.1f%%'

        )

        st.pyplot(fig2)

        st.subheader("📊 Live Comparison View")

        comparison_df = pd.DataFrame({
            "Metrics": ["Study Hours", "Attendance", "Internal", "External", "SGPA"],
            "Value": [
                study_hours,
                attendance,
                internal_marks,
                external_marks,
                prediction
            ]
        })

        st.bar_chart(comparison_df.set_index("Metrics"))

        # =================================================
        # RADAR CHART
        # =================================================

        st.subheader("🕸 Radar Chart Analysis")

        radar_labels = np.array([

            "Study",
            "Attendance",
            "Internal",
            "External",
            "SGPA"

        ])

        stats = [

            study_hours,
            attendance/10,
            internal_marks/3,
            external_marks/7,
            prediction

        ]

        angles = np.linspace(
            0,
            2*np.pi,
            len(radar_labels),
            endpoint=False
        )

        stats = np.concatenate((stats, [stats[0]]))
        angles = np.concatenate((angles, [angles[0]]))

        fig3 = plt.figure(figsize=(6,6))

        ax = fig3.add_subplot(
            polar=True
        )

        ax.plot(angles, stats)
        ax.fill(angles, stats, alpha=0.25)

        ax.set_thetagrids(
            angles[:-1] * 180/np.pi,
            radar_labels
        )

        st.pyplot(fig3)

    else:

        st.warning(
            "⚠️ Please make prediction first."
        )

# =========================================================
# BULK CSV PREDICTION
# =========================================================

elif menu == "📂 Bulk CSV Prediction":

    st.title("📂 Bulk CSV Prediction")

    uploaded_file = st.file_uploader(
        "Upload CSV File",
        type=["csv"]
    )

    if uploaded_file is not None:

        df = pd.read_csv(uploaded_file)

        st.subheader("📄 Uploaded Dataset")

        st.dataframe(df.head())

        try:

            if 'Gender' in df.columns:

                df['Gender'] = df['Gender'].map({

                    'Male': 1,
                    'Female': 0

                })

            if 'Branch' in df.columns:

                branch_mapping = {

                    "CSE": 0,
                    "IT": 1,
                    "ENTC": 2,
                    "Mechanical": 3,
                    "Civil": 4,
                    "AI&DS": 5

                }

                df['Branch'] = df['Branch'].map(
                    branch_mapping
                )

            df_model = df[feature_names]

            predictions = model.predict(df_model)

            df["Predicted_SGPA"] = predictions

            st.subheader("🎯 Prediction Results")

            st.dataframe(df)

            csv = df.to_csv(
                index=False
            ).encode('utf-8')

            st.download_button(

                "⬇️ Download Prediction Results",

                csv,

                "student_predictions.csv",

                "text/csv"

            )

        except Exception as e:

            st.error(f"Error: {e}")

# =========================================================
# DATASET EXPLORER
# =========================================================

elif menu == "📁 Dataset Explorer":

    st.title("📁 Dataset Explorer")

    df = pd.read_csv(
        "final_fixed_realistic_student_dataset.csv"
    )

    st.dataframe(df.head())

    st.subheader("📊 Dataset Statistics")

    st.write(df.describe())

# =========================================================
# PREDICTION HISTORY
# =========================================================

elif menu == "🗂 Prediction History":

    st.title("🗂 Prediction History")

    history_df = pd.read_sql_query(
        "SELECT * FROM predictions",
        conn
    )

    # convert date
    history_df["prediction_date"] = pd.to_datetime(
    history_df["prediction_date"],
    errors="coerce",
    format="ISO8601"
)
    history_df = history_df.dropna(subset=["prediction_date"])

    # =========================
    # SEARCH BY NAME
    # =========================
    search_name = st.text_input("🔎 Search Student Name")

    if search_name:
        history_df = history_df[
            history_df["student_name"].str.contains(search_name, case=False)
        ]

    # =========================
    # DATE FILTER
    # =========================
    st.subheader("📅 Filter by Date")

    date_filter = st.date_input("Select Date")

    if st.button("Apply Filter"):
        history_df = history_df[
            history_df["prediction_date"].dt.date == date_filter
        ]

    st.dataframe(history_df)

    # =========================
    # DOWNLOAD HISTORY
    # =========================
    csv = history_df.to_csv(index=False).encode('utf-8')

    st.download_button(
        "⬇️ Download History CSV",
        csv,
        "history.csv",
        "text/csv"
    )
# =========================================================
# ABOUT PAGE
# =========================================================

elif menu == "ℹ️ About Project":

    st.title("ℹ️ About Project")

    st.markdown("""

    ## 🎓 Student Performance Prediction System

    This project predicts student SGPA
    using Machine Learning and analytics.

    ### 🔧 Technologies Used

    - Python
    - Streamlit
    - Scikit-learn
    - SQLite
    - Pandas
    - Matplotlib
    - ReportLab

    ### 🌟 Features

    - AI Prediction
    - Advanced Analytics
    - Radar Chart
    - PDF Report
    - Bulk CSV Prediction
    - Prediction History
    - Database Integration

    ### 👩‍💻 Developed By

    Shraddha Mali

    """)   