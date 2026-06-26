"""
Reusable UI components for consistent design and UX across the app.
"""
import streamlit as st
from typing import Optional, List, Dict, Callable, Any

# ============================================================================
# LOADING & SKELETON STATES
# ============================================================================

def render_loading_skeleton(height: int = 200, count: int = 1) -> None:
    """Render skeleton loader placeholders."""
    for _ in range(count):
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(90deg, #1e293b 0%, #334155 50%, #1e293b 100%);
                background-size: 200% 100%;
                animation: loading 1.5s infinite;
                height: {height}px;
                border-radius: 8px;
                margin-bottom: 1rem;
            "></div>
            <style>
            @keyframes loading {{
                0% {{ background-position: 200% 0; }}
                100% {{ background-position: -200% 0; }}
            }}
            </style>
            """,
            unsafe_allow_html=True
        )


def render_loading_pulse(text: str = "Loading...") -> None:
    """Render a pulsing loading indicator."""
    st.markdown(
        f"""
        <div style="
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        ">
            <div style="
                width: 12px;
                height: 12px;
                background: #2563eb;
                border-radius: 50%;
                animation: pulse 1s infinite;
                margin-right: 0.5rem;
            "></div>
            <span style="color: #f8fafc; font-size: 0.95rem;">{text}</span>
        </div>
        <style>
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


# ============================================================================
# METRIC & STAT CARDS
# ============================================================================

def render_metric_card(
    label: str,
    value: str | int,
    icon: str = ":material/analytics:",
    change: Optional[str] = None,
    change_type: str = "neutral"  # "positive", "negative", "neutral"
) -> None:
    """
    Render a metric card with icon and optional trend.

    Args:
        label: Card label
        value: Main metric value
        icon: Emoji icon
        change: Percentage or absolute change (e.g., "+5%", "-10")
        change_type: Color indication - positive (green), negative (red), neutral (gray)
    """
    change_color = {
        "positive": "#22c55e",
        "negative": "#ef4444",
        "neutral": "#94a3b8"
    }.get(change_type, "#94a3b8")

    change_html = f"""
        <div style="
            color: {change_color};
            font-size: 0.85rem;
            margin-top: 0.5rem;
            font-weight: 600;
        ">{change}</div>
    """ if change else ""

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #334155;
            display: flex;
            flex-direction: column;
            height: 100%;
        ">
            <div style="
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 0.5rem;
            ">
                <span style="font-size: 1.5rem;">{icon}</span>
                <span style="
                    background: rgba(37, 99, 235, 0.1);
                    padding: 0.25rem 0.5rem;
                    border-radius: 4px;
                    color: #60a5fa;
                    font-size: 0.75rem;
                ">NEW</span>
            </div>
            <div style="
                color: #94a3b8;
                font-size: 0.85rem;
                margin-bottom: 0.5rem;
            ">{label}</div>
            <div style="
                color: #f8fafc;
                font-size: 2rem;
                font-weight: 700;
                margin-bottom: 0.5rem;
            ">{value}</div>
            {change_html}
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================================
# RESULT & CONTENT CARDS
# ============================================================================

def render_status_badge(status: str, label: str = "") -> None:
    """Render a professional status badge."""
    status_colors = {
        "active": "#00e676",
        "inactive": "#ff3b3b",
        "analyzing": "#00e5ff",
        "complete": "#00e676",
        "error": "#ff3b3b",
        "warning": "#f59e0b",
    }
    color = status_colors.get(status.lower(), "#8b9bb4")
    display_label = label or status.upper()

    st.markdown(f"""
    <div style="
        display: inline-flex;
        align-items: center;
        background-color: rgba(0, 229, 255, 0.03);
        border: 1px solid {color};
        border-radius: 4px;
        padding: 0.4rem 0.8rem;
        color: {color};
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        line-height: 1;
    ">
        <span style="
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: {color};
            margin-right: 8px;
        "></span>
        {display_label}
    </div>
    """, unsafe_allow_html=True)


def render_info_banner(message: str, type: str = "info") -> None:
    """Render information banner."""
    colors = {
        "info": ("00e5ff", ":material/info:"),
        "success": ("00e676", ":material/check_circle:"),
        "warning": ("f59e0b", ":material/warning:"),
        "error": ("ff3b3b", ":material/error:")
    }
    color, icon = colors.get(type, ("00e5ff", ":material/info:"))

    st.markdown(f"""
    <div style="
        background-color: rgba({int(color[:2], 16)}, {int(color[2:4], 16)}, {int(color[4:], 16)}, 0.1);
        border: 1px solid #{color};
        border-radius: 6px;
        padding: 1rem;
        margin-bottom: 1rem;
        color: #{color};
    ">{icon} {message}</div>
    """, unsafe_allow_html=True)


def render_settings_group(title: str, icon: str = ":material/settings:", description: str = "") -> None:
    """Render settings group header."""
    st.markdown(f"""
    <div style="margin-bottom: 1rem;">
        <p style="
            font-size: 0.9rem;
            font-weight: 600;
            color: #e2e8f0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin: 0 0 0.5rem 0;
        ">{icon} {title}</p>
        {f'<p style="font-size: 0.85rem; color: #8b9bb4; margin: 0;">{description}</p>' if description else ''}
    </div>
    """, unsafe_allow_html=True)


def render_action_button(text: str, icon: str = "→") -> bool:
    """Render styled action button."""
    return st.button(f"{icon} {text}", use_container_width=True, type="primary")


def render_result_card(
    title: str,
    content: str,
    icon: str = ":material/search:",
    severity: Optional[str] = None,
    collapsible: bool = False
) -> None:
    """Render a result card with severity indicator."""
    severity_colors = {
        "critical": "#ff3b3b",
        "high": "#f59e0b",
        "medium": "#f59e0b",
        "low": "#00e676",
    }
    color = severity_colors.get(severity or "neutral", "#00e5ff")

    if collapsible:
        with st.expander(f"{icon} {title}", expanded=False):
            st.markdown(content)
    else:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #0f182b 0%, #070b14 100%);
                padding: 1.5rem;
                border-radius: 6px;
                border: 1px solid #1d2b3f;
                border-left: 4px solid {color};
            ">
                <div style="
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    margin-bottom: 0.75rem;
                ">
                    <span style="font-size: 1.25rem;">{icon}</span>
                    <span style="
                        color: #e2e8f0;
                        font-weight: 600;
                        font-size: 1rem;
                    ">{title}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(content)


# ============================================================================
# BUTTONS & ACTIONS
# ============================================================================

def render_action_button(
    label: str,
    icon: str = "",
    onclick: Optional[Callable] = None,
    variant: str = "primary",  # "primary", "secondary", "danger", "success"
    width: str = "auto",
    disabled: bool = False
) -> bool:
    """
    Render styled action button.

    Args:
        label: Button label
        icon: Icon emoji
        onclick: Callback function
        variant: Button variant for styling
        width: Button width
        disabled: Whether button is disabled

    Returns:
        Whether button was clicked
    """
    colors = {
        "primary": ("#2563eb", "#1d4ed8"),
        "secondary": ("#64748b", "#475569"),
        "danger": ("#dc2626", "#b91c1c"),
        "success": ("#10b981", "#059669"),
    }
    bg_color, hover_color = colors.get(variant, colors["primary"])

    button_label = f"{icon} {label}" if icon else label

    return st.button(
        button_label,
        disabled=disabled,
        use_container_width=True if width == "full" else False
    )


# ============================================================================
# INFO & STATUS BANNERS
# ============================================================================

def render_info_banner(
    message: str,
    type: str = "info",  # "info", "warning", "error", "success"
    dismissible: bool = False,
    icon: Optional[str] = None
) -> None:
    """
    Render an info banner with customizable styling.

    Args:
        message: Banner message
        type: Banner type for color coding
        dismissible: Whether user can dismiss banner
        icon: Custom icon emoji
    """
    icons = {
        "info": ":material/info:",
        "warning": ":material/warning:",
        "error": ":material/error:",
        "success": ":material/check_circle:"
    }
    colors = {
        "info": "#3b82f6",
        "warning": "#f59e0b",
        "error": "#ef4444",
        "success": "#10b981"
    }

    display_icon = icon or icons.get(type, ":material/info:")
    display_color = colors.get(type, "#3b82f6")

    st.markdown(
        f"""
        <div style="
            background: rgba({hex_to_rgb(display_color)}, 0.1);
            border-left: 4px solid {display_color};
            padding: 1rem;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        ">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 1.25rem;">{display_icon}</span>
                <span style="color: #f8fafc; font-size: 0.95rem;">{message}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================================
# SETTINGS GROUP
# ============================================================================

def render_settings_group(
    title: str,
    icon: str = ":material/settings:",
    description: Optional[str] = None
) -> None:
    """
    Render a settings group header.

    Args:
        title: Group title
        icon: Group icon
        description: Optional description
    """
    st.markdown(
        f"""
        <div style="
            border-top: 1px solid #334155;
            padding-top: 1.5rem;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
        ">
            <div style="
                display: flex;
                align-items: center;
                gap: 0.5rem;
                margin-bottom: 0.5rem;
            ">
                <span style="font-size: 1.25rem;">{icon}</span>
                <span style="
                    color: #f8fafc;
                    font-weight: 600;
                    font-size: 1.1rem;
                ">{title}</span>
            </div>
            {f'<p style="color: #94a3b8; font-size: 0.85rem; margin: 0;">{description}</p>' if description else ''}
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================================
# CODE DISPLAY
# ============================================================================

def render_code_block(
    code: str,
    language: str = "python",
    show_line_numbers: bool = True,
    height: int = 300
) -> None:
    """
    Render code with syntax highlighting and line numbers.

    Args:
        code: Code content
        language: Programming language for syntax highlighting
        show_line_numbers: Whether to show line numbers
        height: Container height in pixels
    """
    st.code(code, language=language)


# ============================================================================
# PROGRESS & STATUS
# ============================================================================

def render_progress_step(
    step_number: int,
    step_name: str,
    status: str = "pending",  # "pending", "running", "completed", "error"
    details: Optional[str] = None
) -> None:
    """
    Render a step in a progress flow.

    Args:
        step_number: Step number
        step_name: Step name/label
        status: Current status
        details: Additional details
    """
    status_colors = {
        "pending": "#94a3b8",
        "running": "#2563eb",
        "completed": "#10b981",
        "error": "#ef4444"
    }
    status_icons = {
        "pending": ":material/hourglass_empty:",
        "running": ":material/play_arrow:",
        "completed": ":material/check_circle:",
        "error": ":material/error:"
    }

    color = status_colors.get(status, "#94a3b8")
    icon = status_icons.get(status, "•")

    st.markdown(
        f"""
        <div style="
            display: flex;
            align-items: flex-start;
            gap: 1rem;
            padding: 1rem;
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border-radius: 8px;
            margin-bottom: 0.5rem;
            border: 1px solid #334155;
        ">
            <div style="
                color: {color};
                font-size: 1.25rem;
                min-width: 2rem;
                text-align: center;
            ">{icon}</div>
            <div style="flex: 1;">
                <div style="
                    color: #f8fafc;
                    font-weight: 600;
                    margin-bottom: 0.25rem;
                ">Step {step_number}: {step_name}</div>
                {f'<div style="color: #94a3b8; font-size: 0.85rem;">{details}</div>' if details else ''}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================================
# BREADCRUMB NAVIGATION
# ============================================================================

def render_breadcrumb(path: List[tuple]) -> None:
    """
    Render breadcrumb navigation.

    Args:
        path: List of (label, page_name) tuples
    """
    breadcrumb_html = ""
    for i, (label, page_name) in enumerate(path):
        separator = " › " if i > 0 else ""
        breadcrumb_html += f'{separator}<span style="color: #60a5fa; cursor: pointer;">{label}</span>'

    st.markdown(
        f"""
        <div style="
            color: #94a3b8;
            font-size: 0.85rem;
            margin-bottom: 1.5rem;
        ">
            {breadcrumb_html}
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def hex_to_rgb(hex_color: str) -> str:
    """Convert hex color to RGB format."""
    hex_color = hex_color.lstrip("#")
    return ",".join(str(int(hex_color[i:i+2], 16)) for i in (0, 2, 4))


def create_severity_badge(severity: str, compact: bool = False) -> str:
    """Create a severity badge HTML."""
    severity_map = {
        "critical": ("#dc2626", "CRITICAL"),
        "high": ("#f97316", "HIGH"),
        "medium": ("#f59e0b", "MEDIUM"),
        "low": ("#10b981", "LOW"),
        "info": ("#3b82f6", "INFO")
    }

    color, label = severity_map.get(severity.lower(), ("#94a3b8", "UNKNOWN"))

    if compact:
        return f'<span style="background: {color}; color: white; padding: 0.1rem 0.4rem; border-radius: 3px; font-size: 0.7rem; font-weight: bold;">{label}</span>'
    else:
        return f'<span style="background: {color}; color: white; padding: 0.3rem 0.6rem; border-radius: 4px; font-size: 0.75rem; font-weight: bold;">{label}</span>'
