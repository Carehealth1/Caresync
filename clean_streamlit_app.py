import streamlit as st
import pandas as pd
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(
    page_title="Clinical Data Platform",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #0f766e, #0ea5e9);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .metric-card {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #0f766e;
        margin: 0.5rem 0;
    }
    .alert-critical {
        background: #fef2f2;
        border-left: 4px solid #ef4444;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .alert-warning {
        background: #fffbeb;
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .alert-info {
        background: #eff6ff;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .process-step {
        background: #f1f5f9;
        padding: 0.75rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        border-left: 3px solid #10b981;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'process_steps' not in st.session_state:
        st.session_state.process_steps = []
    if 'query_type' not in st.session_state:
        st.session_state.query_type = None

def simulate_processing_steps(query_type, query_text):
    """Simulate the multi-agent processing steps"""
    steps = []
    
    if query_type == "Individual Patient":
        steps = [
            {
                "name": "Query Analysis",
                "description": "LLM parsing clinical data requirements",
                "data_points": ["Patient demographics", "Medical history", "Current symptoms", "Lab values", "Medications"],
                "sql": "SELECT * FROM patients p JOIN medical_history mh ON p.id = mh.patient_id WHERE p.patient_id = 'PT-789456'"
            },
            {
                "name": "Schema Mapping", 
                "description": "Mapping clinical concepts to database tables",
                "data_points": ["EHR_PATIENTS table", "LAB_RESULTS table", "MEDICATIONS table", "ENCOUNTERS table"],
                "sql": "JOIN lab_results lr ON p.id = lr.patient_id AND lr.test_date >= DATE_SUB(NOW(), INTERVAL 90 DAY)"
            },
            {
                "name": "Patient Demographics Query",
                "description": "extract_patient_demographics(patient_id)",
                "data_points": ["Name, Age, Gender", "Insurance Info", "Emergency Contacts", "Primary Care Physician"],
                "sql": "SELECT name, age, gender, insurance_id FROM patients WHERE patient_id = 'PT-789456'"
            },
            {
                "name": "Medical History Extraction",
                "description": "extract_medical_history(patient_id, years=5)",
                "data_points": ["Chronic Conditions", "Previous Surgeries", "Allergies", "Family History"],
                "sql": "SELECT diagnosis_code, diagnosis_date, severity FROM medical_history WHERE patient_id = 'PT-789456'"
            },
            {
                "name": "Lab Results Mining",
                "description": "extract_lab_results(patient_id, recent=true)",
                "data_points": ["CBC", "Comprehensive Metabolic Panel", "HbA1c", "Lipid Panel"],
                "sql": "SELECT test_name, result_value, reference_range, test_date FROM lab_results WHERE patient_id = 'PT-789456' ORDER BY test_date DESC"
            },
            {
                "name": "Data Synthesis & Analysis",
                "description": "LLM processing extracted data for clinical insights",
                "data_points": ["Trend Analysis", "Risk Stratification", "Care Gaps", "Clinical Correlations"],
                "sql": "Complex aggregation queries across multiple tables for trend analysis"
            }
        ]
    else:  # Population Health
        steps = [
            {
                "name": "NLP Query Processing",
                "description": "LLM interpreting population health criteria",
                "data_points": ["Medical conditions", "Lab value ranges", "Time constraints", "Demographics", "Risk factors"],
                "sql": 'Parsed criteria: "diabetic patients", "HbA1c > 8%", "last 6 months"'
            },
            {
                "name": "Population SQL Generation",
                "description": "generate_population_query(criteria)",
                "data_points": ["Patient cohort identification", "Clinical criteria mapping", "Date range filtering", "Exclusion criteria"],
                "sql": """SELECT DISTINCT p.patient_id, p.name, p.age, p.gender, 
       lr.result_value as hba1c, lr.test_date
FROM patients p 
JOIN medical_history mh ON p.id = mh.patient_id
JOIN lab_results lr ON p.id = lr.patient_id
WHERE mh.diagnosis_code IN ('E11.9', 'E11.40', 'E11.51') -- Type 2 Diabetes codes
  AND lr.test_name = 'HbA1c'
  AND lr.result_value > 8.0
  AND lr.test_date >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
  AND p.active_status = 1"""
            },
            {
                "name": "Patient Cohort Retrieval",
                "description": "execute_population_query(sql)",
                "data_points": ["Cohort size: 342 patients", "Geographic distribution", "Age demographics", "Severity stratification"],
                "sql": "Query executed across 125,000+ patient records in 2.1 seconds"
            },
            {
                "name": "Statistical Analysis",
                "description": "calculate_population_metrics(cohort)",
                "data_points": ["Mean HbA1c", "Standard deviation", "Risk stratification", "Comorbidity analysis"],
                "sql": "SELECT AVG(result_value), STDDEV(result_value), COUNT(*) FROM cohort_results GROUP BY risk_level"
            },
            {
                "name": "CareHealth Integration",
                "description": "format_for_carehealth_export(patient_list)",
                "data_points": ["Patient identifiers", "Clinical priorities", "Contact information", "Care team assignments"],
                "sql": "SELECT patient_id, name, phone, primary_care_provider, priority_score FROM cohort_final"
            }
        ]
    
    return steps

def generate_individual_results():
    """Generate mock individual patient results"""
    return {
        "type": "individual",
        "patient_info": {
            "id": "PT-789456",
            "name": "Maria Rodriguez",
            "age": 45,
            "gender": "Female",
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "clinical_flags": [
            {
                "type": "critical",
                "message": "HbA1c above target - diabetes management needs optimization",
                "confidence": 95
            },
            {
                "type": "warning", 
                "message": "Blood pressure trending upward - medication adjustment may be needed",
                "confidence": 82
            },
            {
                "type": "info",
                "message": "Patient due for annual eye exam and foot screening",
                "confidence": 100
            }
        ],
        "data_categories": {
            "Demographics & Insurance": {
                "Primary Insurance": "Blue Cross Blue Shield",
                "Emergency Contact": "Carlos Rodriguez (Spouse)",
                "Primary Care Provider": "Dr. Jennifer Smith, MD",
                "Preferred Language": "English",
                "Phone Number": "(555) 123-4567",
                "Address": "123 Main St, Springfield, IL 62701"
            },
            "Medical History": {
                "Active Diagnoses": "Type 2 Diabetes Mellitus, Hypertension",
                "Chronic Conditions": "Diabetes (8 years), HTN (5 years)",
                "Known Allergies": "Penicillin (rash), Shellfish (anaphylaxis)",
                "Surgical History": "Cholecystectomy (2019)",
                "Family History": "Diabetes (mother), CAD (father)"
            },
            "Laboratory Results": {
                "HbA1c": "8.2% (Target: <7.0%)",
                "Fasting Glucose": "165 mg/dL (High)",
                "Blood Pressure": "145/92 mmHg (Elevated)",
                "LDL Cholesterol": "145 mg/dL (Borderline High)",
                "Creatinine": "0.9 mg/dL (Normal)",
                "eGFR": ">60 mL/min/1.73m² (Normal)"
            },
            "Current Medications": {
                "Metformin": "500mg BID (Started 2017)",
                "Lisinopril": "10mg Daily (Started 2020)", 
                "Atorvastatin": "20mg Daily (Started 2021)",
                "Aspirin": "81mg Daily (Cardioprotective)",
                "Multivitamin": "1 tablet daily"
            },
            "Vital Signs Trends": {
                "Weight": "178 lbs (↑5 lbs from 6 months ago)",
                "BMI": "29.2 (Overweight)",
                "Temperature": "98.6°F (Normal)",
                "Heart Rate": "78 bpm (Normal)",
                "Respiratory Rate": "16/min (Normal)"
            }
        },
        "data_quality": {
            "completeness": 87,
            "accuracy": 94,
            "timeliness": 76,
            "consistency": 91
        }
    }

def generate_population_results():
    """Generate mock population health results"""
    
    # Sample patient data with more variety
    patient_data = [
        {"id": "PT-123456", "name": "Sarah Johnson", "age": 62, "hba1c": 9.8, "last_visit": "2025-07-15", "priority": "High", "provider": "Dr. Smith"},
        {"id": "PT-789012", "name": "Michael Chen", "age": 55, "hba1c": 8.9, "last_visit": "2025-08-01", "priority": "High", "provider": "Dr. Johnson"},
        {"id": "PT-345678", "name": "Linda Garcia", "age": 48, "hba1c": 8.4, "last_visit": "2025-07-28", "priority": "Moderate", "provider": "Dr. Williams"},
        {"id": "PT-901234", "name": "Robert Davis", "age": 67, "hba1c": 9.2, "last_visit": "2025-06-30", "priority": "High", "provider": "Dr. Brown"},
        {"id": "PT-567890", "name": "Jennifer Wilson", "age": 52, "hba1c": 8.7, "last_visit": "2025-08-05", "priority": "Moderate", "provider": "Dr. Taylor"},
        {"id": "PT-234567", "name": "David Kim", "age": 59, "hba1c": 9.5, "last_visit": "2025-07-20", "priority": "High", "provider": "Dr. Anderson"},
        {"id": "PT-876543", "name": "Maria Santos", "age": 44, "hba1c": 8.3, "last_visit": "2025-08-08", "priority": "Moderate", "provider": "Dr. Martinez"},
        {"id": "PT-135792", "name": "James Miller", "age": 63, "hba1c": 9.1, "last_visit": "2025-07-10", "priority": "High", "provider": "Dr. Thompson"},
        {"id": "PT-246810", "name": "Susan Lee", "age": 56, "hba1c": 8.6, "last_visit": "2025-07-25", "priority": "Moderate", "provider": "Dr. Garcia"},
        {"id": "PT-369258", "name": "John Anderson", "age": 49, "hba1c": 9.3, "last_visit": "2025-08-02", "priority": "High", "provider": "Dr. Wilson"}
    ]
    
    return {
        "type": "population",
        "cohort_info": {
            "name": "Diabetic Patients with Elevated HbA1c",
            "total_patients": 342,
            "query_executed": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "criteria": "Type 2 Diabetes + HbA1c > 8% in last 6 months"
        },
        "population_metrics": {
            "average_age": 58.3,
            "gender_distribution": {"male": 45.3, "female": 54.7},
            "average_hba1c": 9.1,
            "risk_distribution": {
                "high": 89,
                "moderate": 164,
                "low": 89
            }
        },
        "patient_list": patient_data,
        "care_opportunities": [
            {
                "type": "critical",
                "title": "89 High-Risk Patients Need Immediate Intervention",
                "description": "HbA1c ≥ 9.0% requiring urgent medication adjustment or specialist referral",
                "patient_count": 89,
                "cost_savings": "$267,000/year"
            },
            {
                "type": "warning",
                "title": "164 Patients Approaching High Risk",
                "description": "HbA1c 8.0-8.9% - preventive intervention recommended",
                "patient_count": 164,
                "cost_savings": "$328,000/year"
            },
            {
                "type": "info",
                "title": "Population Health Program Opportunity",
                "description": "Coordinated diabetes management could improve outcomes for entire cohort",
                "patient_count": 342,
                "cost_savings": "$1.2M/year"
            }
        ],
        "geographic_distribution": [
            {"region": "Downtown", "count": 89, "percentage": 26.0},
            {"region": "Suburbs", "count": 142, "percentage": 41.5},
            {"region": "East Side", "count": 67, "percentage": 19.6},
            {"region": "West Side", "count": 44, "percentage": 12.9}
        ],
        "carehealth_export": {
            "ready": True,
            "list_name": "Diabetes_HbA1c_High_Aug2025",
            "patient_count": 342,
            "export_format": "CareHealth Patient List",
            "estimated_sync_time": "3 minutes"
        }
    }

def process_query(query_type, query_text):
    """Process the query and simulate the multi-agent workflow"""
    st.session_state.processing = True
    st.session_state.process_steps = []
    st.session_state.results = None
    st.session_state.query_type = query_type
    
    # Create placeholder for dynamic updates
    placeholder = st.empty()
    
    with placeholder.container():
        st.info(f"🔄 Processing {query_type.lower()} query...")
        progress_bar = st.progress(0)
        status_text = st.empty()
    
    # Simulate processing steps
    steps = simulate_processing_steps(query_type, query_text)
    
    for i, step in enumerate(steps):
        status_text.text(f"Processing: {step['name']}")
        progress_bar.progress((i + 1) / len(steps))
        time.sleep(1.2)  # Simulate processing time
        st.session_state.process_steps.append(step)
    
    # Generate results
    if query_type == "Individual Patient":
        st.session_state.results = generate_individual_results()
    else:
        st.session_state.results = generate_population_results()
    
    st.session_state.processing = False
    placeholder.empty()

def display_individual_results(results):
    """Display individual patient results"""
    # Patient header
    st.markdown(f"""
    <div class="metric-card">
        <h3>🏥 {results['patient_info']['name']}</h3>
        <p><strong>Patient ID:</strong> {results['patient_info']['id']} | 
           <strong>Age:</strong> {results['patient_info']['age']} | 
           <strong>Gender:</strong> {results['patient_info']['gender']}</p>
        <small>📅 Last Updated: {results['patient_info']['last_update']}</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Clinical flags
    st.subheader("🚨 Clinical Alerts")
    for flag in results['clinical_flags']:
        alert_class = f"alert-{flag['type']}"
        icon = "🔴" if flag['type'] == 'critical' else "🟡" if flag['type'] == 'warning' else "🔵"
        st.markdown(f"""
        <div class="{alert_class}">
            {icon} <strong>{flag['message']}</strong><br>
            <small>Confidence: {flag['confidence']}%</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Data categories in columns
    st.subheader("📋 Extracted Data Categories")
    
    # Create tabs for different data categories
    cat_tabs = st.tabs(list(results['data_categories'].keys()))
    
    for tab, (category, data) in zip(cat_tabs, results['data_categories'].items()):
        with tab:
            for key, value in data.items():
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.write(f"**{key}:**")
                with col2:
                    st.write(value)
    
    # Data Quality Assessment
    if 'data_quality' in results:
        st.subheader("📊 Data Quality Assessment")
        quality_cols = st.columns(4)
        quality_metrics = results['data_quality']
        
        with quality_cols[0]:
            st.metric("Completeness", f"{quality_metrics['completeness']}%")
        with quality_cols[1]:
            st.metric("Accuracy", f"{quality_metrics['accuracy']}%")
        with quality_cols[2]:
            st.metric("Timeliness", f"{quality_metrics['timeliness']}%")
        with quality_cols[3]:
            st.metric("Consistency", f"{quality_metrics['consistency']}%")

def display_population_results(results):
    """Display population health results"""
    # Cohort summary
    st.markdown(f"""
    <div class="metric-card">
        <h3>🌐 {results['cohort_info']['name']}</h3>
        <p><strong>{results['cohort_info']['total_patients']} patients</strong> | {results['cohort_info']['criteria']}</p>
        <small>📅 Query executed: {results['cohort_info']['query_executed']}</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Population metrics
    st.subheader("📈 Population Metrics")
    metric_cols = st.columns(4)
    
    with metric_cols[0]:
        st.metric("Average Age", f"{results['population_metrics']['average_age']}")
    with metric_cols[1]:
        st.metric("Average HbA1c", f"{results['population_metrics']['average_hba1c']}%", delta="Above Target")
    with metric_cols[2]:
        st.metric("High Risk Patients", results['population_metrics']['risk_distribution']['high'])
    with metric_cols[3]:
        st.metric("Total Patients", results['cohort_info']['total_patients'])
    
    # Risk distribution chart
    st.subheader("🎯 Risk Stratification")
    risk_data = results['population_metrics']['risk_distribution']
    risk_df = pd.DataFrame(list(risk_data.items()), columns=['Risk Level', 'Count'])
    
    fig = px.bar(risk_df, x='Risk Level', y='Count', color='Risk Level',
                 color_discrete_map={'high': '#ef4444', 'moderate': '#f59e0b', 'low': '#10b981'},
                 title="Patient Risk Distribution")
    st.plotly_chart(fig, use_container_width=True)
    
    # Care opportunities
    st.subheader("💡 Care Opportunities")
    for opp in results['care_opportunities']:
        alert_class = f"alert-{opp['type']}"
        icon = "🔴" if opp['type'] == 'critical' else "🟡" if opp['type'] == 'warning' else "🔵"
        st.markdown(f"""
        <div class="{alert_class}">
            {icon} <strong>{opp['title']}</strong><br>
            {opp['description']}<br>
            <small>👥 {opp['patient_count']} patients • 💰 Potential savings: {opp['cost_savings']}</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Patient list
    st.subheader("👥 Patient List Preview")
    df = pd.DataFrame(results['patient_list'])
    
    # Style the dataframe
    def highlight_hba1c(val):
        if isinstance(val, (int, float)):
            if val >= 9.0:
                return 'background-color: #fecaca'
            elif val >= 8.5:
                return 'background-color: #fed7aa'
        return ''
    
    styled_df = df.style.applymap(highlight_hba1c, subset=['hba1c'])
    st.dataframe(styled_df, use_container_width=True)
    
    # Geographic distribution
    st.subheader("🗺️ Geographic Distribution")
    geo_df = pd.DataFrame(results['geographic_distribution'])
    
    col1, col2 = st.columns(2)
    with col1:
        fig_pie = px.pie(geo_df, values='count', names='region', 
                        title="Patient Distribution by Region")
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        fig_bar = px.bar(geo_df, x='region', y='count', 
                        title="Patient Count by Region")
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # CareHealth export
    if results.get('carehealth_export', {}).get('ready'):
        st.success("✅ Ready for CareHealth Export")
        export_info = results['carehealth_export']
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.info(f"📋 **List Name:** {export_info['list_name']}\n\n👥 **Patient Count:** {export_info['patient_count']}\n\n⏱️ **Estimated Sync Time:** {export_info['estimated_sync_time']}")
        
        with col2:
            if st.button("📤 Export to CareHealth", type="primary"):
                with st.spinner("Exporting to CareHealth..."):
                    time.sleep(2)
                st.success("🚀 Successfully exported 342 patients to CareHealth!")
                st.balloons()

def display_process_flow():
    """Display the multi-agent process flow"""
    if st.session_state.process_steps:
        st.success("✅ Multi-Agent Process Flow Completed")
        
        for i, step in enumerate(st.session_state.process_steps, 1):
            with st.expander(f"Step {i}: ✅ {step['name']}", expanded=i <= 2):
                st.write(f"**🎯 Description:** {step['description']}")
                
                if step.get('data_points'):
                    st.write("**📊 Data Points Processed:**")
                    for dp in step['data_points']:
                        st.write(f"• {dp}")
                
                if step.get('sql'):
                    st.write("**🔧 SQL/Process Generated:**")
                    st.code(step['sql'], language='sql' if 'SELECT' in step['sql'] else None)
        
        # Processing summary
        st.subheader("⚡ Processing Summary")
        summary_cols = st.columns(3)
        
        with summary_cols[0]:
            st.metric("Steps Completed", len(st.session_state.process_steps))
        with summary_cols[1]:
            st.metric("Query Type", st.session_state.query_type or "N/A")
        with summary_cols[2]:
            st.metric("Processing Time", f"{len(st.session_state.process_steps) * 1.2:.1f}s")
    
    else:
        st.info("🔄 Process flow will appear here during query execution")
        
        st.markdown("""
        ### 🤖 How the Multi-Agent System Works:
        
        #### 🔍 **Individual Patient Data Extraction:**
        1. **Query Analysis** - LLM parses clinical data requirements
        2. **Schema Mapping** - Maps clinical concepts to database tables  
        3. **Data Queries** - Executes specific extraction queries
        4. **Medical History** - Retrieves historical patient data
        5. **Lab Results Mining** - Extracts recent laboratory values
        6. **Data Synthesis** - Combines and formats results
        
        #### 🌐 **Population Health Analytics:**
        1. **NLP Processing** - Interprets population health criteria
        2. **SQL Generation** - Creates complex population queries
        3. **Cohort Retrieval** - Executes across large datasets (125K+ records)
        4. **Statistical Analysis** - Calculates population metrics and risk stratification
        5. **CareHealth Integration** - Formats patient lists for export
        
        #### ⚡ **Powered by Snowflake:**
        - **Real-time processing** of massive healthcare datasets
        - **Sub-second query responses** on complex multi-table joins
        - **HIPAA-compliant** data handling and security
        - **Scalable architecture** supporting 1000s of concurrent users
        """)

def main():
    """Main Streamlit application"""
    init_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 style="color: white; margin: 0;">🏥 Clinical Data Platform</h1>
        <p style="color: #e2e8f0; margin: 0.5rem 0 0 0; font-size: 1.1rem;">AI-Powered Patient Data Mining & Population Health Analytics</p>
        <p style="color: #cbd5e1; margin: 0.25rem 0 0 0; font-size: 0.9rem;">Powered by Snowflake Data Cloud & Multi-Agent AI Orchestration</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs([
        "🔍 Individual Patient Data", 
        "🌐 Population Health Analytics", 
        "⚡ Multi-Agent Process Flow"
    ])
    
    with tab1:
        st.header("🔍 Individual Patient Data Extraction")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("📝 Query Input")
            
            # Sample queries
            sample_queries = [
                "Extract complete clinical profile for diabetic patient Maria Rodriguez",
                "Pull all lab results and medication history for patient PT-789456", 
                "Get comprehensive cardiac risk assessment data for 45-year-old female",
                "Retrieve 5-year medical history with focus on chronic disease management"
            ]
            
            selected_sample = st.selectbox("💡 Sample Queries:", ["Select a sample query..."] + sample_queries)
            
            query_text = st.text_area(
                "🎯 Patient Data Query:",
                value=selected_sample if selected_sample != "Select a sample query..." else "",
                placeholder="Specify patient data to extract (demographics, labs, medications, history...).",
                height=120,
                help="Describe what patient data you want to extract using natural language"
            )
            
            col1a, col1b = st.columns([1, 1])
            with col1a:
                if st.button("🔍 Extract Patient Data", disabled=st.session_state.processing, type="primary"):
                    if query_text.strip() and query_text != "Select a sample query...":
                        process_query("Individual Patient", query_text)
                        st.rerun()
                    else:
                        st.warning("Please enter a query or select a sample query")
            
            with col1b:
                if st.button("🗑️ Clear Results"):
                    st.session_state.results = None
                    st.session_state.process_steps = []
                    st.rerun()
        
        with col2:
            st.subheader("📋 Extracted Clinical Data")
            
            if st.session_state.processing:
                st.info("🔄 Processing patient data extraction...")
            elif st.session_state.results and st.session_state.results.get("type") == "individual":
                display_individual_results(st.session_state.results)
            else:
                st.markdown("""
                <div style="text-align: center; padding: 3rem; color: #64748b;">
                    <h3>💡 Ready to Extract Patient Data</h3>
                    <p>Enter a patient data query to extract comprehensive clinical information from EHR systems</p>
                    <p><small>Powered by AI-driven clinical data extraction with real-time processing</small></p>
                </div>
                """, unsafe_allow_html=True)
    
    with tab2:
        st.header("🌐 Population Health Analytics")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("🎯 Population Query")
            
            # Sample population queries
            pop_queries = [
                "Find all diabetic patients with HbA1c > 8% in the last 6 months",
                "Identify hypertensive patients not on ACE inhibitors or ARBs",
                "List pediatric patients due for immunizations in next 30 days",
                "Find all patients with cardiovascular risk factors over age 50",
                "Locate patients with chronic kidney disease and diabetes",
                "Identify women over 40 who haven't had mammograms in 2 years"
            ]
            
            selected_pop_query = st.selectbox("💡 Sample Population Queries:", ["Select a sample query..."] + pop_queries)
            
            pop_query_text = st.text_area(
                "🎯 Population Analytics Query:",
                value=selected_pop_query if selected_pop_query != "Select a sample query..." else "",
                placeholder="Describe patient population criteria using natural language (e.g., 'diabetic patients with high HbA1c')...",
                height=120,
                help="Use natural language to describe the patient population you want to analyze"
            )
            
            col2a, col2b = st.columns([1, 1])
            with col2a:
                if st.button("📊 Analyze Population", disabled=st.session_state.processing, type="primary"):
                    if pop_query_text.strip() and pop_query_text != "Select a sample query...":
                        process_query("Population Health", pop_query_text)
                        st.rerun()
                    else:
                        st.warning("Please enter a query or select a sample query")
            
            with col2b:
                if st.button("🗑️ Clear Results", key="clear_pop"):
                    st.session_state.results = None
                    st.session_state.process_steps = []
                    st.rerun()
        
        with col2:
            st.subheader("📊 Population Health Results")
            
            if st.session_state.processing:
                st.info("🔄 Processing population health analytics...")
            elif st.session_state.results and st.session_state.results.get("type") == "population":
                display_population_results(st.session_state.results)
            else:
                st.markdown("""
                <div style="text-align: center; padding: 3rem; color: #64748b;">
                    <h3>🌐 Ready for Population Analysis</h3>
                    <p>Enter population criteria to analyze patient cohorts and identify care opportunities</p>
                    <p><small>Results can be exported directly to CareHealth patient management system</small></p>
                </div>
                """, unsafe_allow_html=True)
    
    with tab3:
        st.header("⚡ Multi-Agent Process Flow")
        display_process_flow()

if __name__ == "__main__":
    main()
