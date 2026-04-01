import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

from streamlit_option_menu import option_menu


def admin_panel():

    st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #f0f9ff, #e0f7fa); color: #1a1a1a; }
    .stTitle { color: #007acc; font-size: 38px; font-weight: bold; text-align: center; }
    div.stButton > button { background-color:#ff7f7f; color: white; font-weight: bold; border-radius: 8px; height: 40px; width: 180px; }
    div.stButton > button:hover { background-color: #fb8c00; color: #fff; }
    .stFileUploader>div>div { background-color: #b2ebf2; border-radius: 8px; padding: 10px; color: #1a1a1a; }
    .stDataFrame>div { background-color: #e1f5fe; border-radius: 8px; padding: 5px; color: #1a1a1a; }
    h2, h3, h4 { color: #0288d1; font-weight: bold; }
    div.stMetric > div { background-color: #ffd54f; border-radius: 10px; padding: 10px; color: #1a1a1a; }
    .stSuccess { background-color: #4caf50; color: white; border-radius: 8px; padding: 10px; }
    .stInfo { background-color: #29b6f6; color: white; border-radius: 8px; padding: 10px; }
    </style>
""", unsafe_allow_html=True)



    st.title("👨‍💼 Admin Dashboard")

    if "last_feedback_count" not in st.session_state:
        st.session_state["last_feedback_count"] = 0

    # -----------------------------
    # FOLDERS (AUTO CREATE)
    # -----------------------------
    DATA_FOLDER = "data_storage"
    FEEDBACK_FILE = os.path.join(DATA_FOLDER, "feedback.csv")
    REPORT_FILE = os.path.join(DATA_FOLDER, "final_report.csv")

    os.makedirs(DATA_FOLDER, exist_ok=True)
    feedback_file = "feedback.csv"

    if os.path.exists(feedback_file):
        feedback_df = pd.read_csv(feedback_file)
        current_count = len(feedback_df)
    else:
        feedback_df = pd.DataFrame(columns=["Student_ID", "Feedback"])
        current_count = 0

# 🔴 Calculate new notifications
    new_notifications = current_count - st.session_state["last_feedback_count"]
    feedback_label = "Feedback"
    if new_notifications > 0:
        feedback_label = f"Feedback 🔴 ({new_notifications})"
    default_tab = st.session_state.get("selected_tab", "Upload Dataset")
    if "Feedback" in default_tab:
        default_tab = feedback_label
    # -----------------------------
    # TOP MENU
    # -----------------------------
    

    
    tabs = [
        "Upload Dataset",
        "Previous Data",
        "Analysis",
        "Risk Students",
        feedback_label,   # dynamic label
        "Final Report",
        "Logout"
    ]

    if "selected_tab" not in st.session_state:
        st.session_state["selected_tab"] = "Upload Dataset"

    selected_tab = option_menu(
        menu_title=None,
        options=tabs,
        icons=[
            "upload", "folder", "bar-chart",
            "exclamation-triangle", "chat", "download","logout"
        ],
        orientation="horizontal",
        

        default_index = tabs.index(default_tab) if default_tab in tabs else 0,  # ✅ IMPORTANT FIX
    styles={
        "container": {
            "padding": "5px",
            "background-color": "#f9f9f9"
        },
        "nav-link": {"text-align": "center","font-weight": "bold"},
        "nav-link-selected": {"background-color": "#ff4d4d","font-weight": "bold"}
    }
    )
    # Map display back to real tab
    selected_tab = tabs[tabs.index(selected_tab)]

# Save current tab
    if selected_tab != st.session_state.get("selected_tab"):
        st.session_state["selected_tab"] = selected_tab
    # -----------------------------
    # UPLOAD DATASET
    # -----------------------------
    if selected_tab == "Upload Dataset":

        data_storages = st.file_uploader("📂 Upload CSV Dataset", type=["csv"])

        if data_storages:
            file_path = os.path.join(DATA_FOLDER, data_storages.name)

            with open(file_path, "wb") as f:
                f.write(data_storages.getbuffer())

            data = pd.read_csv(data_storages)
            data.columns = data.columns.str.strip()

            st.session_state["data"] = data.copy()
            st.session_state["data_storages_name"] = data_storages.name
            st.success("✅ File Saved Successfully")
            data.to_csv("main_dataset.csv", index=False)
        elif "data" in st.session_state:
            data = st.session_state["data"]
        else:
            st.warning("Upload dataset to continue")
            st.stop()

        st.write(f"Rows: {data.shape[0]} | Columns: {data.shape[1]}")
        st.dataframe(data.head(10))


    # -----------------------------
    # LOAD DATA (GLOBAL USE)
    # -----------------------------
    data = None

# Load from session
    if "data" in st.session_state:
        data = st.session_state["data"]

# Load from saved file
    elif os.path.exists("main_dataset.csv"):
        data = pd.read_csv("main_dataset.csv")
        st.session_state["data"] = data

# 🚨 Only block specific tabs (NOT Previous Data)
    if data is None and selected_tab not in ["Upload Dataset", "Previous Data"]:
        st.warning("⚠️ Upload dataset first")
        st.stop()

    # -----------------------------
    # PREVIOUS DATASETS
    # -----------------------------
    if selected_tab == "Previous Data":

        files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".csv")]

        if files:
            selected_file = st.selectbox("Select file", files)
            prev_path = os.path.join(DATA_FOLDER, selected_file)
            prev_df = pd.read_csv(prev_path)
            st.success(f"Viewing: {selected_file}")
            st.write(f"Rows: {prev_df.shape[0]} | Columns: {prev_df.shape[1]}")

            st.dataframe(prev_df, use_container_width=True)
            col1, col2, col3 = st.columns(3)
            # ✅ NEW: ANALYZE BUTTON
            with col1:
                if st.button("🚀 View Analysis"):
                    st.session_state["data"] = prev_df.copy()
                    st.session_state["uploaded_file_name"] = selected_file
                    st.session_state["selected_tab"] = "Analysis"
                  
                    st.success("✅ Dataset loaded for analysis!")
                    st.rerun()
            with col2:
                if st.button("🗑 Delete File"):
                    os.remove(os.path.join(DATA_FOLDER, selected_file))
                    st.rerun()
            with col3:
                st.download_button(
                    "📥 Download",
                    prev_df.to_csv(index=False),
                    file_name=selected_file
                )
        else:
            st.info("No files available")

    # -----------------------------
    # AUTO DETECT
    # -----------------------------
    cgpa_col = next((c for c in data.columns if "cgpa" in c.lower()), None)
    attendance_col = next((c for c in data.columns if "attendance" in c.lower()), None)
    behaviour_col = next((c for c in data.columns if "behaviour" in c.lower() or "behavior" in c.lower()), None)

    if cgpa_col is None:
        st.error("❌ CGPA column missing")
        return

    # -----------------------------
    # PREPARE DATA
    # -----------------------------
    model_data = pd.DataFrame()
    model_data["CGPA"] = pd.to_numeric(data[cgpa_col], errors='coerce')
    model_data["Attendance"] = pd.to_numeric(data[attendance_col], errors='coerce') if attendance_col else 75
    if behaviour_col:
        le = LabelEncoder()
        model_data["Behaviour"] = le.fit_transform(data[behaviour_col].astype(str))
    else:
        model_data["Behaviour"] = 1


    model_data = model_data.fillna(model_data.mean())

    def performance(row):
        if row["Attendance"] < 40:
            return "Poor"
        att_level = "Excellent" if row["Attendance"] >= 85 else "Good" if row["Attendance"] >= 75 else "Average" if row["Attendance"] >= 60 else "Poor"
        if row["CGPA"] >= 8 and att_level in ["Excellent","Good"]:
            return "Excellent"
        elif row["CGPA"] >= 6.5 and att_level in ["Good","Average"]:
            return "Good"
        elif row["CGPA"] >= 5:
            return "Average"
        else:
            return "Poor"

    model_data["Performance"] = model_data.apply(performance, axis=1)

        # -----------------------------
    # CO, PO, RECOMMENDATION
    # -----------------------------
    def co_attainment(perf):
        return {"Excellent":85, "Good":70, "Average":55, "Poor":40}.get(perf, 50)

    model_data["CO"] = model_data["Performance"].apply(co_attainment)
    model_data["PO"] = model_data["CO"].apply(lambda x: round(x * 0.9, 2))

    def recommend(row):
        rec = []
        if row["Performance"] == "Poor":
            rec += ["Improve study habits","Attend extra classes"]
        if row["Attendance"] < 60:
            rec.append("Increase attendance")
        if row["CGPA"] < 6:
            rec.append("Focus on weak subjects")
        if row["Performance"] == "Excellent":
            rec.append("Keep up the good work")
        if len(rec) == 0:
            rec.append("Maintain current performance")
        return ", ".join(rec)

    model_data["Recommendation"] = model_data.apply(recommend, axis=1)
    # SAVE FOR CHATBOT
    
    # -----------------------------
# ADD STUDENT ID (GLOBAL FIX)
# -----------------------------
    id_col = next(
        (c for c in data.columns if "id" in c.lower() or "student" in c.lower()),
        None
    )

    model_data_with_id = model_data.copy()

    if id_col:
        model_data_with_id["Student_ID"] = data[id_col].astype(str)
    else:
        model_data_with_id["Student_ID"] = ["STU_" + str(i+1) for i in range(len(data))]


    # -----------------------------
    # MODEL TRAINING
    # -----------------------------
    X = model_data[["CGPA","Attendance","Behaviour"]]
    y = model_data["Performance"]

    X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2,random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    lr = LogisticRegression(max_iter=2000)
    dt = DecisionTreeClassifier()
    rf = RandomForestClassifier()

    lr.fit(X_train_scaled, y_train)
    dt.fit(X_train, y_train)
    rf.fit(X_train, y_train)

    acc_lr = accuracy_score(y_test, lr.predict(X_test_scaled))
    acc_dt = accuracy_score(y_test, dt.predict(X_test))
    acc_rf = accuracy_score(y_test, rf.predict(X_test))


    # -----------------------------
    # ANALYSIS
    # -----------------------------
    if selected_tab == "Analysis":

        acc_df = pd.DataFrame({
            "Model": ["Logistic", "Decision Tree", "Random Forest"],
            "Accuracy": [acc_lr, acc_dt, acc_rf]
        })

        st.dataframe(acc_df)
        st.bar_chart(acc_df.set_index("Model"))

       
        # -----------------------------
    # BEST MODEL
    # -----------------------------
        best_name = "Random Forest" if acc_rf >= acc_lr and acc_rf >= acc_dt else "Decision Tree" if acc_dt>=acc_lr else "Logistic Regression"
        st.success(f"🏆 Best Model: {best_name}")
        st.info(f"Accuracy: {round(max(acc_lr, acc_dt, acc_rf)*100,2)}%")
     
        # -----------------------------
    # CONFUSION MATRIX
    # -----------------------------
        st.subheader("🧩 Confusion Matrix")

        labels = sorted(list(set(y)))
        full_pred = rf.predict(X) if best_name=="Random Forest" else dt.predict(X) if best_name=="Decision Tree" else lr.predict(scaler.transform(X))

        cm = confusion_matrix(y, full_pred, labels=labels)
        fig, ax = plt.subplots(figsize=(4, 3))
        sns.heatmap(cm, annot=True, fmt="d", cmap="YlGnBu",xticklabels=labels, yticklabels=labels, ax=ax, annot_kws={"size": 8})
        ax.set_xlabel("Predicted")
        ax.set_ylabel("Actual")
        ax.tick_params(axis='both', labelsize=7)
        st.pyplot(fig, use_container_width=False)

            # -----------------------------
    # PERFORMANCE DISTRIBUTION
    # -----------------------------
        st.subheader("📊 Performance Distribution")
        perf_counts = model_data["Performance"].value_counts()

        col1,col2,col3,col4 = st.columns(4)
        col1.metric("🟢 Excellent",perf_counts.get("Excellent",0))
        col2.metric("🔵 Good",perf_counts.get("Good",0))
        col3.metric("🟡 Average",perf_counts.get("Average",0))
        col4.metric("🔴 Poor",perf_counts.get("Poor",0))


    # -----------------------------
    # RISK STUDENTS
    # -----------------------------
    if selected_tab == "Risk Students":
        
        risk = model_data_with_id[model_data_with_id["Performance"] == "Poor"]

        st.write(f"⚠️ Risk Students: {len(risk)}")

        if not risk.empty:
            st.dataframe(
                risk[["Student_ID","CGPA","Attendance","Behaviour","Performance"]],
                use_container_width=True
            )
        else:
            st.success("No risk students")
        if len(risk) > 0:
            st.error(f"⚠️ {len(risk)} students are at risk!")
                # -----------------------------
        # 🚨 SMART ALERT PANEL
        # -----------------------------
        st.markdown("## 🚨 Alerts Summary")

        # Thresholds (you can change based on dataset)
        LOW_MARKS = 5      # CGPA 기준 (since you use CGPA not marks)
        LOW_ATTENDANCE = 75

        # Conditions
        low_marks_df = model_data_with_id[model_data_with_id["CGPA"] < LOW_MARKS]
        low_attendance_df = model_data_with_id[model_data_with_id["Attendance"] < LOW_ATTENDANCE]
        high_risk_df = model_data_with_id[
            (model_data_with_id["CGPA"] < LOW_MARKS) &
            (model_data_with_id["Attendance"] < LOW_ATTENDANCE)
        ]

        # Counts
        low_marks_count = len(low_marks_df)
        low_attendance_count = len(low_attendance_df)
        high_risk_count = len(high_risk_df)

        # UI Cards
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div style="background-color:#ffe6e6;padding:20px;border-radius:12px;text-align:center">
                <h3>🔴 Low Marks</h3>
                <h1>{low_marks_count}</h1>
                <p>CGPA below {LOW_MARKS}</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div style="background-color:#fff4e6;padding:20px;border-radius:12px;text-align:center">
                <h3>⚠️ Low Attendance</h3>
                <h1>{low_attendance_count}</h1>
                <p>Below {LOW_ATTENDANCE}%</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div style="background-color:#ffe6cc;padding:20px;border-radius:12px;text-align:center">
                <h3>🔥 High Risk</h3>
                <h1>{high_risk_count}</h1>
                <p>Both Conditions</p>
            </div>
            """, unsafe_allow_html=True)

        # -----------------------------
        # 📊 Expandable Student Lists
        # -----------------------------
        with st.expander("🔴 View Low Marks Students"):
            st.dataframe(low_marks_df[["Student_ID","CGPA","Attendance","Performance"]])

        with st.expander("⚠️ View Low Attendance Students"):
            st.dataframe(low_attendance_df[["Student_ID","CGPA","Attendance","Performance"]])

        with st.expander("🔥 View High Risk Students"):
            st.dataframe(high_risk_df[["Student_ID","CGPA","Attendance","Performance"]])


    # -----------------------------
    # FEEDBACK SAVE + VIEW
    # -----------------------------
    st.session_state["last_feedback_count"] = current_count
    if "Feedback" in selected_tab:
        st.subheader("💬 Student Feedback")

        feedback_file = "feedback.csv"

        if os.path.exists(feedback_file):
            feedback_df = pd.read_csv(feedback_file)
        else:
            feedback_df = pd.DataFrame(columns=["Student_ID", "Feedback"])

    # ✅ SHOW ALERT IF NEW FEEDBACK ARRIVES
        current_count = len(feedback_df)

        if current_count > st.session_state["last_feedback_count"]:
            st.toast("🔔 New Feedback Received!", icon="🚨")
            st.session_state["last_feedback_count"] = current_count

    # DISPLAY FEEDBACK
        if not feedback_df.empty:
            st.dataframe(
                feedback_df.groupby("Student_ID")["Feedback"]
                .apply(lambda x: ", ".join(x)).reset_index(),
                use_container_width=True
            )

        # SHOW LATEST MESSAGE
            latest = feedback_df.iloc[-1]
            st.success(f"🆕 Latest Feedback from {latest['Student_ID']}")
        else:
            st.info("No feedback submitted yet.")


    # -----------------------------
# FINAL REPORT (ADVANCED)
# -----------------------------
    if selected_tab == "Final Report":
        st.markdown("## 📄 Advanced Student Report System")

        final_report = model_data_with_id.copy()

    # -----------------------------
    # 📊 METRICS DASHBOARD
    # -----------------------------
        col1, col2, col3 = st.columns(3)

        col1.metric("📊 Avg CGPA", round(final_report["CGPA"].mean(), 2))
        col2.metric("📅 Avg Attendance", round(final_report["Attendance"].mean(), 1))
        col3.metric("🎯 Total Students", len(final_report))

    # -----------------------------
    # 📊 GRAPHS
    # -----------------------------
        st.subheader("📊 Performance Insights")

        col1, col2 = st.columns(2)

        with col1:
            fig1, ax1 = plt.subplots()
            final_report["Performance"].value_counts().plot(
                kind="pie", autopct="%1.1f%%", ax=ax1
            )
            ax1.set_ylabel("")
            st.pyplot(fig1)

        with col2:
            fig2, ax2 = plt.subplots()
            sns.histplot(final_report["CGPA"], bins=10, kde=True, ax=ax2)
            st.pyplot(fig2)

    # -----------------------------
    # 🚨 ALERTS
    # -----------------------------
        st.subheader("🚨 Smart Alerts")

        low_cgpa = final_report[final_report["CGPA"] < 5]
        low_att = final_report[final_report["Attendance"] < 75]

        if not low_cgpa.empty:
            st.error(f"❌ {len(low_cgpa)} students have low CGPA")

        if not low_att.empty:
            st.warning(f"⚠️ {len(low_att)} students have low attendance")

        if low_cgpa.empty and low_att.empty:
            st.success("✅ No critical alerts")

    # -----------------------------
    # 💡 AI SUGGESTIONS
    # -----------------------------
        st.subheader("💡 Suggestions")

        def generate_suggestion(row):
            if row["Performance"] == "Poor":
                return "Focus on basics + attend remedial classes"
            elif row["Performance"] == "Average":
                return "Practice regularly and improve weak areas"
            elif row["Performance"] == "Good":
                return "Keep consistency and aim higher"
            else:
                return "Excellent work! Try advanced learning"

        final_report["Suggestions"] = final_report.apply(generate_suggestion, axis=1)

        st.dataframe(final_report[[
            "Student_ID","CGPA","Attendance","Performance","Suggestions"
        ]])

    # 🏆 TOP PERFORMER (SAFE VERSION)

        if "CGPA" in final_report.columns and not final_report["CGPA"].isna().all():
            top_index = final_report["CGPA"].idxmax()
            top_student = final_report.loc[top_index]

            student_id = top_student.get("Student_ID", "Unknown")

            st.success(
                f"🏆 Top Performer: {student_id} (CGPA: {round(top_student['CGPA'], 2)})"
            )

        else:
            st.warning("⚠️ Cannot determine top performer (CGPA missing)")

    # -----------------------------
    # 📄 SAVE CSV
    # -----------------------------
        final_report.to_csv(REPORT_FILE, index=False)

        st.download_button(
            "📥 Download CSV Report",
            final_report.to_csv(index=False),
            file_name="final_report.csv"
        )


         # -----------------------------
# LOGOUT FUNCTION
# -----------------------------
    if selected_tab == "Logout":
        st.session_state["admin_logged_in"] = False
        st.session_state["logout_msg"] = "👋 Logged out successfully"

    # Reset only needed things
        if "data" in st.session_state:
            del st.session_state["data"]

        st.rerun()