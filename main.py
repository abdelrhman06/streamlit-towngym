import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date
import time
import hashlib
import re

# =========================
# CONFIG
# =========================

SPREADSHEET_ID = '1bJAoyCIjb387jOPVA4cUS6R8YTHdFZE0xpONJiQKC7s'
WORKSHEET_NAME = "Leads"

# Admin password (MUST be changed in Streamlit secrets for production)
try:
    ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]
except:
    ADMIN_PASSWORD = "towngym2025"  # Default - CHANGE THIS!

# Session timeout (in seconds)
SESSION_TIMEOUT = 3600  # 1 hour

# Rate limiting
MAX_SUBMISSIONS_PER_HOUR = 10  # Maximum form submissions per hour from same user

SERVICE_ACCOUNT_FILE = "creds.json"  # ملف الـ Service Account


# =========================
# GOOGLE SHEETS HELPERS
# =========================

@st.cache_resource
def get_gsheet_client():
    scope = ['https://www.googleapis.com/auth/spreadsheets']

    # Try to load from Streamlit secrets first (for cloud deployment)
    try:
        creds_dict = dict(st.secrets["gsheet_credentials"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    except:
        # Fallback to local file (for local development)
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scope)

    client = gspread.authorize(creds)
    return client


def get_worksheet():
    client = get_gsheet_client()
    sh = client.open_by_key(SPREADSHEET_ID)
    try:
        ws = sh.worksheet(WORKSHEET_NAME)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=WORKSHEET_NAME, rows=1000, cols=30)
        # أول مرّة نضيف الـ header
        headers = [
            "Timestamp",
            "Company Name",
            "Industry",
            "Size",
            "Location",
            "HR/Contact Name",
            "Role",
            "LinkedIn Link",
            "Interest Level",
            "Notes",
        ]
        ws.append_row(headers, value_input_option="RAW")
    return ws


def append_lead_row(row):
    ws = get_worksheet()
    ws.append_row(row, value_input_option="USER_ENTERED")


def load_data_as_df():
    ws = get_worksheet()
    records = ws.get_all_records()
    if not records:
        return pd.DataFrame()
    df = pd.DataFrame(records)
    return df


# =========================
# SECURITY HELPERS
# =========================

def sanitize_input(text):
    """Sanitize user input to prevent injection attacks"""
    if not text:
        return ""
    # Remove any potential HTML/script tags
    text = re.sub(r'<[^>]*>', '', str(text))
    # Remove special characters that could be used for injection
    text = re.sub(r'[<>\"\'%;()&+]', '', str(text))
    return text.strip()

def validate_email(email):
    """Validate email format"""
    if not email:
        return True  # Email is optional
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_url(url):
    """Validate URL format"""
    if not url:
        return True  # URL is optional
    pattern = r'^https?://(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    return re.match(pattern, url) is not None

def check_rate_limit():
    """Check if user has exceeded submission rate limit"""
    if 'submission_times' not in st.session_state:
        st.session_state.submission_times = []

    # Remove submissions older than 1 hour
    current_time = time.time()
    st.session_state.submission_times = [
        t for t in st.session_state.submission_times
        if current_time - t < 3600
    ]

    # Check if limit exceeded
    if len(st.session_state.submission_times) >= MAX_SUBMISSIONS_PER_HOUR:
        return False

    return True

def record_submission():
    """Record a new submission timestamp"""
    if 'submission_times' not in st.session_state:
        st.session_state.submission_times = []
    st.session_state.submission_times.append(time.time())


# =========================
# UI HELPERS
# =========================

