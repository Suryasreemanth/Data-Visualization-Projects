# -*- coding: utf-8 -*-
"""Visualization Project Demonstration.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1oUQTPrFVcMunqYdGQhsBNpe0TcySHivd

# Summary

### About the Dataset:

This dataset contains shopping transaction data from 10 shopping malls in Istanbul, collected between 2021 and 2023. It provides detailed information on customer behavior, including demographics, payment methods, product categories, quantities purchased, and the shopping mall location. Key attributes include invoice numbers, customer IDs, age, gender, product categories, price, payment method, transaction date, and shopping mall names. This dataset is a valuable resource for analyzing shopping trends, patterns, and customer preferences in Istanbul.

Link For the Documentation: https://www.kaggle.com/datasets/mehmettahiraslan/customer-shopping-dataset

Below is the data summary which provides a comprehensive overview of the dataset's structure, highlighting the presence of missing values, understanding these characteristics is essential for conducting thorough exploratory data analysis and addressing any data preprocessing requirements.
"""


### @title Importing Libaries:
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash
from dash import Dash, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc

### @title Reading the Data.

url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTX0MxQdh3gr8MGpEhBoBw_YpeflymBZi4uc8aXP9uwrQhU5rJAswqfgVRAbZEhvk0lLW5DbfxJL8ID/pub?gid=258299125&single=true&output=csv'
df = pd.read_csv(url)
df.head()

df.info()

"""* The dataset contains a total of 99,457 entries and 10 columns.

* All columns are complete, with no missing values. The columns contain a mix of data types: `float64`, `int64`, and `object`.

* `age`, `quantity`, and `price` columns contain numerical data.

* `invoice_no`, `customer_id`, `gender`, `category`, `payment_method`, `invoice_date`, and `shopping_mall` contain categorical or text data.

### Purpose for Visualization Exploration:

*  Visualizations will help identify how customer age and gender influence purchasing decisions, allowing for insights into target demographics for different product categories.

*  Exploring the relationship between payment methods (cash, credit card, debit card) and product categories can reveal preferences and help businesses optimize payment options for different types of products.

* Analyzing shopping patterns across different shopping malls and over time will provide insights into regional shopping preferences and seasonal trends, allowing businesses to tailor their marketing strategies.

### Limitations of Visualization :

* Visualizing multiple variables simultaneously, such as age, gender, payment method, and category, can create overcrowded charts that are difficult to interpret without careful aggregation or simplification.

* Handling a large number of transactions might lead to visualizations that become too dense, making it challenging to extract clear insights unless data is carefully filtered or aggregated into meaningful segments.

* Generating time-based visualizations (e.g., monthly or seasonal trends) requires appropriate handling of dates and might overlook patterns influenced by external factors (e.g., holidays or economic shifts), which could affect the accuracy of insights.

### Plan Moving Forward

1. **Data Exploration:**

* Quick Overview: Conduct initial checks on the dataset to confirm its structure and confirm that all attributes (e.g., age, gender, product category) are correctly formatted for analysis.

* Aggregation & Summarization: Aggregate data by various segments (e.g., by age group, mall, or payment method) to generate meaningful insights that can drive visualizations.

2. Design Visualizations:

* Customer Demographics: Develop bar charts or histograms to visualize the distribution of customers by age and gender. Consider adding breakdowns by shopping mall or payment method for more granular insights.
*Payment Methods & Product Categories: Use pie charts or bar charts to visualize the distribution of payment methods used for different product categories.
* Temporal Trends: Create line graphs or heatmaps to show trends over time, identifying periods of high or low sales.
* Mall-specific Analysis: Generate comparisons between different malls with visualizations like stacked bar charts or maps, showing regional shopping habits.

3. Web App Development:

* User Interface: Build an interface on Dash framework that allows users to filter data by specific parameters (e.g., shopping mall, time period, or demographic group).
* Interactive Features: Implement interactive elements like dropdowns, checkboxes, and hover tooltips to enhance user experience.

<br>

# Visualization Mock-up

### a) Plotly Visualizations

**Spending Amount vs. Customer Age Across Different Product Categories**
"""

