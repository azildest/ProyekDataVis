import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker
from matplotlib.ticker import ScalarFormatter
import streamlit as st

def create_sum_rent_df(df):
    sum_rent_df = df.groupby("weathersit").cnt.sum().sort_values(ascending=False).reset_index()
    return sum_rent_df

def create_sum_casual_df(df):
    sum_casual_df = df.groupby("weathersit").casual_day.sum().sort_values(ascending=False).reset_index()
    return sum_casual_df

def create_sum_registered_df(df):
    sum_registered_df = df.groupby("weathersit").registered_day.sum().sort_values(ascending=False).reset_index()
    return sum_registered_df

def create_year_trend_df(df):
    year_trend_df = df.resample(rule='M', on='dteday').agg({
    "instant": "nunique",
    "cnt": "sum"
    })

    year_trend_df['year'] = year_trend_df.index.year
    year_trend_df['month'] = year_trend_df.index.month

    year_trend_df = year_trend_df.reset_index()

    year_trend_df.rename(columns={
        "instant": "days",
        "cnt": "total_rental"
    }, inplace=True)
    return year_trend_df

def create_sum_seasonal_rent_df(df):
    season_mapping = {1: 'Winter', 2: 'Spring', 3: 'Summer', 4: 'Fall'}

    df['season'] = df['season'].replace(season_mapping)

    unique_dates_df = df.drop_duplicates(subset='dteday')
    sum_seasonal_rent_df = unique_dates_df.groupby("season").cnt.sum().sort_values(ascending=False).reset_index()
    return sum_seasonal_rent_df


def create_weather_rent_df(df):
    weather_mapping = {1: 'Clear or Cloudy', 2: 'Mist', 3: 'Light Rain or Snow', 4: 'Heavy Rain or Snow'}

    df['weathersit'] = df['weathersit'].replace(weather_mapping)
    unique_dates_df = df.drop_duplicates(subset='dteday')

    weather_rent_df = unique_dates_df.groupby("weathersit").cnt.sum().sort_values(ascending=False).reset_index()
    return weather_rent_df


def create_registered_trend_df(df):
    df['year'] = pd.to_datetime(df['dteday']).dt.year
    df['month'] = pd.to_datetime(df['dteday']).dt.month_name()

    registered_trend = day_hour_df.groupby(['year', 'month'])['registered_day'].sum().reset_index()
    return registered_trend

day_hour_df = pd.read_csv("day_hour.csv")

datetime_columns = ["dteday"]
day_hour_df.sort_values(by="dteday", inplace=True)
day_hour_df.reset_index(inplace=True)
 
for column in datetime_columns:
    day_hour_df[column] = pd.to_datetime(day_hour_df[column])
    
min_date = day_hour_df["dteday"].min()
max_date = day_hour_df["dteday"].max()

with st.sidebar:    
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
main_df = day_hour_df[(day_hour_df["dteday"] >= str(start_date)) & 
                (day_hour_df["dteday"] <= str(end_date))]

#helper function
sum_rent = create_sum_rent_df(main_df)
sum_casual_df = create_sum_casual_df(main_df)
sum_registered_df = create_sum_registered_df(main_df)
year_trend_df = create_year_trend_df(main_df)
sum_seasonal_rent_df = create_sum_seasonal_rent_df(main_df)
weather_rent_df = create_weather_rent_df(main_df)
registered_trend_df = create_registered_trend_df(main_df)

#Dashboard
st.header('Bicycle Sharing Dashboard')
st.write('Dataset dapat diakses di: [Kaggle](https://www.kaggle.com/datasets/lakshmi25npathi/bike-sharing-dataset?resource=download&select=day.csv)')
 
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_rent = sum_rent['cnt'].sum()
    formatted_total_rent = "{:,.0f}".format(total_rent)

    st.metric("Total penyewaan", value=formatted_total_rent)
    
with col3:
    total_casual = sum_casual_df['casual_day'].sum()
    formatted_total_casual = "{:,.0f}".format(total_casual)
    
    st.metric("Pengguna kasual", value=formatted_total_casual)
    
with col4:
    total_registered = sum_registered_df['registered_day'].sum()
    formatted_total_registered = "{:,.0f}".format(total_registered)
    
    st.metric("Pengguna terdaftar", value=formatted_total_registered)

#jumlah penyewaan sepeda (line chart)
st.subheader("Jumlah Penyewaan Sepeda Berdasarkan Bulan dan Tahun")
fig, ax = plt.subplots(figsize=(10, 5))

ax.plot(
    year_trend_df["dteday"],
    year_trend_df["total_rental"],
    marker='o',
    linewidth=2,
    color="#72BCD4"
)

ax.get_yaxis().get_major_formatter().set_scientific(False)
ax.tick_params(axis='x', labelrotation=45)
ax.tick_params(axis='both', labelsize=10)

st.pyplot(fig)

#musim yang paling tinggi dan rendah
st.subheader('Performa Sewa Terbaik dan Terburuk Berdasarkan Musim')

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="cnt", y="season", data=sum_seasonal_rent_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Kinerja Sewa Musiman Terbaik", loc="center", fontsize=15)
ax[0].tick_params(axis ='y', labelsize=12)

sns.barplot(x="cnt", y="season", data=sum_seasonal_rent_df.sort_values(by="cnt", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Kinerja Sewa Musiman Terburuk", loc="center", fontsize=15)
ax[1].tick_params(axis='y', labelsize=12)

ax[0].get_xaxis().get_major_formatter().set_scientific(False)
ax[1].get_xaxis().get_major_formatter().set_scientific(False)

st.pyplot(fig)

#ini cuaca
st.subheader('Perbandingan Kondisi Cuaca Terhadap Jumlah Penyewaan')

fig, ax = plt.subplots(figsize=(12, 6))

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="weathersit", y="cnt", data=weather_rent_df.head(5), palette=colors)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis ='y', labelsize=12)

ax.get_yaxis().get_major_formatter().set_scientific(False)

st.pyplot(fig)

#registered users
day_hour_df['year'] = pd.to_datetime(day_hour_df['dteday']).dt.year
day_hour_df['month'] = pd.to_datetime(day_hour_df['dteday']).dt.month_name()

registered_trend = day_hour_df.groupby(['year', 'month'])['registered_day'].sum().reset_index()

st.subheader('Jumlah Pengguna Terdaftar Berdasarkan Bulan dan Tahun')

plt.figure(figsize=(12, 6))
bar_width = 0.35

bar_2011 = plt.bar(registered_trend[registered_trend['year'] == 2011]['month'], registered_trend[registered_trend['year'] == 2011]['registered_day'], width=bar_width, label='2011', color='#D3D3D3')
bar_2012 = plt.bar(registered_trend[registered_trend['year'] == 2012]['month'], registered_trend[registered_trend['year'] == 2012]['registered_day'], width=bar_width, label='2012', color='#72BCD4', align='edge')

plt.xlabel('Bulan')
plt.ylabel('Jumlah Pengguna Terdaftar')
plt.title('Jumlah Pengguna Terdaftar Berdasarkan Bulan dan Tahun')
plt.ticklabel_format(style='plain', axis='y')
plt.legend()

st.pyplot(plt)
st.caption('Copyright © Azzila 2024')