import streamlit as st
import pandas as pd
import sqlite3
import datetime
import plotly.express as px
import plotly.graph_objects as go
import openai
from dateutil.relativedelta import relativedelta

# Database setup
def init_db():
    conn = sqlite3.connect('brainboost.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    branch TEXT,
                    course TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS study_sessions (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    date TEXT,
                    hours REAL,
                    topic TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )''')
    conn.commit()
    conn.close()

def get_user_id(name, branch, course):
    conn = sqlite3.connect('brainboost.db')
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE name=? AND branch=? AND course=?", (name, branch, course))
    result = c.fetchone()
    if result:
        user_id = result[0]
    else:
        c.execute("INSERT INTO users (name, branch, course) VALUES (?, ?, ?)", (name, branch, course))
        user_id = c.lastrowid
        conn.commit()
    conn.close()
    return user_id

def save_session(user_id, date, hours, topic):
    conn = sqlite3.connect('brainboost.db')
    c = conn.cursor()
    c.execute("INSERT INTO study_sessions (user_id, date, hours, topic) VALUES (?, ?, ?, ?)", (user_id, date, hours, topic))
    conn.commit()
    conn.close()

def get_sessions(user_id, months=6):
    conn = sqlite3.connect('brainboost.db')
    start_date = (datetime.datetime.now() - relativedelta(months=months)).strftime('%Y-%m-%d')
    df = pd.read_sql_query("SELECT * FROM study_sessions WHERE user_id=? AND date >= ?", conn, params=(user_id, start_date))
    conn.close()
    df['date'] = pd.to_datetime(df['date'])
    return df

def calculate_streak(df):
    if df.empty:
        return 0
    df = df.sort_values('date')
    df['date_only'] = df['date'].dt.date
    unique_dates = df['date_only'].drop_duplicates().sort_values()
    streak = 0
    max_streak = 0
    prev_date = None
    for date in unique_dates:
        if prev_date is None or (date - prev_date).days == 1:
            streak += 1
        else:
            max_streak = max(max_streak, streak)
            streak = 1
        prev_date = date
    max_streak = max(max_streak, streak)
    return max_streak

def calculate_consistency(df):
    if df.empty:
        return 0
    total_days = (df['date'].max() - df['date'].min()).days + 1
    study_days = df['date'].dt.date.nunique()
    return study_days / total_days * 100 if total_days > 0 else 0

# AI functions
def generate_revision_questions(topic, api_key):
    if not api_key:
        return ["Please set your API key in settings (use 'ollama' for local setup)."]
    openai.api_key = api_key
    openai.base_url = "http://localhost:11434/v1"
    try:
        response = openai.chat.completions.create(
            model="llama3.2",
            messages=[
                {"role": "system", "content": "You are a helpful tutor."},
                {"role": "user", "content": f"Generate 5 revision questions on the topic: {topic}"}
            ]
        )
        questions = response.choices[0].message.content.strip().split('\n')
        return questions
    except Exception as e:
        return [f"Error: {str(e)}"]

def generate_practice_questions(topic, api_key):
    if not api_key:
        return ["Please set your API key in settings (use 'ollama' for local setup)."]
    openai.api_key = api_key
    openai.base_url = "http://localhost:11434/v1"
    try:
        response = openai.chat.completions.create(
            model="llama3.2",
            messages=[
                {"role": "system", "content": "You are a helpful tutor."},
                {"role": "user", "content": f"Generate 5 practice questions with answers on the topic: {topic}"}
            ]
        )
        content = response.choices[0].message.content.strip()
        return content.split('\n\n')
    except Exception as e:
        return [f"Error: {str(e)}"]

# Main app
def main():
    st.set_page_config(page_title="BrainBoost - Smart Study Analyser", page_icon="🧠")
    st.title("🧠 BrainBoost - Smart Study Analyser")

    init_db()

    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Login", "Dashboard", "Log Session", "Revision", "Practice", "Settings"])

    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""

    if page == "Login":
        st.header("User Login")
        name = st.text_input("Name")
        branch = st.text_input("Branch")
        course = st.text_input("Course")
        if st.button("Login"):
            if name and branch and course:
                user_id = get_user_id(name, branch, course)
                st.session_state.user_id = user_id
                st.success("Logged in successfully!")
            else:
                st.error("Please fill all fields.")

    elif page == "Dashboard":
        if st.session_state.user_id is None:
            st.error("Please login first.")
        else:
            st.header("Dashboard")
            df = get_sessions(st.session_state.user_id)
            if df.empty:
                st.info("No study sessions logged yet.")
            else:
                # Visualizations
                st.subheader("Study Hours Over Time")
                df_monthly = df.groupby(df['date'].dt.to_period('M'))['hours'].sum().reset_index()
                df_monthly['date'] = df_monthly['date'].dt.to_timestamp()
                fig = px.line(df_monthly, x='date', y='hours', title="Monthly Study Hours")
                st.plotly_chart(fig)

                st.subheader("Topics Studied")
                topic_counts = df['topic'].value_counts()
                fig2 = px.bar(topic_counts, title="Study Topics")
                st.plotly_chart(fig2)

                # Metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Hours", f"{df['hours'].sum():.1f}")
                with col2:
                    streak = calculate_streak(df)
                    st.metric("Current Streak", f"{streak} days")
                with col3:
                    consistency = calculate_consistency(df)
                    st.metric("Consistency", f"{consistency:.1f}%")

    elif page == "Log Session":
        if st.session_state.user_id is None:
            st.error("Please login first.")
        else:
            st.header("Log Study Session")
            date = st.date_input("Date", datetime.date.today())
            hours = st.number_input("Hours Studied", min_value=0.0, step=0.5)
            topic = st.text_input("Topic")
            if st.button("Log Session"):
                if hours > 0 and topic:
                    save_session(st.session_state.user_id, date.strftime('%Y-%m-%d'), hours, topic)
                    st.success("Session logged!")
                else:
                    st.error("Please enter hours and topic.")

    elif page == "Revision":
        if st.session_state.user_id is None:
            st.error("Please login first.")
        else:
            st.header("Revision Helper")
            topic = st.text_input("Enter topic for revision")
            if st.button("Generate Questions"):
                if topic:
                    questions = generate_revision_questions(topic, st.session_state.api_key)
                    for q in questions:
                        st.write(q)
                else:
                    st.error("Please enter a topic.")

    elif page == "Practice":
        if st.session_state.user_id is None:
            st.error("Please login first.")
        else:
            st.header("Practice Helper")
            topic = st.text_input("Enter topic for practice")
            if st.button("Generate Questions"):
                if topic:
                    questions = generate_practice_questions(topic, st.session_state.api_key)
                    for q in questions:
                        st.write(q)
                else:
                    st.error("Please enter a topic.")

    elif page == "Settings":
        st.header("Settings")
        api_key = st.text_input("OpenAI API Key", value=st.session_state.api_key, type="password")
        if st.button("Save"):
            st.session_state.api_key = api_key
            st.success("API Key saved!")

if __name__ == "__main__":
    main()