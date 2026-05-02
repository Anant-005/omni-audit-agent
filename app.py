import streamlit as st
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# Load environment variables
load_dotenv()

# 1. Page Configuration (Professional UI)
st.set_page_config(page_title="Omni-Audit Scanner", page_icon="🛡️", layout="wide")

# Custom CSS for a clean, professional corporate look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    h1, h2, h3 { color: #2c3e50; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stButton>button { background-color: #0056b3; color: white; border-radius: 4px; }
    .stButton>button:hover { background-color: #004494; color: white; }
    .stTextInput>div>div>input { border: 1px solid #ced4da; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Setup Gemini Model
try:
    # Using Gemini 2.5 Flash for optimal reasoning and speed
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
except Exception as e:
    st.error(f"Failed to initialize Gemini API. Check your .env file. Error: {e}")

# 3. Define the LangChain LCEL Pipeline
# This replaces the fragile Agent wrappers with a robust, modern LangChain structure
audit_prompt = PromptTemplate.from_template(
    """
    You are a Senior Security Auditor. Review the following code file named '{file_name}'.
    
    File Content:
    {file_content}
    
    Perform a strict, professional security audit:
    1. Identify hardcoded API keys, secrets, or database credentials.
    2. Check for insecure coding practices (e.g., eval(), shell=True, unparameterized queries).
    3. Assign a Risk Level: [Critical, High, Medium, Low, Safe].
    4. Provide immediate remediation steps if vulnerabilities are found.
    
    If the file is clean, respond exactly with: "Status: Secure. No vulnerabilities detected."
    Keep the output structured using markdown.
    """
)

# The modern LCEL Chain: Prompt -> LLM
audit_chain = audit_prompt | llm

# 4. Streamlit UI Design
st.title("🛡️ Omni-Audit: Automated Security Scanner")
st.markdown("Scan local repositories for exposed credentials and insecure coding patterns using LangChain and Gemini.")
st.markdown("---")

# Input for the local directory path
target_path = st.text_input("Target Directory Path:", placeholder="e.g., C:/Users/YourName/Desktop/Project")

if st.button("Run Security Audit"):
    if target_path and os.path.exists(target_path):
        # Identify relevant files to scan
        valid_extensions = ('.py', '.js', '.env', '.json', '.yaml', '.yml', '.txt')
        files_to_scan = [os.path.join(target_path, f) for f in os.listdir(target_path) 
                         if f.endswith(valid_extensions)]
        
        if not files_to_scan:
            st.warning("No scannable code or config files found in the specified directory.")
        else:
            st.info(f"Scan initialized. Analyzing {len(files_to_scan)} files...")
            st.markdown("---")

            # Audit Loop
            for file_path in files_to_scan:
                file_name = os.path.basename(file_path)
                
                with st.expander(f"📄 Audit Report: {file_name}", expanded=True):
                    try:
                        # Read the file natively
                        with open(file_path, 'r', encoding='utf-8') as f:
                            file_content = f.read()
                        
                        # Execute the LangChain pipeline
                        response = audit_chain.invoke({
                            "file_name": file_name,
                            "file_content": file_content
                        })
                        
                        # Display the AI's response
                        st.markdown(response.content)
                        
                    except UnicodeDecodeError:
                        st.error("Error: Could not read file. Ensure it is a valid text/code file.")
                    except Exception as e:
                        st.error(f"Audit failed for {file_name}: {e}")
    else:
        st.error("Invalid directory path. Please check the path and try again.")