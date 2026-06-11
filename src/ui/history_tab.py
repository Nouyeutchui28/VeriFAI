import streamlit as st
import pandas as pd
from datetime import datetime
from .api_client import get_api_client

def render_history_tab():
    """Render the scan history explorer tab."""
    st.markdown("### 🕒 Scan History Explorer")
    st.markdown("Browse and review previous security analysis results stored in InsForge.")

    api_client = get_api_client()
    
    try:
        with st.spinner("Fetching scan history..."):
            # Use user-specific history method
            response = api_client.get_scan_history_insforge(limit=50)
            
            if not response:
                st.info("No scans found in your history. Start by running a new scan!")
                return

            # Convert to DataFrame for easier display
            df = pd.DataFrame(response)
            
            # Format display columns
            display_df = df.copy()
            if 'start_time' in display_df.columns:
                display_df['start_time'] = pd.to_datetime(display_df['start_time']).dt.strftime('%Y-%m-%d %H:%M')
            
            # Reorder and rename columns for UI
            cols_to_show = ['project_name', 'status', 'start_time']
            available_cols = [c for c in cols_to_show if c in display_df.columns]
            display_df = display_df[available_cols]
            
            # Display history table
            selected_scan_id = None
            
            st.markdown('<div class="scanner-panel">', unsafe_allow_html=True)
            
            # Custom selection using a selectbox for now
            scan_options = {f"{row['project_name']} ({row['start_time']})": row['id'] for _, row in df.iterrows()}
            selected_label = st.selectbox("Select a scan to review", options=list(scan_options.keys()))
            selected_scan_id = scan_options[selected_label]
            
            if st.button("📂 Load Results", type="primary", use_container_width=True):
                with st.spinner("Loading analysis results..."):
                    # Use InsForge specific result fetch
                    results_res = api_client.get_results_insforge(selected_scan_id)
                    
                    if "error" not in results_res:
                        # Reconstruct the analysis results state
                        st.session_state.analysis_results = {
                            "result_id": results_res.get("id"),
                            "code_content": results_res.get("code_snippet"),
                            "llm_analysis": results_res.get("llm_analysis"),
                            "semgrep_results": results_res.get("semgrep_json"),
                            "patch_suggestions": results_res.get("patches"),
                            "fixed_code": results_res.get("fixed_code"),
                            "severity_count": results_res.get("severity_count"),
                            "target_path": "remote_storage"
                        }
                        st.success(f"✅ Loaded results for: {selected_label}")
                        st.session_state.current_page = "📊 Security Scanner"
                        st.rerun()
                    else:
                        st.error(f"Could not load results: {results_res['error']}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )

    except Exception as e:
        st.error(f"Error loading history: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
