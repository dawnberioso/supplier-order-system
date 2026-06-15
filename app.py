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

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 0rem;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1.1em;
    }
    </style>
    """, unsafe_allow_html=True)

# Header
st.title("📦 Supplier Order Entry Management System")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings & Navigation")
    
    # Get available suppliers
    suppliers = st.session_state.data_handler.get_all_suppliers()
    
    if suppliers:
        selected_supplier = st.selectbox(
            "Select Supplier:",
            suppliers,
            key="supplier_select"
        )
        st.session_state.current_supplier = selected_supplier
    else:
        st.warning("No suppliers found. Create one first!")
        selected_supplier = None
    
    st.markdown("---")
    st.subheader("Quick Actions")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Add New Supplier"):
            st.session_state.show_new_supplier = True
    with col2:
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    st.markdown("---")
    st.subheader("GitHub Sync")
    
    if st.button("📤 Push to GitHub"):
        with st.spinner("Syncing to GitHub..."):
            success = st.session_state.data_handler.push_to_github()
            if success:
                st.success("✅ Successfully pushed to GitHub!")
            else:
                st.error("❌ Failed to push to GitHub")
    
    if st.button("📥 Pull from GitHub"):
        with st.spinner("Pulling from GitHub..."):
            success = st.session_state.data_handler.pull_from_github()
            if success:
                st.success("✅ Successfully pulled from GitHub!")
            else:
                st.warning("⚠️ No changes to pull")

# Main content area
if not selected_supplier:
    st.info("👈 Please select a supplier from the sidebar to get started.")
else:
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 View & Edit Rules",
        "➕ Add New Rule",
        "📊 Analytics",
        "📁 Import/Export",
        "ℹ️ Supplier Info"
    ])
    
    # Tab 1: View & Edit Rules
    with tab1:
        st.subheader(f"Order Rules for {selected_supplier}")
        
        # Get supplier data
        supplier_rules = st.session_state.data_handler.get_supplier_rules(selected_supplier)
        
        if not supplier_rules or len(supplier_rules) == 0:
            st.info("No rules yet. Add your first rule using the 'Add New Rule' tab!")
        else:
            # Convert to DataFrame for easier viewing
            df = pd.DataFrame(supplier_rules)
            
            # Search/Filter section
            col1, col2, col3 = st.columns(3)
            with col1:
                search_customer = st.text_input("🔍 Search by Customer:", value="")
            with col2:
                search_product = st.text_input("🔍 Search by Product:", value="")
            with col3:
                if st.button("Clear Filters"):
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
            
            st.write(f"Showing {len(filtered_df)} of {len(df)} rules")
            
            # Editable data grid
            st.subheader("Edit Rules")
            edited_df = st.data_editor(
                filtered_df,
                use_container_width=True,
                num_rows="dynamic",
                key="rules_editor"
            )
            
            # Save changes
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                _filter_active = bool(search_customer or search_product)
                if st.button("💾 Save Changes"):
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
                            st.info(f"Filter was active — merged your edits with {len(hidden)} hidden rows so nothing was lost.")
                        else:
                            updated_rules = edited_df.to_dict('records')
                        st.session_state.data_handler.update_supplier_rules(
                            selected_supplier,
                            updated_rules
                        )
                        st.success("✅ Rules updated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error saving rules: {str(e)}")
            
            with col2:
                if st.button("🗑️ Delete All Shown"):
                    if st.session_state.data_handler.delete_supplier_rules(selected_supplier):
                        st.success("✅ Rules deleted!")
                        st.rerun()
                    else:
                        st.error("❌ Error deleting rules")
            
            # Display statistics
            st.markdown("---")
            st.subheader("📊 Quick Stats")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Rules", len(df))
            with col2:
                st.metric("Unique Customers", df['customer'].nunique())
            with col3:
                st.metric("Unique Products", df['ordered_product'].nunique())
            with col4:
                # Pull last_updated from the supplier file (not the rules rows)
                _info = st.session_state.data_handler.get_supplier_info(selected_supplier)
                _last = _info.get('last_updated', 'N/A')
                st.metric("Last Updated", str(_last)[:10] if _last != 'N/A' else "N/A")
    
    # Tab 2: Add New Rule
    with tab2:
        st.subheader(f"Add New Rule - {selected_supplier}")
        
        with st.form("new_rule_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                customer = st.text_input("Customer Name *")
                ordered_product = st.text_input("Ordered Product *")
                ordered_unit = st.text_input("Ordered Unit (e.g., box, bag, jar)")
            
            with col2:
                fresho_product = st.text_input("Fresho Product (Substitute) *")
                fresho_qty = st.text_input("Fresho Quantity")
                other_comments = st.text_area("Other Comments", height=100)
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("➕ Add Rule", use_container_width=True)
            with col2:
                st.form_submit_button("Clear Form", use_container_width=True)
            
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
        st.subheader(f"Analytics - {selected_supplier}")
        
        supplier_rules = st.session_state.data_handler.get_supplier_rules(selected_supplier)
        
        if supplier_rules:
            df = pd.DataFrame(supplier_rules)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Top Customers")
                top_customers = df['customer'].value_counts().head(10)
                st.bar_chart(top_customers)
            
            with col2:
                st.subheader("Top Ordered Products")
                top_products = df['ordered_product'].value_counts().head(10)
                st.bar_chart(top_products)
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Ordered Units Distribution")
                units = df['ordered_unit'].value_counts()
                st.bar_chart(units)
            
            with col2:
                st.metric("Total Rules", len(df))
                st.metric("Unique Customers", df['customer'].nunique())
                st.metric("Unique Products", df['ordered_product'].nunique())
                st.metric("Rules with Comments", len(df[df['other_comments'].notna()]))
        else:
            st.info("No data to analyze yet.")
    
    # Tab 4: Import/Export
    with tab4:
        st.subheader(f"Import/Export - {selected_supplier}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📥 Import from CSV")
            
            uploaded_file = st.file_uploader(
                "Choose a CSV file",
                type=['csv'],
                key="csv_upload"
            )
            
            if uploaded_file is not None:
                try:
                    df_import = pd.read_csv(uploaded_file)
                    
                    st.write("Preview of imported data:")
                    st.dataframe(df_import)
                    
                    if st.button("✅ Import This Data"):
                        # Convert to list of dicts
                        rules = df_import.to_dict('records')
                        
                        # Add timestamps
                        for rule in rules:
                            rule['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        if st.session_state.data_handler.update_supplier_rules(
                            selected_supplier,
                            rules
                        ):
                            st.success(f"✅ Imported {len(rules)} rules successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Error importing data")
                
                except Exception as e:
                    st.error(f"❌ Error reading CSV: {str(e)}")
        
        with col2:
            st.subheader("📤 Export to CSV")
            
            supplier_rules = st.session_state.data_handler.get_supplier_rules(selected_supplier)
            
            if supplier_rules:
                df_export = pd.DataFrame(supplier_rules)
                
                csv = df_export.to_csv(index=False)
                
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"{selected_supplier}_rules_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
                st.success(f"Ready to download! ({len(supplier_rules)} rules)")
            else:
                st.info("No data to export yet.")
    
    # Tab 5: Supplier Info
    with tab5:
        st.subheader(f"Supplier Information - {selected_supplier}")
        
        supplier_info = st.session_state.data_handler.get_supplier_info(selected_supplier)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Supplier Name:** {supplier_info.get('supplier_name', 'N/A')}")
            st.write(f"**Created:** {supplier_info.get('created_at', 'N/A')}")
            st.write(f"**Last Updated:** {supplier_info.get('last_updated', 'N/A')}")
            st.write(f"**Total Rules:** {len(st.session_state.data_handler.get_supplier_rules(selected_supplier))}")
        
        with col2:
            st.subheader("Actions")
            
            new_name = st.text_input("Rename supplier:", value=selected_supplier)
            
            if st.button("Update Supplier Name"):
                if st.session_state.data_handler.rename_supplier(selected_supplier, new_name):
                    st.success(f"✅ Renamed to {new_name}")
                    st.rerun()
                else:
                    st.error("❌ Error renaming supplier")
            
            st.markdown("---")
            
            if st.button("🗑️ Delete Entire Supplier", type="secondary"):
                if st.session_state.data_handler.delete_supplier(selected_supplier):
                    st.success("✅ Supplier deleted!")
                    st.rerun()
                else:
                    st.error("❌ Error deleting supplier")

# Add New Supplier Modal
if st.session_state.get('show_new_supplier', False):
    with st.form("new_supplier_form"):
        st.subheader("Create New Supplier")
        
        supplier_name = st.text_input("Supplier Name *")
        description = st.text_area("Description (optional)")
        
        if st.form_submit_button("Create Supplier"):
            if not supplier_name:
                st.error("❌ Please enter a supplier name")
            else:
                if st.session_state.data_handler.create_supplier(supplier_name, description):
                    st.success(f"✅ Supplier '{supplier_name}' created!")
                    st.session_state.show_new_supplier = False
                    st.rerun()
                else:
                    st.error("❌ Error creating supplier")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
    <p>Supplier Order Entry Management System v1.0</p>
    <p>Built with Streamlit | Data stored in GitHub</p>
    </div>
    """, unsafe_allow_html=True)
