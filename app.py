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
    # Update this path if your file location changes
    path = (r'C:/Users/Friend/OneDrive/Desktop/Ecommerce/Population_Analysis/population_by_country_2020.csv')
    df = pd.read_csv(path, encoding='latin-1')
    
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

# 4. Interactive Multiselect Component & Plotting
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
    st.dataframe(filtered_df[['Country (or dependency)', 'Population (2020)', 'Yearly Change', 'Density (P/Km2)', 'Med. Age', 'Urban Pop %']])
    
    # Dynamic Population Chart Visualization
    st.subheader("📈 Population Distribution Chart")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(filtered_df['Country (or dependency)'], filtered_df['Population (2020)'], color='#4F8BF9')
    ax.set_ylabel("Population Size")
    ax.set_xlabel("Country")
    plt.xticks(rotation=45)
    fig.tight_layout()
    
    st.pyplot(fig)
else:
    st.warning("Please select at least one country out of the dropdown menu to inspect values.")