def show_lead_form():
    st.header("🏋️‍♂️ Towngym Corporate Leads Form – New Maadi")

    with st.form("lead_form"):
        company_name = st.text_input("Company Name *", placeholder="e.g., ABC Corporation")

        industry = st.text_input("Industry", placeholder="e.g., Software, Banking, Education")

        size = st.text_input("Size", placeholder="e.g., 50 employees, 100-200 employees")

        location = st.text_input("Location", placeholder="e.g., New Maadi, Zahraa El Maadi")

        hr_contact_name = st.text_input("HR/Contact Name *", placeholder="Full name")

        role = st.text_input("Role", placeholder="e.g., HR Manager, CEO")

        linkedin_link = st.text_input("LinkedIn Link", placeholder="https://linkedin.com/in/...")

        interest_level = st.selectbox(
            "Interest Level",
            options=["Low", "Medium", "High"]
        )

        notes = st.text_area("Notes", placeholder="Any additional information", height=100)

        submitted = st.form_submit_button("✅ Submit Lead", use_container_width=True, type="primary")

        if submitted:
            # Check rate limit
            if not check_rate_limit():
                st.error("⏰ Too many submissions. Please wait before submitting again (max 10 per hour).")
                st.stop()

            # Validation
            errors = []

            # Required fields
            if not company_name.strip():
                errors.append("Company Name is required")
            if not hr_contact_name.strip():
                errors.append("HR/Contact Name is required")

            # Validate LinkedIn URL if provided
            if linkedin_link and not validate_url(linkedin_link):
                errors.append("Invalid LinkedIn URL format")

            # Length validation
            if len(company_name) > 200:
                errors.append("Company Name is too long (max 200 characters)")
            if len(notes) > 1000:
                errors.append("Notes are too long (max 1000 characters)")

            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Sanitize all inputs
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                row = [
                    timestamp,                          # Timestamp
                    sanitize_input(company_name),       # Company Name
                    sanitize_input(industry),           # Industry
                    sanitize_input(size),               # Size
                    sanitize_input(location),           # Location
                    sanitize_input(hr_contact_name),    # HR/Contact Name
                    sanitize_input(role),               # Role
                    linkedin_link.strip() if linkedin_link else "",  # LinkedIn Link
                    interest_level,                     # Interest Level
                    sanitize_input(notes)               # Notes
                ]
                try:
                    append_lead_row(row)
                    record_submission()  # Record this submission
                    st.success("✅ Lead successfully submitted to Google Sheets!")
                    st.balloons()

                    # Show summary
                    with st.expander("📊 View Submission Summary"):
                        st.write(f"**Company:** {sanitize_input(company_name)}")
                        st.write(f"**Industry:** {sanitize_input(industry)}")
                        st.write(f"**Size:** {sanitize_input(size)}")
                        st.write(f"**Location:** {sanitize_input(location)}")
                        st.write(f"**HR/Contact:** {sanitize_input(hr_contact_name)} ({sanitize_input(role)})")
                        st.write(f"**Interest Level:** {interest_level}")
                        st.write(f"**Timestamp:** {timestamp}")
                except Exception as e:
                    st.error(f"❌ Error saving lead: {e}")


def map_interest_to_score(level):
    mapping = {"Low": 1, "Medium": 2, "High": 3}
    return mapping.get(level, 0)


def compute_lead_score(row):
    score = 0
    score += map_interest_to_score(row.get("Interest Level", ""))
    # ممكن تضيف حاجات تانية للـ scoring
    return score


