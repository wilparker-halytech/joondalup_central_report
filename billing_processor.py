"""
Illuminator Central Billing Processor - Core Business Logic
Handles all billing calculations, overlap detection, and summary generation
"""

import pandas as pd
from collections import defaultdict


class IlluminatorBillingProcessor:
    """
    Core billing processor for Illuminator Central usage data.
    
    Handles:
    - CSV parsing
    - Overlap detection between lighting scenarios
    - Billable duration calculation
    - Summary generation for invoicing
    """
    
    def __init__(self, rate_per_kwh, scenario_mappings, composite_rules):
        """
        Initialize the billing processor.
        
        Args:
            rate_per_kwh (float or None): Electricity cost per kilowatt-hour.
                                         If None, uses rates from CSV data.
                                         If provided, overrides all CSV rates.
            scenario_mappings (dict): Maps scenarios to bookable areas
            composite_rules (dict): Defines which scenarios include others
        """
        self.rate_per_kwh = rate_per_kwh
        self.scenario_to_area = scenario_mappings
        self.composite_rules = composite_rules
    
    def parse_illuminator_csv(self, uploaded_file):
        """
        Parse the Illuminator Central CSV export.
        
        Args:
            uploaded_file: File-like object containing CSV data
            
        Returns:
            pandas.DataFrame: Cleaned and parsed usage data
            
        Raises:
            ValueError: If the file is not a valid Illuminator Central CSV
        """
        try:
            # Read CSV, skipping the header line
            df = pd.read_csv(uploaded_file, skiprows=1)
        except Exception as e:
            raise ValueError(f"Unable to read CSV file. Please ensure it's a valid CSV format. Error: {str(e)}")
        
        # Validate required columns exist
        required_columns = ['Club', 'Facility', 'Lighting', 'Turn on', 'Turn off', 'Rated power (kW)']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(
                f"Invalid Illuminator Central CSV file. Missing required columns: {', '.join(missing_columns)}.\n\n"
                f"Expected columns: {', '.join(required_columns)}\n"
                f"Found columns: {', '.join(df.columns.tolist())}\n\n"
                f"Please upload a CSV file exported from Illuminator Central."
            )
        
        # Check if file is empty
        if len(df) == 0:
            raise ValueError("The CSV file is empty. Please upload a file with usage data.")
        
        # Remove summary rows
        df = df[df['Club'].notna() & ~df['Club'].str.contains('Total', na=False)]
        df = df[df['Turn on'].notna()]
        
        # Check if there's any data after filtering
        if len(df) == 0:
            raise ValueError("No valid usage data found in the CSV file after filtering. Please check the file format.")
        
        # Clean up the data
        try:
            df['Turn on'] = pd.to_datetime(df['Turn on'], format='%d/%m/%Y %H:%M:%S')
            df['Turn off'] = pd.to_datetime(df['Turn off'], format='%d/%m/%Y %H:%M:%S')
        except Exception as e:
            raise ValueError(f"Invalid date/time format in 'Turn on' or 'Turn off' columns. Expected format: DD/MM/YYYY HH:MM:SS. Error: {str(e)}")
        
        df['Date'] = df['Turn on'].dt.date
        df['Scenario'] = df['Facility'] + ' - ' + df['Lighting'].str.strip('-')
        
        # Ensure Cost/kWh is numeric (handle dollar sign format like "$1")
        if 'Cost/kWh' in df.columns:
            # Remove dollar sign and convert to float
            df['Cost/kWh'] = df['Cost/kWh'].astype(str).str.replace('$', '', regex=False)
            df['Cost/kWh'] = pd.to_numeric(df['Cost/kWh'], errors='coerce')
        
        return df
    
    def find_unmapped_scenarios(self, df):
        """
        Find scenarios in the CSV that are not in the configuration.
        
        Args:
            df (pandas.DataFrame): Parsed usage data
            
        Returns:
            list: List of dicts with unmapped scenario information
        """
        unmapped = []
        scenario_counts = {}
        
        for _, row in df.iterrows():
            scenario = row['Scenario']
            facility = row['Facility']
            
            if pd.notna(scenario) and scenario not in self.scenario_to_area:
                if scenario not in scenario_counts:
                    scenario_counts[scenario] = {
                        'scenario': scenario,
                        'facility': facility,
                        'count': 0
                    }
                scenario_counts[scenario]['count'] += 1
        
        # Sort by usage count (most used first)
        unmapped = sorted(scenario_counts.values(), key=lambda x: x['count'], reverse=True)
        
        return unmapped
    
    def detect_overlapping_scenarios(self, usage_events):
        """
        Detect overlapping scenarios and mark redundant periods.
        
        When a higher lux level (e.g., 100 lux) is active at the same time
        as a lower lux level (e.g., 50 lux), the lower level is redundant
        because it's included in the higher level.
        
        Args:
            usage_events (list): List of usage event dictionaries
            
        Returns:
            list: Events with redundant_periods marked
        """
        events = usage_events.copy()
        
        for i, event in enumerate(events):
            scenario = event['Scenario']
            start = event['Turn on']
            end = event['Turn off']
            
            # Check if this scenario includes other scenarios
            if scenario in self.composite_rules:
                # Get the list of included scenarios (just scenario names)
                included_scenarios = self.composite_rules[scenario].get('includes', 
                                    self.composite_rules[scenario] if isinstance(self.composite_rules[scenario], list) 
                                    else [])
                
                # Check each other event
                for j, other_event in enumerate(events):
                    if i == j:
                        continue
                    
                    # If the other event is included in this scenario
                    if other_event['Scenario'] in included_scenarios:
                        other_start = other_event['Turn on']
                        other_end = other_event['Turn off']
                        
                        # Calculate overlap period
                        overlap_start = max(start, other_start)
                        overlap_end = min(end, other_end)
                        
                        # If there is an overlap
                        if overlap_start < overlap_end:
                            if 'redundant_periods' not in events[j]:
                                events[j]['redundant_periods'] = []
                            
                            events[j]['redundant_periods'].append({
                                'start': overlap_start,
                                'end': overlap_end,
                                'reason': f"Included in {scenario}"
                            })
        
        return events
    
    def calculate_billable_duration(self, event):
        """
        Calculate actual billable duration excluding redundant periods.
        
        Args:
            event (dict): Usage event with possible redundant_periods
            
        Returns:
            tuple: (billable_minutes, redundant_minutes, notes)
                - billable_minutes (int): Minutes to bill
                - redundant_minutes (int): Minutes excluded
                - notes (list): Explanation of exclusions
        """
        # Total duration in minutes
        total_duration = (event['Turn off'] - event['Turn on']).total_seconds() / 60
        
        # If no redundant periods, bill for full duration
        if 'redundant_periods' not in event:
            return int(round(total_duration)), 0, []
        
        # Calculate redundant duration
        redundant_duration = 0
        notes = []
        
        for period in event['redundant_periods']:
            duration = (period['end'] - period['start']).total_seconds() / 60
            redundant_duration += duration
            notes.append(
                f"{period['start'].strftime('%H:%M')}-{period['end'].strftime('%H:%M')}: "
                f"{period['reason']}"
            )
        
        # Billable duration = total - redundant
        billable_duration = total_duration - redundant_duration
        
        return int(round(billable_duration)), int(round(redundant_duration)), notes
    
    def generate_daily_summaries(self, df):
        """
        Generate daily usage summaries grouped by Date, Club, and Bookable Area.
        
        Creates ONE row per date/club/area combination, even if multiple
        lighting scenarios were used.
        
        Args:
            df (pandas.DataFrame): Parsed usage data
            
        Returns:
            list: List of summary dictionaries ready for CSV export
        """
        summaries = []
        
        # Group by date and club
        for (date, club), club_data in df.groupby(['Date', 'Club']):
            events = club_data.to_dict('records')
            
            # Detect overlapping scenarios
            events = self.detect_overlapping_scenarios(events)
            
            # Group events by bookable area
            area_groups = defaultdict(list)
            for event in events:
                area = self.scenario_to_area.get(event['Scenario'], event['Facility'])
                area_groups[area].append(event)
            
            # Create ONE combined summary per area
            for area, area_events in area_groups.items():
                summary = self.create_combined_summary(date, club, area, area_events)
                summaries.append(summary)
        
        return summaries
    
    def create_combined_summary(self, date, club, area, events):
        """
        Create combined summary for all scenarios in a date/club/area.
        
        Combines multiple lighting scenarios (e.g., North 50, North 100,
        South 50, South 100) into a single invoice line.
        
        Args:
            date: Usage date
            club (str): Club name
            area (str): Bookable area name
            events (list): All events for this date/club/area
            
        Returns:
            dict: Summary with all billing information
        """
        detailed_lines = []
        short_items = []
        total_cost = 0
        total_duration = 0
        
        earliest_start = None
        latest_end = None
        
        # Get facility name from first event
        facility = events[0]['Facility'] if events else "Unknown"
        
        # Process each scenario
        for event in events:
            billable_minutes, redundant_minutes, notes = self.calculate_billable_duration(event)
            
            # Track session start/end times
            if earliest_start is None or event['Turn on'] < earliest_start:
                earliest_start = event['Turn on']
            if latest_end is None or event['Turn off'] > latest_end:
                latest_end = event['Turn off']
            
            # Calculate cost for this scenario
            billable_hours = billable_minutes / 60
            scenario_name = str(event['Lighting']).strip('-').strip() if pd.notna(event['Lighting']) else 'Unknown'
            
            # Use override rate if provided, otherwise use rate from CSV (with fallback)
            if self.rate_per_kwh is not None:
                effective_rate = self.rate_per_kwh
            else:
                # Try to get rate from CSV, fallback to 0.263 if missing
                effective_rate = event.get('Cost/kWh', 0.263)
            
            cost = round(billable_hours * event['Rated power (kW)'] * effective_rate, 2)
            total_cost += cost
            total_duration += billable_minutes
            
            start_time = event['Turn on'].strftime('%H:%M')
            end_time = event['Turn off'].strftime('%H:%M')
            
            # Build detailed line for this scenario
            detail_line = f"{scenario_name}: {start_time}-{end_time} | {billable_minutes} min | ${cost:.2f}"
            redundant_scenario = None
            
            if redundant_minutes > 0:
                # Extract the scenario name from redundancy note
                redundant_scenario = "higher lux"
                for note in notes:
                    if "Included in" in note:
                        parts = note.split("Included in ")
                        if len(parts) > 1:
                            full_scenario = parts[1]
                            # Get just the lighting part (e.g., "South 100 lux")
                            if " - " in full_scenario:
                                redundant_scenario = full_scenario.split(" - ")[-1]
                            else:
                                redundant_scenario = full_scenario
                detail_line += f" ({redundant_minutes} min in {redundant_scenario})"
            
            detailed_lines.append(detail_line)
            
            # Build short summary item (only if billable minutes > 0)
            if billable_minutes > 0:
                short_item = f"{scenario_name}: {start_time}-{end_time} ({billable_minutes}min)"
                if redundant_minutes > 0 and redundant_scenario:
                    short_item += f" ({redundant_minutes}min in {redundant_scenario})"
                short_items.append(short_item)
        
        # Build compact detailed summary with day of week
        day_of_week = pd.to_datetime(date).strftime('%a')  # Mon, Tue, Wed, etc.
        detailed_summary = f"{facility} | {area} | Date: {date} ({day_of_week}) | Club: {club}\n"
        detailed_summary += f"Session: {earliest_start.strftime('%H:%M')}-{latest_end.strftime('%H:%M')} | Total Duration: {total_duration} min | Total Cost: ${total_cost:.2f}\n"
        detailed_summary += "\n".join(detailed_lines)
        
        # Build short summary (invoice line)
        short_summary = " | ".join(short_items) + f" | Total: ${total_cost:.2f}"
        
        return {
            'Date': date,
            'Club': club,
            'Area': area,
            'Start Time': earliest_start.strftime('%H:%M'),
            'End Time': latest_end.strftime('%H:%M'),
            'Duration (minutes)': total_duration,
            'Detailed Summary': detailed_summary,
            'Short Summary': short_summary,
            'Total Cost': round(total_cost, 2)
        }