# Grouping data by age and category and calculating the mean price
df_grouped = df.groupby(["age", "category"]).mean(numeric_only=True).reset_index()

# Creating a line plot to visualize spending amount versus customer age using symbols
fig1 = px.line(df_grouped, x='age', y='price', symbol='category', color='category',
              title='Spending Amount vs. Customer Age Across Different Product Categories',
              labels={'age': 'Customer Age', 'price': 'Average Purchase Amount', 'category': 'Product Category'},
              color_discrete_sequence=px.colors.qualitative.Pastel)

# Customizing the markers for better visualization
fig1.update_traces(marker=dict(size=10, line=dict(width=1.5, color='DarkSlateGrey')))

# Updating layout for better clarity
fig1.update_layout(xaxis_title='Customer Age',
                  yaxis_title='Average Purchase Amount',
                  legend_title='Product Category')

fig1.show()

"""**Box plot to show the distribution of purchase amounts by category**"""

fig2 = px.box(df_grouped, x='category', y='price',
              title='Purchase Amount Distribution by Category',
              labels={'category': 'Product Category', 'price': 'Purchase Amount'},
              color='category')
fig2.update_layout(xaxis_title='Product Category', yaxis_title='Purchase Amount')
fig2.show()

"""**Visualizing total sales per payment method**"""

df['total_sales'] = df['quantity'] * df['price']
total_sales = df.groupby('payment_method')['total_sales'].sum().reset_index()

# Create bar plot
fig_3 = go.Figure()

# Add bar trace
fig_3.add_trace(go.Bar(
    x=total_sales['payment_method'],
    y=total_sales['total_sales'],
    name='Total Sales',
    marker_color='lightblue'
))

# Add horizontal line for average sales
average_sales = total_sales['total_sales'].mean()
fig_3.add_shape(type='line',
               x0=-0.5,
               x1=len(total_sales) - 0.5,
               y0=average_sales,
               y1=average_sales,
               line=dict(color='red', dash='dash'))

# Add annotation for average line
fig_3.add_annotation(
    x=len(total_sales) - 0.5,
    y=average_sales,
    text='Average Sales',
    showarrow=True,
    arrowhead=2,
    ax=-30,
    ay=-30,
    font=dict(color='red')
)

# Highlighting a specific payment method (e.g., Cash) with a rectangle
fig_3.add_shape(type='rect',
               x0=-0.5,
               x1=0.5,
               y0=0,
               y1=total_sales['total_sales'].max(),
               line=dict(color='green', width=2),
               fillcolor='rgba(0, 255, 0, 0.1)')  # Corrected fillcolor

# Update layout
fig_3.update_layout(
    title='Total Sales by Payment Method',
    xaxis_title='Payment Method',
    yaxis_title='Total Sales',
    yaxis=dict(range=[0, total_sales['total_sales'].max() + 10]),
    template='plotly_white'
)

# Show the plot
fig_3.show()

"""**Visualizing Spending Amounts and Their Differences from Median by Payment Method**"""

df['median_price'] = df.groupby('payment_method')['price'].transform('median')
df['difference'] = df['price'] - df['median_price']

fig_4 = px.scatter(
    df,
    x='payment_method',
    y='price',
    color='difference',
    color_continuous_scale=px.colors.diverging.RdYlBu,  # Diverging color map
    title='Spending Amount with Difference from Median Spending',
    labels={'difference': 'Difference from Median'},
    color_continuous_midpoint=0  # Center point for the diverging color map
)

fig_4.update_layout(
    template='plotly_white',
    xaxis_title='Payment Method',
    yaxis_title='Spending Amount'
)

fig_4.show()

categorical_variable = 'category'
continuous_variable = 'price'

# Interesting question
question = f"How does the total {continuous_variable} of all products vary across different {categorical_variable}?"
print(question)

# Calculate total value for each category
total_value_per_category = df.groupby(categorical_variable)[continuous_variable].sum().reset_index()

# Create the horizontal histogram
fig_5 = px.histogram(
    total_value_per_category,
    y=categorical_variable,
    x=continuous_variable,
    orientation='h',
    title="Total Price Distribution by Category"
)

