import streamlit as st
import pandas as pd
from ..core.infra_engine import run_infra_scan

def render_infra_tab(model_selection, llm_temperature):
    """Render the Infrastructure Reconnaissance tab (Shodan-style)."""
    st.title("🌐 Infrastructure Reconnaissance")
    st.markdown("Scan public-facing assets to identify open services and potential misconfigurations.")

    target = st.text_input("Enter Target (Domain or IP)", placeholder="example.com or 192.168.1.1")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        scan_button = st.button("🚀 Start Recon", type="primary", use_container_width=True)
    
    if scan_button and target:
        with st.status(f"🔍 Scanning {target}...", expanded=True) as status:
            status.update(label="📡 Probing ports and banners...", state="running")
            results = run_infra_scan(target)
            
            if "error" in results:
                st.error(results["error"])
                return

            status.update(label="🧠 Analyzing findings with AI...", state="running")
            
            # AI Analysis of the banners
            llm = None
            findings_str = "\n".join([f"Port {f['port']}: {f['banner']}" for f in results['findings']])
            
            prompt = f"""
            As a security expert, analyze these service banners discovered on {target} ({results['ip']}):
            {findings_str}
            
            Identify:
            1. Likely software and versions.
            2. Potential vulnerabilities (CVEs) associated with these versions.
            3. Risk of exposure.
            """
            
            ai_analysis = llm.invoke(prompt).content if llm else "AI Analysis unavailable."
            status.update(label="✅ Recon Complete!", state="complete")

        # Display Results
        st.success(f"Discovered {len(results['findings'])} open services on {results['ip']}")
        
        tab1, tab2 = st.tabs(["📊 Service Map", "🧠 AI Intelligence Report"])
        
        with tab1:
            if results['findings']:
                df = pd.DataFrame(results['findings'])
                st.table(df)
            else:
                st.info("No open services found on common ports.")
                
        with tab2:
            st.markdown(ai_analysis)

    elif scan_button:
        st.warning("Please enter a valid target.")
