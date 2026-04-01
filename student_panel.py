import streamlit as st
import pandas as pd
import os
import ollama
from chatbot import chatbot_response
from streamlit_option_menu import option_menu

def student_panel():

    st.title("🧑‍🎓 Student Panel")

    # -----------------------------
    # CHECK DATASET
    # -----------------------------
    if not os.path.exists("main_dataset.csv"):
        st.error("🚫 No dataset uploaded by Admin")
        st.stop()

    data = pd.read_csv("main_dataset.csv")

    for col in data.columns:
        data[col] = data[col].astype(str).str.strip()

    feedback_file = "feedback.csv"

    if os.path.exists(feedback_file):
        feedback_df = pd.read_csv(feedback_file)
    else:
        feedback_df = pd.DataFrame(columns=["Student_ID", "Feedback"])

    # -----------------------------
    # LOGIN
    # -----------------------------
    st.subheader("🔍 Login")

    sid = st.text_input("Enter Student ID")

    id_cols = [col for col in data.columns if "id" in col.lower()]

    if not sid:
        st.stop()

    if not id_cols:
        st.error("No ID column found")
        st.stop()

    id_col = id_cols[0]

    student = data[
        data[id_col].astype(str).str.strip().str.lower() == sid.strip().lower()
    ]

    if student.empty:
        st.error("Student not found ❌")
        st.stop()

    st.success(f"Welcome {sid} ✅")

    # 🔥 RESET CHAT WHEN NEW STUDENT LOGS IN
    if "last_sid" not in st.session_state:
        st.session_state["last_sid"] = sid

    if st.session_state["last_sid"] != sid:
        st.session_state.chat_history = []
        st.session_state["last_sid"] = sid

    # -----------------------------
    # SAFE COLUMN DETECTION
    # -----------------------------
    cgpa_col = next((c for c in student.columns if "cgpa" in c.lower()), None)
    attendance_col = next((c for c in student.columns if "attendance" in c.lower()), None)

    cgpa = 0
    attendance = 0

    try:
        if cgpa_col:
            cgpa = float(student[cgpa_col].values[0])
    except:
        st.warning("CGPA issue")

    try:
        if attendance_col:
            attendance = float(student[attendance_col].values[0])
    except:
        st.warning("Attendance issue")

    # -----------------------------
    # PERFORMANCE
    # -----------------------------
    def performance(cgpa, attendance):
        if attendance < 40:
            return "Poor"
        elif cgpa >= 8:
            return "Excellent"
        elif cgpa >= 6.5:
            return "Good"
        elif cgpa >= 5:
            return "Average"
        else:
            return "Poor"

    perf = performance(cgpa, attendance)

    def co_attainment(perf):
        return {"Excellent":85, "Good":70, "Average":55, "Poor":40}.get(perf, 50)

    co = co_attainment(perf)
    po = round(co * 0.9, 2)

    # -----------------------------
    # MENU
    # -----------------------------
    selected = option_menu(
        menu_title=None,
        options=["Result", "Feedback", "AI Chatbot"],
        icons=["bar-chart", "chat", "robot"],
        orientation="horizontal",
        styles={
        "container": {
            "padding": "5px",
            "background-color": "#f9f9f9"
        },
        "nav-link": {"text-align": "center","font-weight": "bold"},
        "nav-link-selected": {"background-color": "#ff4d4d","font-weight": "bold"}
    }
    )

    # -----------------------------
    # RESULT TAB
    # -----------------------------
    if selected == "Result":

        st.subheader("📌 Student Details")
        st.dataframe(student)

        if attendance_col:
            if attendance < 50:
                st.warning(f"⚠️ Low Attendance: {attendance}%")
            else:
                st.info(f"📅 Attendance: {attendance}%")
        else:
            st.warning("Attendance not available")

        st.subheader("📊 Performance")
        st.success(perf)

        st.subheader("🎯 CO & PO Attainment")
        col1, col2 = st.columns(2)
        col1.metric("CO", co)
        col2.metric("PO", po)

        st.subheader("📢 Recommendation")

        rec = []

        if perf == "Poor":
            rec += ["Improve study habits", "Attend extra classes"]

        if attendance < 60:
            rec.append("Increase attendance")

        if cgpa < 6:
            rec.append("Focus on weak subjects")

        if perf == "Excellent":
            rec.append("Keep up the good work")

        if len(rec) == 0:
            rec.append("Maintain current performance")

        st.info(", ".join(rec))

    # -----------------------------
    # FEEDBACK TAB
    # -----------------------------
    elif selected == "Feedback":

        st.subheader("💬 Submit Grievance")

        fb = st.text_area("Write your Grievance")

        if st.button("Submit Grievance"):
            if fb.strip():
                new = pd.DataFrame([{"Student_ID": sid, "Feedback": fb}])
                feedback_df = pd.concat([feedback_df, new], ignore_index=True)
                feedback_df.to_csv(feedback_file, index=False)
                st.success("Saved ✅")
            else:
                st.warning("Enter Grievance")

        

    # -----------------------------
    # 🤖 CHATBOT TAB
    # -----------------------------
    elif selected == "AI Chatbot":

        st.markdown("""
        <style>
        .chat-container {
            max-width: 800px;
            margin: auto;
        }
        .user-msg {
            background-color: #10a37f;
            color: white;
            padding: 12px;
            border-radius: 12px;
            margin: 8px 0;
            text-align: right;
            width: fit-content;
            margin-left: auto;
        }
        .bot-msg {
            background-color: #f1f1f1;
            padding: 12px;
            border-radius: 12px;
            margin: 8px 0;
            width: fit-content;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

        st.markdown("## 🤖 AI Assistant")
        st.caption("Ask anything about your performance")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Display chat
        for sender, text in st.session_state.chat_history:
            if sender == "You":
                st.markdown(f"<div class='user-msg'>🧑 {text}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='bot-msg'>🤖 {text}</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Input box (ChatGPT style)
        msg = st.chat_input("Type your question...")

        if msg:
            with st.spinner("Thinking..."):
                try:
                    response = chatbot_response(sid, msg)
                except Exception as e:
                    response = f"⚠️ Error: {str(e)}"

            st.session_state.chat_history.append(("You", msg))
            st.session_state.chat_history.append(("AI", response))

            st.rerun()

        # Optional clear button
        if st.button("🗑 Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()