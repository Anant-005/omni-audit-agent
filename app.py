import streamlit as st
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# Load environment variables
load_dotenv()

# 1. Page Configuration (Professional UI)
st.set_page_config(page_title="Omni-Audit Web", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    h1, h2, h3 { color: #2c3e50; font-family: 'Segoe UI', sans-serif; }
    .stButton>button { background-color: #0056b3; color: white; width: 100%; border-radius: 4px; border: none; height: 3em;}
    .stButton>button:hover { background-color: #004494; color: white; }
    </style>
    """, unsafe_allow_html=True)

# 2. Setup Gemini 2.5 Flash
try:
    # Model pulls GOOGLE_API_KEY from Streamlit Secrets automatically in cloud
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
except Exception as e:
    st.error("Missing API Key. Add GOOGLE_API_KEY to your Streamlit Secrets.")

# 3. LangChain LCEL Audit Logic
audit_prompt = PromptTemplate.from_template(
    """
    You are a Senior Security Auditor. Review the following code file named '{file_name}'.
    
    File Content:
    {file_content}
    
    Perform a strict, professional security audit:
    1. Identify hardcoded API keys, secrets, or database credentials.
    2. Check for insecure coding practices (e.g., eval(), shell=True).
    3. Assign a Risk Level: [Critical, High, Medium, Low, Safe].
    4. Provide immediate remediation steps.
    
    Keep the output structured using markdown.
    """
)

audit_chain = audit_prompt | llm

# 4. Streamlit UI Design
st.title("🛡️ Omni-Audit: Web Security Agent")
st.markdown("### Autonomous Intelligence for Secure Code Deployment")

# --- UPDATED TEXTBOX / UPLOADER WITH FILE TYPES ---
uploaded_files = st.file_uploader(
    "Upload project files for audit (Supported: .py, .js, .ts, .env, .json, .yaml, .txt)", 
    accept_multiple_files=True,
    help="Drag and drop your code files here to scan for credentials and vulnerabilities."
)

if st.button("Initiate Sovereign Cloud Audit"):
    if not uploaded_files:
        st.warning("Protocol Warning: Please upload at least one file to initiate the scan.")
    else:
        st.info(f"Audit in progress. Analyzing {len(uploaded_files)} files...")
        st.markdown("---")
        
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            
            with st.expander(f"📄 Audit Report: {file_name}", expanded=True):
                try:
                    # Extract text content from the uploaded file
                    file_bytes = uploaded_file.getvalue()
                    stringio = file_bytes.decode("utf-8")
                    
                    # Execute the Audit Chain
                    response = audit_chain.invoke({
                        "file_name": file_name,
                        "file_content": stringio
                    })
                    
                    st.markdown(response.content)
                    
                except UnicodeDecodeError:
                    st.error(f"Error: {file_name} appears to be a binary file. Only text-based code files can be audited.")
                except Exception as e:
                    st.error(f"Audit failure for {file_name}: {e}")

st.markdown("---")
st.caption("Omni-Audit Agent | Powering Secure AI/ML Development at Bennett University")
