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
    return pd.read_csv('https://raw.githubusercontent.com/NoorRokhimHendroYono/Dicoding-Submission-Noor-Rokhim-Hendro-Yono/refs/heads/master/dashboard/Project_Data_Clean.csv')

def create_top_categories_bycity_df(df):
    return df.rename(columns={"product_category_name_english": "category_name"})

def specified_city(df, city):
    lowercase_city = city.lower()
    customer_city_df = df[df.customer_city == lowercase_city]
    title = f"Top 5 Product Categories in {city}"
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
    transaction_df = df.groupby(pd.to_datetime(df['order_approved_at']).dt.to_period('M')).agg({
        'order_id': 'nunique'
    }).rename(columns={'order_id': 'order_count'}).reset_index()
    transaction_df['order_approved_at'] = transaction_df['order_approved_at'].dt.to_timestamp()
    return transaction_df

def create_rfm_df(df):
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

# Prepare datasets
top_categories_bycity_df = create_top_categories_bycity_df(all_df)
transaction_df = create_transaction_df(all_df)
rfm_df = create_rfm_df(all_df)

# Top 5 Most Popular Category in Leading Cities
st.markdown("<h2 class='medium-font'>Top 5 Product Categories by City 🏙️</h2>", unsafe_allow_html=True)
cities = ['Sobral', 'Rio de Janeiro', 'Campos Dos Goytacazes', 'Bom Principio', 'Vassouras']
city_tabs = st.tabs(cities)

for tab, city in zip(city_tabs, cities):
    with tab:
        city_df, title = specified_city(top_categories_bycity_df, city)
        fig = show_figures(city_df, title)
        st.pyplot(fig)

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
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.set_facecolor('#1e2130')
    fig.patch.set_facecolor('#0e1117')
    plt.tight_layout()
    st.pyplot(fig)
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown("<h3 class='small-font'>RFM (Recency, Frequency, Monetary) Analysis</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    def plot_rfm(data, metric, ax, color):
        sns.barplot(y=metric, x='customer_unique_id', data=data, color=color, ax=ax)
        ax.set_title(f'Top 5 Customers - {metric}', fontsize=16, color='white')
        ax.tick_params(axis='both', labelsize=10, colors='white')
        ax.set_xlabel('Customer ID', fontsize=12, color='white')
        ax.set_ylabel(metric, fontsize=12, color='white')
        ax.set_ylim(bottom=0)
        ax.set_facecolor('#1e2130')
        for i, v in enumerate(data[metric]):
            ax.text(i, v, f'{v:,.0f}', ha='center', va='bottom', fontsize=10, color='white')
    
    for col, (metric, color) in zip([col1, col2, col3], 
                                    [('Recency', '#FF9800'), ('Frequency', '#2196F3'), ('Monetary', '#4CAF50')]):
        with col:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            fig, ax = plt.subplots(figsize=(8, 6))
            plot_rfm(rfm_df.sort_values(metric, ascending=False if metric != 'Recency' else True).head(5), metric, ax, color)
            fig.patch.set_facecolor('#0e1117')
            st.pyplot(fig)
            st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("📊 RFM Analysis Explanation"):
        st.markdown("""
        <div style='background-color: #1e2130; padding: 15px; border-radius: 5px;'>
        <p><strong style='color: #FF9800;'>Recency:</strong> Days since last purchase. Lower values indicate more recent activity.</p>
        <p><strong style='color: #2196F3;'>Frequency:</strong> Total number of purchases. Higher values represent more frequent buyers.</p>
        <p><strong style='color: #4CAF50;'>Monetary:</strong> Total purchase value. Higher values indicate more valuable customers.</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>Created by Noor Rokhim Hendro Yono | Bangkit 2024</p>", unsafe_allow_html=True)
