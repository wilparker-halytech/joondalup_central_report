"""
Illuminator Central Billing Processor - Web Interface
Streamlit app for processing Illuminator usage data
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import io
from ruamel.yaml import YAML
from pathlib import Path

# Import the business logic
from billing_processor import IlluminatorBillingProcessor

# Page config
st.set_page_config(
    page_title="Illuminator Billing Processor",
    page_icon="💡",
    layout="wide"
)

# Load configuration
def load_config():
    """Load configuration from config.yaml file"""
    config_path = Path("config.yaml")
    
    if not config_path.exists():
        st.error("""
        ❌ **Configuration file not found!**
        
        Please create a `config.yaml` file in the same directory as this app.
        
        You can download the template from the documentation or create one with:
        - scenario_mappings
        - composite_rules
        - billing settings
        """)
        st.stop()
    
    try:
        yaml_handler = YAML()
        yaml_handler.preserve_quotes = True
        with open(config_path, 'r') as f:
            config = yaml_handler.load(f)
        return config
    except Exception as e:
        st.error(f"""
        ❌ **Error reading configuration file!**
        
        The config.yaml file has a syntax error:
        ```
        {str(e)}
        ```
        
        Please fix the YAML syntax and refresh the page.
        """)
        st.stop()

# Load config at startup
config = load_config()

# ============================================================================
# SIDEBAR
# ============================================================================

st.sidebar.title("⚙️ Settings")

with st.sidebar:
    # Rate input - optional override
    rate_per_kwh = st.number_input(
        "Override Rate ($/kWh)",
        min_value=0.0,
        max_value=10.0,
        value=None,
        step=0.001,
        format="%.3f",
        placeholder="from CSV",
        help="Leave blank to use rates from CSV data. Enter a value to override all rates in the report."
    )
    
    st.markdown("---")
    st.markdown("### 📋 Configuration")
    
    # Show rate source
    if rate_per_kwh is not None:
        st.info(f"💰 **Rate:** ${rate_per_kwh:.3f}/kWh (override)")
    else:
        st.info(f"💰 **Rate:** from CSV data")
    
    # Show config file status
    config_path = Path("config.yaml")
    if config_path.exists():
        st.success("✅ config.yaml loaded")
        
        # Show summary
        num_scenarios = len(config.get('scenario_mappings', {}))
        num_rules = len(config.get('composite_rules', {}))
        
        st.info(f"""
        **Mappings:** {num_scenarios} scenarios  
        **Rules:** {num_rules} composite rules
        """)
        
        with st.expander("📄 View Config"):
            # Display using ruamel.yaml to show formatted version
            yaml_handler = YAML()
            string_stream = io.StringIO()
            yaml_handler.dump(config, string_stream)
            st.code(string_stream.getvalue(), language='yaml')
    else:
        st.error("❌ config.yaml not found")
    
    st.markdown("---")
    st.markdown("### 📊 About")
    st.markdown("""
    This tool:
    - ✅ Prevents double-charging
    - ✅ Handles overlapping scenarios
    - ✅ Groups by date/club/area
    - ✅ Generates invoice summaries
    - ✅ Uses external config file
    """)

# ============================================================================
# MAIN CONTENT - TABS
# ============================================================================

tab1, tab2, tab3 = st.tabs(["📤 Process File", "📖 Instructions", "ℹ️ Help"])

# ----------------------------------------------------------------------------
# TAB 1: PROCESS FILE
# ----------------------------------------------------------------------------

def get_facility_name(scenario_name):
    """Extract facility name from scenario (everything before the last dash section)"""
    # Examples:
    # "Admiral Park - North 50 lux" -> "Admiral Park"
    # "Percy Doyle - Pitch 1 50 lux" -> "Percy Doyle"
    parts = scenario_name.split(' - ')
    if len(parts) >= 2:
        return parts[0]
    return scenario_name

def get_existing_areas_for_facility(facility_name, config):
    """Get all unique areas already mapped for this facility"""
    areas = set()
    for scenario, area in config['scenario_mappings'].items():
        if get_facility_name(scenario) == facility_name:
            areas.add(area)
    return sorted(list(areas))
    
with tab1:
    uploaded_file = st.file_uploader(
        "Upload Illuminator Central CSV Export",
        type=['csv'],
        help="Select the CSV file exported from Illuminator Central"
    )
    
    if uploaded_file is not None:
        try:
            # Reload config on each upload to pick up any changes
            config = load_config()
            st.success("✅ Configuration reloaded")
            
            # Get mappings from config file
            scenario_mappings = config.get('scenario_mappings', {})
            composite_rules = config.get('composite_rules', {})
            
            if not scenario_mappings:
                st.error("""
                ❌ **No scenario mappings found in config.yaml!**
                
                Please add scenario mappings to your config.yaml file.
                """)
                st.stop()
            
            # Initialize the processor with config
            processor = IlluminatorBillingProcessor(
                rate_per_kwh, 
                scenario_mappings, 
                composite_rules
            )
            
            with st.spinner('Analyzing CSV...'):
                # Parse the CSV
                df = processor.parse_illuminator_csv(uploaded_file)
                
                # Check for unmapped scenarios
                unmapped_scenarios = processor.find_unmapped_scenarios(df)
                
                # Reset file pointer for potential second read
                uploaded_file.seek(0)
            
            if unmapped_scenarios:
                # STRICT MODE: Block processing until all scenarios are mapped
                st.error(f"❌ **Cannot Process: {len(unmapped_scenarios)} Unmapped Scenarios Found**")
                
                st.markdown("""
                ---
                ### 🔧 Configuration Required
                
                The CSV contains scenarios that are not in your `config.yaml`. 
                Please map each scenario to a bookable area below, then download 
                the updated configuration file.
                
                **Steps:**
                1. Map each scenario below
                2. Click "Download Updated Config"
                3. Replace your `config.yaml` with the downloaded file
                4. Restart Streamlit and upload the CSV again
                """)
                
                # Initialize session state for new mappings
                if 'new_mappings' not in st.session_state:
                    st.session_state.new_mappings = {}
                
                # Show progress at the top
                mapped_count = len(st.session_state.new_mappings)
                total_count = len(unmapped_scenarios)
                remaining = total_count - mapped_count
                progress = mapped_count / total_count if total_count > 0 else 0
                
                # Progress bar
                st.progress(progress)
                
                # Status message
                if remaining > 0:
                    st.warning(f"⚠️ **{remaining} scenarios still need mapping** ({mapped_count}/{total_count} complete)")
                else:
                    st.success(f"✅ **All scenarios mapped!** ({mapped_count}/{total_count})")
                
                st.markdown("---")
                st.subheader("⚠️ Unmapped Scenarios")
                
                # Group scenarios by facility
                facility_groups = {}
                for item in unmapped_scenarios:
                    facility = item['facility']
                    if facility not in facility_groups:
                        facility_groups[facility] = []
                    facility_groups[facility].append(item)
                
                # Show scenarios grouped by facility
                for facility, items in facility_groups.items():
                    # Get existing areas already mapped for this facility
                    suggested_areas = get_existing_areas_for_facility(facility, config)
                    
                    # If no existing areas, provide a generic default
                    if not suggested_areas:
                        suggested_areas = ["Field"]
                    
                    # Add custom option
                    suggested_areas.append("⚙️ Custom...")
                    
                    with st.expander(f"📍 **{facility}** ({len(items)} scenarios)", expanded=True):
                        for item in items:
                            scenario = item['scenario']
                            count = item['count']
                            
                            # Check if this scenario is already mapped
                            is_mapped = scenario in st.session_state.new_mappings
                            
                            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                            
                            with col1:
                                # Visual indicator: ✅ mapped, ⚠️ unmapped
                                icon = "✅" if is_mapped else "⚠️"
                                st.markdown(f"{icon} **{scenario.replace(facility + ' - ', '')}**")
                                st.caption(f"Used {count} times")
                            
                            with col2:
                                # Show current mapping or dropdown
                                if is_mapped:
                                    current_mapping = st.session_state.new_mappings[scenario]
                                    st.text_input(
                                        "Area:",
                                        value=current_mapping,
                                        key=f"map_{scenario}",
                                        disabled=True,
                                        label_visibility="collapsed"
                                    )
                                else:
                                    # Dropdown with suggested areas
                                    selected_area = st.selectbox(
                                        "Select area:",
                                        options=suggested_areas,
                                        key=f"dropdown_{scenario}",
                                        label_visibility="collapsed"
                                    )
                            
                            with col3:
                                # Show custom input if "Custom..." selected
                                if not is_mapped:
                                    selected_area = st.session_state.get(f"dropdown_{scenario}", suggested_areas[0])
                                    if selected_area == "⚙️ Custom...":
                                        custom_area = st.text_input(
                                            "Custom name:",
                                            key=f"custom_{scenario}",
                                            placeholder="Enter custom area...",
                                            label_visibility="collapsed"
                                        )
                            
                            with col4:
                                if is_mapped:
                                    # Show edit button for mapped scenarios
                                    if st.button("✏️", key=f"btn_{scenario}", help="Edit mapping"):
                                        del st.session_state.new_mappings[scenario]
                                        st.rerun()
                                else:
                                    # Show save button for unmapped scenarios
                                    if st.button("💾", key=f"btn_{scenario}", help="Save mapping"):
                                        selected_area = st.session_state.get(f"dropdown_{scenario}", suggested_areas[0])
                                        
                                        if selected_area == "⚙️ Custom...":
                                            # Use custom input
                                            custom_area = st.session_state.get(f"custom_{scenario}", "")
                                            if custom_area and custom_area.strip():
                                                st.session_state.new_mappings[scenario] = custom_area.strip()
                                                st.rerun()
                                            else:
                                                st.error("❌ Enter custom area name!")
                                        else:
                                            # Use selected dropdown value
                                            st.session_state.new_mappings[scenario] = selected_area
                                            st.rerun()
                            
                            st.markdown("---")
                
                # Show summary of mappings
                mapped_count = len(st.session_state.new_mappings)
                total_count = len(unmapped_scenarios)
                
                st.markdown("---")
                
                if mapped_count > 0:
                    with st.expander(f"✅ Mapped Scenarios ({mapped_count})", expanded=False):
                        for scenario, area in st.session_state.new_mappings.items():
                            st.success(f"✅ `{scenario}` → **{area}**")
                
                # Calculate unmapped
                unmapped_list = [item['scenario'] for item in unmapped_scenarios 
                                if item['scenario'] not in st.session_state.new_mappings]
                
                if unmapped_list:
                    with st.expander(f"⚠️ Still Unmapped ({len(unmapped_list)})", expanded=True):
                        for scenario in unmapped_list:
                            st.warning(f"⚠️ `{scenario}` - **Not yet mapped**")
                
                # Generate updated config
                if mapped_count == total_count:
                    st.markdown("---")
                    st.success("🎉 All scenarios mapped! Download your updated config below.")
                    
                    # Load original config with ruamel.yaml to preserve comments
                    yaml_handler = YAML()
                    yaml_handler.preserve_quotes = True
                    
                    with open(Path("config.yaml"), 'r') as f:
                        updated_config = yaml_handler.load(f)
                    
                    # Add new mappings to scenario_mappings
                    if 'scenario_mappings' not in updated_config:
                        updated_config['scenario_mappings'] = {}
                    
                    updated_config['scenario_mappings'].update(st.session_state.new_mappings)
                    
                    # Dump to string with preserved formatting
                    string_stream = io.StringIO()
                    yaml_handler.dump(updated_config, string_stream)
                    updated_yaml = string_stream.getvalue()
                    
                    st.download_button(
                        label="📥 Download Updated Config",
                        data=updated_yaml,
                        file_name="config.yaml",
                        mime="text/yaml",
                        help="Download this file and replace your existing config.yaml"
                    )
                    
                    st.info("""
                    **Next Steps:**
                    1. Save the downloaded file as `config.yaml` in your project folder
                    2. Restart Streamlit: Press `Ctrl+C` then run `streamlit run streamlit_app.py`
                    3. Upload your CSV again - processing will now work!
                    """)
                else:
                    remaining = total_count - mapped_count
                    st.warning(f"⚠️ Please map the remaining {remaining} scenarios to continue.")
                
                # Stop execution here - don't show processing UI
                st.stop()
            
            # If we get here, all scenarios are mapped - continue with normal processing
            st.success(f"✅ All {len(df)} records use mapped scenarios!")
            
            with st.spinner('Generating billing summaries...'):
                
                # Show statistics
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Records", len(df))
                col2.metric("Clubs", df['Club'].nunique())
                col3.metric("Date Range", f"{df['Date'].min()} to {df['Date'].max()}")
                col4.metric("Facilities", df['Facility'].nunique())
                
                # Generate summaries
                summaries = processor.generate_daily_summaries(df)
                
                st.success(f"✅ Generated {len(summaries)} billing summaries")
                
                # Summary statistics
                output_df = pd.DataFrame(summaries)
                total_billed = output_df['Total Cost'].sum()
                
                st.metric("Total Billed", f"${total_billed:.2f}")
                
                # Preview
                st.subheader("📋 Preview (first 5 records)")
                preview_df = output_df[['Date', 'Club', 'Area', 'Short Summary', 'Total Cost']].head()
                st.dataframe(preview_df, use_container_width=True)
                
                # Download button
                csv_buffer = io.StringIO()
                output_df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
                
                st.download_button(
                    label="⬇️ Download Billing Import CSV",
                    data=csv_buffer.getvalue(),
                    file_name=f"billing_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    help="Download the processed billing data for import to booking system"
                )
                
                # Sample detailed view
                with st.expander("👁️ View Sample Detailed Summary"):
                    sample = summaries[0]
                    st.text(sample['Detailed Summary'])
        
        except ValueError as e:
            # User-friendly errors from validation
            st.error(f"❌ **Invalid File Format**")
            st.error(str(e))
            st.info("""
            **How to get a valid Illuminator Central CSV:**
            1. Log into Illuminator Central
            2. Navigate to Reports or Usage section
            3. Select the date range you want
            4. Click "Export to CSV" or similar
            5. Upload the downloaded CSV file here
            """)
            st.stop()
        except Exception as e:
            st.error(f"❌ **Unexpected Error**")
            st.error(f"An unexpected error occurred while processing the file: {str(e)}")
            st.exception(e)
            st.stop()

# ----------------------------------------------------------------------------
# TAB 2: INSTRUCTIONS
# ----------------------------------------------------------------------------

with tab2:
    st.markdown("""
    ## 📖 How to Use
    
    ### Step 1: Configure Facilities
    1. Edit `config.yaml` to add your facilities
    2. Map Illuminator scenarios to bookable areas
    3. Define composite rules (e.g., 100 lux includes 50 lux)
    4. Set electricity rate
    
    ### Step 2: Export from Illuminator Central
    1. Log into Illuminator Central
    2. Generate usage report for desired date range
    3. Download as CSV file
    
    ### Step 3: Upload File
    1. Click "Browse files" above
    2. Select your Illuminator CSV export
    3. Wait for processing to complete
    
    ### Step 4: Download Results
    1. Review the summary statistics
    2. Check the preview table
    3. Click "Download Billing Import CSV"
    4. Import the file into your booking system
    
    ## 📊 Output Format
    
    The generated CSV contains:
    - **Date** - Usage date
    - **Club** - Club name
    - **Area** - Bookable area (from config.yaml)
    - **Start Time** - Session start time
    - **End Time** - Session end time
    - **Duration (minutes)** - Total billable minutes
    - **Detailed Summary** - Full breakdown for staff/disputes
    - **Short Summary** - Invoice-friendly one-liner
    - **Total Cost** - Daily cost for that club/area
    
    ## ⚙️ Configuration File
    
    All facility mappings are in `config.yaml`:
    ```yaml
    scenario_mappings:
      "Admiral Park - North 50 lux": "Field 1"
      "Admiral Park - North 100 lux": "Field 1"
      # Add your facilities...
    
    composite_rules:
      "Admiral Park - North 100 lux":
        includes:
          - "Admiral Park - North 50 lux"
        power_kw: 1.67
      # Add your rules...
    
    billing:
      rate_per_kwh: 0.263
    ```
    
    ## ⚠️ Important Notes
    
    - The tool automatically detects overlapping scenarios (e.g., 50 lux + 100 lux)
    - Lower lux levels are marked as redundant when higher levels are active
    - Only the highest lux level is billed during overlap periods
    - **Facility** = Where lights are installed (e.g., "Admiral Park")
    - **Area** = What customers book (e.g., "Field 1")
    - Edit `config.yaml` to add or modify facilities (no code changes needed!)
    """)

# ----------------------------------------------------------------------------
# TAB 3: HELP
# ----------------------------------------------------------------------------

with tab3:
    st.markdown("""
    ## ℹ️ Help & Support
    
    ### Common Issues
    
    **"Error processing file"**
    - Ensure you're uploading an Illuminator Central CSV export
    - Check the file isn't corrupted
    - Verify it contains the expected columns (Club, Facility, Lighting, Turn on, Turn off, etc.)
    
    **"No scenario mappings found"**
    - Check that `config.yaml` exists in the same folder as this app
    - Verify the `scenario_mappings:` section has entries
    - Make sure the YAML syntax is correct (no tabs, proper indentation)
    
    **"Unmapped scenario" warnings**
    - A scenario in your CSV is not in `config.yaml`
    - Add the missing scenario to `scenario_mappings`
    - Map it to the appropriate bookable area
    
    **"Total doesn't match manual calculation"**
    - Check the rate per kWh is correct
    - Verify composite rules are set up correctly
    - Review the detailed summary for specific entries
    - Remember: overlapping scenarios are automatically detected
    
    ### Understanding the Output
    
    **Detailed Summary:**
    - Shows ALL scenarios (including 0-minute redundant ones)
    - Explains exactly what was billed and why
    - Use for dispute resolution and auditing
    
    **Short Summary:**
    - Shows only scenarios with billable minutes > 0
    - Clean, invoice-ready format
    - Use for importing to booking system
    
    ### Configuration Required
    
    Before production use, update:
    1. **Scenario Mappings** - Map all scenarios to bookable areas
    2. **Composite Rules** - Define which scenarios include others
    3. **Power Ratings** - Set correct kW for each composite rule
    4. **Rate per kWh** - Set correct electricity rate
    
    ### Contact
    
    For technical support or questions:
    - Email: support@halytech.com.au
    - Documentation: Available in the GitHub repository
    """)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.8em;'>
Illuminator Billing Processor | Powered by Halytech | Version 1.0
</div>
""", unsafe_allow_html=True)
