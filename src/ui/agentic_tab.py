"""
Agentic PatchOps Tab (3-Agent Cooperative System)
=================================================
Interactive UI for Open Agent Hackathon 2026:
- PlannerAgent (OWASP Triage & Execution Scoping)
- SpecialistAgent (Zetaris Data Fabric & Meterless Nightshift NVIDIA models)
- EvaluatorAgent (Critic, AST Verification & Dynamic Self-Healing)
- Meterless H-MEM (Hierarchical Memory across critique iterations)
- Zetaris Virtualized Data Layer
"""

import os
import streamlit as st
from datetime import datetime

from src.core.multi_agent.orchestrator import MultiAgentOrchestrator
from src.core.hmem_engine import get_hmem_engine
from src.core.zetaris_connector import get_zetaris_connector
from src.core.nightshift_client import get_nightshift_client
from src.core.file_utils import apply_patch

def render_agentic_tab():
    st.markdown("""
        <div style="background: linear-gradient(135deg, #0d121f 0%, #151d30 100%); padding: 1.5rem; border-radius: 16px; border: 1px solid rgba(0, 229, 160, 0.2); margin-bottom: 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h2 style="margin: 0; color: #00e5a0; font-family: 'Syne', sans-serif;">🤖 VeriFAI Agentic PatchOps</h2>
                    <p style="margin: 0.35rem 0 0; color: #8b909e; font-size: 0.95rem;">
                        Autonomous 3-Agent Security Remediation Loop with Dynamic Peer Critique & Self-Healing
                    </p>
                </div>
                <div style="text-align: right;">
                    <span style="background: rgba(0, 229, 160, 0.15); color: #00e5a0; padding: 0.35rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">
                        Open Agent Hackathon 2026
                    </span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 1. Mandatory Sponsor Tech Telemetry Bar
    col_sponsor1, col_sponsor2, col_sponsor3 = st.columns(3)
    
    nightshift = get_nightshift_client()
    hmem = get_hmem_engine()
    zetaris = get_zetaris_connector()

    with col_sponsor1:
        st.markdown(f"""
            <div style="background: #101624; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 1rem;">
                <div style="color: #76b900; font-weight: 700; font-size: 0.85rem; text-transform: uppercase;">Primary AI Provider</div>
                <div style="color: #ffffff; font-weight: 600; font-size: 1rem; margin-top: 0.25rem;">Meterless Nightshift</div>
                <div style="color: #8b909e; font-size: 0.8rem; margin-top: 0.2rem;">Model: <code>{nightshift.default_model}</code></div>
                <div style="margin-top: 0.5rem;"><span style="color: #00e5a0; font-size: 0.75rem;">● NVIDIA Inference Active</span></div>
            </div>
        """, unsafe_allow_html=True)

    with col_sponsor2:
        st.markdown(f"""
            <div style="background: #101624; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 1rem;">
                <div style="color: #00b4d8; font-weight: 700; font-size: 0.85rem; text-transform: uppercase;">Intelligence Engine</div>
                <div style="color: #ffffff; font-weight: 600; font-size: 1rem; margin-top: 0.25rem;">Meterless H-MEM Engine</div>
                <div style="color: #8b909e; font-size: 0.8rem; margin-top: 0.2rem;">Hierarchical Memory (3-Tier)</div>
                <div style="margin-top: 0.5rem;"><span style="color: #00e5a0; font-size: 0.75rem;">● {len(hmem.episodic_memory)} Stored Episodes</span></div>
            </div>
        """, unsafe_allow_html=True)

    with col_sponsor3:
        st.markdown(f"""
            <div style="background: #101624; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 1rem;">
                <div style="color: #9d4edd; font-weight: 700; font-size: 0.85rem; text-transform: uppercase;">Unified Data Layer</div>
                <div style="color: #ffffff; font-weight: 600; font-size: 1rem; margin-top: 0.25rem;">Zetaris Data Fabric</div>
                <div style="color: #8b909e; font-size: 0.8rem; margin-top: 0.2rem;">Virtualized Code & Advisory Lake</div>
                <div style="margin-top: 0.5rem;"><span style="color: #00e5a0; font-size: 0.75rem;">● Workspace: {zetaris.workspace_id}</span></div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Control & Target Selection
    st.subheader("1. Target Vulnerability Selection")
    
    preset_targets = {
        "SQLite SQL Injection (OWASP A03:2021)": "vuln_test.py",
        "Flask Debug Misconfiguration (OWASP A05:2021)": "sample_misconfig_test.py"
    }

    selected_label = st.selectbox(
        "Choose Target Code Asset:",
        list(preset_targets.keys())
    )
    target_rel_path = preset_targets[selected_label]
    target_full_path = os.path.abspath(target_rel_path)

    # Preview Code
    if os.path.exists(target_full_path):
        with open(target_full_path, "r", encoding="utf-8", errors="ignore") as f:
            target_code = f.read()
        with st.expander("📄 View Target Code Asset", expanded=False):
            st.code(target_code, language="python")

    # Run Button
    col_btn, col_info = st.columns([1, 2])
    with col_btn:
        start_btn = st.button("🚀 Launch 3-Agent Cooperative Loop", type="primary", use_container_width=True)

    with col_info:
        st.caption("Executes: **PlannerAgent** (OWASP Scoping) ➔ **SpecialistAgent** (Zetaris + Nightshift NVIDIA) ➔ **EvaluatorAgent** (Critic & Self-Healing AST Verification).")

    # 3. Dynamic Execution Stream
    if start_btn:
        st.markdown("---")
        st.subheader("2. Real-Time Multi-Agent Collaboration Stream")

        status_container = st.empty()
        debate_container = st.container()

        # Build mock/parsed finding matching the target
        if "sql" in target_rel_path.lower():
            findings = [{
                "check_id": "python.sqlite3.security.sql-injection",
                "start": {"line": 6, "col": 5},
                "extra": {
                    "message": "Detected unsafe dynamic string formatting in database query.",
                    "severity": "ERROR",
                    "metadata": {"owasp": "A03:2021-Injection", "cwe": "CWE-89"}
                }
            }]
        else:
            findings = [{
                "check_id": "python.flask.security.audit.hardcoded-config.avoid_hardcoded_config_DEBUG",
                "start": {"line": 6, "col": 1},
                "extra": {
                    "message": "Hardcoded variable DEBUG detected in Flask application.",
                    "severity": "WARNING",
                    "metadata": {"owasp": "A05:2021-Security Misconfiguration", "cwe": "CWE-489"}
                }
            }]

        orchestrator = MultiAgentOrchestrator(max_critique_rounds=3)
        pipeline = orchestrator.run_remediation_pipeline(target_full_path, findings)

        last_diff = None
        last_patched_code = None

        with debate_container:
            for event in pipeline:
                evt_type = event.get("type")
                
                if evt_type == "status":
                    status_container.info(event["message"])
                
                elif evt_type == "agent_action":
                    agent = event.get("agent")
                    iter_str = f" • Attempt #{event['iteration']}" if "iteration" in event else ""
                    
                    if "Planner" in agent:
                        st.markdown(f"📋 **{agent}**{iter_str}: *{event['message']}*")
                    elif "Specialist" in agent:
                        st.markdown(f"🤖 **{agent}**{iter_str}: *{event['message']}*")
                    elif "Evaluator" in agent:
                        st.markdown(f"🧐 **{agent} (Critic)**{iter_str}: *{event['message']}*")
                
                elif evt_type == "plan_ready":
                    plan = event.get("plan", {})
                    st.success(f"✅ Strategy formulated: {len(plan.get('execution_order', []))} vulnerability prioritized for remediation.")
                
                elif evt_type == "patch_generated":
                    last_diff = event.get("diff")
                    with st.expander(f"📝 Drafted Patch ({event.get('provider')} - {event.get('model')})", expanded=True):
                        st.code(last_diff, language="diff")
                
                elif evt_type == "critique_result":
                    approved = event.get("approved")
                    score = event.get("score")
                    critique = event.get("critique")
                    if approved:
                        st.markdown(f"""
                            <div style="background: rgba(0, 229, 160, 0.1); border-left: 4px solid #00e5a0; padding: 0.75rem 1rem; border-radius: 8px; margin: 0.5rem 0;">
                                <strong style="color: #00e5a0;">✅ CRITIC APPROVAL (Score {score}/100)</strong><br>
                                <span style="color: #e8eaf0; font-size: 0.9rem;">{critique}</span>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div style="background: rgba(255, 64, 96, 0.1); border-left: 4px solid #ff4060; padding: 0.75rem 1rem; border-radius: 8px; margin: 0.5rem 0;">
                                <strong style="color: #ff4060;">❌ CRITIC REJECTION (Score {score}/100)</strong><br>
                                <span style="color: #e8eaf0; font-size: 0.9rem;">{critique}</span>
                            </div>
                        """, unsafe_allow_html=True)
                
                elif evt_type == "self_healing_trigger":
                    st.warning(event.get("message"))
                
                elif evt_type == "workflow_complete":
                    summary = event.get("summary")
                    st.balloons()
                    st.markdown("""
                        <div style="background: #131b2e; border: 1px solid #00e5a0; border-radius: 12px; padding: 1.25rem; margin-top: 1rem;">
                            <h4 style="color: #00e5a0; margin: 0 0 0.5rem;">🎉 Multi-Agent Remediation Verified & Complete</h4>
                            <p style="color: #8b909e; font-size: 0.9rem; margin: 0;">
                                • Vulnerability neutralized without syntax or AST regressions.<br>
                                • Hierarchical Memory updated with verified pattern.<br>
                                • Audit log synced to Zetaris Virtual Data Fabric.
                            </p>
                        </div>
                    """, unsafe_allow_html=True)

        # 4. Apply Patch Button
        if last_diff:
            st.markdown("<br>", unsafe_allow_html=True)
            col_apply, col_reset = st.columns([1, 2])
            with col_apply:
                if st.button("💾 Apply Verified Patch to File", type="primary", use_container_width=True):
                    target_dir = os.path.dirname(os.path.abspath(target_full_path))
                    res = apply_patch(last_diff, target_dir)
                    if res.get("applied"):
                        st.success(f"Patch applied successfully to `{os.path.basename(target_full_path)}`!")
                    else:
                        st.error(f"Failed to apply patch: {res.get('error')}")
