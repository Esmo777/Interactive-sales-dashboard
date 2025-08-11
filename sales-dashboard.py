import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

# Set Streamlit page configuration for a professional and clean style.
st.set_page_config(layout="wide", page_title="Superstore Sales Dashboard", page_icon="📊")

# --- Data Loading and Preprocessing ---
# Use @st.cache_data for optimal performance.
@st.cache_data
def load_data(path):
    """
    Loads the CSV file and performs data preprocessing.
    """
    df = pd.read_csv(path)
    # Convert the date column to datetime format
    df['Order Date'] = pd.to_datetime(df['Order Date'], format='%m/%d/%Y')
    # Extract year and month
    df['Year'] = df['Order Date'].dt.year
    df['Month'] = df['Order Date'].dt.month
    # Create a 'YYYY-MM' column for time-series charts
    df['Month-Year'] = df['Order Date'].dt.to_period('M').astype(str)
    return df

try:
    # Try to load the data
    df = load_data("Sample - Superstore.csv")
except FileNotFoundError:
    st.error("Error: The file 'Sample - Superstore.csv' was not found. Please ensure it is in the same directory.")
    st.stop()


# --- Custom CSS for professional styling ---
st.markdown("""
    <style>
        /* General styles for the dashboard */
        .main {
            background-color: #f0f2f6;
            color: #333333;
            font-family: 'Open Sans', sans-serif;
        }
        /* Hide the default Streamlit menu */
        .st-emotion-cache-18ni91u.ezrtsby2 {
            visibility: hidden;
        }
        /* Padding and margins for the main container */
        .reportview-container .main .block-container {
            padding-top: 2rem;
            padding-right: 2rem;
            padding-left: 2rem;
            padding-bottom: 2rem;
        }
        /* Button styling for exports */
        .stButton button {
            color: white;
            background-color: #26547C; /* Dark blue */
            border-radius: 5px;
            border: 1px solid #26547C;
            font-weight: bold;
            padding: 8px 16px;
        }
        .stButton button:hover {
            background-color: #386fa8; /* Lighter blue on hover */
        }
        .st-emotion-cache-12fmj2r.e1ewe7hr3 {
            color: white;
            background-color: #26547C;
            border-radius: 5px;
            border: 1px solid #26547C;
        }
        /* KPI card styling */
        .kpi-card {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            height: 100%;
        }
        .kpi-card h3 {
            font-size: 1.2rem;
            color: #555555;
            margin: 0 0 10px 0;
            font-family: 'Open Sans', sans-serif;
        }
        .kpi-card .value {
            font-size: 2rem;
            font-weight: bold;
            color: #26547C; /* Dark blue for main data */
            font-family: 'Roboto', sans-serif;
        }
        /* Borders for chart containers */
        .st-emotion-cache-13k623y.e1ewe7hr2 {
            border-color: #dddddd;
            border-radius: 10px;
        }
        /* Sidebar styling */
        .st-emotion-cache-10o96hp.ezrtsby0 {
            background-color: #f9f9f9;
        }
        
        /* --- Styles for dark mode --- */
        .dark-mode {
            background-color: #1a1a1a;
            color: #f0f2f6;
        }
        .dark-mode .st-emotion-cache-10o96hp.ezrtsby0 {
            background-color: #262626; /* Sidebar color in dark mode */
        }
        .dark-mode .kpi-card {
            background-color: #262626;
            box-shadow: 0 4px 6px rgba(255, 255, 255, 0.1);
        }
        .dark-mode .kpi-card h3 {
            color: #bbbbbb;
        }
        .dark-mode .kpi-card .value {
            color: #F7882F; /* Orange accent for dark mode */
        }
        .dark-mode .stButton button {
            color: #f0f2f6;
            background-color: #F7882F;
            border: 1px solid #F7882F;
        }
        .dark-mode .st-emotion-cache-12fmj2r.e1ewe7hr3 {
            color: #f0f2f6;
            background-color: #F7882F;
            border: 1px solid #F7882F;
        }
        .dark-mode .st-emotion-cache-13k623y.e1ewe7hr2 {
            border-color: #383838;
        }
    </style>
    """, unsafe_allow_html=True)


