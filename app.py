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
        --deep-navy: #030B3A;
        --light-blue: #3AA6F9;
        --accent-teal: #1ABADC;
        --success-green: #10B981;
        --warning-amber: #F59E0B;
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
        color: white !important;
        box-shadow: 0 4px 15px rgba(58, 166, 249, 0.25);
    }

    /* Modern button styling with animations */
    .stButton > button {
        border-radius: 8px !important;
        border: none !important;
        background: linear-gradient(135deg, var(--deep-navy), var(--light-blue)) !important;
        color: white !important;
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

    /* Secondary button styling */
    .stButton > button[kind="secondary"] {
        background: transparent !important;
        border: 2px solid var(--deep-navy) !important;
        color: var(--deep-navy) !important;
    }

    .stButton > button[kind="secondary"]:hover {
        background: linear-gradient(135deg, rgba(3, 11, 58, 0.1), rgba(58, 166, 249, 0.1)) !important;
        border-color: var(--light-blue) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 20px rgba(3, 11, 58, 0.15) !important;
    }

    /* Form submit button with gradient */
    .stFormSubmitButton > button {
        border-radius: 8px !important;
        background: linear-gradient(135deg, var(--light-blue), var(--accent-teal)) !important;
        color: white !important;
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
        color: white !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
        border: none !important;
    }

    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, var(--light-blue), var(--success-green)) !important;
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 8px 20px rgba(16, 185, 129, 0.4) !important;
    }

    /* Header styling with gradient text */
    h1, h2, h3, h4, h5, h6 {
        background: linear-gradient(135deg, var(--deep-navy), var(--light-blue));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
        letter-spacing: 0.5px;
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
        max-height: 440px;
        overflow: auto;
        border-radius: 10px;
        border: 1px solid rgba(3, 11, 58, 0.12);
        margin-bottom: 0.5rem;
    }

    .styled-rules-table {
        border-collapse: collapse;
        width: 100%;
        font-size: 0.9rem;
        font-family: 'Segoe UI', 'Trebuchet MS', sans-serif;
    }

    .styled-rules-table th {
        background: linear-gradient(135deg, var(--deep-navy), var(--light-blue));
        color: white !important;
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

    /* Customer column (first) in navy bold */
    .styled-rules-table td:first-child {
        color: var(--deep-navy);
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

# Logo indented above heading
logo_file = None
if os.path.exists("image_499fc5.png"):
    logo_file = "image_499fc5.png"
elif os.path.exists("Logo.png"):
    logo_file = "Logo.png"

col1, col2, col3 = st.columns([1.2, 1, 1])
with col2:
    if logo_file:
        st.image(logo_file, use_container_width=False, width=350)

col_left, col_center, col_right = st.columns([1, 2, 1])
with col_center:
    st.markdown("<h1 style='text-align: center; margin-top: -10px;'>🚀 Supplier Order Entry System</h1>", unsafe_allow_html=True)

st.markdown("---")

# Sidebar
with st.sidebar:
    st.markdown("<h2>🗂️ Navigation</h2>", unsafe_allow_html=True)

    # Get available suppliers
    suppliers = st.session_state.data_handler.get_all_suppliers()

    if suppliers:
        selected_supplier = st.selectbox(
            "🏭 Select Supplier:",
            suppliers,
            key="supplier_select"
        )
        st.session_state.current_supplier = selected_supplier
    else:
        st.info("📦 No suppliers yet. Create your first supplier!")
        selected_supplier = None

    st.markdown("---")
    st.markdown("<h3>⚡ Quick Actions</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✨ Add New Supplier", use_container_width=True):
            st.session_state.show_new_supplier = True
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    st.toggle(
        "✏️ Edit Rules mode",
        key="edit_rules_mode",
        help="On: edit the rules table. Off: browse the full-screen Rules Overview."
    )

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

# Main content area
if not selected_supplier:
    st.info("👈 Select a supplier from the sidebar to get started.")
else:
    # Create tabs
    tab1, tab_fav, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 View & Edit Rules",
        "⭐ Favorites",
        "➕ Add New Rule",
        "📈 Analytics",
        "💾 Import / Export",
        "ℹ️ Supplier Info"
    ])

    # Tab 1: View & Edit Rules
    with tab1:
        st.markdown(f"<h3>📋 Order Rules for {selected_supplier}</h3>", unsafe_allow_html=True)

        # Get supplier data
        supplier_rules = st.session_state.data_handler.get_supplier_rules(selected_supplier)

        if not supplier_rules or len(supplier_rules) == 0:
            st.info("📦 No rules yet. Create your first rule using the ➕ Add tab!")
        else:
            # Convert to DataFrame for easier viewing
            df = pd.DataFrame(supplier_rules)

            # Search/Filter section
            st.markdown("<h4>🔍 Search & Filter</h4>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                search_customer = st.text_input("👤 Customer:", value="", placeholder="Search customer...")
            with col2:
                search_product = st.text_input("📦 Product:", value="", placeholder="Search product...")
            with col3:
                # Spacer to align the button with the labelled inputs beside it
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                if st.button("🗑️ Clear", use_container_width=True):
                    search_customer = ""
                    search_product = ""

            # Apply filters
            filtered_df = df.copy()
            if search_customer:
                filtered_df = filtered_df[
                    filtered_df['customer'].str.contains(search_customer, case=False, na=False)
                ]
            if search_product:
                filtered_df = filtered_df[
                    filtered_df['ordered_product'].str.contains(search_product, case=False, na=False)
                ]

            st.markdown(f"<p style='color: #666;'><b>📊 Showing {len(filtered_df)} of {len(df)} rules</b></p>", unsafe_allow_html=True)

            # Proper, bold, capitalized column labels reused below
            _col_labels = {
                "customer": "Customer",
                "ordered_product": "Ordered Product",
                "ordered_unit": "Ordered Unit",
                "fresho_product": "Fresho Product",
                "fresho_qty": "Fresho Qty",
                "other_comments": "Other Comments",
                "created_at": "Created At",
            }

            if st.session_state.get("edit_rules_mode", False):
                # ----- Edit mode (toggled on from sidebar Quick Actions) -----
                st.markdown("<h4>✏️ Edit Rules</h4>", unsafe_allow_html=True)
                edited_df = st.data_editor(
                    filtered_df,
                    use_container_width=True,
                    num_rows="dynamic",
                    height=600,
                    key="rules_editor",
                    column_config={
                        col: st.column_config.TextColumn(label)
                        for col, label in _col_labels.items()
                    }
                )

                # Save changes
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    _filter_active = bool(search_customer or search_product)
                    if st.button("💾 Save", use_container_width=True):
                        try:
                            if _filter_active and len(edited_df) < len(df):
                                # Safety: a filter is active, so edited_df is only the
                                # visible subset. Merge edits back into the full set
                                # instead of overwriting and dropping hidden rows.
                                full = df.copy()
                                # Rows shown keep their edits; hidden rows are preserved.
                                hidden = full.loc[~full.index.isin(filtered_df.index)]
                                merged = pd.concat([hidden, edited_df], ignore_index=True)
                                updated_rules = merged.to_dict('records')
                                st.info(f"ℹ️ Merged {len(hidden)} hidden rows with your edits.")
                            else:
                                updated_rules = edited_df.to_dict('records')
                            st.session_state.data_handler.update_supplier_rules(
                                selected_supplier,
                                updated_rules
                            )
                            st.success("✅ Rules saved successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Save failed: {str(e)}")

                with col2:
                    if st.button("🗑️ Delete", use_container_width=True, key="delete_rules_btn"):
                        if st.session_state.data_handler.delete_supplier_rules(selected_supplier):
                            st.success("✅ Rules deleted!")
                            st.rerun()
                        else:
                            st.error("❌ Delete failed")
            else:
                # ----- View mode: full-screen, searchable, expandable overview -----
                st.markdown("<h4>👁️ Rules Overview</h4>", unsafe_allow_html=True)
                st.caption("Hover the table and use the 🔍 search and ⛶ fullscreen icons at its top-right. "
                           "Turn on ✏️ Edit Rules mode in the sidebar to make changes.")
                _overview = filtered_df.rename(columns=_col_labels).fillna("")
                _styled = _overview.style.set_properties(
                    subset=["Customer"], **{"color": "#030B3A", "font-weight": "bold"}
                )
                st.dataframe(
                    _styled,
                    use_container_width=True,
                    hide_index=True,
                    height=620,
                )

            # Display statistics
            st.markdown("---")
            st.markdown("<h3>📊 Quick Stats</h3>", unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("📋 Total", len(df))
            with col2:
                st.metric("👥 Customers", df['customer'].nunique())
            with col3:
                st.metric("📦 Products", df['ordered_product'].nunique())
            with col4:
                # Pull last_updated from the supplier file (not the rules rows)
                _info = st.session_state.data_handler.get_supplier_info(selected_supplier)
                _last = _info.get('last_updated', 'N/A')
                st.metric("⏱️ Updated", str(_last)[:10] if _last != 'N/A' else "N/A")

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

    # Tab 2: Add New Rule
    with tab2:
        st.markdown(f"<h3>➕ Create New Rule - {selected_supplier}</h3>", unsafe_allow_html=True)

        with st.form("new_rule_form"):
            col1, col2 = st.columns(2)

            with col1:
                customer = st.text_input("👤 Customer Name *")
                ordered_product = st.text_input("📦 Ordered Product *")
                ordered_unit = st.text_input("📏 Unit (e.g., box, bag, jar)")

            with col2:
                fresho_product = st.text_input("🔄 Fresho Substitute *")
                fresho_qty = st.text_input("⚖️ Quantity")
                other_comments = st.text_area("📝 Notes", height=100)

            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("➕ Create", use_container_width=True)
            with col2:
                st.form_submit_button("🔄 Reset", use_container_width=True)

            if submitted:
                if not customer or not ordered_product or not fresho_product:
                    st.error("❌ Please fill in all required fields (marked with *)")
                else:
                    new_rule = {
                        'customer': customer,
                        'ordered_product': ordered_product,
                        'ordered_unit': ordered_unit or '',
                        'fresho_product': fresho_product,
                        'fresho_qty': fresho_qty or '',
                        'other_comments': other_comments or '',
                        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }

                    if st.session_state.data_handler.add_rule(selected_supplier, new_rule):
                        st.success("✅ Rule added successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Error adding rule")

    # Tab 3: Analytics
    with tab3:
        st.markdown(f"<h3>📈 Analytics - {selected_supplier}</h3>", unsafe_allow_html=True)

        supplier_rules = st.session_state.data_handler.get_supplier_rules(selected_supplier)

        if supplier_rules:
            df = pd.DataFrame(supplier_rules)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("<h4>👥 Top Customers</h4>", unsafe_allow_html=True)
                top_customers = df['customer'].value_counts().head(10)
                st.bar_chart(top_customers)

            with col2:
                st.markdown("<h4>📦 Top Products</h4>", unsafe_allow_html=True)
                top_products = df['ordered_product'].value_counts().head(10)
                st.bar_chart(top_products)

            st.markdown("---")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("<h4>📏 Unit Types</h4>", unsafe_allow_html=True)
                units = df['ordered_unit'].value_counts()
                st.bar_chart(units)

            with col2:
                st.markdown("<h4>📊 Summary</h4>", unsafe_allow_html=True)
                st.metric("📋 Total Rules", len(df))
                st.metric("👥 Customers", df['customer'].nunique())
                st.metric("📦 Products", df['ordered_product'].nunique())
                st.metric("📝 With Notes", len(df[df['other_comments'].notna()]))
        else:
            st.info("📊 No data to analyze yet.")

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

                    st.markdown("<p style='color: #666;'><b>📋 Preview:</b></p>", unsafe_allow_html=True)
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

    # Tab 5: Supplier Info
    with tab5:
        st.markdown(f"<h3>ℹ️ Details - {selected_supplier}</h3>", unsafe_allow_html=True)

        supplier_info = st.session_state.data_handler.get_supplier_info(selected_supplier)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<h4>📋 Information</h4>", unsafe_allow_html=True)
            st.markdown(f"**🏭 Name:** {supplier_info.get('supplier_name', 'N/A')}")
            st.markdown(f"**📅 Created:** {supplier_info.get('created_at', 'N/A')}")
            st.markdown(f"**⏱️ Updated:** {supplier_info.get('last_updated', 'N/A')}")
            st.markdown(f"**📋 Rules:** {len(st.session_state.data_handler.get_supplier_rules(selected_supplier))}")

        with col2:
            st.markdown("<h4>⚙️ Manage</h4>", unsafe_allow_html=True)

            new_name = st.text_input("🏷️ New name:", value=selected_supplier)

            if st.button("✏️ Update", use_container_width=True):
                if st.session_state.data_handler.rename_supplier(selected_supplier, new_name):
                    st.success(f"✅ Updated to {new_name}")
                    st.rerun()
                else:
                    st.error("❌ Update failed")

            st.markdown("---")

            if st.button("🗑️ Delete", type="secondary", use_container_width=True, key="delete_supplier_btn"):
                if st.session_state.data_handler.delete_supplier(selected_supplier):
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
    <div style='text-align: center; color: #666; font-size: 0.85em; padding: 1.5rem;'>
    <p style='font-weight: 700; background: linear-gradient(135deg, #030B3A, #3AA6F9); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;'>🚀 Supplier Order Entry System v2.0</p>
    <p>Built with Streamlit ⚡ Powered by GitHub</p>
    </div>
    """, unsafe_allow_html=True)
