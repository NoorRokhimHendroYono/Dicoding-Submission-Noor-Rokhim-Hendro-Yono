import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

# Set page configuration
st.set_page_config(layout="wide", page_title="Brazilian E-Commerce Insights", page_icon="🇧🇷")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
    }
    
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .big-font {
        font-size: 32px !important;
        font-weight: 700;
        color: #4CAF50;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .medium-font {
        font-size: 24px !important;
        color: #2196F3;
        font-weight: 500;
    }
    .small-font {
        font-size: 18px !important;
        color: #FFC107;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e2130;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 20px;
        color: white;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50;
        transform: translateY(-5px);
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4);
    }
    .stExpander {
        background-color: #1e2130;
        border: 1px solid #4CAF50;
        border-radius: 5px;
        padding: 10px;
    }
    .chart-container {
        background-color: #1e2130;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        return pd.read_csv('https://raw.githubusercontent.com/NoorRokhimHendroYono/Dicoding-Submission-Noor-Rokhim-Hendro-Yono/refs/heads/master/dashboard/Project_Data_Clean.csv')
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame to avoid further errors

def create_top_categories_bycity_df(df):
    if 'product_category_name_english' not in df.columns:
        st.error("Kolom 'product_category_name_english' tidak ditemukan dalam dataset.")
        return pd.DataFrame()
    return df.rename(columns={"product_category_name_english": "category_name"})

def specified_city(df, city):
    if 'customer_city' not in df.columns:
        st.error("Kolom 'customer_city' tidak ditemukan.")
        return pd.DataFrame(), ""
    
    lowercase_city = city.lower()
    customer_city_df = df[df.customer_city.str.lower() == lowercase_city]
    
    if customer_city_df.empty:
        st.warning(f"Tidak ada data untuk kota {city}.")
        return pd.DataFrame(), ""
    
    title = f"Top 5 Kategori Produk di {city}"
    return customer_city_df, title

def show_figures(df, title):
    city_agg_df = df.groupby(by="category_name").agg({
        'order_id': 'nunique'
    }).reset_index().sort_values(by='order_id', ascending=False).head(5)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = sns.color_palette("viridis", 5)
    
    bars = sns.barplot(y="category_name", x="order_id", data=city_agg_df, palette=colors, ax=ax)
    ax.set_title(title, loc="center", fontsize=20, pad=20, color='white')
    ax.set_ylabel("Category", fontsize=14, color='white')
    ax.set_xlabel("Number of Transactions", fontsize=14, color='white')
    ax.tick_params(axis='both', labelsize=12, colors='white')
    
    for i, v in enumerate(city_agg_df['order_id']):
        ax.text(v + 3, i, f"{v:,}", va='center', fontsize=12, color='white')
    
    ax.set_facecolor('#1e2130')
    fig.patch.set_facecolor('#0e1117')
    plt.tight_layout()
    return fig

def create_transaction_df(df):
    if 'order_approved_at' not in df.columns or 'order_id' not in df.columns:
        st.error("Kolom 'order_approved_at' atau 'order_id' tidak ditemukan.")
        return pd.DataFrame()
    
    transaction_df = df.groupby(pd.to_datetime(df['order_approved_at']).dt.to_period('M')).agg({
        'order_id': 'nunique'
    }).rename(columns={'order_id': 'order_count'}).reset_index()
    transaction_df['order_approved_at'] = transaction_df['order_approved_at'].dt.to_timestamp()
    return transaction_df

def create_rfm_df(df):
    if 'order_approved_at' not in df.columns or 'customer_id' not in df.columns:
        st.error("Kolom 'order_approved_at' atau 'customer_id' tidak ditemukan.")
        return pd.DataFrame()
    
    df['order_approved_at'] = pd.to_datetime(df['order_approved_at'])
    recent_date = df['order_approved_at'].max()
    rfm_df = df.groupby("customer_id").agg({
        "order_approved_at": lambda x: (recent_date - x.max()).days,
        'order_id': 'count',
        'total_order_value': 'sum'
    }).reset_index()
    rfm_df.columns = ['customer_id', 'Recency', 'Frequency', 'Monetary']
    rfm_df['customer_unique_id'] = pd.factorize(rfm_df['customer_id'])[0] + 1
    return rfm_df

# Load data
all_df = load_data()

# Main app
st.markdown("<h1 class='big-font' style='text-align: center;'>Project Data Analyst</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #2196F3;'>Brazilian E-Commerce Public Dataset</h2>", unsafe_allow_html=True)

# Check the columns in the loaded DataFrame
st.write(all_df.columns)

# Verify if the required column 'order_approved_at' exists
if 'order_approved_at' not in all_df.columns:
    st.error("The 'order_approved_at' column is missing from the dataset.")
else:
    # Prepare datasets
    transaction_df = create_transaction_df(all_df)
    top_categories_bycity_df = create_top_categories_bycity_df(all_df)
    rfm_df = create_rfm_df(all_df)

# Top 5 Most Popular Category in Leading Cities
st.markdown("<h2 class='medium-font'>Top 5 Product Categories by City 🏙️</h2>", unsafe_allow_html=True)
cities = ['Franca', 'Sao Bernardo Do Campo', 'Guarulhos', 'Brasilia', 'Montes Claros']
city_tabs = st.tabs(cities)

for tab, city in zip(city_tabs, cities):
    with tab:
        city_df, title = specified_city(top_categories_bycity_df, city)
        if not city_df.empty:
            fig = show_figures(city_df, title)
            st.pyplot(fig)
        else:
            st.write(f"Tidak ada data untuk {city}.")

# Order Frequencies and RFM Analysis
st.markdown("<h2 class='medium-font'>Order Trends and Customer Analysis 📊</h2>", unsafe_allow_html=True)
tab1, tab2 = st.tabs(['📈 Order Trends', '👥 Customer Segmentation'])

with tab1:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(20, 10))
    ax.plot(transaction_df['order_approved_at'], transaction_df['order_count'], marker='o', linewidth=2, color="#4CAF50")
    ax.set_title("Monthly Order Trends", loc='center', fontsize=24, color='white')
    ax.set_xlabel("Date", fontsize=16, color='white')
    ax.set_ylabel("Number of Orders", fontsize=16, color='white')
    ax.tick_params(axis='x', labelrotation=45, labelsize=12, colors='white')
    ax.tick_params(axis='y', labelsize=12, colors='white')
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.set_facecolor("#1e2130")
    fig.patch.set_facecolor('#0e1117')
    st.pyplot(fig)
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(20, 10))
    ax.scatter(rfm_df['Recency'], rfm_df['Frequency'], s=rfm_df['Monetary']/100, alpha=0.7, color='#FFC107')
    ax.set_title("Customer Segmentation by RFM", loc='center', fontsize=24, color='white')
    ax.set_xlabel("Recency (Days Since Last Purchase)", fontsize=16, color='white')
    ax.set_ylabel("Frequency (Number of Orders)", fontsize=16, color='white')
    ax.tick_params(axis='x', labelsize=12, colors='white')
    ax.tick_params(axis='y', labelsize=12, colors='white')
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.set_facecolor("#1e2130")
    fig.patch.set_facecolor('#0e1117')
    st.pyplot(fig)
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>Created by Noor Rokhim Hendro Yono | Bangkit 2024</p>", unsafe_allow_html=True)