# --- Sidebar for filters and configuration ---
with st.sidebar:
    st.title("📊 Superstore Dashboard")
    st.markdown("---")

    # Bonus: Switch for light/dark mode
    dark_mode = st.checkbox("Dark Mode", value=False)
    
    # Apply dark mode styles if enabled
    if dark_mode:
        st.markdown(
            f"""
            <style>
                .main {{ background-color: #1a1a1a; color: #f0f2f6; }}
                .st-emotion-cache-10o96hp.ezrtsby0 {{ background-color: #262626; }}
                h1, h2, h3, h4, h5, h6 {{ color: #f0f2f6; }}
                .kpi-card {{ background-color: #262626; box-shadow: 0 4px 6px rgba(255, 255, 255, 0.1); }}
                .kpi-card h3 {{ color: #bbbbbb; }}
                .kpi-card .value {{ color: #F7882F; }}
                .stButton button {{ color: #f0f2f6; background-color: #F7882F; border: 1px solid #F7882F; }}
                .st-emotion-cache-12fmj2r.e1ewe7hr3 {{ color: #f0f2f6; background-color: #F7882F; border: 1px solid #F7882F; }}
                .st-emotion-cache-13k623y.e1ewe7hr2 {{ border-color: #383838; }}
            </style>
            """, unsafe_allow_html=True
        )

    st.subheader("Filters")

    # Dynamic filter for date range
    start_date = pd.to_datetime(df['Order Date']).min().date()
    end_date = pd.to_datetime(df['Order Date']).max().date()
    date_range = st.date_input(
        "Order Date Range",
        value=(start_date, end_date),
        min_value=start_date,
        max_value=end_date
    )

    # Initialize the filtered dataframe
    if len(date_range) == 2:
        df_filtered = df[(df['Order Date'].dt.date >= date_range[0]) & (df['Order Date'].dt.date <= date_range[1])]
    else:
        df_filtered = df.copy()

    # Multi-select filters for Region, Category, Sub-Category, and Segment
    selected_region = st.multiselect(
        "Region",
        options=df_filtered['Region'].unique(),
        default=df_filtered['Region'].unique()
    )
    df_filtered = df_filtered[df_filtered['Region'].isin(selected_region)]

    selected_category = st.multiselect(
        "Category",
        options=df_filtered['Category'].unique(),
        default=df_filtered['Category'].unique()
    )
    df_filtered = df_filtered[df_filtered['Category'].isin(selected_category)]
    
    selected_sub_category = st.multiselect(
        "Sub-Category",
        options=df_filtered['Sub-Category'].unique(),
        default=df_filtered['Sub-Category'].unique()
    )
    df_filtered = df_filtered[df_filtered['Sub-Category'].isin(selected_sub_category)]
    
    selected_segment = st.multiselect(
        "Customer Segment",
        options=df_filtered['Segment'].unique(),
        default=df_filtered['Segment'].unique()
    )
    df_filtered = df_filtered[df_filtered['Segment'].isin(selected_segment)]
    
    # Section for data export
    st.markdown("---")
    st.subheader("Export Data")

    # Export functions
    def to_excel(df):
        """Converts the dataframe to an in-memory Excel file."""
        output = BytesIO()
        # Corrected the engine name from 'openyxl' to 'openpyxl'
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        processed_data = output.getvalue()
        return processed_data
    
    def to_summary(df_filtered):
        """Creates a text summary of the data."""
        summary = (
            f"Sales Summary:\n"
            f"Total Sales: ${df_filtered['Sales'].sum():,.2f}\n"
            f"Total Profit: ${df_filtered['Profit'].sum():,.2f}\n"
            f"Number of Orders: {df_filtered['Order ID'].nunique():,}\n"
        )
        return summary

    if not df_filtered.empty:
        # Prepare data for download
        csv_data = df_filtered.to_csv(index=False).encode('utf-8')
        excel_data = to_excel(df_filtered)
        summary_data = to_summary(df_filtered)
        
        st.download_button(
            label="Export Filtered Data as CSV",
            data=csv_data,
            file_name='filtered_superstore_data.csv',
            mime='text/csv'
        )
        st.download_button(
            label="Export Filtered Data as Excel",
            data=excel_data,
            file_name='filtered_superstore_data.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        st.download_button(
            label="Export Summary as Text",
            data=summary_data,
            file_name='superstore_summary.txt',
            mime='text/plain'
        )

