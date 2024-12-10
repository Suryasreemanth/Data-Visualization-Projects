
"""### Importing Libaries:"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash
from dash import Dash, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
from networkx.algorithms import community
from dash.dependencies import Input, Output, State

"""### Reading the Data."""

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

# Data Visualizations

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

# Adding annotation for the maximum average purchase amount
max_point = df_grouped.loc[df_grouped['price'].idxmax()]  # Get the row with the max price
fig1.add_annotation(
    x=max_point['age'],
    y=max_point['price'],
    text=f"Max {max_point['category']}: ${max_point['price']:.2f}",
    showarrow=True,
    arrowhead=2,
    ax=0,
    ay=-40,
    font=dict(size=12, color="black")
)

# Updating layout for better clarity
fig1.update_layout(xaxis_title='Customer Age',
                  yaxis_title='Average Purchase Amount',
                  legend_title='Product Category')

fig1.show()

"""**Visualizing total sales per payment method**"""

categorical_variable = 'category'
continuous_variable = 'price'

# Calculate total value for each category
total_value_per_category = df.groupby(categorical_variable)[continuous_variable].sum().reset_index()

# Create the figure
fig2 = px.bar(total_value_per_category, x=categorical_variable, y=continuous_variable)

# Add annotations
fig2.add_annotation(
    x=total_value_per_category[categorical_variable].iloc[total_value_per_category[continuous_variable].idxmax()],  # Corresponding category
    y=total_value_per_category[continuous_variable].max(),  # Maximum total value
    text="Highest Total Value",
    showarrow=True,
    arrowhead=2,
    ax=0,
    ay=-40,
    font=dict(size=12, color="black")
)

fig2.add_annotation(
    x=total_value_per_category[categorical_variable].iloc[total_value_per_category[continuous_variable].idxmin()],  # Corresponding category
    y=total_value_per_category[continuous_variable].min(),  # Minimum total value
    text="Lowest Total Value",
    showarrow=True,
    arrowhead=2,
    ax=0,
    ay=40,
    font=dict(size=12, color="black")
)

# Show the plot
fig2.show()

# Calculate total sales per payment method
df['total_sales'] = df['quantity'] * df['price']
total_sales = df.groupby('payment_method')['total_sales'].sum().reset_index()
fig3 = go.Figure()

# Add bar trace
fig3.add_trace(go.Bar(
    x=total_sales['payment_method'],
    y=total_sales['total_sales'],
    marker_color='lightblue'
))

# Add horizontal line for average sales
average_sales = total_sales['total_sales'].mean()
fig3.add_shape(type='line',
               x0=-0.5,
               x1=len(total_sales) - 0.5,
               y0=average_sales,
               y1=average_sales,
               line=dict(color='red', dash='dash'))

# Add annotation for the average sales line
fig3.add_annotation(
    x=len(total_sales) - 0.5,
    y=average_sales,
    text='Average Sales',
    showarrow=True,
    arrowhead=2,
    ax=-40,
    ay=-30,
    font=dict(color='red', size=12)
)

# Add annotation to highlight "Cash"
fig3.add_annotation(
    x=0,
    y=total_sales['total_sales'].max(),
    text="Cash has the highest total sales",
    showarrow=True,
    arrowhead=2,
    ax=50,
    ay=-50,
    font=dict(color='green', size=12)
)

# Update layout
fig3.update_layout(
    title='Total Sales by Payment Method',
    xaxis_title='Payment Method',
    yaxis_title='Total Sales',
    yaxis=dict(range=[0, total_sales['total_sales'].max() + 10]),
    height=480,
    title_y=1,
    template='plotly_white'
)

"""**Visualizing Spending Amounts and Their Differences from Median by Payment Method**"""

df['median_price'] = df.groupby('payment_method')['price'].transform('median')
df['difference'] = df['price'] - df['median_price']

fig4 = px.scatter(
    df,
    x='payment_method',
    y='price',
    color='difference',
    color_continuous_scale=px.colors.diverging.RdYlBu,  # Diverging color map
    title='Spending Amount with Difference from Median Spending',
    labels={'difference': 'Difference from Median'},
    color_continuous_midpoint=0  # Center point for the diverging color map
)

fig4.update_layout(
    template='plotly_white',
    xaxis_title='Payment Method',
    yaxis_title='Spending Amount'
)

fig4.show()

"""### Filtering the Data"""

# Register callbacks
def register_callbacks(app):
    @app.callback(
        Output('overview-plot', 'figure'),
        [Input('category-dropdown', 'value'),
         Input('shared-data', 'data')]
    )
    def update_overview(selected_category, data):
        df = pd.DataFrame(data)
        return update_overview_plot(selected_category, df)

    @app.callback(
        Output('bar-plot', 'figure'),
        [Input('overview-plot', 'selectedData'),
         Input('category-dropdown', 'value'),
         Input('shared-data', 'data')]
    )
    def update_bar(selectedData, selected_category, data):
        df = pd.DataFrame(data)
        if selectedData is not None:
            point = selectedData['points'][0]['customdata']
            selected_category = point
        return update_bar_plot(selected_category, df)

    @app.callback(
        Output('overview-plot', 'selectedData'),
        [Input('bar-plot', 'selectedData')]
    )
    def update_overview_selection(selectedData):
        return selectedData  # Sync selection between the plots

