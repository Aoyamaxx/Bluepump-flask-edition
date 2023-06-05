import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from scipy.stats import ttest_ind, mannwhitneyu
import scipy.stats
import matplotlib.pyplot as plt
import seaborn as sns

# Initialize the DB connection
engine = create_engine('sqlite:///d:/Github Rep/Bluepump-flask-edition/static/data_analysis_tool/user_tracking_Qualtrics.db')

# Read data from the tables into pandas dataframes
df_click_a = pd.read_sql_table('donate_clickA', con=engine)
df_click_b = pd.read_sql_table('donate_clickB', con=engine)
df_popup_b = pd.read_sql_table('donate_popupB', con=engine)

# Convert the data to numeric
df_click_a['header_clicks'] = pd.to_numeric(df_click_a['header_clicks'])
df_click_a['index_clicks'] = pd.to_numeric(df_click_a['index_clicks'])
df_click_b['header_clicks'] = pd.to_numeric(df_click_b['header_clicks'])
df_click_b['index_clicks'] = pd.to_numeric(df_click_b['index_clicks'])

# Calculate total clicks per user
df_click_a['total_clicks'] = df_click_a['header_clicks'] + df_click_a['index_clicks']
df_click_b['total_clicks'] = df_click_b['header_clicks'] + df_click_b['index_clicks']

# First filter out the 'clicked_donate' events from the 'donate_popupB' table
df_popup_donate = df_popup_b[df_popup_b['action'] == 'clicked_donate']

# Groupby 'visitor_id' and sum 'total_clicks' for df_click_a and df_click_b
df_click_a_sum = df_click_a.groupby('visitor_id')['total_clicks'].sum().reset_index()
df_click_b_sum = df_click_b.groupby('visitor_id')['total_clicks'].sum().reset_index()

# Groupby 'visitor_id' and count 'action' for df_popup_donate
df_popup_donate_counts = df_popup_donate.groupby('visitor_id').size().reset_index()
df_popup_donate_counts.columns = ['visitor_id', 'donate_counts']

# Merge df_click_b_sum and df_popup_donate_counts
df_click_b_sum = pd.merge(df_click_b_sum, df_popup_donate_counts, on='visitor_id', how='outer').fillna(0)

# Add 'donate_counts' to 'total_clicks' for df_click_b_sum
df_click_b_sum['total_clicks'] += df_click_b_sum['donate_counts']

# Create new dataframes with all unique visitor IDs from the site_visit tables
df_visit_a = pd.read_sql_table('site_visitA', con=engine)
df_visit_b = pd.read_sql_table('site_visitB', con=engine)

# Get the unique visitor IDs
visitor_ids_a = df_visit_a['visitor_id'].unique()
visitor_ids_b = df_visit_b['visitor_id'].unique()

# Create new dataframes with these IDs and initialize the total_clicks column to zero
df_total_clicks_a = pd.DataFrame({'visitor_id': visitor_ids_a, 'total_clicks': np.zeros(len(visitor_ids_a))})
df_total_clicks_b = pd.DataFrame({'visitor_id': visitor_ids_b, 'total_clicks': np.zeros(len(visitor_ids_b))})

# Now, map the total_clicks from df_click_a_sum and df_click_b_sum to df_total_clicks_a and df_total_clicks_b
df_total_clicks_a.set_index('visitor_id', inplace=True)
df_total_clicks_a.loc[df_click_a_sum['visitor_id'], 'total_clicks'] = df_click_a_sum.set_index('visitor_id')['total_clicks']

df_total_clicks_b.set_index('visitor_id', inplace=True)
df_total_clicks_b.loc[df_click_b_sum['visitor_id'], 'total_clicks'] = df_click_b_sum.set_index('visitor_id')['total_clicks']

# Fill NaN values with 0
df_total_clicks_a.fillna(0, inplace=True)
df_total_clicks_b.fillna(0, inplace=True)

# Perform the t-test
t_stat, p_val_t = ttest_ind(df_total_clicks_a['total_clicks'], df_total_clicks_b['total_clicks'])
print(f"T-Test results:\nStatistic: {t_stat}\nP-value: {p_val_t}")

# Mann-Whitney U Test
u_stat, p_val_u = mannwhitneyu(df_total_clicks_a['total_clicks'], df_total_clicks_b['total_clicks'])
print("\nMann-Whitney U test results:")
print(f"U statistic: {u_stat}")
print(f"P-value: {p_val_u}")

# Check the results:
print('Total clicks for version A:', df_total_clicks_a['total_clicks'].sum())
print('Total clicks for version B:', df_total_clicks_b['total_clicks'].sum())

# Get the number of unique visitors for each table
unique_visitor_a = df_visit_a['visitor_id'].nunique()
unique_visitor_b = df_visit_b['visitor_id'].nunique()

print(f"Unique visitor in 'site_visitA': {unique_visitor_a}")
print(f"Unique visitor in 'site_visitB': {unique_visitor_b}")

print(len(df_total_clicks_a), len(df_total_clicks_b))

# Visualization of total clicks
plt.figure(figsize=(10, 5))
sns.kdeplot(df_total_clicks_a['total_clicks'], label='Version A', shade=True)
sns.kdeplot(df_total_clicks_b['total_clicks'], label='Version B', shade=True)
plt.legend(title='Version')
plt.title('Distribution of Total Donate Clicks')
plt.xlabel('Total Donate Clicks')

# Box plot
plt.figure(figsize=(10, 5))
sns.boxplot(data=[df_total_clicks_a['total_clicks'], df_total_clicks_b['total_clicks']], notch=True, flierprops = dict(markerfacecolor = '0.50', markersize = 2))
plt.xticks([0, 1], ['Version A', 'Version B'])
plt.title('Box Plot of Total Donate Clicks')
plt.ylabel('Total Donate Clicks')

# Bar plot
clicks_data = {'Version A': df_total_clicks_a['total_clicks'].sum(), 'Version B': df_total_clicks_b['total_clicks'].sum()}
plt.bar(clicks_data.keys(), clicks_data.values(), color=['blue', 'green'])
plt.title('Total Donate Clicks for Each Version')
plt.ylabel('Total Clicks')

# Histogram
plt.figure(figsize=(10, 5))
plt.hist(df_total_clicks_a['total_clicks'], bins=30, alpha=0.5, label='Version A')
plt.hist(df_total_clicks_b['total_clicks'], bins=30, alpha=0.5, label='Version B')
plt.legend(loc='upper right')
plt.title('Histogram of Total Donate Clicks')
plt.xlabel('Total Donate Clicks')
plt.ylabel('Frequency')

plt.show()

# Calculate means
means = [df_total_clicks_a['total_clicks'].mean(), df_total_clicks_b['total_clicks'].mean()]

# Calculate standard errors
se = [scipy.stats.sem(df_total_clicks_a['total_clicks']), scipy.stats.sem(df_total_clicks_b['total_clicks'])]

# Create a bar plot with error bars
plt.bar([0, 1], means, yerr=se, align='center', alpha=0.5, ecolor='black', capsize=10)
plt.xticks([0, 1], ['Version A', 'Version B'])
plt.ylabel('Mean Total Clicks')
plt.title('Confidence Intervals of Mean Total Clicks')
plt.show()