# Order the bars by total value
fig_5.update_layout(
    yaxis=dict(categoryorder='total descending'),
    title=dict(x=0.5),
    xaxis_title=continuous_variable.capitalize(),
    yaxis_title=categorical_variable.capitalize()
)

"""<br>

### b) Scratch Drawings
"""

app = Dash("Shopping Data Insights", external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
# Defining layout
app.layout = html.Div([

    html.H1("Istanbul Shopping Data Insights", className="text-center"),

    # Container for icons with background colors
    html.Div([

        dbc.Button(
            html.I(className="fas fa-info-circle", style={"fontSize": "2rem"}),
            color="primary",  # Blue color
            href="#",
            style={"margin": "20px", "borderRadius": "50%"},
            title="About the Dataset"
        ),
        html.P("About the Dataset", style={"textAlign": "center", "color": "blue"}),

        dbc.Button(
            html.I(className="fas fa-chart-bar", style={"fontSize": "2rem"}),
            color="secondary",  # Gray color
            href="#",
            style={"margin": "20px", "borderRadius": "50%"},
            title="Data Distribution"
        ),
        html.P("Distribution", style={"textAlign": "center", "color": "gray"}),

        # Relationships icon with green background
        dbc.Button(
            html.I(className="fas fa-link", style={"fontSize": "2rem"}),
            color="success",  # Green color
            href="#",
            style={"margin": "20px", "borderRadius": "50%"},
            title="Relationships"
        ),
        html.P("Relationships", style={"textAlign": "center", "color": "green"}),

        # Insights icon with yellow background
        dbc.Button(
            html.I(className="fas fa-lightbulb", style={"fontSize": "2rem"}),
            color="warning",  # Yellow color
            href="#",
            style={"margin": "20px", "borderRadius": "50%"},
            title="Insights"
        ),
        html.P("Insights", style={"textAlign": "center", "color": "yellow"}),
    ], style={"display": "flex", "justifyContent": "center", "alignItems": "center", "flexWrap": "wrap"}),

    # About the Dataset Section
    html.Div([
        html.H2("About the Dataset"),
        dcc.Markdown("""
        This dataset contains shopping transaction data from 10 shopping malls in Istanbul,
        collected between 2021 and 2023. It provides detailed information on customer behavior,
        including demographics, payment methods, product categories, quantities purchased, and the
        shopping mall location.

        Key attributes include:
        - Invoice numbers
        - Customer IDs
        - Age, Gender
        - Product categories
        - Price
        - Payment method
        - Transaction date
        - Shopping mall names

        This dataset is a valuable resource for analyzing shopping trends, patterns, and customer
        preferences in Istanbul.
        """, style={'color': 'black', 'backgroundColor': 'lightgray', 'padding': '20px'})
    ], style={'padding': '20px'}),  # Padding added for readability

    # Data Visualizations Section
    html.Div([
        html.H2("Data Visualizations"),
        dcc.Graph(id='spending-age-line-chart', figure=fig1),
        dcc.Graph(id='purchase-amount-box-chart', figure=fig2),
        dcc.Graph(id='total-sales-payment-method', figure=fig_3),
        dcc.Graph(id='spending-amount-median', figure=fig_4),

    ], style={'padding': '20px'})  # Padding added for readability
])

if __name__ == '__main__':
    # Run the app
    app.run_server(debug=True, jupyter_mode="inline", jupyter_height=1000)

"""**What I want to make it final WebApp**
---
I aim to build a multi-page dashboard using Dash, with four pages: About the Dataset, Data Distributions, Relationships between Columns (e.g., how one column correlates with another), and Insights. I encountered issues with the page router in Dash and was unable to complete the multi-page functionality. I will either attempt to finish it within the notebook or consider alternative approaches, such as using Streamlit or creating separate pages in a folder on desktop to run the app.

# Recording

https://indiana-my.sharepoint.com/:v:/g/personal/syedidhi_iu_edu/EfSwf55Kx-JDhjtMe9VtLFUB_vWBrhQefW6K4jQGVPhtvA?e=gydNof
"""
