"""
Patch Review Module - Enhanced patch visibility, review, and application UI.

This module provides a comprehensive patch review interface with:
- Side-by-side diff view
- Step-by-step workflow
- Visual status indicators
- Direct code application with safety features
"""

import os
import streamlit as st
from typing import Optional, Dict, Any


def parse_multi_file_patch(patch_text: str) -> Dict[str, str]:
    """Split a multi-file unified diff into a dictionary of {filepath: diff}."""
    if not patch_text or patch_text == "No patch suggestions.":
        return {}
    
    files = {}
    current_file = None
    current_lines = []
    
    for line in patch_text.splitlines():
        if line.startswith('+++ '):
            # Save previous file if exists
            if current_file and current_lines:
                files[current_file] = "\n".join(current_lines)
            
            # Start new file
            new_path = line[4:].strip()
            if new_path.startswith('b/'): new_path = new_path[2:]
            current_file = new_path
            current_lines = [f"--- a/{new_path}", line] # Re-add headers
        elif current_file:
            if not line.startswith('--- '): # Skip the old-file header as we re-add it
                current_lines.append(line)
                
    # Save last file
    if current_file and current_lines:
        files[current_file] = "\n".join(current_lines)
        
    return files

def render_patch_review_panel(
    patch_text: str,
    original_code: str,
    patched_code: Optional[str],
    target_path: str,
    patch_root: str = ".",
    patch_file_path: str = "main.py",
    on_apply: callable = None,
    on_edit: callable = None,
    on_download: callable = None,
):
    """
    Enhanced patch review panel with multi-file selection support and precise zipping.
    """
    import re
    from ..core.file_utils import read_file_content
    
    # Use result_id for unique button keys to avoid caching issues
    result_id = st.session_state.get("analysis_results", {}).get("result_id", "default")
    
    # ... rest of CSS ...
    st.markdown("""
    <style>
    .patch-panel { background: #0f172a; border: 1px solid rgba(0, 229, 160, 0.2); border-radius: 14px; padding: 1.5rem; margin: 1rem 0; }
    .patch-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; padding-bottom: 0.75rem; border-bottom: 1px solid rgba(255, 255, 255, 0.1); }
    .patch-title { font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700; color: #00e5a0; margin: 0; }
    .file-chip { background: rgba(0, 102, 255, 0.1); color: #0066ff; padding: 0.2rem 0.6rem; border-radius: 6px; font-size: 0.8rem; font-family: 'DM Mono', monospace; }
    .diff-pane { background: #1a1d24; border-radius: 10px; overflow: hidden; border: 1px solid rgba(255, 255, 255, 0.08); }
    .diff-header { padding: 0.5rem 1rem; background: rgba(255, 255, 255, 0.03); border-bottom: 1px solid rgba(255, 255, 255, 0.08); font-size: 0.8rem; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)
    
    if not patch_text or patch_text == "No patch suggestions.":
        st.info(":material/warning: No patches detected. Try scanning code with known vulnerabilities.")
        return

    # 1. PARSE PATCHES
    file_patches = parse_multi_file_patch(patch_text)
    if not file_patches:
        st.error(":material/error: Malformed patch detected. AI failed to generate valid diff headers.")
        with st.expander("Debug Raw Output"): st.code(patch_text)
        return

    # 2. FILE SELECTION
    st.markdown('<div class="patch-panel">', unsafe_allow_html=True)
    st.markdown('<div class="patch-header"><p class="patch-title">:material/build: Multi-File Security Patch Review</p></div>', unsafe_allow_html=True)
    
    selected_file = st.selectbox(
        "Select file to review fix:",
        options=list(file_patches.keys()),
        format_func=lambda x: f":material/description: {x}",
        key=f"selector_{result_id}"
    )
    
    current_patch = file_patches[selected_file]
    
    # 3. DYNAMIC CONTENT LOADING
    # If it's a directory scan, we load the original from disk
    actual_original = original_code
    if os.path.isdir(target_path):
        full_orig_path = os.path.join(target_path, selected_file)
        if os.path.exists(full_orig_path):
            actual_original = read_file_content(full_orig_path)
    
    # Generate preview
    current_patched_preview = extract_patched_code(actual_original, current_patch)

    # 4. STATS
    additions = current_patch.count('\n+') - 1
    deletions = current_patch.count('\n-') - 1
    st.markdown(f"**Changes:** <span style='color:#00e5a0;'>+{additions}</span> / <span style='color:#ff4060;'>-{deletions}</span>", unsafe_allow_html=True)

    # 5. DIFF VIEW
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='diff-header' style='color:#ff4060;'>Original: {selected_file}</div>", unsafe_allow_html=True)
        st.code(actual_original[:4000], language="python")
    with col2:
        st.markdown(f"<div class='diff-header' style='color:#00e5a0;'>AI Fixed Version</div>", unsafe_allow_html=True)
        if current_patched_preview:
            st.code(current_patched_preview[:4000], language="python")
        else:
            st.warning("Preview generation failed. Review raw diff below.")

    # 6. ACTIONS
    st.markdown("### :material/bolt: Execution")
    a_col1, a_col2, a_col3 = st.columns([1, 1, 2])
    
    with a_col1:
        if st.button(":material/search: Validate Fix", use_container_width=True, key=f"val_{result_id}_{selected_file}"):
            from ..core.file_utils import apply_patch
            res = apply_patch(current_patch, patch_root, dry_run=True)
            if res.get("applied"): st.success(":material/check_circle: Valid!")
            else: st.error(f":material/error: {res.get('message')}")
            
    with a_col2:
        if st.button(":material/check_circle: Apply to File", type="primary", use_container_width=True, key=f"app_{result_id}_{selected_file}"):
            from ..core.file_utils import apply_patch
            res = apply_patch(current_patch, patch_root, dry_run=False)
            if res.get("applied"): 
                st.success(":material/check_circle: Applied!")
                st.session_state.patch_applied = True
            else: st.error(":material/error: Failed")

    with a_col3:
        if st.button(":material/shield: Verify & Unlock Project Download", use_container_width=True, type="secondary", key=f"ver_{result_id}"):
            # 1. Determine scan target
            if st.session_state.get("patch_applied") and target_path:
                # If patches were applied to disk, scan the whole project directory/file
                # Clear memory paste to avoid confusion
                if "scanner_paste_code" in st.session_state: del st.session_state["scanner_paste_code"]
                
                # Setup target for directory/file scan
                if os.path.isdir(target_path):
                    # For directories, we use the path
                    st.session_state.pop("scanner_zip_file", None) # Clear ZIP
                    st.session_state.pop("scanner_uploaded_file", None)
                    st.session_state.scanner_github_repo_path = target_path
                else:
                    # For single files, we clear upload/zip states so it falls back to Paste mode
                    st.session_state.pop("scanner_zip_file", None)
                    st.session_state.pop("scanner_uploaded_file", None)
                    try:
                        with open(target_path, "r") as f:
                            st.session_state.scanner_paste_code = f.read()
                    except:
                        st.session_state.scanner_paste_code = current_patched_preview
            else:
                # If not applied to disk, use the in-memory preview
                st.session_state.pop("scanner_zip_file", None)
                st.session_state.pop("scanner_uploaded_file", None)
                st.session_state.scanner_paste_code = current_patched_preview or original_code

            # 2. Trigger Scan Request
            st.session_state.run_scan_request = True
            st.session_state.patch_verified = True
            
            # 3. Force clean state for redirection
            from ..utils.state import AppState
            st.balloons()
            st.success(":material/search: Security verification initiated...")
            import time
            time.sleep(1)
            AppState.set_page(":material/analytics: Security Scanner")

    # Final Project ZIP Download
    if st.session_state.get("patch_verified"):
        st.markdown("---")
        st.markdown("### :material/folder: Export Secured Version")
        from ..core.file_utils import create_zip_from_any
        try:
            zip_bytes = create_zip_from_any(target_path)
            st.download_button(
                ":material/download: Download All Files (ZIP)",
                data=zip_bytes,
                file_name=f"secured_{os.path.basename(target_path)}.zip" if os.path.isdir(target_path) else f"secured_{selected_file}.zip",
                mime="application/zip",
                type="primary",
                use_container_width=True,
                key=f"zip_dl_{result_id}" # Use result_id to ensure a fresh button for every scan
            )
        except Exception as e:
            st.error(f"ZIP Error: {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)
    with st.expander("View Raw Patch (Unified Diff)"):
        st.code(current_patch, language="diff")

        if st.button(
            ":material/sync: Reset",
            key="patch_reset_btn",
            use_container_width=True,
        ):
            st.session_state.patch_review_step = 0
            st.session_state.patch_validated = False
            st.session_state.patch_applied = False
            st.session_state.patch_verified = False
            st.session_state.patch_error = None
            st.session_state.patch_edited_text = patch_text
            st.success("Patch workflow reset.")
            st.rerun()

    
    st.markdown('</div>', unsafe_allow_html=True)


def extract_patched_code(original_code: str, patch_text: str) -> Optional[str]:
    """
    Apply patch to code in memory and return the patched version.
    This reconstructs the entire file properly.
    
    Args:
        original_code: Original source code
        patch_text: Unified diff patch
        
    Returns:
        Patched code or None if patch cannot be applied
    """
    import re
    
    if not original_code or not patch_text:
        return None
        
    orig_lines = original_code.splitlines(keepends=True)
    patch_lines = patch_text.splitlines()
    
    # Parse hunks
    hunks = []
    for line in patch_lines:
        if line.startswith('@@'):
            hunks.append({'header': line, 'lines': []})
        elif hunks and not line.startswith('---') and not line.startswith('+++'):
            hunks[-1]['lines'].append(line)
            
    if not hunks:
        return None

    new_lines = []
    orig_index = 0
    
    for hunk in hunks:
        match = re.match(r"@@ -(\d+),(\d+) \+(\d+),(\d+) @@", hunk['header'])
        if not match:
            continue
        old_start = int(match.group(1)) - 1
        
        # Add unchanged lines before the hunk
        while orig_index < old_start and orig_index < len(orig_lines):
            new_lines.append(orig_lines[orig_index])
            orig_index += 1
            
        # Apply hunk lines
        for hl in hunk['lines']:
            if hl.startswith('+') and not hl.startswith('+++'):
                new_lines.append(hl[1:] + '\n')
            elif hl.startswith('-') and not hl.startswith('---'):
                orig_index += 1
            else:
                # context line
                if orig_index < len(orig_lines):
                    new_lines.append(orig_lines[orig_index])
                    orig_index += 1
                    
    # Append remaining original lines
    while orig_index < len(orig_lines):
        new_lines.append(orig_lines[orig_index])
        orig_index += 1
        
    return ''.join(new_lines)