import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import pymysql


def get_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='stock_analysis_db',
        port=3306
    )


st.set_page_config(page_title="Stock Dashboard", layout="wide")
st.title("Stock Analysis Dashboard")


option = st.sidebar.selectbox("Select Visualization", [
    "Top 10 Most Volatile Stocks",
    "Top 5 Cumulative Returns",
    "Sector-wise Performance",
    "Monthly Top Gainers and Losers",
    "Stock Price Correlation Heatmap"
])


if option == "Top 10 Most Volatile Stocks":
    conn = get_connection()
    df = pd.read_sql("""SELECT Ticker, Company, AVG(Volatility) AS Avg_Volatility FROM Volatility_Analysis GROUP BY Ticker, Company ORDER BY Avg_Volatility DESC LIMIT 10""", conn)
    conn.close()
    fig = px.bar(df, x='Company', y='Avg_Volatility', title="Top 10 Most Volatile Stocks",labels={'Avg_Volatility': 'Volatility'})
    st.plotly_chart(fig, use_container_width=True)


elif option == "Top 5 Cumulative Returns":
    conn = get_connection()
    top_5_query = """
   
    SELECT Ticker, Company, AVG(Cumulative_Return) AS avg_return
    FROM Cumulative_Return
    GROUP BY Ticker, Company
    ORDER BY avg_return DESC
    LIMIT 5

    """
    top_5_df = pd.read_sql(top_5_query, conn)
    top_5_tickers = tuple(top_5_df['Ticker'].tolist())

    history_query = f"""
        SELECT date, Ticker, Company, Cumulative_Return
        FROM Cumulative_Return
        WHERE Ticker IN {top_5_tickers}
    """
    df = pd.read_sql(history_query, conn)
    conn.close()

    df['date'] = pd.to_datetime(df['date'])
    df['Normalized_Return'] = df.groupby('Ticker')['Cumulative_Return'].transform(
        lambda x: (x - x.min()) / (x.max() - x.min())
    )
    fig = px.line(df, x='date', y='Normalized_Return', color='Company', title=" Cumulative Return Over Time" ,labels={'Normalized_Return': 'Cumulative Return'})
    st.plotly_chart(fig, use_container_width=True)


elif option == "Sector-wise Performance":
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM Sector_wise_Performance", conn)
    conn.close()
    fig = px.bar(df, x='Sector', y='Yearly_Return', title="Sector-wise Average Yearly Return")
    st.plotly_chart(fig, use_container_width=True)


elif option == "Monthly Top Gainers and Losers":
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM Month_wise_data", conn)
    conn.close()
    months = df['month'].unique()
    selected_month = st.selectbox("Select Month", sorted(months))
    month_df = df[df['month'] == selected_month]
    gainers = month_df[month_df['Rank'] > 0].sort_values(by='Rank')
    losers = month_df[month_df['Rank'] < 0].sort_values(by='Rank')
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 5 Gainers")
        fig1 = px.bar(gainers, x='Company', y='Daily_Return', title="Top 5 Gainers")
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.subheader("Top 5 Losers")
        fig2 = px.bar(losers, x='Company', y='Daily_Return', title="Top 5 Losers")
        st.plotly_chart(fig2, use_container_width=True)


elif option == "Stock Price Correlation Heatmap":
    df = pd.read_csv(r"C:\\Users\\judej\\OneDrive\\Desktop\\Stock analaysis\\Main\\Required Df\\Correlation.csv", index_col=0)
    df = df.loc[:, ~df.columns.duplicated()].copy()
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(df, cmap='coolwarm', center=0, annot=False)
    st.pyplot(fig)
