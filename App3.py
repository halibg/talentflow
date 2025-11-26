import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import uuid
import os
import json
from datetime import datetime
from io import StringIO

# --- CONFIGURATION ---
st.set_page_config(
    page_title="TalentFlow 360",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CONSTANTS & DEFAULTS ---
DEFAULT_CSV_DB = """Name,Email,Phone,Current Role,Company,Location,Stage,Experience,Relevant Experience,Notice Period,ECTC,Keywords
Arjun Sharma,arjun.sharma@example.com,9876543210,Senior Backend Engineer,TechCorp Solutions,Bangalore,Technical R1,5.5,4,30,24,"Python, Django, AWS, PostgreSQL"
Priya Verma,priya.v@example.com,9898989898,Frontend Developer,Creative Studio,Mumbai,Managerial Round,3,3,60,12,"React, TypeScript, Tailwind, Redux"
Rohan Gupta,rohan.g@example.com,7776665554,DevOps Engineer,Cloud Systems,Pune,Hired,7,6,15,30,"Kubernetes, Docker, Jenkins, Terraform"
Sneha Patil,sneha.p@example.com,8888888888,Data Scientist,DataWiz,Bangalore,Applied,2,2,90,15,"Python, Pandas, Machine Learning, SQL"
Vikram Singh,vikram.s@example.com,9991112223,Product Manager,Innovate Inc,Delhi,Rejected,8,5,30,40,"Agile, Jira, Product Strategy, Roadmapping"
Anjali Desai,anjali.d@example.com,9988776655,UX Designer,Designify,Pune,Screening,4,4,45,18,"Figma, Adobe XD, User Research, Prototyping"
"""

CANDIDATES_FILE = 'candidates.csv'
INTERVIEWS_FILE = 'interviews.json'

STAGES = [
    'Applied', 'Screening', 'Technical R1', 'Technical R2', 
    'Managerial Round', 'Offer Released', 'Hired', 'Rejected'
]

# --- UTILS ---

def generate_id():
    return str(uuid.uuid4())[:8]

def load_data():
    """Loads candidates from local CSV or falls back to default string."""
    if 'candidates' not in st.session_state:
        if os.path.exists(CANDIDATES_FILE):
            try:
                df = pd.read_csv(CANDIDATES_FILE)
                # Ensure ID column exists
                if 'id' not in df.columns:
                    df['id'] = [generate_id() for _ in range(len(df))]
                st.session_state.candidates = df
            except Exception:
                st.session_state.candidates = pd.read_csv(StringIO(DEFAULT_CSV_DB))
                st.session_state.candidates['id'] = [generate_id() for _ in range(len(st.session_state.candidates))]
        else:
            st.session_state.candidates = pd.read_csv(StringIO(DEFAULT_CSV_DB))
            st.session_state.candidates['id'] = [generate_id() for _ in range(len(st.session_state.candidates))]

    if 'interviews' not in st.session_state:
        if os.path.exists(INTERVIEWS_FILE):
            try:
                with open(INTERVIEWS_FILE, 'r') as f:
                    st.session_state.interviews = json.load(f)
            except:
                st.session_state.interviews = []
        else:
            st.session_state.interviews = []

def save_data():
    """Saves session state to local files."""
    if 'candidates' in st.session_state:
        st.session_state.candidates.to_csv(CANDIDATES_FILE, index=False)
    
    if 'interviews' in st.session_state:
        with open(INTERVIEWS_FILE, 'w') as f:
            json.dump(st.session_state.interviews, f)

def extract_sheet_id(url):
    import re
    match = re.search(r'/d/(.*?)(\/|$)', url)
    return match.group(1) if match else None

# --- COMPONENTS ---

def sidebar():
    with st.sidebar:
        st.title("TalentFlow 360")
        st.caption("Recruitment Management System")
        st.markdown("---")
        
        page = st.radio(
            "Navigate",
            ["Dashboard", "Candidates", "Smart Search", "Interviews", "Import Data"],
            index=0
        )
        
        st.markdown("---")
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown('<div style="background-color:#6366f1;color:white;border-radius:50%;width:30px;height:30px;text-align:center;line-height:30px;font-weight:bold;">CQ</div>', unsafe_allow_html=True)
        with col2:
            st.markdown("**CloudQ Admin**\n\n<span style='color:grey;font-size:0.8em'>Kochi Dev Center</span>", unsafe_allow_html=True)
            
        return page

def render_dashboard():
    st.title("Recruitment Analytics")
    df = st.session_state.candidates
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Candidates", len(df))
    with col2:
        active_count = len(df[~df['Stage'].isin(['Hired', 'Rejected'])])
        st.metric("Active Pipeline", active_count)
    with col3:
        avg_np = int(df['Notice Period'].mean()) if not df.empty else 0
        st.metric("Avg Notice Period", f"{avg_np} Days")
    with col4:
        hired = len(df[df['Stage'] == 'Hired'])
        st.metric("Positions Closed", hired)
        
    st.markdown("---")
    
    # Charts
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Pipeline Stages")
        stage_counts = df['Stage'].value_counts().reset_index()
        stage_counts.columns = ['Stage', 'Count']
        fig_bar = px.bar(stage_counts, x='Count', y='Stage', orientation='h', color='Count', color_continuous_scale='Teal')
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with c2:
        st.subheader("Location Distribution")
        loc_counts = df['Location'].value_counts().reset_index()
        loc_counts.columns = ['Location', 'Count']
        fig_pie = px.pie(loc_counts, values='Count', names='Location', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

def render_database():
    st.title("Candidate Database")
    df = st.session_state.candidates
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        search_term = st.text_input("🔍 Search Name/Email")
    with col2:
        loc_filter = st.selectbox("Location", ["All"] + list(df['Location'].unique()))
    with col3:
        role_filter = st.selectbox("Role", ["All"] + list(df['Current Role'].unique()))
    with col4:
        stage_filter = st.selectbox("Stage", ["All"] + list(df['Stage'].unique()))
        
    # Apply Filters
    filtered_df = df.copy()
    if search_term:
        filtered_df = filtered_df[filtered_df['Name'].str.contains(search_term, case=False) | filtered_df['Email'].str.contains(search_term, case=False)]
    if loc_filter != "All":
        filtered_df = filtered_df[filtered_df['Location'] == loc_filter]
    if role_filter != "All":
        filtered_df = filtered_df[filtered_df['Current Role'] == role_filter]
    if stage_filter != "All":
        filtered_df = filtered_df[filtered_df['Stage'] == stage_filter]
        
    # Editable Table
    st.caption("Tip: You can edit cells directly below. Changes are saved automatically.")
    
    # Configure columns for the data editor
    column_config = {
        "Stage": st.column_config.SelectboxColumn(
            "Stage",
            help="Current recruitment stage",
            width="medium",
            options=STAGES,
            required=True,
        ),
        "Email": st.column_config.LinkColumn("Email"),
        "id": None # Hide ID
    }
    
    edited_df = st.data_editor(
        filtered_df,
        column_config=column_config,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="editor"
    )
    
    # Logic to update the main dataframe based on edits
    # Note: Streamlit data_editor returns the edited state. 
    # We update the session state only if the lengths match (simple update) or handle adds/deletes.
    # For this simple conversion, we essentially replace the rows in the main DF that correspond to the IDs in the edited DF.
    
    if not filtered_df.equals(edited_df):
        # Update main dataframe with changes from edited view
        # This is a simplified update logic
        for index, row in edited_df.iterrows():
            idx_in_main = st.session_state.candidates[st.session_state.candidates['id'] == row['id']].index
            if not idx_in_main.empty:
                st.session_state.candidates.loc[idx_in_main[0]] = row
        save_data()

    # Download
    st.download_button(
        label="Download CSV",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name='candidates_export.csv',
        mime='text/csv',
    )

def render_search():
    st.title("Smart Candidate Mapping")
    st.markdown("Find the perfect match based on skills and constraints.")
    
    with st.form("search_form"):
        c1, c2 = st.columns([2, 1])
        with c1:
            keywords = st.text_input("Skills / Keywords (comma separated)", placeholder="e.g. Python, AWS, React")
        with c2:
            location = st.selectbox("Location Preference", ["All"] + list(st.session_state.candidates['Location'].unique()))
            
        c3, c4 = st.columns(2)
        with c3:
            max_np = st.number_input("Max Notice Period (Days)", value=90, step=15)
        with c4:
            max_ectc = st.number_input("Max ECTC (LPA)", value=50, step=5)
            
        submitted = st.form_submit_button("Find Matches")
        
    if submitted:
        df = st.session_state.candidates
        
        # Filtering Logic
        mask = (df['Notice Period'] <= max_np) & (df['ECTC'] <= max_ectc)
        
        if location != "All":
            mask = mask & (df['Location'] == location)
            
        if keywords:
            search_terms = [k.strip().lower() for k in keywords.split(',')]
            # Combine fields for search
            df['Searchable'] = df['Keywords'].fillna('') + ' ' + df['Current Role'] + ' ' + df['Name']
            df['Searchable'] = df['Searchable'].str.lower()
            
            # Check if all keywords exist
            keyword_mask = df['Searchable'].apply(lambda x: all(term in x for term in search_terms))
            mask = mask & keyword_mask
            
        results = df[mask]
        
        st.subheader(f"Search Results ({len(results)} found)")
        
        if results.empty:
            st.info("No matches found.")
        else:
            for _, row in results.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div style="padding: 1rem; background-color: white; border-radius: 0.5rem; margin-bottom: 1rem; border: 1px solid #e5e7eb; color: black;">
                        <div style="display:flex; justify-content:space-between; align-items:center">
                            <div>
                                <h4 style="margin:0; font-weight:bold">{row['Name']}</h4>
                                <p style="margin:0; font-size:0.9em; color:#4b5563">{row['Current Role']} @ {row['Company']}</p>
                            </div>
                            <span style="background:#f3f4f6; padding:0.2rem 0.6rem; border-radius:99px; font-size:0.8em">{row['Stage']}</span>
                        </div>
                        <div style="margin-top:0.5rem; display:flex; gap:1rem; font-size:0.85em; color:#6b7280;">
                            <span>📍 {row['Location']}</span>
                            <span>⏱ NP: {row['Notice Period']}d</span>
                            <span>💰 {row['ECTC']} LPA</span>
                            <span>💼 {row['Experience']} Yrs</span>
                        </div>
                        <div style="margin-top:0.5rem">
                            <small style="color:#0d9488">Skills: {row['Keywords']}</small>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Move {row['Name'].split()[0]} to Screening", key=f"btn_{row['id']}"):
                        # Update stage
                        idx = st.session_state.candidates[st.session_state.candidates['id'] == row['id']].index[0]
                        st.session_state.candidates.at[idx, 'Stage'] = 'Screening'
                        save_data()
                        st.success(f"Moved {row['Name']} to Screening!")
                        st.rerun()

def render_scheduler():
    st.title("Interview Scheduler")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Schedule New")
        with st.form("schedule_form"):
            # Filter out rejected/hired
            active_df = st.session_state.candidates[~st.session_state.candidates['Stage'].isin(['Rejected', 'Hired'])]
            
            candidate_opts = {f"{row['Name']} - {row['Current Role']}": row['id'] for _, row in active_df.iterrows()}
            
            selected_label = st.selectbox("Select Candidate", list(candidate_opts.keys()))
            round_type = st.selectbox("Round", ["Screening", "Technical L1", "Technical L2", "Managerial", "HR Discussion"])
            
            c_date = st.date_input("Date")
            c_time = st.time_input("Time")
            interviewer = st.text_input("Interviewer Email")
            
            if st.form_submit_button("Send Invitation"):
                if selected_label:
                    cid = candidate_opts[selected_label]
                    cname = selected_label.split(' - ')[0]
                    new_interview = {
                        "id": generate_id(),
                        "candidateId": cid,
                        "candidateName": cname,
                        "type": round_type,
                        "date": str(c_date),
                        "time": str(c_time),
                        "interviewer": interviewer,
                        "status": "Scheduled"
                    }
                    st.session_state.interviews.append(new_interview)
                    save_data()
                    st.success("Interview Scheduled!")
    
    with col2:
        st.subheader("Upcoming Interviews")
        if not st.session_state.interviews:
            st.info("No interviews scheduled.")
        else:
            for inv in st.session_state.interviews:
                st.markdown(f"""
                <div style="padding:1rem; background-color:white; margin-bottom:0.5rem; border-radius:0.5rem; border:1px solid #e2e8f0; display:flex; justify-content:space-between; align-items:center; color: black;">
                    <div style="display:flex; gap:1rem; align-items:center">
                        <div style="background:#e0e7ff; color:#4f46e5; padding:0.5rem; border-radius:0.5rem">📅</div>
                        <div>
                            <div style="font-weight:bold">{inv['candidateName']}</div>
                            <div style="font-size:0.8em; color:#64748b">{inv['type']} • {inv['interviewer']}</div>
                        </div>
                    </div>
                    <div style="text-align:right">
                        <div style="font-weight:600">{inv['time']}</div>
                        <div style="font-size:0.8em; color:#64748b">{inv['date']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

def render_importer():
    st.title("Import Data")
    st.markdown("Connect external data sources.")
    
    # Google Sheets
    st.subheader("Google Sheets Integration")
    st.info("Ensure your Sheet is 'Published to Web' (File > Share > Publish to Web > CSV).")
    
    sheet_url = st.text_input("Paste Google Sheet URL")
    if st.button("Sync Google Sheet"):
        if sheet_url:
            try:
                # Attempt to extract ID and construct export URL if standard URL is pasted
                sheet_id = extract_sheet_id(sheet_url)
                final_url = sheet_url
                if sheet_id:
                     final_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
                
                new_data = pd.read_csv(final_url)
                
                # Basic validation
                required_cols = ['Name', 'Email']
                if not all(col in new_data.columns for col in required_cols):
                    st.error(f"CSV missing required columns: {required_cols}")
                else:
                    # Merge logic
                    current_emails = st.session_state.candidates['Email'].str.lower().tolist()
                    new_candidates = []
                    
                    for _, row in new_data.iterrows():
                        if str(row['Email']).lower() not in current_emails:
                            # Normalize data
                            row_dict = row.to_dict()
                            row_dict['id'] = generate_id()
                            
                            # Ensure defaults for missing fields
                            if 'Stage' not in row_dict or pd.isna(row_dict['Stage']): row_dict['Stage'] = 'Applied'
                            if 'Location' not in row_dict: row_dict['Location'] = 'Unknown'
                            
                            new_candidates.append(row_dict)
                    
                    if new_candidates:
                        new_df = pd.DataFrame(new_candidates)
                        st.session_state.candidates = pd.concat([st.session_state.candidates, new_df], ignore_index=True)
                        save_data()
                        st.success(f"Successfully imported {len(new_candidates)} new candidates!")
                    else:
                        st.warning("No new unique candidates found (based on Email).")
                        
            except Exception as e:
                st.error(f"Error importing sheet: {e}")
        else:
            st.error("Please enter a URL.")

    st.divider()
    
    # Local CSV
    st.subheader("Upload Local CSV")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        try:
            new_data = pd.read_csv(uploaded_file)
            st.write("Preview:", new_data.head())
            if st.button("Import Uploaded File"):
                st.session_state.candidates = pd.concat([st.session_state.candidates, new_data], ignore_index=True)
                # Ensure IDs
                st.session_state.candidates['id'] = st.session_state.candidates.apply(
                    lambda x: x['id'] if 'id' in x and pd.notnull(x['id']) else generate_id(), axis=1
                )
                save_data()
                st.success("File imported successfully!")
        except Exception as e:
            st.error(f"Error reading file: {e}")

# --- MAIN APP LOGIC ---

def main():
    load_data()
    page = sidebar()
    
    if page == "Dashboard":
        render_dashboard()
    elif page == "Candidates":
        render_database()
    elif page == "Smart Search":
        render_search()
    elif page == "Interviews":
        render_scheduler()
    elif page == "Import Data":
        render_importer()

if __name__ == "__main__":
    main()