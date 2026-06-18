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
        --deep-navy: #00E676;     /* neon green (gradient start) */
        --light-blue: #00C9FF;    /* neon cyan (gradient end) */
        --accent-teal: #00C2EA;
        --success-green: #00E676;
        --warning-amber: #F59E0B;
        --btn-text: #06324a;      /* dark text for the bright gradient */
        --head-text: #0a4d5c;     /* readable heading colour */
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
        background: linear-gradient(135deg, #0AA15A, #0A93B5) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    h1 { font-weight: 800; }

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

    # Full-width buttons so every action is a uniform rectangle (no wrapping)
    if st.button("✨ Add New Supplier", use_container_width=True):
        st.session_state.show_new_supplier = True

    if st.button("📅 Shift Coverage", use_container_width=True):
        st.session_state.show_shift_coverage = True
        st.rerun()

    st.markdown("---")
    st.markdown("<h3>💾 Save Status</h3>", unsafe_allow_html=True)

    if st.session_state.data_handler.is_connected():
        st.success("✅ Connected to GitHub — changes save automatically.")
    else:
        st.warning(
            "⚠️ Not connected to GitHub. The app can show data but "
            "changes won't save. Add GITHUB_TOKEN and GITHUB_REPO in "
            "Settings → Secrets to enable saving."
        )

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
        st.markdown("<h4>👤 Edit one employee's schedule</h4>", unsafe_allow_html=True)
        ncol = min(len(employees), 4)
        ecols = st.columns(ncol)
        for i, emp in enumerate(employees):
            if ecols[i % ncol].button(f"👤 {emp}", key=f"sc_emp_{i}", use_container_width=True):
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

        st.markdown("<h4>✏️ Edit all coverage</h4>", unsafe_allow_html=True)
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

    st.markdown("---")
    st.markdown("<h4>📥 Import Shift Coverage (CSV)</h4>", unsafe_allow_html=True)
    st.caption("CSV columns: employee, supplier, days, shift, time, notes")
    up_sc = st.file_uploader("Choose a CSV file", type=["csv"], key="sc_csv")
    if up_sc is not None:
        try:
            dfi = pd.read_csv(up_sc).fillna("")
            low = {c.lower().strip(): c for c in dfi.columns}
            imported = [{k: str(r.get(low.get(k, ""), "")) for k in sc_cols}
                        for _, r in dfi.iterrows()]
            st.dataframe(dfi, use_container_width=True)
            ic1, ic2 = st.columns(2)
            if ic1.button("✅ Replace all with import", key="sc_imp_replace", use_container_width=True):
                if _dh.update_shift_coverage(imported):
                    st.success(f"✅ Imported {len(imported)} rows (replaced).")
                    st.rerun()
            if ic2.button("➕ Append to existing", key="sc_imp_append", use_container_width=True):
                if _dh.update_shift_coverage(sc_rows + imported):
                    st.success(f"✅ Appended {len(imported)} rows.")
                    st.rerun()
        except Exception as e:
            st.error(f"❌ Error reading CSV: {e}")

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
    tab1, tab_fav, tab4, tab5 = st.tabs([
        "📋 Supplier Rules",
        "⭐ Favorites",
        "💾 Import / Export",
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
            "created_at": "Created At",
        }
        cust_cols = list(cust_labels.keys())
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
            st.caption("Edit any cell directly, then click Save. Add or delete rows with the grid controls.")
            supplier_rules = _dh.get_supplier_rules(selected_supplier)
            df = _frame(supplier_rules, cust_cols)

            c1, c2, c3 = st.columns(3)
            with c1:
                search_customer = st.text_input("👤 Customer:", value="", placeholder="Search customer...", key="cr_sc")
            with c2:
                search_product = st.text_input("📦 Product:", value="", placeholder="Search product...", key="cr_sp")
            with c3:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                if st.button("🗑️ Clear", use_container_width=True, key="cr_clear"):
                    search_customer = ""
                    search_product = ""

            filtered_df = df.copy()
            if search_customer:
                filtered_df = filtered_df[filtered_df['customer'].str.contains(search_customer, case=False, na=False)]
            if search_product:
                filtered_df = filtered_df[filtered_df['ordered_product'].str.contains(search_product, case=False, na=False)]
            st.markdown(f"<p style='color:#8b95a7;'><b>📊 Showing {len(filtered_df)} of {len(df)} rules</b></p>", unsafe_allow_html=True)

            edited_df = st.data_editor(
                filtered_df, use_container_width=True, num_rows="dynamic", height=560,
                key="cr_editor",
                column_config={c: st.column_config.TextColumn(l) for c, l in cust_labels.items()})

            b1, b2, b3 = st.columns([1, 1, 2])
            with b1:
                _filter_active = bool(search_customer or search_product)
                if st.button("💾 Save", use_container_width=True, key="cr_save"):
                    try:
                        if _filter_active and len(edited_df) < len(df):
                            full = df.copy()
                            hidden = full.loc[~full.index.isin(filtered_df.index)]
                            merged = pd.concat([hidden, edited_df], ignore_index=True)
                            updated = merged.to_dict('records')
                            st.info(f"ℹ️ Merged {len(hidden)} hidden rows with your edits.")
                        else:
                            updated = edited_df.to_dict('records')
                        _dh.update_supplier_rules(selected_supplier, updated)
                        st.success("✅ Customer rules saved!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Save failed: {e}")
            with b2:
                if st.button("🗑️ Delete All", use_container_width=True, key="delete_rules_btn"):
                    if _dh.delete_supplier_rules(selected_supplier):
                        st.success("✅ Rules deleted!")
                        st.rerun()
                    else:
                        st.error("❌ Delete failed")

            with st.expander("📥 Import Customer Rules (CSV)"):
                st.caption("CSV columns: customer, ordered_product, ordered_unit, fresho_product, fresho_qty, other_comments")
                up = st.file_uploader("Choose a CSV file", type=["csv"], key="cr_csv")
                if up is not None:
                    try:
                        dfi = pd.read_csv(up).fillna("")
                        low = {c.lower().strip(): c for c in dfi.columns}
                        rows = [{k: str(r.get(low.get(k, ""), "")) for k in cust_cols} for _, r in dfi.iterrows()]
                        st.dataframe(dfi, use_container_width=True)
                        ir1, ir2 = st.columns(2)
                        if ir1.button("✅ Replace all", key="cr_imp_rep", use_container_width=True):
                            _dh.update_supplier_rules(selected_supplier, rows)
                            st.success("✅ Imported!")
                            st.rerun()
                        if ir2.button("➕ Append", key="cr_imp_app", use_container_width=True):
                            _dh.update_supplier_rules(selected_supplier, (supplier_rules or []) + rows)
                            st.success("✅ Appended!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error reading CSV: {e}")

        else:
            st.markdown("<h4>📦 Product Rules</h4>", unsafe_allow_html=True)
            st.caption("Product-level defaults (no customer): the Fresho product/quantity to use for each ordered product.")
            product_rules = _dh.get_product_rules(selected_supplier)
            pdf = _frame(product_rules, prod_cols)

            edited_p = st.data_editor(
                pdf, use_container_width=True, num_rows="dynamic", height=560,
                key="pr_editor",
                column_config={c: st.column_config.TextColumn(l) for c, l in prod_labels.items()})

            p1, p2, p3 = st.columns([1, 1, 2])
            with p1:
                if st.button("💾 Save", use_container_width=True, key="pr_save"):
                    rows = [r for r in edited_p.fillna("").to_dict('records')
                            if any(str(v).strip() for v in r.values())]
                    if _dh.update_product_rules(selected_supplier, rows):
                        st.success("✅ Product rules saved!")
                        st.rerun()
                    else:
                        st.error("❌ Save failed")
            with p2:
                if st.button("🗑️ Delete All", use_container_width=True, key="pr_delete"):
                    if _dh.update_product_rules(selected_supplier, []):
                        st.success("✅ Deleted!")
                        st.rerun()
                    else:
                        st.error("❌ Delete failed")

            with st.expander("📥 Import Product Rules (CSV)"):
                st.caption("CSV columns: ordered_product, fresho_product, fresho_qty, ordered_unit, notes")
                up = st.file_uploader("Choose a CSV file", type=["csv"], key="pr_csv")
                if up is not None:
                    try:
                        dfi = pd.read_csv(up).fillna("")
                        low = {c.lower().strip(): c for c in dfi.columns}
                        rows = [{k: str(r.get(low.get(k, ""), "")) for k in prod_cols} for _, r in dfi.iterrows()]
                        st.dataframe(dfi, use_container_width=True)
                        pir1, pir2 = st.columns(2)
                        if pir1.button("✅ Replace all", key="pr_imp_rep", use_container_width=True):
                            _dh.update_product_rules(selected_supplier, rows)
                            st.success("✅ Imported!")
                            st.rerun()
                        if pir2.button("➕ Append", key="pr_imp_app", use_container_width=True):
                            _dh.update_product_rules(selected_supplier, (product_rules or []) + rows)
                            st.success("✅ Appended!")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error reading CSV: {e}")

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

        if not customer_list:
            st.info("👤 No customers yet. Add rules with customer names first, then come back to set their favorites.")
        else:
            fav_customer = st.selectbox("👤 Select Customer:", customer_list, key="fav_customer_select")

            # Favorites belonging to the chosen customer
            cust_favs = [f for f in all_favorites
                         if str(f.get("customer", "")).strip() == fav_customer]
            fav_cols = ["ordered_product", "fresho_product", "notes"]
            fav_labels = {
                "ordered_product": "Ordered Product",
                "fresho_product": "Fresho Product",
                "notes": "Notes",
            }

            if cust_favs:
                fav_df = pd.DataFrame(cust_favs)
                for c in fav_cols:
                    if c not in fav_df.columns:
                        fav_df[c] = ""
                fav_df = fav_df[fav_cols]
            else:
                fav_df = pd.DataFrame(columns=fav_cols)

            st.markdown(f"<h4>✏️ Favorite Products for {fav_customer}</h4>", unsafe_allow_html=True)
            edited_fav = st.data_editor(
                fav_df,
                use_container_width=True,
                num_rows="dynamic",
                key="favorites_editor",
                column_config={
                    col: st.column_config.TextColumn(label)
                    for col, label in fav_labels.items()
                }
            )

            if st.button("💾 Save Favorites", use_container_width=False):
                try:
                    # Preserve every other customer's favorites; replace only this customer's
                    others = [f for f in all_favorites
                              if str(f.get("customer", "")).strip() != fav_customer]
                    new_for_customer = []
                    for rec in edited_fav.fillna("").to_dict('records'):
                        # Skip rows that are completely empty
                        if not any(str(v).strip() for v in rec.values()):
                            continue
                        rec["customer"] = fav_customer
                        new_for_customer.append(rec)
                    merged = others + new_for_customer
                    st.session_state.data_handler.update_supplier_favorites(
                        selected_supplier, merged
                    )
                    st.success(f"✅ Favorites saved for {fav_customer}!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Save failed: {str(e)}")

    # Tab 4: Import/Export
    with tab4:
        st.markdown(f"<h3>💾 Trade Data - {selected_supplier}</h3>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<h4>📥 Import CSV</h4>", unsafe_allow_html=True)

            uploaded_file = st.file_uploader(
                "Choose a CSV file",
                type=['csv'],
                key="csv_upload"
            )

            if uploaded_file is not None:
                try:
                    df_import = pd.read_csv(uploaded_file)

                    st.markdown("<p style='color: #8b95a7;'><b>📋 Preview:</b></p>", unsafe_allow_html=True)
                    st.dataframe(df_import, use_container_width=True)

                    if st.button("✅ Import", use_container_width=True):
                        # Convert to list of dicts
                        rules = df_import.to_dict('records')

                        # Add timestamps
                        for rule in rules:
                            rule['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        if st.session_state.data_handler.update_supplier_rules(
                            selected_supplier,
                            rules
                        ):
                            st.success(f"✅ Imported {len(rules)} rules!")
                            st.rerun()
                        else:
                            st.error("❌ Import failed")

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

        with col2:
            st.markdown("<h4>📤 Export CSV</h4>", unsafe_allow_html=True)

            supplier_rules = st.session_state.data_handler.get_supplier_rules(selected_supplier)

            if supplier_rules:
                df_export = pd.DataFrame(supplier_rules)

                csv = df_export.to_csv(index=False)

                st.download_button(
                    label="⬇️ Download",
                    data=csv,
                    file_name=f"{selected_supplier}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

                st.success(f"✅ Ready! ({len(supplier_rules)} rules)")
            else:
                st.info("📦 Nothing to export yet.")

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
            st.markdown(f"**📋 Rules:** {len(_dh.get_supplier_rules(selected_supplier))}")
            st.markdown(f"**🕐 Time Shift AUT:** {details.get('time_shift_aut') or '—'}")
            st.markdown(f"**🕐 Time Shift UKT:** {details.get('time_shift_ukt') or '—'}")
            st.markdown(f"**👤 POC:** {details.get('poc') or '—'}")
            st.markdown(f"**👥 Team PH:** {details.get('team_ph') or '—'}")
            st.markdown(f"**📝 Information:** {details.get('information') or '—'}")

            st.markdown("<h4>📆 Required Days per Customer</h4>", unsafe_allow_html=True)
            req = _dh.get_required_days(selected_supplier)
            req_cols = ["customer", "required_days"]
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
            if st.button("💾 Save Required Days", key="save_reqdays"):
                rows = [r for r in edited_req.fillna("").to_dict("records")
                        if any(str(v).strip() for v in r.values())]
                if _dh.update_required_days(selected_supplier, rows):
                    st.success("✅ Required days saved!")
                    st.rerun()
                else:
                    st.error("❌ Save failed")

            up_req = st.file_uploader(
                "📥 Import Required Days (CSV columns: customer, required_days)",
                type=["csv"], key="reqdays_csv")
            if up_req is not None:
                try:
                    dfi = pd.read_csv(up_req).fillna("")
                    low = {c.lower().strip(): c for c in dfi.columns}
                    rows = [{
                        "customer": str(r.get(low.get("customer", ""), "")),
                        "required_days": str(r.get(low.get("required_days",
                                          low.get("required days", "")), "")),
                    } for _, r in dfi.iterrows()]
                    st.dataframe(dfi, use_container_width=True)
                    if st.button("✅ Import these required days", key="imp_reqdays"):
                        if _dh.update_required_days(selected_supplier, rows):
                            st.success(f"✅ Imported {len(rows)} rows!")
                            st.rerun()
                        else:
                            st.error("❌ Import failed")
                except Exception as e:
                    st.error(f"❌ Error reading CSV: {e}")

        with col2:
            st.markdown("<h4>⚙️ Manage</h4>", unsafe_allow_html=True)

            with st.form("supplier_details_form"):
                st.markdown("**✏️ Editable details**")
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

            up_det = st.file_uploader(
                "📥 Import Details (CSV columns: time_shift_aut, time_shift_ukt, poc, team_ph, information)",
                type=["csv"], key="details_csv")
            if up_det is not None:
                try:
                    dfd = pd.read_csv(up_det).fillna("")
                    if len(dfd) > 0:
                        row = dfd.iloc[0]
                        low = {c.lower().strip(): c for c in dfd.columns}
                        newdet = {k: str(row.get(low.get(k, ""), "")) for k in
                                  ["time_shift_aut", "time_shift_ukt", "poc", "team_ph", "information"]}
                        st.dataframe(dfd, use_container_width=True)
                        if st.button("✅ Import these details", key="imp_details"):
                            if _dh.update_supplier_details(selected_supplier, newdet):
                                st.success("✅ Details imported!")
                                st.rerun()
                            else:
                                st.error("❌ Import failed")
                except Exception as e:
                    st.error(f"❌ Error reading CSV: {e}")

            st.markdown("---")
            new_name = st.text_input("🏷️ Rename supplier:", value=selected_supplier)
            if st.button("✏️ Update Name", use_container_width=True):
                if _dh.rename_supplier(selected_supplier, new_name):
                    st.success(f"✅ Updated to {new_name}")
                    st.rerun()
                else:
                    st.error("❌ Update failed")

            st.markdown("---")
            if st.button("🗑️ Delete Supplier", type="secondary", use_container_width=True, key="delete_supplier_btn"):
                if _dh.delete_supplier(selected_supplier):
                    st.success("✅ Deleted!")
                    st.rerun()
                else:
                    st.error("❌ Delete failed")

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

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #8b95a7; font-size: 0.85em; padding: 1.5rem;'>
    <p style='font-weight: 700; background: linear-gradient(135deg, #00E676, #00C9FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;'>🚀 Supplier Order Entry System v2.0</p>
    <p>Built with Streamlit ⚡ Powered by GitHub</p>
    </div>
    """, unsafe_allow_html=True)