def update_plots(category, data):
    # Convert the data from the dcc.Store back into a DataFrame
    df = pd.DataFrame(data)
    return scatter_plot(category, df), bar_plot(category, df)

# Function to create Scatter plot
def scatter_plot(category, df):
    filtered_df = df[df['category'] == category]
    fig6 = px.scatter(
        filtered_df,
        x='age',
        y='price',
        color='category',
        title=f'Scatter Plot for {category}',
        labels={'age': 'Customer Age', 'price': 'Price'}
    )
    return fig6

# Function to create Bar plot
def bar_plot(category, df):
    filtered_df = df[df['category'] == category]
    popular_categories = filtered_df.groupby(['shopping_mall', 'category']).size().reset_index(name='count')
    fig7 = px.bar(
        popular_categories,
        x='shopping_mall',
        y='count',
        color='category',
        title=f'Bar Plot for {category}',
        labels={'count': 'Number of Transactions'}
    )
    return fig7

# Function to create the "overview" scatter plot
def update_overview_plot(selected_category, df):
    df['highlight'] = df['category'] == selected_category  # Creating a column to highlight the selected category
    fig6 = px.scatter(
        df,
        x='age',
        y='price',
        color='highlight',
        color_discrete_map={True: 'red', False: 'gray'},  # Highlighting selected category in red, rest in gray color.
        title=f'Overview Visualization for {selected_category}',
        labels={'age': 'Customer Age', 'price': 'Price'}
    )
    return fig6

# Function to create the second bar plot
def update_bar_plot(selected_category, df):
    filtered_df = df[df['category'] == selected_category]
    popular_categories = filtered_df.groupby(['shopping_mall', 'category']).size().reset_index(name='count')
    fig7 = px.bar(
        popular_categories,
        x='shopping_mall',
        y='count',
        color='category',
        title=f'Bar Plot for {selected_category}',
        labels={'count': 'Number of Transactions'}
    )
    return fig7

"""<br>

### b) Scratch Drawings

# Deploying the Web App on Render

https://data-visualization-projects-1.onrender.com
"""

# Initialize the app
app = Dash("Shopping Data Insights", external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server
# Define global layout with `dcc.Store`
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),  # Location component to track the URL
    dcc.Store(id='shared-data', data=df.to_dict('records')),  # Store component at the top level
    html.H1("Istanbul Shopping Data Insights", className="text-center"),

    # Navigation buttons
    html.Div([
        dbc.Button(
            html.I(className="fas fa-info-circle", style={"fontSize": "2rem"}),
            color="primary",
            href="/about",
            style={"margin": "20px", "borderRadius": "50%"},
            title="About the Dataset"
        ),
        html.P("About the Dataset", style={"textAlign": "center", "color": "blue"}),

        dbc.Button(
            html.I(className="fas fa-chart-bar", style={"fontSize": "2rem"}),
            color="secondary",
            href="/distributions",
            style={"margin": "20px", "borderRadius": "50%"},
            title="Data Distribution"
        ),
        html.P("Distribution", style={"textAlign": "center", "color": "gray"}),

        dbc.Button(
            html.I(className="fas fa-filter", style={"fontSize": "2rem"}),
            color="info",
            href="/filter",
            style={"margin": "20px", "borderRadius": "50%"},
            title="Filter"
        ),
        html.P("Product Category Trends", style={"textAlign": "center", "color": "teal"}),

        dbc.Button(
            html.I(className="fas fa-chart-line", style={"fontSize": "2rem"}),
            color="warning",
            href="/critical-insights",
            style={"margin": "20px", "borderRadius": "50%"},
            title="Critical Insights"
        ),
        html.P("Critical Insights", style={"textAlign": "center", "color": "orange"}),
    ], style={"display": "flex", "justifyContent": "center", "alignItems": "center", "flexWrap": "wrap"}),

    # Content area for dynamic pages
    html.Div(id='page-content', style={'padding': '20px'})
])