def show_admin_dashboard():
    st.header("📊 Admin Dashboard – Corporate Leads")

    # Top controls
    top_col1, top_col2, top_col3 = st.columns([2, 2, 2])
    with top_col1:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_resource.clear()
            st.rerun()

    df = load_data_as_df()

    if df.empty:
        st.info("📭 No leads found. Start adding leads from the Lead Form page!")
        return

    # Clean data - remove empty rows
    df = df[df["Company Name"].notna() & (df["Company Name"] != "")]

    # Convert Timestamp to datetime if exists
    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors='coerce')

    # Lead Score
    df["Lead Score"] = df.apply(compute_lead_score, axis=1)

    # Search functionality
    with top_col2:
        search_term = st.text_input("🔍 Search", placeholder="Company name, contact, industry...", label_visibility="collapsed")

    if search_term:
        search_mask = df.apply(lambda row: search_term.lower() in str(row).lower(), axis=1)
        df = df[search_mask]
        st.info(f"🔍 Found {len(df)} results for '{search_term}'")

    # KPIs Section
    st.markdown("### 📈 Key Metrics")
    total_leads = len(df)
    high_interest = (df["Interest Level"] == "High").sum() if "Interest Level" in df.columns else 0
    medium_interest = (df["Interest Level"] == "Medium").sum() if "Interest Level" in df.columns else 0
    low_interest = (df["Interest Level"] == "Low").sum() if "Interest Level" in df.columns else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🎯 Total Leads", total_leads)
    col2.metric("🔥 High Interest", high_interest, delta=f"{round(high_interest/total_leads*100) if total_leads > 0 else 0}%")
    col3.metric("⚡ Medium Interest", medium_interest, delta=f"{round(medium_interest/total_leads*100) if total_leads > 0 else 0}%")
    col4.metric("📊 Low Interest", low_interest, delta=f"{round(low_interest/total_leads*100) if total_leads > 0 else 0}%")

    st.markdown("---")

    # Charts Section
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("#### 📍 Leads by Location")
        if "Location" in df.columns and not df["Location"].isna().all():
            location_counts = df["Location"].value_counts().head(10)
            st.bar_chart(location_counts)
        else:
            st.info("No location data available")

    with chart_col2:
        st.markdown("#### 🏢 Leads by Industry")
        if "Industry" in df.columns and not df["Industry"].isna().all():
            industry_counts = df["Industry"].value_counts().head(10)
            st.bar_chart(industry_counts)
        else:
            st.info("No industry data available")

    st.markdown("---")

    # Interest Level Distribution
    st.markdown("#### 🎯 Interest Level Distribution")
    if "Interest Level" in df.columns:
        interest_col1, interest_col2 = st.columns([2, 1])
        with interest_col1:
            interest_counts = df["Interest Level"].value_counts()
            st.bar_chart(interest_counts)
        with interest_col2:
            st.markdown("**Breakdown:**")
            for level in ["High", "Medium", "Low"]:
                count = interest_counts.get(level, 0)
                percentage = round(count / total_leads * 100) if total_leads > 0 else 0
                st.metric(f"{level}", f"{count} ({percentage}%)")

    st.markdown("---")

    # Recent Leads Section
    st.markdown("### 🆕 Recent Leads (Last 7 Days)")
    if "Timestamp" in df.columns:
        seven_days_ago = pd.Timestamp.now() - pd.Timedelta(days=7)
        recent_df = df[df["Timestamp"] >= seven_days_ago].sort_values("Timestamp", ascending=False)

        if len(recent_df) > 0:
            recent_col1, recent_col2, recent_col3 = st.columns(3)
            recent_col1.metric("📊 New Leads (7d)", len(recent_df))

            high_recent = (recent_df["Interest Level"] == "High").sum() if "Interest Level" in recent_df.columns else 0
            recent_col2.metric("🔥 High Interest", high_recent)

            # Calculate average score
            avg_score = round(recent_df["Lead Score"].mean(), 1) if len(recent_df) > 0 else 0
            recent_col3.metric("⭐ Avg Score", avg_score)

            # Show recent leads table
            recent_display_cols = [col for col in ["Timestamp", "Company Name", "Location", "HR/Contact Name", "Interest Level"] if col in recent_df.columns]
            if recent_display_cols:
                st.dataframe(recent_df[recent_display_cols].head(10), use_container_width=True, hide_index=True)
        else:
            st.info("No leads added in the last 7 days")

    st.markdown("---")

    # Top Leads Table
    st.markdown("### 🏆 Top 20 Leads by Score")
    display_cols = [col for col in ["Timestamp", "Company Name", "Location", "Industry", "HR/Contact Name", "Interest Level", "Lead Score"] if col in df.columns]
    if display_cols:
        top_leads = df.sort_values("Lead Score", ascending=False)[display_cols].head(20)
        st.dataframe(
            top_leads,
            use_container_width=True,
            hide_index=True
        )

    st.markdown("---")

    # Filters Section
    st.markdown("### 🔍 Filter & Export Leads")

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        if "Location" in df.columns:
            location_options = sorted([loc for loc in df["Location"].dropna().unique() if loc])
            location_filter = st.multiselect(
                "📍 Filter by Location",
                options=location_options,
                default=[]
            )
        else:
            location_filter = []

    with filter_col2:
        if "Interest Level" in df.columns:
            interest_options = sorted([lvl for lvl in df["Interest Level"].dropna().unique() if lvl])
            interest_filter = st.multiselect(
                "🎯 Filter by Interest",
                options=interest_options,
                default=[]
            )
        else:
            interest_filter = []

    with filter_col3:
        if "Industry" in df.columns:
            industry_options = sorted([ind for ind in df["Industry"].dropna().unique() if ind])
            industry_filter = st.multiselect(
                "🏢 Filter by Industry",
                options=industry_options,
                default=[]
            )
        else:
            industry_filter = []

    # Apply filters
    filtered_df = df.copy()
    if location_filter:
        filtered_df = filtered_df[filtered_df["Location"].isin(location_filter)]
    if interest_filter:
        filtered_df = filtered_df[filtered_df["Interest Level"].isin(interest_filter)]
    if industry_filter:
        filtered_df = filtered_df[filtered_df["Industry"].isin(industry_filter)]

    # Show filtered count
    st.info(f"📊 Showing {len(filtered_df)} of {total_leads} leads")

    # Display filtered table with action buttons
    st.markdown("#### 📋 All Leads")

    # Add action columns for each lead
    for idx, row in filtered_df.iterrows():
        with st.expander(f"🏢 {row.get('Company Name', 'N/A')} - {row.get('Interest Level', 'N/A')} Interest"):
            detail_col1, detail_col2, detail_col3 = st.columns([2, 2, 1])

            with detail_col1:
                st.write(f"**📍 Location:** {row.get('Location', 'N/A')}")
                st.write(f"**🏢 Industry:** {row.get('Industry', 'N/A')}")
                st.write(f"**👥 Size:** {row.get('Size', 'N/A')}")

            with detail_col2:
                st.write(f"**👤 Contact:** {row.get('HR/Contact Name', 'N/A')}")
                st.write(f"**💼 Role:** {row.get('Role', 'N/A')}")
                st.write(f"**⭐ Score:** {row.get('Lead Score', 0)}")

            with detail_col3:
                # Quick action buttons
                linkedin = row.get('LinkedIn Link', '')
                if linkedin and linkedin.strip():
                    st.link_button("🔗 LinkedIn", linkedin, use_container_width=True)

            # Notes section
            if row.get('Notes', ''):
                st.write(f"**📝 Notes:** {row.get('Notes', '')}")

            # Timestamp
            if 'Timestamp' in row and pd.notna(row['Timestamp']):
                st.caption(f"Added: {row['Timestamp']}")

    # Download Section
    st.markdown("---")
    st.markdown("### 📥 Export Data")

    export_col1, export_col2 = st.columns([1, 3])

    with export_col1:
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f'towngym_leads_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            mime='text/csv',
            use_container_width=True
        )

    with export_col2:
        st.caption(f"💾 Download includes {len(filtered_df)} filtered leads • Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def admin_login():
    st.sidebar.subheader("Admin Login")

    # Initialize session state
    if "is_admin" not in st.session_state:
        st.session_state["is_admin"] = False
    if "login_time" not in st.session_state:
        st.session_state["login_time"] = None
    if "failed_attempts" not in st.session_state:
        st.session_state["failed_attempts"] = 0
    if "lockout_time" not in st.session_state:
        st.session_state["lockout_time"] = None

    # Check session timeout
    if st.session_state["is_admin"] and st.session_state["login_time"]:
        if time.time() - st.session_state["login_time"] > SESSION_TIMEOUT:
            st.session_state["is_admin"] = False
            st.session_state["login_time"] = None
            st.sidebar.warning("⏰ Session expired. Please login again.")

    # Check lockout (5 failed attempts = 15 min lockout)
    if st.session_state["lockout_time"]:
        if time.time() - st.session_state["lockout_time"] < 900:  # 15 minutes
            remaining = int(900 - (time.time() - st.session_state["lockout_time"]))
            st.sidebar.error(f"🔒 Too many failed attempts. Try again in {remaining // 60} minutes.")
            return
        else:
            st.session_state["lockout_time"] = None
            st.session_state["failed_attempts"] = 0

    if not st.session_state["is_admin"]:
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            if password == ADMIN_PASSWORD:
                st.session_state["is_admin"] = True
                st.session_state["login_time"] = time.time()
                st.session_state["failed_attempts"] = 0
                st.sidebar.success("Logged in as admin ✅")
                st.rerun()
            else:
                st.session_state["failed_attempts"] += 1
                if st.session_state["failed_attempts"] >= 5:
                    st.session_state["lockout_time"] = time.time()
                    st.sidebar.error("🔒 Too many failed attempts. Locked for 15 minutes.")
                else:
                    remaining = 5 - st.session_state["failed_attempts"]
                    st.sidebar.error(f"❌ Wrong password ({remaining} attempts remaining)")
    else:
        st.sidebar.success("Admin mode active")
        # Show session time remaining
        if st.session_state["login_time"]:
            time_remaining = SESSION_TIMEOUT - (time.time() - st.session_state["login_time"])
            st.sidebar.caption(f"⏱️ Session: {int(time_remaining // 60)} min remaining")

        if st.sidebar.button("Logout"):
            st.session_state["is_admin"] = False
            st.session_state["login_time"] = None
            st.rerun()


# =========================
# MAIN APP
# =========================

def main():
    st.set_page_config(page_title="Towngym Corporate Leads", page_icon="🏋️", layout="wide")

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Lead Form", "Admin Dashboard"])

    # Admin login section
    admin_login()

    if page == "Lead Form":
        show_lead_form()
    elif page == "Admin Dashboard":
        if st.session_state.get("is_admin", False):
            show_admin_dashboard()
        else:
            st.error("Admins only. Please login from the sidebar.")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p>🏋️ Towngym New Maadi | Corporate Partnership Program</p>
            <p style='font-size: 0.8em;'>All submissions are automatically saved to Google Sheets</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
