import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from data_handler import DataHandler

# Page configuration
st.set_page_config(
    page_title="Supplier Order Entry System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data_handler' not in st.session_state:
    st.session_state.data_handler = DataHandler()

if 'current_supplier' not in st.session_state:
    st.session_state.current_supplier = None

# Custom CSS with modern button styling, animations, gradients, and company colors
st.markdown("""
    <style>
    :root {
        --deep-navy: #FF0099;     /* neon pink (gradient start) */
        --light-blue: #FF77CC;    /* lighter pink (gradient end) */
        --accent-teal: #FF55BB;
        --success-green: #00E676;
        --warning-amber: #F59E0B;
        --btn-text: #06324a;      /* dark text on bright pink */
        --head-text: #8c0052;
    }

    * {
        box-sizing: border-box;
    }

    .main {
        padding: 0rem 0rem;
    }

    /* Tab styling with gradient background */
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(90deg, rgba(3, 11, 58, 0.05), rgba(58, 166, 249, 0.05));
        border-radius: 12px;
        padding: 0.6rem;
        margin-bottom: 1.5rem;
        gap: 0.75rem;
        display: flex;
    }

    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1.15em;
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.3s ease;
        flex: 1 1 0;
        padding: 0.85rem 1.25rem;
        justify-content: center;
    }

    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background: linear-gradient(135deg, var(--deep-navy), var(--light-blue)) !important;
        color: #06324a !important;
        box-shadow: 0 4px 15px rgba(58, 166, 249, 0.25);
    }

    /* Modern button styling with animations */
    .stButton > button {
        border-radius: 8px !important;
        border: none !important;
        background: linear-gradient(135deg, var(--deep-navy), var(--light-blue)) !important;
        color: #06324a !important;
        font-weight: 800 !important;
        font-family: 'Segoe UI', 'Trebuchet MS', sans-serif !important;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        padding: 0.6rem 1.2rem !important;
        position: relative;
        overflow: hidden;
    }

    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.1);
        transition: left 0.3s ease;
        z-index: 0;
    }

    .stButton > button:hover::before {
        left: 100%;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, var(--light-blue), var(--deep-navy)) !important;
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 8px 20px rgba(58, 166, 249, 0.4) !important;
    }

    .stButton > button:active {
        transform: translateY(-1px) scale(0.98) !important;
    }

    /* Keep the gradient on every button kind (Streamlit defaults to "secondary") */
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, var(--deep-navy), var(--light-blue)) !important;
        border: none !important;
        color: #06324a !important;
    }

    .stButton > button[kind="secondary"]:hover {
        background: linear-gradient(135deg, var(--light-blue), var(--deep-navy)) !important;
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 8px 20px rgba(58, 166, 249, 0.4) !important;
    }

    /* Force the button label and icon white on the gradient */
    .stButton > button p,
    .stButton > button span,
    .stButton > button div {
        color: #06324a !important;
    }

    /* Form submit button with gradient */
    .stFormSubmitButton > button {
        border-radius: 8px !important;
        background: linear-gradient(135deg, var(--light-blue), var(--accent-teal)) !important;
        color: #06324a !important;
        font-weight: 800 !important;
        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
        padding: 0.7rem 1.5rem !important;
        border: none !important;
    }

    .stFormSubmitButton > button:hover {
        background: linear-gradient(135deg, var(--accent-teal), var(--light-blue)) !important;
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 8px 20px rgba(26, 186, 220, 0.4) !important;
    }

    /* Download button */
    .stDownloadButton > button {
        border-radius: 8px !important;
        background: linear-gradient(135deg, var(--success-green), var(--light-blue)) !important;
        color: #06324a !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
        border: none !important;
    }

    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, var(--light-blue), var(--success-green)) !important;
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 8px 20px rgba(16, 185, 129, 0.4) !important;
    }

    /* Headings: medium green-to-teal gradient that stays readable on
       light, dark, and system themes (the bright neon is only on buttons) */
    h1, h2, h3, h4, h5, h6 {
        background: linear-gradient(135deg, #CC0066, #FF0099) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    h1 { font-weight: 800; }

    /* Sidebar keeps its original teal/green colour scheme */
    [data-testid="stSidebarContent"] .stButton > button,
    [data-testid="stSidebarContent"] .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #00E676, #00C9FF) !important;
        color: #06324a !important;
    }
    [data-testid="stSidebarContent"] .stButton > button:hover,
    [data-testid="stSidebarContent"] .stButton > button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #00C9FF, #00E676) !important;
        box-shadow: 0 8px 20px rgba(0, 201, 255, 0.4) !important;
        transform: translateY(-3px) scale(1.02) !important;
    }
    [data-testid="stSidebarContent"] .stButton > button p,
    [data-testid="stSidebarContent"] .stButton > button span,
    [data-testid="stSidebarContent"] .stButton > button div {
        color: #06324a !important;
    }

    /* Input field styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border-radius: 6px !important;
        border: 2px solid var(--light-blue) !important;
        transition: all 0.3s ease !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--deep-navy) !important;
        box-shadow: 0 0 0 3px rgba(58, 166, 249, 0.1) !important;
    }

    /* Logo container with animation */
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 1.5rem 0;
        animation: fadeInDown 0.6s ease-out;
        background: transparent;
    }

    .logo-container img {
        max-height: 600px;
        width: auto;
        transition: all 0.3s ease;
        background-color: transparent !important;
        mix-blend-mode: screen;
        margin-bottom: -20px;
        margin-left: 120px;
    }

    .logo-container img:hover {
        transform: scale(1.08);
        mix-blend-mode: lighten;
    }

    /* Styled read-only rules table */
    .styled-rules-wrap {
        max-height: 82vh;
        overflow: auto;
        border-radius: 10px;
        border: 1px solid rgba(3, 11, 58, 0.12);
        margin-bottom: 0.5rem;
        background: #ffffff;   /* white card: readable on light/dark/system */
    }

    .styled-rules-table {
        border-collapse: collapse;
        width: 100%;
        font-size: 0.9rem;
        font-family: 'Segoe UI', 'Trebuchet MS', sans-serif;
        background: #ffffff;
    }

    .styled-rules-table th {
        background: linear-gradient(135deg, var(--deep-navy), var(--light-blue));
        color: #06324a !important;
        font-weight: 800;
        text-align: left;
        padding: 10px 14px;
        position: sticky;
        top: 0;
        white-space: nowrap;
    }

    .styled-rules-table td {
        padding: 8px 14px;
        border-bottom: 1px solid rgba(3, 11, 58, 0.06);
        color: #333;
    }

    .styled-rules-table tr:nth-child(even) td {
        background: rgba(58, 166, 249, 0.04);
    }

    /* Customer column (first) in dark bold */
    .styled-rules-table td:first-child {
        color: #0a2e3a;
        font-weight: 700;
    }

    /* Shift-coverage table: bold the Employee (1st) and Supplier (2nd) columns */
    .sc-table td:nth-child(1),
    .sc-table td:nth-child(2) {
        color: #0a2e3a;
        font-weight: 700;
    }

    /* Message styling */
    .stSuccess {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(26, 186, 220, 0.1));
        border-left: 4px solid var(--success-green);
        border-radius: 6px;
        animation: slideInLeft 0.4s ease-out;
    }

    .stError {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(249, 115, 115, 0.1));
        border-left: 4px solid #EF4444;
        border-radius: 6px;
        animation: slideInLeft 0.4s ease-out;
    }

    .stWarning {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(251, 191, 36, 0.1));
        border-left: 4px solid var(--warning-amber);
        border-radius: 6px;
        animation: slideInLeft 0.4s ease-out;
    }

    .stInfo {
        background: linear-gradient(135deg, rgba(58, 166, 249, 0.1), rgba(26, 186, 220, 0.1));
        border-left: 4px solid var(--light-blue);
        border-radius: 6px;
        animation: slideInLeft 0.4s ease-out;
    }

    /* Animations */
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes slideInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .stTabs [data-baseweb="tab-list"] button {
            font-size: 0.95em;
            padding: 0.5rem 0.8rem;
        }

        .stButton > button,
        .stFormSubmitButton > button,
        .stDownloadButton > button {
            padding: 0.5rem 1rem !important;
            font-size: 0.95em;
        }

        h1 { font-size: 1.8em !important; }
        h2 { font-size: 1.5em !important; }
        h3 { font-size: 1.3em !important; }
        h4 { font-size: 1.1em !important; }
    }

    @media (max-width: 480px) {
        .stButton > button,
        .stFormSubmitButton > button,
        .stDownloadButton > button {
            padding: 0.5rem 0.8rem !important;
            font-size: 0.9em;
            width: 100% !important;
        }

        h1 { font-size: 1.5em !important; }
        h2 { font-size: 1.3em !important; }
        h3 { font-size: 1.1em !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# App title (logo removed)
col_left, col_center, col_right = st.columns([1, 2, 1])
with col_center:
    st.markdown("<h1 style='text-align: center;'>🚀 Supplier Order Entry System</h1>", unsafe_allow_html=True)

st.markdown("---")


# ---- Reusable "are you sure?" delete confirmation pop-up ----
@st.dialog("⚠️ Confirm permanent delete")
def _confirm_delete_dialog():
    st.warning(st.session_state.get(
        "_del_message",
        "Are you sure you want to permanently delete this? This cannot be undone."))
    cc1, cc2 = st.columns(2)
    if cc1.button("✅ Yes, delete", use_container_width=True, key="_del_yes"):
        fn = st.session_state.get("_del_action")
        st.session_state["_del_result"] = "ok" if (callable(fn) and fn()) else "fail"
        st.session_state["_del_action"] = None
        st.rerun()
    if cc2.button("❌ Cancel", use_container_width=True, key="_del_no"):
        st.session_state["_del_action"] = None
        st.rerun()


def _ask_delete(message, action):
    st.session_state["_del_message"] = message
    st.session_state["_del_action"] = action
    _confirm_delete_dialog()


# Show the outcome of a confirmed delete (after the dialog closes)
_del_res = st.session_state.pop("_del_result", None)
if _del_res == "ok":
    st.toast("✅ Deleted.")
elif _del_res == "fail":
    st.toast("❌ Delete failed.")

# ---- Google sign-in (activates automatically once [auth] secrets are set) ----
# Written defensively: if authentication isn't configured yet, the app stays
# open and simply greets the visitor generically — it will not error.
auth_configured = True
try:
    _is_logged_in = st.user.is_logged_in
except Exception:
    auth_configured = False
    _is_logged_in = False

if auth_configured and _is_logged_in:
    visitor_name = (getattr(st.user, "name", None)
                    or getattr(st.user, "email", None)
                    or "there")
else:
    visitor_name = "there"

# If sign-in IS configured but the visitor hasn't logged in, show a login page.
if auth_configured and not _is_logged_in:
    st.markdown(
        """
        <div style='text-align: center; padding: 2.5rem 1rem 1rem;'>
            <h2>👋 Welcome!</h2>
            <p style='font-size: 1.15rem; color: #8b95a7;'>
                Please sign in with Google to continue.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.button("🔐 Sign in with Google", use_container_width=True, on_click=st.login)
    st.stop()

# Sidebar
with st.sidebar:
    st.markdown("<h2>🗂️ Navigation</h2>", unsafe_allow_html=True)

    # Get available suppliers
    suppliers = st.session_state.data_handler.get_all_suppliers()

    if suppliers:
        selected_supplier = st.selectbox(
            "🏭 Select Supplier:",
            suppliers,
            index=None,
            placeholder="Choose a supplier...",
            key="supplier_select"
        )
        st.session_state.current_supplier = selected_supplier
    else:
        st.info("📦 No suppliers yet. Create your first supplier!")
        selected_supplier = None

    st.markdown("---")
    st.markdown("<h3>⚡ Quick Actions</h3>", unsafe_allow_html=True)

    st.markdown("**Suppliers**", unsafe_allow_html=False)
    if st.button("✨ Add New Supplier", use_container_width=True):
        st.session_state.show_new_supplier = True

    st.markdown("**Views**", unsafe_allow_html=False)
    if st.button("📅 Shift Coverage", use_container_width=True):
        st.session_state.show_shift_coverage = True
        st.rerun()

    if st.button("⭐ Favorites", use_container_width=True):
        st.session_state.show_favorites_hint = True
        st.rerun()

    # Show who's signed in (only when Google sign-in is configured)
    if auth_configured and _is_logged_in:
        st.markdown("---")
        st.caption(f"👤 Signed in as **{visitor_name}**")
        st.button("🚪 Log out", use_container_width=True, on_click=st.logout)

# ---- Shift Coverage page (replaces the dashboard when active) ----
if st.session_state.get('show_shift_coverage'):
    _dh = st.session_state.data_handler
    st.markdown("<h1 style='text-align:center;'>📅 Shift Coverage</h1>", unsafe_allow_html=True)
    if st.button("⬅️ Back to Dashboard", key="sc_back"):
        st.session_state.show_shift_coverage = False
        st.session_state.sc_employee = None
        st.rerun()
    st.markdown("---")

    sc_cols = ["employee", "supplier", "days", "shift", "time", "notes"]
    sc_labels = {"employee": "Employee", "supplier": "Supplier", "days": "Days",
                 "shift": "Shift", "time": "Time", "notes": "Notes"}
    sc_rows = _dh.get_shift_coverage()

    def _sc_df(records, cols):
        if records:
            d = pd.DataFrame(records)
            for c in cols:
                if c not in d.columns:
                    d[c] = ""
            return d[cols]
        return pd.DataFrame(columns=cols)

    employees = sorted({str(r.get("employee", "")).strip() for r in sc_rows
                        if str(r.get("employee", "")).strip()})
    if employees:
        st.markdown("<h4>👤 Employee's Schedule</h4>", unsafe_allow_html=True)
        ncol = min(len(employees), 5)
        ecols = st.columns(ncol)
        for i, emp in enumerate(employees):
            if ecols[i % ncol].button(emp, key=f"sc_emp_{i}", use_container_width=True):
                st.session_state.sc_employee = emp
                st.rerun()

    sel_emp = st.session_state.get('sc_employee')

    if sel_emp and sel_emp in employees:
        st.markdown(f"<h4>✏️ {sel_emp}'s schedule (per supplier)</h4>", unsafe_allow_html=True)
        emp_cols = ["supplier", "days", "shift", "time", "notes"]
        emp_df = _sc_df([r for r in sc_rows if str(r.get("employee", "")).strip() == sel_emp], emp_cols)
        edited_emp = st.data_editor(
            emp_df, num_rows="dynamic", use_container_width=True, key="sc_emp_editor",
            column_config={c: st.column_config.TextColumn(sc_labels[c]) for c in emp_cols})
        c1, c2 = st.columns(2)
        if c1.button(f"💾 Save {sel_emp}'s schedule", key="sc_save_emp", use_container_width=True):
            others = [r for r in sc_rows if str(r.get("employee", "")).strip() != sel_emp]
            newrows = []
            for rec in edited_emp.fillna("").to_dict("records"):
                if not any(str(v).strip() for v in rec.values()):
                    continue
                newrows.append({"employee": sel_emp, **{k: rec.get(k, "") for k in emp_cols}})
            if _dh.update_shift_coverage(others + newrows):
                st.success("✅ Saved!")
                st.rerun()
            else:
                st.error("❌ Save failed")
        if c2.button("⬅️ Back to full table", key="sc_emp_back", use_container_width=True):
            st.session_state.sc_employee = None
            st.rerun()
    else:
        if sc_rows:
            st.markdown("<h4>👁️ Coverage Overview</h4>", unsafe_allow_html=True)
            ov = _sc_df(sc_rows, sc_cols).rename(columns=sc_labels).fillna("")
            html = ov.to_html(index=False, escape=True,
                              classes="styled-rules-table sc-table", border=0)
            st.markdown(f"<div class='styled-rules-wrap'>{html}</div>", unsafe_allow_html=True)

        with st.expander("✏️ Edit All Coverage"):
            all_df = _sc_df(sc_rows, sc_cols)
            edited_all = st.data_editor(
                all_df, num_rows="dynamic", use_container_width=True, key="sc_all_editor",
                column_config={c: st.column_config.TextColumn(sc_labels[c]) for c in sc_cols})
            if st.button("💾 Save Coverage", key="sc_save_all"):
                newrows = [r for r in edited_all.fillna("").to_dict("records")
                           if any(str(v).strip() for v in r.values())]
                if _dh.update_shift_coverage(newrows):
                    st.success("✅ Coverage saved!")
                    st.rerun()
                else:
                    st.error("❌ Save failed")

    st.stop()

# Main content area
if not selected_supplier:
    # Greet by first name only (e.g. "Dawn Berioso" -> "Dawn")
    _greeting_name = visitor_name.split("@")[0].split()[0] if visitor_name != "there" else "there"
    st.markdown(
        f"""
        <div style='text-align: center; padding: 3rem 1rem;'>
            <h2>👋 Hi, {_greeting_name}!</h2>
            <p style='font-size: 1.25rem; color: #8b95a7; margin-top: 0.5rem;'>
                Which supplier are you looking for?
            </p>
            <p style='font-size: 1rem; color: #8b95a7; margin-top: 1.5rem;'>
                👈 Pick one from the <b>🏭 Select Supplier</b> dropdown in the sidebar to get started.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
else:
    # Create tabs
    tab1, tab_fav, tab5 = st.tabs([
        "📋 Supplier Rules",
        "⭐ Favorites",
        "ℹ️ Supplier Information"
    ])

    # Tab 1: Supplier Rules (Customer Rules / Product Rules)
    with tab1:
        _dh = st.session_state.data_handler
        st.markdown(f"<h3>📋 Supplier Rules - {selected_supplier}</h3>", unsafe_allow_html=True)

        rules_view = st.radio(
            "Choose a rules set:",
            ["👤 Customer Rules", "📦 Product Rules"],
            horizontal=True, key="rules_view_choice", label_visibility="collapsed")

        cust_labels = {
            "customer": "Customer", "ordered_product": "Ordered Product",
            "ordered_unit": "Ordered Unit", "fresho_product": "Fresho Product",
            "fresho_qty": "Fresho Qty", "other_comments": "Other Comments",
            "created_by": "Created By",
        }
        cust_cols = list(cust_labels.keys())
        # Who is making the edit (for the "Created By" stamp), date as dd/mm/yy
        _stamp_name = (visitor_name.split("@")[0].split()[0]
                       if visitor_name and visitor_name != "there" else "User")
        _stamp = f"{_stamp_name} {datetime.now().strftime('%d/%m/%y')}"
        prod_labels = {
            "ordered_product": "Ordered Product", "fresho_product": "Fresho Product",
            "fresho_qty": "Fresho Qty", "ordered_unit": "Ordered Unit", "notes": "Notes",
        }
        prod_cols = list(prod_labels.keys())

        def _frame(records, cols):
            d = pd.DataFrame(records) if records else pd.DataFrame(columns=cols)
            for c in cols:
                if c not in d.columns:
                    d[c] = ""
            return d[cols]

        if rules_view == "👤 Customer Rules":
            st.markdown("<h4>👤 Customer Rules</h4>", unsafe_allow_html=True)
            supplier_rules = _dh.get_supplier_rules(selected_supplier)
            meta = _dh.get_rules_meta(selected_supplier)

            # Columns follow the data: whatever columns your rows have (so uploads show up),
            # falling back to the standard set when empty, plus any columns you've added.
            if supplier_rules:
                all_cols = []
                for r in supplier_rules:
                    for k in r.keys():
                        if str(k) not in all_cols:
                            all_cols.append(str(k))
            else:
                all_cols = list(cust_cols)
            for c in meta["extra_columns"]:
                if c not in all_cols:
                    all_cols.append(c)

            labels = dict(cust_labels)
            for c in all_cols:
                labels.setdefault(c, c)
            labels.update(meta["labels"])

            def _cust_frame(records, cols):
                d = pd.DataFrame(records) if records else pd.DataFrame(columns=cols)
                if 'created_at' in d.columns and 'created_by' not in d.columns and 'created_by' in cols:
                    d['created_by'] = d['created_at']
                for c in cols:
                    if c not in d.columns:
                        d[c] = ""
                return d[cols].fillna("")

            df = _cust_frame(supplier_rules, all_cols)

            _cr_sort = st.checkbox("🔤 Sort A→Z", key="cr_sort_az")
            if _cr_sort and len(df) > 0:
                df = df.sort_values(by=df.columns[0], ignore_index=True)
            st.markdown(f"<p style='color:#8b95a7;'><b>📊 {len(df)} rows</b></p>", unsafe_allow_html=True)

            edited_df = st.data_editor(
                df, use_container_width=True, num_rows="dynamic", height=800,
                key="cr_editor",
                column_config={c: st.column_config.TextColumn(labels.get(c, c)) for c in all_cols})

            b1, b2, b3 = st.columns([1, 1, 2])
            with b1:
                if st.button("💾 Save", use_container_width=True, key="cr_save"):
                    try:
                        updated = edited_df.to_dict('records')
                        for rec in updated:
                            if 'created_by' in all_cols and not str(rec.get('created_by', '')).strip():
                                rec['created_by'] = _stamp
                        _dh.update_supplier_rules(selected_supplier, updated)
                        st.success("✅ Customer rules saved!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Save failed: {e}")
            with b2:
                if st.button("🗑️ Delete All", use_container_width=True, key="delete_rules_btn"):
                    _ask_delete(
                        f"Permanently delete ALL customer rules for '{selected_supplier}'? "
                        "This cannot be undone.",
                        lambda: _dh.delete_supplier_rules(selected_supplier))

            with st.expander("📁 Import / Export Customer Rules"):
                # Export
                if supplier_rules:
                    _cr_exp = pd.DataFrame(supplier_rules)
                    for c in all_cols:
                        if c not in _cr_exp.columns:
                            _cr_exp[c] = ""
                    st.download_button(
                        "⬇️ Export CSV", data=_cr_exp.to_csv(index=False),
                        file_name=f"{selected_supplier}_customer_rules_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv", use_container_width=True, key="cr_export")
                else:
                    st.caption("No data to export yet.")
                st.markdown("---")
                st.caption("Your CSV's own column names are kept exactly. "
                           "**Upload & replace** = your file becomes the data. "
                           "**Add to existing** = rows added on top.")
                up = st.file_uploader("Choose a CSV file", type=["csv"], key="cr_csv")
                if up is not None:
                    try:
                        dfi = pd.read_csv(up).fillna("")
                        rows = [{str(k): ("" if str(v) == "nan" else str(v)) for k, v in r.items()}
                                for r in dfi.to_dict('records')]
                        st.dataframe(dfi, use_container_width=True)
                        ir1, ir2 = st.columns(2)
                        if ir1.button("⬆️ Upload & replace everything", key="cr_imp_rep", use_container_width=True):
                            _dh.update_supplier_rules(selected_supplier, rows)
                            st.success(f"✅ Uploaded {len(rows)} rows!")
                            st.rerun()
                        if ir2.button("➕ Add to existing", key="cr_imp_app", use_container_width=True):
                            _dh.update_supplier_rules(selected_supplier, (supplier_rules or []) + rows)
                            st.success(f"✅ Added {len(rows)} rows!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error reading CSV: {e}")

            with st.expander("🛠️ Manage columns (rename, add or delete columns)"):
                rc1, rc2, rc3 = st.columns([2, 2, 1])
                with rc1:
                    col_sel = st.selectbox("Column", all_cols,
                                           format_func=lambda c: labels.get(c, c), key="cr_col_sel")
                with rc2:
                    new_title = st.text_input("New title", value=labels.get(col_sel, col_sel), key="cr_col_title")
                with rc3:
                    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                    if st.button("Rename", key="cr_col_rename", use_container_width=True):
                        meta["labels"][col_sel] = new_title.strip() or col_sel
                        _dh.update_rules_meta(selected_supplier, meta)
                        st.success("✅ Title updated!")
                        st.rerun()
                st.markdown("---")
                ac1, ac2 = st.columns([3, 1])
                with ac1:
                    new_col = st.text_input("New column name", key="cr_col_addtxt",
                                            placeholder="e.g. Order Term")
                with ac2:
                    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                    if st.button("➕ Add column", key="cr_col_add", use_container_width=True):
                        name = new_col.strip()
                        if name and name not in all_cols:
                            meta["extra_columns"].append(name)
                            _dh.update_rules_meta(selected_supplier, meta)
                            st.success(f"✅ Added '{name}'!")
                            st.rerun()
                        else:
                            st.warning("Enter a unique, non-empty column name.")
                st.markdown("---")
                dc1, dc2 = st.columns([3, 1])
                with dc1:
                    to_del = st.multiselect("Delete column(s)", all_cols,
                                            format_func=lambda c: labels.get(c, c), key="cr_col_delsel")
                with dc2:
                    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                    if st.button("🗑️ Delete column", key="cr_col_del", use_container_width=True):
                        if to_del:
                            def _do_del_cols(_meta=dict(meta), _td=list(to_del),
                                             _rules=list(supplier_rules or [])):
                                _meta["extra_columns"] = [c for c in _meta["extra_columns"] if c not in _td]
                                for k in _td:
                                    _meta["labels"].pop(k, None)
                                _dh.update_rules_meta(selected_supplier, _meta)
                                cleaned = [{k: v for k, v in rec.items() if k not in _td} for rec in _rules]
                                return _dh.update_supplier_rules(selected_supplier, cleaned)
                            _ask_delete(
                                "Permanently delete column(s) "
                                f"{', '.join(labels.get(c, c) for c in to_del)} and their data? "
                                "This cannot be undone.", _do_del_cols)
                        else:
                            st.warning("Select a column to delete first.")
                st.caption("Rename, add, or delete any column. (Deleting 'customer' or 'ordered_product' "
                           "just means the search boxes stop filtering on it.)")

        else:
            st.markdown("<h4>📦 Product Rules</h4>", unsafe_allow_html=True)
            st.caption("Product-level defaults (no customer): the Fresho product/quantity to use for each ordered product.")
            product_rules = _dh.get_product_rules(selected_supplier)
            pmeta = _dh.get_product_rules_meta(selected_supplier)

            # Columns follow the data: whatever columns your rows have (so uploads show up),
            # falling back to the standard set when empty, plus any columns you've added.
            if product_rules:
                p_all_cols = []
                for r in product_rules:
                    for k in r.keys():
                        if str(k) not in p_all_cols:
                            p_all_cols.append(str(k))
            else:
                p_all_cols = list(prod_cols)
            for c in pmeta["extra_columns"]:
                if c not in p_all_cols:
                    p_all_cols.append(c)

            p_labels = dict(prod_labels)
            for c in p_all_cols:
                p_labels.setdefault(c, c)
            p_labels.update(pmeta["labels"])

            pdf = _frame(product_rules, p_all_cols)

            _pr_sort = st.checkbox("🔤 Sort A→Z", key="pr_sort_az")
            if _pr_sort and len(pdf) > 0:
                pdf = pdf.sort_values(by=pdf.columns[0], ignore_index=True)
            st.markdown(f"<p style='color:#8b95a7;'><b>📊 {len(pdf)} rows</b></p>", unsafe_allow_html=True)

            edited_p = st.data_editor(
                pdf, use_container_width=True, num_rows="dynamic", height=800,
                key="pr_editor",
                column_config={c: st.column_config.TextColumn(p_labels.get(c, c)) for c in p_all_cols})

            p1, p2, p3 = st.columns([1, 1, 2])
            with p1:
                if st.button("💾 Save", use_container_width=True, key="pr_save"):
                    try:
                        rows = [r for r in edited_p.fillna("").to_dict('records')
                                if any(str(v).strip() for v in r.values())]
                        if _dh.update_product_rules(selected_supplier, rows):
                            st.success("✅ Product rules saved!")
                            st.rerun()
                        else:
                            st.error("❌ Save failed")
                    except Exception as e:
                        st.error(f"❌ Save failed: {e}")
            with p2:
                if st.button("🗑️ Delete All", use_container_width=True, key="pr_delete"):
                    _ask_delete(
                        f"Permanently delete ALL product rules for '{selected_supplier}'? "
                        "This cannot be undone.",
                        lambda: _dh.update_product_rules(selected_supplier, []))

            with st.expander("📁 Import / Export Product Rules"):
                # Export
                if product_rules:
                    _pr_exp = pd.DataFrame(product_rules)
                    for c in p_all_cols:
                        if c not in _pr_exp.columns:
                            _pr_exp[c] = ""
                    st.download_button(
                        "⬇️ Export CSV", data=_pr_exp.to_csv(index=False),
                        file_name=f"{selected_supplier}_product_rules_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv", use_container_width=True, key="pr_export")
                else:
                    st.caption("No data to export yet.")
                st.markdown("---")
                st.caption("Your CSV's own column names are kept exactly. "
                           "**Upload & replace** = your file becomes the data. "
                           "**Add to existing** = rows added on top.")
                up = st.file_uploader("Choose a CSV file", type=["csv"], key="pr_csv")
                if up is not None:
                    try:
                        dfi = pd.read_csv(up).fillna("")
                        rows = [{str(k): ("" if str(v) == "nan" else str(v)) for k, v in r.items()}
                                for r in dfi.to_dict('records')]
                        st.dataframe(dfi, use_container_width=True)
                        pir1, pir2 = st.columns(2)
                        if pir1.button("⬆️ Upload & replace everything", key="pr_imp_rep", use_container_width=True):
                            _dh.update_product_rules(selected_supplier, rows)
                            st.success(f"✅ Uploaded {len(rows)} rows!")
                            st.rerun()
                        if pir2.button("➕ Add to existing", key="pr_imp_app", use_container_width=True):
                            _dh.update_product_rules(selected_supplier, (product_rules or []) + rows)
                            st.success(f"✅ Added {len(rows)} rows!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error reading CSV: {e}")

            with st.expander("🛠️ Manage columns (rename, add or delete columns)"):
                prc1, prc2, prc3 = st.columns([2, 2, 1])
                with prc1:
                    p_col_sel = st.selectbox("Column", p_all_cols,
                                             format_func=lambda c: p_labels.get(c, c), key="pr_col_sel")
                with prc2:
                    p_new_title = st.text_input("New title", value=p_labels.get(p_col_sel, p_col_sel), key="pr_col_title")
                with prc3:
                    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                    if st.button("Rename", key="pr_col_rename", use_container_width=True):
                        pmeta["labels"][p_col_sel] = p_new_title.strip() or p_col_sel
                        _dh.update_product_rules_meta(selected_supplier, pmeta)
                        st.success("✅ Title updated!")
                        st.rerun()
                st.markdown("---")
                pac1, pac2 = st.columns([3, 1])
                with pac1:
                    p_new_col = st.text_input("New column name", key="pr_col_addtxt",
                                              placeholder="e.g. Order Term")
                with pac2:
                    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                    if st.button("➕ Add column", key="pr_col_add", use_container_width=True):
                        name = p_new_col.strip()
                        if name and name not in p_all_cols:
                            pmeta["extra_columns"].append(name)
                            _dh.update_product_rules_meta(selected_supplier, pmeta)
                            st.success(f"✅ Added '{name}'!")
                            st.rerun()
                        else:
                            st.warning("Enter a unique, non-empty column name.")
                st.markdown("---")
                pdc1, pdc2 = st.columns([3, 1])
                with pdc1:
                    p_to_del = st.multiselect("Delete column(s)", p_all_cols,
                                              format_func=lambda c: p_labels.get(c, c), key="pr_col_delsel")
                with pdc2:
                    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                    if st.button("🗑️ Delete column", key="pr_col_del", use_container_width=True):
                        if p_to_del:
                            def _do_del_pcols(_meta=dict(pmeta), _td=list(p_to_del),
                                              _rules=list(product_rules or [])):
                                _meta["extra_columns"] = [c for c in _meta["extra_columns"] if c not in _td]
                                for k in _td:
                                    _meta["labels"].pop(k, None)
                                _dh.update_product_rules_meta(selected_supplier, _meta)
                                cleaned = [{k: v for k, v in rec.items() if k not in _td} for rec in _rules]
                                return _dh.update_product_rules(selected_supplier, cleaned)
                            _ask_delete(
                                "Permanently delete column(s) "
                                f"{', '.join(p_labels.get(c, c) for c in p_to_del)} and their data? "
                                "This cannot be undone.", _do_del_pcols)
                        else:
                            st.warning("Select a column to delete first.")
                st.caption("Rename, add, or delete any column. (Deleting 'ordered_product' "
                           "just means the search box stops filtering on it.)")

    # Favorites tab: most-ordered products, organized per customer
    with tab_fav:
        st.markdown(f"<h3>⭐ Favorites - {selected_supplier}</h3>", unsafe_allow_html=True)
        st.caption("Pick a customer, then list the products they order most. Each customer keeps their own favorites.")

        all_favorites = st.session_state.data_handler.get_supplier_favorites(selected_supplier)
        all_rules = st.session_state.data_handler.get_supplier_rules(selected_supplier)

        # Build the customer list from existing rules and any saved favorites
        customers = set()
        for _r in all_rules:
            _c = str(_r.get("customer", "")).strip()
            if _c:
                customers.add(_c)
        for _f in all_favorites:
            _c = str(_f.get("customer", "")).strip()
            if _c:
                customers.add(_c)
        customer_list = sorted(customers)

        if st.session_state.get("show_favorites_hint"):
            st.info("👆 You're in the Favorites tab — pick a customer below.")
            st.session_state.show_favorites_hint = False

        if not customer_list:
            st.info("👤 No saved customers yet — type a name below to start.")
            fav_customer = st.text_input("Customer name:", key="fav_manual_name", placeholder="e.g. The Blue Anchor")
        else:
            fc1, fc2 = st.columns([3, 1])
            fav_customer = fc1.selectbox("👤 Select Customer:", customer_list, key="fav_customer_select")
            if fc2.text_input("Or type new:", key="fav_new_name", placeholder="new customer"):
                fav_customer = st.session_state.fav_new_name

            cust_favs = [f for f in all_favorites
                         if str(f.get("customer", "")).strip() == fav_customer]
            fav_cols = ["product_name", "product_quantity", "unit", "notes"]
            fav_labels = {
                "product_name": "Product Name",
                "product_quantity": "Product Quantity",
                "unit": "Unit (box/kg/g)",
                "notes": "Notes",
            }

            def _fav_frame(records, cols):
                d = pd.DataFrame(records) if records else pd.DataFrame(columns=cols)
                # migrate older favorites that used 'ordered_product'
                if 'ordered_product' in d.columns and 'product_name' not in d.columns:
                    d['product_name'] = d['ordered_product']
                for c in cols:
                    if c not in d.columns:
                        d[c] = ""
                return d[cols]

            fav_df = _fav_frame(cust_favs, fav_cols)

            st.markdown(f"<h4>✏️ Favorite Products for {fav_customer}</h4>", unsafe_allow_html=True)
            edited_fav = st.data_editor(
                fav_df, use_container_width=True, num_rows="dynamic", key="favorites_editor",
                column_config={c: st.column_config.TextColumn(l) for c, l in fav_labels.items()})

            if st.button("💾 Save Favorites", use_container_width=False, key="fav_save"):
                try:
                    others = [f for f in all_favorites
                              if str(f.get("customer", "")).strip() != fav_customer]
                    new_for_customer = []
                    for rec in edited_fav.fillna("").to_dict('records'):
                        if not any(str(v).strip() for v in rec.values()):
                            continue
                        clean = {k: rec.get(k, "") for k in fav_cols}
                        clean["customer"] = fav_customer
                        new_for_customer.append(clean)
                    st.session_state.data_handler.update_supplier_favorites(
                        selected_supplier, others + new_for_customer)
                    st.success(f"✅ Favorites saved for {fav_customer}!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Save failed: {str(e)}")

            with st.expander("📁 Import / Export Favorites (all customers)"):
                # Export
                if all_favorites:
                    _fav_exp = pd.DataFrame(all_favorites)
                    st.download_button(
                        "⬇️ Export CSV", data=_fav_exp.to_csv(index=False),
                        file_name=f"{selected_supplier}_favorites_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv", use_container_width=True, key="fav_export")
                else:
                    st.caption("No favorites to export yet.")
                st.markdown("---")
                st.caption("CSV columns: customer, product_name, product_quantity, unit, notes  "
                           "**Upload & replace** = your file becomes all favorites. "
                           "**Add to existing** = rows added on top.")
                fav_up = st.file_uploader("Choose a CSV file", type=["csv"], key="fav_csv")
                if fav_up is not None:
                    try:
                        dfi = pd.read_csv(fav_up).fillna("")
                        imp_cols = ["customer"] + fav_cols
                        rows = [{str(k): ("" if str(v) == "nan" else str(v)) for k, v in r.items()}
                                for r in dfi.to_dict('records')]
                        st.dataframe(dfi, use_container_width=True)
                        fi1, fi2 = st.columns(2)
                        if fi1.button("⬆️ Upload & replace everything", key="fav_imp_rep", use_container_width=True):
                            st.session_state.data_handler.update_supplier_favorites(selected_supplier, rows)
                            st.success(f"✅ Imported {len(rows)} favorites!")
                            st.rerun()
                        if fi2.button("➕ Add to existing", key="fav_imp_app", use_container_width=True):
                            st.session_state.data_handler.update_supplier_favorites(
                                selected_supplier, (all_favorites or []) + rows)
                            st.success(f"✅ Added {len(rows)} favorites!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error reading CSV: {e}")

    # Tab 5: Supplier Information
    with tab5:
        st.markdown(f"<h3>ℹ️ Supplier Information - {selected_supplier}</h3>", unsafe_allow_html=True)

        _dh = st.session_state.data_handler
        supplier_info = _dh.get_supplier_info(selected_supplier)
        details = _dh.get_supplier_details(selected_supplier)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<h4>📋 Information</h4>", unsafe_allow_html=True)
            st.markdown(f"**🏭 Name:** {supplier_info.get('supplier_name', 'N/A')}")
            st.markdown(f"**🕐 Time Shift AUT:** {details.get('time_shift_aut') or '—'}")
            st.markdown(f"**🕐 Time Shift UKT:** {details.get('time_shift_ukt') or '—'}")
            st.markdown(f"**👤 POC:** {details.get('poc') or '—'}")
            st.markdown(f"**👥 Team PH:** {details.get('team_ph') or '—'}")
            st.markdown(f"**📝 Information:** {details.get('information') or '—'}")

            st.markdown("<h4>📆 Required Days</h4>", unsafe_allow_html=True)
            req = _dh.get_required_days(selected_supplier)
            req_cols = ["customer", "required_days"]

            # Display as simple list
            if req:
                for _rrow in req:
                    _c = _rrow.get("customer", "").strip()
                    _d = _rrow.get("required_days", "").strip()
                    if _c:
                        st.markdown(f"**{_c}:** {_d or '—'}")
            else:
                st.caption("No required days set yet.")

            with st.expander("✏️ Edit Required Days"):
                if req:
                    req_df = pd.DataFrame(req)
                    for c in req_cols:
                        if c not in req_df.columns:
                            req_df[c] = ""
                    req_df = req_df[req_cols]
                else:
                    req_df = pd.DataFrame(columns=req_cols)

                edited_req = st.data_editor(
                    req_df, use_container_width=True, num_rows="dynamic",
                    key="reqdays_editor",
                    column_config={
                        "customer": st.column_config.TextColumn("Customer"),
                        "required_days": st.column_config.TextColumn("Required Days"),
                    })
                # Auto-save on change
                _rd_prev_key = f"_rd_prev_{selected_supplier}"
                _rd_current = [r for r in edited_req.fillna("").to_dict("records")
                               if any(str(v).strip() for v in r.values())]
                _rd_prev = st.session_state.get(_rd_prev_key, req or [])
                if _rd_current != _rd_prev:
                    if _dh.update_required_days(selected_supplier, _rd_current):
                        st.session_state[_rd_prev_key] = _rd_current
                        st.toast("✅ Required Days saved")

        with col2:
            st.markdown("<h4>⚙️ Manage</h4>", unsafe_allow_html=True)

            # Rename + Delete side by side
            mn1, mn2, mn3 = st.columns([3, 1, 1])
            new_name = mn1.text_input("🏷️ Rename:", value=selected_supplier, label_visibility="collapsed",
                                      placeholder="Supplier name")
            if mn2.button("✏️ Update", use_container_width=True, key="sup_rename_btn"):
                if _dh.rename_supplier(selected_supplier, new_name):
                    st.success(f"✅ Renamed to {new_name}")
                    st.rerun()
                else:
                    st.error("❌ Update failed")
            if mn3.button("🗑️ Delete", use_container_width=True, key="delete_supplier_btn"):
                _ask_delete(
                    f"Permanently delete the entire supplier '{selected_supplier}' and ALL its "
                    "rules, favourites and details? This cannot be undone.",
                    lambda: _dh.delete_supplier(selected_supplier))

            st.markdown("---")
            with st.expander("✏️ Edit Supplier Details"):
                with st.form("supplier_details_form"):
                    d_aut = st.text_input("🕐 Time Shift AUT", value=details.get("time_shift_aut", ""))
                    d_ukt = st.text_input("🕐 Time Shift UKT", value=details.get("time_shift_ukt", ""))
                    d_poc = st.text_input("👤 POC", value=details.get("poc", ""))
                    d_team = st.text_input("👥 Team PH", value=details.get("team_ph", ""))
                    d_info = st.text_area("📝 Information", value=details.get("information", ""), height=100)
                    if st.form_submit_button("💾 Save Details"):
                        if _dh.update_supplier_details(selected_supplier, {
                            "time_shift_aut": d_aut, "time_shift_ukt": d_ukt,
                            "poc": d_poc, "team_ph": d_team, "information": d_info,
                        }):
                            st.success("✅ Details saved!")
                            st.rerun()
                        else:
                            st.error("❌ Save failed")

# Add New Supplier Modal
if st.session_state.get('show_new_supplier', False):
    with st.form("new_supplier_form"):
        st.markdown("<h3>🏭 New Supplier</h3>", unsafe_allow_html=True)

        supplier_name = st.text_input("🏷️ Name *")
        description = st.text_area("📝 Description (optional)")

        if st.form_submit_button("✅ Create"):
            if not supplier_name:
                st.error("❌ Name required")
            else:
                if st.session_state.data_handler.create_supplier(supplier_name, description):
                    st.success(f"✅ Created '{supplier_name}'!")
                    st.session_state.show_new_supplier = False
                    st.rerun()
                else:
                    st.error("❌ Create failed")

# Footer with mini save status
_connected = st.session_state.data_handler.is_connected()
_status_icon = "🟢" if _connected else "🟡"
_status_text = "Auto-saving" if _connected else "Not saving (check GitHub secrets)"
st.markdown("---")
st.markdown(f"""
    <div style='text-align: center; color: #8b95a7; font-size: 0.8em; padding: 1rem 1.5rem;'>
    <p style='font-weight: 700; background: linear-gradient(135deg, #FF0099, #FF77CC); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;'>🚀 Supplier Order Entry System v2.0</p>
    <p>{_status_icon} {_status_text} &nbsp;·&nbsp; Built with Streamlit</p>
    </div>
    """, unsafe_allow_html=True)