# --- Main dashboard content ---
if df_filtered.empty:
    st.error("No data available for the selected filters. Please adjust your filters.")
else:
    st.title("Superstore Sales Dashboard")
    st.markdown("A dynamic and interactive dashboard to analyze sales performance.")
    
    # --- KPI Cards ---
    st.markdown("---")
    st.subheader("Key Performance Indicators (KPIs)")
    col1, col2, col3, col4 = st.columns(4)
    
    total_sales = df_filtered['Sales'].sum()
    with col1:
        st.markdown(f'<div class="kpi-card"><h3>💰 Total Sales</h3><div class="value">${total_sales:,.2f}</div></div>', unsafe_allow_html=True)
    
    total_profit = df_filtered['Profit'].sum()
    with col2:
        st.markdown(f'<div class="kpi-card"><h3>📈 Total Profit</h3><div class="value">${total_profit:,.2f}</div></div>', unsafe_allow_html=True)
    
    total_orders = df_filtered['Order ID'].nunique()
    with col3:
        st.markdown(f'<div class="kpi-card"><h3>📦 Total Orders</h3><div class="value">{total_orders:,}</div></div>', unsafe_allow_html=True)
        
    top_product_data = df_filtered.groupby('Product Name')['Quantity'].sum().idxmax()
    with col4:
        st.markdown(f'<div class="kpi-card"><h3>🏆 Top Product</h3><div class="value">{top_product_data}</div></div>', unsafe_allow_html=True)
        
    st.markdown("---")
    
    # --- Visualizations ---
    # Sales and profit evolution over time (line chart)
    st.subheader("Sales and Profit Over Time")
    time_series_df = df_filtered.groupby('Month-Year')[['Sales', 'Profit']].sum().reset_index()
    time_series_df['Month-Year'] = pd.to_datetime(time_series_df['Month-Year'])
    time_series_df = time_series_df.sort_values('Month-Year')
    
    fig_time = go.Figure()
    fig_time.add_trace(go.Scatter(x=time_series_df['Month-Year'], y=time_series_df['Sales'], mode='lines', name='Sales', line=dict(color='#26547C')))
    fig_time.add_trace(go.Scatter(x=time_series_df['Month-Year'], y=time_series_df['Profit'], mode='lines', name='Profit', line=dict(color='#F7882F')))
    fig_time.update_layout(
        title_text="Monthly Sales and Profit Trends",
        xaxis_title="Date",
        yaxis_title="Amount ($)",
        template='plotly_white',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode="x unified",
        xaxis=dict(gridcolor='#e0e0e0'),
        yaxis=dict(gridcolor='#e0e0e0')
    )
    if dark_mode:
        fig_time.update_layout(template='plotly_dark')
    st.plotly_chart(fig_time, use_container_width=True)
    
    st.markdown("---")
    
    col_viz1, col_viz2 = st.columns(2)
    
    # Sales and profit by region (bar chart)
    with col_viz1:
        st.subheader("Sales & Profit by Region")
        region_df = df_filtered.groupby('Region')[['Sales', 'Profit']].sum().reset_index()
        fig_region = go.Figure(data=[
            go.Bar(name='Sales', x=region_df['Region'], y=region_df['Sales'], marker_color='#26547C'),
            go.Bar(name='Profit', x=region_df['Region'], y=region_df['Profit'], marker_color='#F7882F')
        ])
        fig_region.update_layout(
            barmode='group',
            title_text="Sales and Profit by Region",
            template='plotly_white',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(title=None),
            yaxis=dict(title='Amount ($)', gridcolor='#e0e0e0')
        )
        if dark_mode:
            fig_region.update_layout(template='plotly_dark')
        st.plotly_chart(fig_region, use_container_width=True)

    # Sales distribution by category (donut chart)
    with col_viz2:
        st.subheader("Sales Distribution by Category")
        category_df = df_filtered.groupby('Category')['Sales'].sum().reset_index()
        fig_category = px.pie(
            category_df,
            values='Sales',
            names='Category',
            hole=0.4,
            title='Sales by Product Category',
            color_discrete_sequence=px.colors.sequential.Agsunset,
            hover_data={'Sales': ':.2f'}
        )
        fig_category.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#000000', width=1)))
        fig_category.update_layout(
            template='plotly_white',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            uniformtext_minsize=12, uniformtext_mode='hide'
        )
        if dark_mode:
            fig_category.update_layout(template='plotly_dark')
        st.plotly_chart(fig_category, use_container_width=True)
    
    st.markdown("---")

    col_geo, col_heat = st.columns(2)
    
    # Interactive map of sales by state (choropleth map)
    with col_geo:
        st.subheader("Geographical Sales Performance")
        geo_df = df_filtered.groupby('State')['Sales'].sum().reset_index()
        
        # Create a dictionary to map full state names to two-letter abbreviations
        us_state_abbrev = {
            'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR',
            'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
            'District of Columbia': 'DC', 'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI',
            'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS',
            'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
            'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
            'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
            'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
            'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK',
            'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
            'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT',
            'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV',
            'Wisconsin': 'WI', 'Wyoming': 'WY'
        }
        
        # Map the full state names in the DataFrame to their abbreviations
        geo_df['State'] = geo_df['State'].map(us_state_abbrev)
        
        fig_map = go.Figure(data=go.Choropleth(
            # Use the newly created state abbreviations for locations
            locations=geo_df['State'],
            locationmode='USA-states',
            z=geo_df['Sales'],
            colorscale='bluyl',
            marker_line_color='white',
            marker_line_width=0.5,
            colorbar_title='Total Sales ($)',
            hovertemplate="State: %{location}<br>Sales: %{z:,.2f}<extra></extra>"
        ))
        
        fig_map.update_layout(
            title_text='Total Sales by State',
            geo=dict(
                scope='usa',
                projection=go.layout.geo.Projection(type='albers usa'),
                showlakes=True,
                lakecolor='rgb(255, 255, 255)',
                bgcolor='rgba(0,0,0,0)'
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        fig_map.update_geos(showsubunits=True, subunitcolor="lightgray")
        if dark_mode:
            fig_map.update_layout(template='plotly_dark', geo_bgcolor='rgba(0,0,0,0)')
        
        st.plotly_chart(fig_map, use_container_width=True)
        
    # Heatmap of sales by category and region
    with col_heat:
        st.subheader("Sales Heatmap by Category and Region")
        heatmap_df = df_filtered.groupby(['Region', 'Category'])['Sales'].sum().reset_index()
        
        # Pivot the table for the correct heatmap format
        pivot_table = heatmap_df.pivot_table(index='Region', columns='Category', values='Sales', aggfunc='sum').fillna(0)

        fig_heatmap = go.Figure(data=go.Heatmap(
            z=pivot_table.values,
            x=pivot_table.columns,
            y=pivot_table.index,
            colorscale='YlGnBu',
            colorbar=dict(title='Total Sales ($)'),
            hovertemplate="Region: %{y}<br>Category: %{x}<br>Sales: %{z:,.2f}<extra></extra>"
        ))
        
        fig_heatmap.update_layout(
            title='Sales by Category and Region',
            xaxis_title='Product Category',
            yaxis_title='Region',
            template='plotly_white',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        if dark_mode:
            fig_heatmap.update_layout(template='plotly_dark')

        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    st.markdown("---")
    
    # --- Filtered raw data table ---
    st.subheader("Filtered Raw Data")
    st.dataframe(df_filtered, use_container_width=True)
