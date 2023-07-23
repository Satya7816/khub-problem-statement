import pandas as pd
import plotly.graph_objects as go
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_data', methods=['POST'])
def process_data():
    if 'data_file' in request.files:
        data_file = request.files['data_file']
        if data_file.filename == '':
            return render_template('nofileprovided.html')

        # Check if the file is in CSV or Excel format
        if data_file.filename.lower().endswith('.csv'):
            # Read CSV data
            data = pd.read_csv(data_file)
        elif data_file.filename.lower().endswith(('.xls', '.xlsx')):
            # Read Excel data
            data = pd.read_excel(data_file)
        else:
            return render_template('invalidfile.html')

        # Get filter values from HTML form
        graduation_filter = request.form.get('graduation_filter', default='all')
        current_year_filter = request.form.get('current_year_filter', type=int, default=0)

        # Filtering the data based on the input values
        filtered_data = data.copy()

        if graduation_filter != 'all':
            filtered_data = filtered_data[filtered_data['graduation'] == graduation_filter]

        if current_year_filter:
            filtered_data = filtered_data[filtered_data['year'] == current_year_filter]

        # Generate visualizations and data tables
        bar_plot_div = generate_bar_chart(filtered_data)
        pie_plot_div = generate_pie_chart(filtered_data)
        graduation_table = generate_data_table(filtered_data)

        # Redirect to the output.html template with the generated visualizations and data tables
        return render_template('output.html', bar_plot_div=bar_plot_div, pie_plot_div=pie_plot_div,
                               graduation_table=graduation_table)

    return "Error: No file provided."

def generate_bar_chart(filtered_data):
    bar_fig = go.Figure()
    bar_fig.add_trace(go.Bar(x=filtered_data['name'], y=filtered_data['year'], name='Year'))

    bar_fig.update_layout(barmode='group', title='Current Year by Name', xaxis_title='Name', yaxis_title='Current Year')

    return bar_fig.to_html(full_html=False)

def generate_pie_chart(filtered_data):
    graduation_counts = filtered_data['graduation'].value_counts()
    pie_fig = go.Figure(go.Pie(labels=graduation_counts.index, values=graduation_counts.values, hole=0.3))
    pie_fig.update_layout(title='Graduation Distribution')

    return pie_fig.to_html(full_html=False)

def generate_data_table(filtered_data):
    data_table = filtered_data[['name', 'graduation', 'year']].to_html(index=False)
    return data_table

if __name__ == '__main__':
    app.run(debug=True)