# Define callbacks for dynamic page content
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/about':
        return html.Div([
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
        ])
    elif pathname == '/distributions':
        return html.Div([
            html.H2("Data Visualizations"),
            dcc.Graph(id='spending-age-line-chart', figure=fig1),
            html.Div(children=[
            html.H3("Takeaway Message for line plot: "),
            html.P("The key takeaway from the line plot is that "
               "Technology has the highest average price"
               ", while Food & Beverage has the minimum average price of $14.43.")
    ], style={'padding': '10px', 'backgroundColor': '#f9f9f9'}),

            dcc.Graph(id='purchase-amount-box-chart', figure=fig2),
            html.Div(children=[
            html.H3("Takeaway Message for Histogram: "),
            html.P("The key takeaway from the histogram is that "
                  "Clothing has the highest total number of sales of $31 million, "
                  "whereas Souvenir has the least sales of $174k.")
        ], style={'padding': '10px', 'backgroundColor': '#f9f9f9'}),

            dcc.Graph(id='total-sales-payment-method', figure=fig3),
            html.Div(children=[
            html.H3("Takeaway Message for Bar Plot: "),
            html.P("The key takeaway from the bar chart is that "
               "Cash is the most popular payment method, resulting in the highest total sales, "
               "followed by Credit Card and then Debit Card. This trend suggests that customers prefer cash "
               "transactions, which could inform strategies to enhance cash payment facilities and promotions.")
    ], style={'padding': '10px', 'backgroundColor': '#f9f9f9'}),

            dcc.Graph(id='spending-amount-median', figure=fig4),
            html.Div(children=[
            html.H3("Takeaway Message for Scatter Plot: "),
            html.P("The key takeaway from the scatter plot is that all payments from Cash, Credit Card, and Debit Card have the same median price of $203.3. Most spending amounts are close to the median, although there are some outliers exceeding $5000.")
        ], style={'padding': '10px', 'backgroundColor': '#f9f9f9'}),

        ])

    elif pathname == '/filter':
      return html.Div([
          html.H1(children='Interactive Visualizations'),

          html.H3(children='Select a category to update the visualizations:', style={'color': 'blue'}),

          dcc.Dropdown(
              id='category-dropdown',
              options=[{'label': category, 'value': category} for category in df['category'].unique()],
              value=df['category'].unique()[0],  # Default value (first category)
              clearable=False
          ),

          # Graphs that will be dynamically updated
          html.Div([
              html.Div(dcc.Graph(id='overview-plot'), style={'width': '48%', 'display': 'inline-block'}),
              html.Div(dcc.Graph(id='bar-plot'), style={'width': '48%', 'display': 'inline-block'})
          ])
      ])

    elif pathname == '/critical-insights':
        return html.Div([
            # Page Title
            html.H2("Critical Insights", style={'textAlign': 'center', 'marginBottom': '20px'}),

            # Summary Cards for Key Insights
            html.Div([
                html.Div([
                    html.H4("Clothing Sales", style={'textAlign': 'center'}),
                    html.P("Top-selling category with $31M in revenue.", style={'textAlign': 'center'})
                ], style={
                    'backgroundColor': '#d9edf7',
                    'padding': '15px',
                    'borderRadius': '10px',
                    'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)',
                    'margin': '10px',
                    'width': '30%',
                    'textAlign': 'center'
                }),

                html.Div([
                    html.H4("Souvenir Sales", style={'textAlign': 'center'}),
                    html.P("Least popular category with $174K in revenue.", style={'textAlign': 'center'})
                ], style={
                    'backgroundColor': '#f2dede',
                    'padding': '15px',
                    'borderRadius': '10px',
                    'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)',
                    'margin': '10px',
                    'width': '30%',
                    'textAlign': 'center'
                }),

                html.Div([
                    html.H4("Mall of Istanbul", style={'textAlign': 'center'}),
                    html.P("Highest transactions among all malls.", style={'textAlign': 'center'})
                ], style={
                    'backgroundColor': '#dff0d8',
                    'padding': '15px',
                    'borderRadius': '10px',
                    'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)',
                    'margin': '10px',
                    'width': '30%',
                    'textAlign': 'center'
                })
            ], style={
                'display': 'flex',
                'justifyContent': 'space-around',
                'marginBottom': '30px'
            }),

            # Strategic Takeaways Section
            html.Div([
                html.H3("Strategic Takeaways", style={'textAlign': 'center', 'marginTop': '30px', 'marginBottom': '20px'}),
                dcc.Markdown(
                    """
                    - Focus marketing efforts on **Clothing**, the top-performing category.
                    - Enhance **cash payment facilities** to accommodate customer preferences.
                    - Investigate and develop strategies to improve performance in **Forum Istanbul**.
                    - Leverage promotional campaigns targeting **specific age groups**, given no clear trends in spending by age.
                    """,
                    style={
                        'color': 'black',
                        'backgroundColor': '#f8f9fa',
                        'padding': '15px',
                        'borderRadius': '10px',
                        'boxShadow': '0px 2px 4px rgba(0, 0, 0, 0.1)',
                        'lineHeight': '1.8'
                    }
                )
            ])
        ])

    else:
        # Default page (e.g., homepage)
        return html.Div([
            html.H2("Welcome to Istanbul Shopping Data Insights"),
            html.P("Use the navigation buttons above to explore the dataset and visualizations.")
        ])

register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True, jupyter_mode="inline", jupyter_height=1000)

"""# Recording

https://indiana-my.sharepoint.com/:v:/g/personal/syedidhi_iu_edu/EfSwf55Kx-JDhjtMe9VtLFUB_vWBrhQefW6K4jQGVPhtvA?e=gydNof
"""
