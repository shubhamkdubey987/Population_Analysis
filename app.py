import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 1. Page Configuration
st.set_page_config(page_title="Global Population Dashboard (2020)", layout="wide")

st.title("🌍 Global Population Analysis Dashboard")
st.markdown("An interactive web application built with Streamlit to analyze world demographics.")

# 2. Cached Data Loading & Cleaning Function
@st.cache_data
def load_and_clean_data():
    # File name remains exactly as requested
    path = ('population_by_country_2020.csv')
    df = pd.read_csv(path, encoding='latin-1')
    
    # Strip whitespace from columns globally
    df.columns = df.columns.str.strip()
    
    # Clean broken text encoding characters from headers
    df = df.rename(columns={
        'Density (P/KmÂ²)': 'Density (P/Km2)', 
        'Land Area (KmÂ²)': 'Land Area (Km2)'
    })
    
    # Handle missing numerical records
    df['Migrants (net)'] = df['Migrants (net)'].fillna(0)
    
    # Strip '%' and 'N.A.' strings, then cast to pure numeric formats
    cols_to_clean = ['Yearly Change', 'Urban Pop %', 'World Share', 'Fert. Rate', 'Med. Age']
    for col in cols_to_clean:
        df[col] = df[col].astype(str).str.replace('%', '', regex=False)
        df[col] = df[col].str.replace('N.A.', '0', regex=False).str.strip()
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
    return df

# Initialize dataframe
df = load_and_clean_data()

# 3. High-Level Metrics Banner
st.subheader("📊 Key Global Statistics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    max_pop_country = df.loc[df['Population (2020)'].idxmax(), 'Country (or dependency)']
    max_pop_value = df['Population (2020)'].max()
    st.metric(label=f"Most Populous ({max_pop_country})", value=f"{max_pop_value:,}")

with col2:
    total_world_pop = df['Population (2020)'].sum()
    st.metric(label="Total Logged Population", value=f"{total_world_pop:,}")

with col3:
    highest_density_country = df.loc[df['Density (P/Km2)'].idxmax(), 'Country (or dependency)']
    max_density = df['Density (P/Km2)'].max()
    st.metric(label=f"Highest Density ({highest_density_country})", value=f"{max_density:,} P/Km²")

with col4:
    avg_age = round(df[df['Med. Age'] > 0]['Med. Age'].mean(), 1)
    st.metric(label="Average Median Age", value=f"{avg_age} Years")

st.markdown("---")

# 4. Interactive Multiselect Component & Table
st.subheader("🔍 Compare Countries Side-by-Side")
all_countries = sorted(df['Country (or dependency)'].unique())

selected_countries = st.multiselect(
    "Select one or more countries to display:", 
    all_countries, 
    default=["India", "China", "United States"]
)

if selected_countries:
    filtered_df = df[df['Country (or dependency)'].isin(selected_countries)]
    
    # Display clean table data
    st.dataframe(
        filtered_df[['Country (or dependency)', 'Population (2020)', 'Yearly Change', 'Density (P/Km2)', 'Med. Age', 'Urban Pop %']],
        use_container_width=True
    )
    
    st.markdown("---")
    
    # 5. Visualizations Section
    st.subheader("📊 Dynamic Data Visualizations")
    
    # --- ROW 1: BAR CHARTS ---
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("#### 📈 Population Size Comparison")
        st.bar_chart(
            filtered_df,
            x='Country (or dependency)',
            y='Population (2020)',
            color="#4F8BF9"
        )
        
    with chart_col2:
        st.markdown("#### ⚡ Yearly Growth Rate (%)")
        st.bar_chart(
            filtered_df,
            x='Country (or dependency)',
            y='Yearly Change',
            color="#FF4B4B"
        )
        
    st.markdown("---")
    
    # --- ROW 2: PIE CHART & HISTOGRAM ---
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        st.markdown("#### 🍕 Population Share Breakdown")
        # Generate a clean Pie Chart of the selected countries' relative sizes
        fig_pie, ax_pie = plt.subplots(figsize=(6, 5))
        ax_pie.pie(
            filtered_df['Population (2020)'], 
            labels=filtered_df['Country (or dependency)'], 
            autopct='%1.1f%%', 
            startangle=140,
            colors=['#4F8BF9', '#FF4B4B', '#FFD166', '#06D6A0', '#118AB2', '#073B4C']
        )
        ax_pie.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        fig_pie.patch.set_alpha(0.0)  # Transparent background to match streamlit theme
        st.pyplot(fig_pie)
        
    with chart_col4:
        st.markdown("#### 📊 Global Median Age Distribution (All Countries)")
        # Generate a Histogram showing where the world fits on age distribution
        fig_hist, ax_hist = plt.subplots(figsize=(6, 5))
        # Filtering out '0' values which represent missing data
        valid_ages = df[df['Med. Age'] > 0]['Med. Age']
        ax_hist.hist(valid_ages, bins=15, color='#06D6A0', edgecolor='white', alpha=0.85)
        ax_hist.set_xlabel("Median Age")
        ax_hist.set_ylabel("Number of Countries")
        fig_hist.patch.set_alpha(0.0)  # Transparent background
        st.pyplot(fig_hist)
        
    st.markdown("---")
    
    # --- ROW 3: TREND SCATTER CHART ---
    st.markdown("#### 🎯 Median Age vs. Urbanization Levels")
    st.scatter_chart(
        filtered_df,
        x='Med. Age',
        y='Urban Pop %',
        color='Country (or dependency)',
        size='Population (2020)'
    )

else:
    st.warning("Please select at least one country out of the dropdown menu to inspect values.")