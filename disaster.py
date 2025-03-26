from gdacs.api import GDACSAPIReader
from gdacs.api import GDACSAPIError
from flask import Flask,json,render_template,request,jsonify,session,redirect,url_for
import plotly.graph_objects as go
import plotly.express as px
from collections import Counter
import mysql.connector
import webbrowser
import smtplib
from email.mime.text import MIMEText
from apscheduler.schedulers.background import BackgroundScheduler
from sign_up import sign_up_bp
from login import login_bp
from more_info import more_info_bp
import os


app = Flask(__name__,template_folder="templates")

data = {'latitude' : [],'longitude' : [],'country_names' : [],
            'disaster_type' : [],'is_current' : [],
            'disaster_names' : [],'exact_description' : [],
            'alert_level' : [],'alert_color' : [],
            'from_date' : [],'time' : [],'severity_text' : [],
            'icon' : [],'legend_icon_names' : [],'legend_icon_pics' : [],
            'event_type' : [],'event_id' : [],
            'user_disaster_distance' : {'data_index' : [],'distance' : []}
        }

app.config['data'] = data
app.register_blueprint(sign_up_bp)
app.register_blueprint(login_bp,data = data)
app.register_blueprint(more_info_bp)

def periodic_task():
    for attributes in data:
        if attributes != 'user_disaster_distance':
            data[attributes] = []
        else:
            data['user_disaster_distance']['data_index'] = []
            data['user_disaster_distance']['distance'] = []
        
    try:
        client = GDACSAPIReader()
        geojson_obj = client.latest_events()
    except GDACSAPIError as error:
        print(f"Error fetching GDACS data: {error}")
        return  # Just return instead of trying to render template
        
    disaster_count = {}
    
    disaster_alert_count = {'Earthquake' : {'green' : 0,'orange' : 0,'red' : 0},
                            'Flood' : {'green' : 0,'orange' : 0,'red' : 0},
                            'Forest' : {'green' : 0,'orange' : 0,'red' : 0},
                            'Tropical' : {'green' : 0,'orange' : 0,'red' : 0},
                            'Tsunami' : {'green' : 0,'orange' : 0,'red' : 0},
                            'Drought' : {'green' : 0,'orange' : 0,'red' : 0},
                            'Eruption' : {'green' : 0,'orange' : 0,'red' : 0}
                            }
    
    disaster_count_pie_chart = {}
    for feature in geojson_obj.features:
        geometry = feature['geometry']
        data['longitude'].append(geometry['coordinates'][0])
        data['latitude'].append(geometry['coordinates'][1])

        properties = feature['properties']
        disaster_name = properties['name']
        description = properties['description']
        description = description.split(' ')
        data['legend_icon_names'].append(description[0].split(' ')[0])

        data['exact_description'].append(properties['htmldescription'])
        data['icon'].append(properties['iconoverall'])
        data['event_type'].append(properties['eventtype'])
        data['event_id'].append(properties['eventid'])
        
        data['alert_level'].append(properties['alertlevel'])
        alert_level = properties['alertlevel']

        if 'Green' in alert_level:
            data['alert_color'].append('bg-success')
            disaster_alert_count[description[0]]['green'] += 1
        elif 'Orange' in alert_level:
            data['alert_color'].append('bg-warning')
            disaster_alert_count[description[0]]['orange'] += 1
        else:
            data['alert_color'].append('bg-danger')
            disaster_alert_count[description[0]]['red'] += 1
        
        data['is_current'].append(properties['iscurrent'])
        
        country = properties['country']
        if(len(country) == 0):
            country = "OffShore"
            disaster_name += ' OffShore'
            
        data['country_names'].append(country)
        data['disaster_names'].append(disaster_name)
        
        date_time = properties['fromdate'].split('T')
        data['from_date'].append(date_time[0])
        data['time'].append(date_time[1])

        severitydata = properties['severitydata']
        data['severity_text'].append(severitydata['severitytext'])
    
    disaster_count = Counter(data['legend_icon_names'])
    data['disaster_type'] = data['legend_icon_names']
    data['legend_icon_names'] = list(set(data['legend_icon_names']))
    
    # Fix the icon paths to use the correct alert level
    baselink = "https://www.gdacs.org/images/gdacs_icons/maps/"
    for i in range(len(data['legend_icon_names'])):
        disaster_type = data['legend_icon_names'][i]
        # Get the alert level for this disaster type
        alert_level = "Green"  # Default to Green if not found
        for j in range(len(data['disaster_type'])):
            if data['disaster_type'][j] == disaster_type:
                alert_level = data['alert_level'][j]
                break
                
        if disaster_type == 'Flood':
            data['legend_icon_pics'].append(baselink + alert_level + "/FL.png")
        elif disaster_type == 'Earthquake':
            data['legend_icon_pics'].append(baselink + alert_level + "/EQ.png")
        elif disaster_type == 'Forest':
            data['legend_icon_pics'].append(baselink + alert_level + "/WF.png")
            data['legend_icon_names'][i] += ' fires'
        elif disaster_type == 'Tropical':
            data['legend_icon_pics'].append(baselink + alert_level + "/TC.png")
            data['legend_icon_names'][i] += ' Cyclone'
        elif disaster_type == 'Tsunami':
            data['legend_icon_pics'].append(baselink + alert_level + "/TS.png")
        elif disaster_type == 'Drought':
            data['legend_icon_pics'].append(baselink + alert_level + "/DR.png")
        else:
            data['legend_icon_names'][i] = 'Volcano ' + disaster_type
            data['legend_icon_pics'].append(baselink + alert_level + "/VO.png")

    disaster_count_pie_chart['Earthquakes'] = disaster_count['Earthquake']
    disaster_count_pie_chart['Floods'] = disaster_count['Flood']
    disaster_count_pie_chart['Forest Fires'] = disaster_count['Forest']
    disaster_count_pie_chart['Tropical Cyclones'] = disaster_count['Tropical']
    disaster_count_pie_chart['Tsunamis'] = disaster_count['Tsunami']
    disaster_count_pie_chart['Droughts'] = disaster_count['Drought']
    disaster_count_pie_chart['Volcanic Eruptions'] = disaster_count['Eruption']

    # Plotting of pie chart
    pie_chart_colors = ['#8B4513', '#3366CC', '#8B0000', '#808080', '#00008B', '#D2B48C', '#FFD700']
    
    # Create pie chart data for JavaScript
    pie_data = {
        'labels': list(disaster_count_pie_chart.keys()),
        'values': list(disaster_count_pie_chart.values()),
        'colors': pie_chart_colors
    }
    
    # Creating different traces of graphs individually for red,orange and green alerts
    green_disasters,orange_disasters,red_disasters = [],[],[]

    for disaster_color in disaster_alert_count.values():
        green_disasters.append(disaster_color['green'])
        orange_disasters.append(disaster_color['orange'])
        red_disasters.append(disaster_color['red'])
   
    # Create bar graph data for JavaScript
    bar_data = {
        'categories': list(disaster_count_pie_chart.keys()),
        'green': green_disasters,
        'orange': orange_disasters,
        'red': red_disasters
    }
    
    try:
        # Use absolute paths for saving files
        templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
        
        # Generate enhanced pie chart HTML
        pie_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Global Disaster Distribution</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .chart-container {{
                    width: 90%;
                    max-width: 900px;
                    margin: 20px auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                }}
                h1 {{
                    text-align: center;
                    color: #333;
                    margin-bottom: 30px;
                }}
                .chart-description {{
                    color: #555;
                    margin-bottom: 20px;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="chart-container">
                <h1>Global Disaster Distribution</h1>
                <p class="chart-description">Current distribution of global disasters by type</p>
                <div id="pie-chart"></div>
            </div>
            
            <script>
                // Pie chart data
                const pieData = {{
                    labels: {pie_data['labels']},
                    values: {pie_data['values']},
                    colors: {pie_chart_colors}
                }};
                
                // Create the pie chart
                const pieTrace = {{
                    type: 'pie',
                    labels: pieData.labels,
                    values: pieData.values,
                    textinfo: 'label+percent',
                    insidetextorientation: 'radial',
                    textfont: {{
                        size: 14
                    }},
                    marker: {{
                        colors: pieData.colors
                    }},
                    hoverinfo: 'label+value+percent'
                }};
                
                const pieLayout = {{
                    showlegend: true,
                    legend: {{
                        orientation: 'v',
                        xanchor: 'center',
                        yanchor: 'top',
                        y: -0.1,
                        x: 0.5
                    }},
                    height: 500,
                    margin: {{
                        l: 50,
                        r: 50,
                        t: 30,
                        b: 30
                    }}
                }};
                
                Plotly.newPlot('pie-chart', [pieTrace], pieLayout, {{responsive: true}});
            </script>
        </body>
        </html>
        """
        
        # Generate enhanced bar graph HTML
        bar_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Disaster Alert Levels</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .chart-container {{
                    width: 90%;
                    max-width: 900px;
                    margin: 20px auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                }}
                h1 {{
                    text-align: center;
                    color: #333;
                    margin-bottom: 30px;
                }}
                .chart-description {{
                    color: #555;
                    margin-bottom: 20px;
                    text-align: center;
                }}
                .legend-item {{
                    display: inline-block;
                    margin-right: 20px;
                }}
                .legend-color {{
                    display: inline-block;
                    width: 20px;
                    height: 20px;
                    border-radius: 50%;
                    margin-right: 5px;
                    vertical-align: middle;
                }}
            </style>
        </head>
        <body>
            <div class="chart-container">
                <h1>Disaster Alert Levels</h1>
                <p class="chart-description">Current distribution of disasters by severity level</p>
                <div id="bar-chart"></div>
            </div>
            
            <script>
                // Bar chart data
                const barData = {{
                    categories: {list(disaster_count_pie_chart.keys())},
                    green: {green_disasters},
                    orange: {orange_disasters},
                    red: {red_disasters}
                }};
                
                // Green alert bars
                const greenTrace = {{
                    x: barData.categories,
                    y: barData.green,
                    name: 'Green Alert',
                    type: 'bar',
                    marker: {{
                        color: '#27ae60',
                        opacity: 0.9
                    }},
                    hovertemplate: '<b>%{{x}}</b><br>Green alerts: %{{y}}<extra></extra>'
                }};
                
                // Orange alert bars
                const orangeTrace = {{
                    x: barData.categories,
                    y: barData.orange,
                    name: 'Orange Alert',
                    type: 'bar',
                    marker: {{
                        color: '#e67e22',
                        opacity: 0.9
                    }},
                    hovertemplate: '<b>%{{x}}</b><br>Orange alerts: %{{y}}<extra></extra>'
                }};
                
                // Red alert bars
                const redTrace = {{
                    x: barData.categories,
                    y: barData.red,
                    name: 'Red Alert',
                    type: 'bar',
                    marker: {{
                        color: '#c0392b',
                        opacity: 0.9
                    }},
                    hovertemplate: '<b>%{{x}}</b><br>Red alerts: %{{y}}<extra></extra>'
                }};
                
                const layout = {{
                    title: 'Disasters by Alert Level',
                    barmode: 'stack',
                    xaxis: {{
                        title: 'Disaster Types',
                        tickangle: -45
                    }},
                    yaxis: {{
                        title: 'Number of Disasters'
                    }},
                    legend: {{
                        orientation: 'h',
                        yanchor: 'bottom',
                        y: 1.02,
                        xanchor: 'center',
                        x: 0.5
                    }},
                    margin: {{
                        b: 100
                    }},
                    hovermode: 'closest'
                }};
                
                Plotly.newPlot('bar-chart', [greenTrace, orangeTrace, redTrace], layout, {{responsive: true}});
            </script>
        </body>
        </html>
        """
        
        # Save the HTML files
        with open(os.path.join(templates_dir, 'pie_chart.html'), 'w') as f:
            f.write(pie_html)
            
        with open(os.path.join(templates_dir, 'bar_graph.html'), 'w') as f:
            f.write(bar_html)
            
        print(f"Successfully updated charts with enhanced UI. Total disasters: {len(data['disaster_names'])}")
    except Exception as e:
        print(f"Error saving chart files: {e}")
        import traceback
        print(traceback.format_exc())

periodic_task()  # Initial data fetch
@app.route('/')
def info():
    return redirect(url_for('home_page'))

@app.route('/map')
def map():
    return render_template('map.html',data = data)

@app.route('/pie')
def pie():
    return render_template('pie_chart.html')

@app.route('/bar')
def bar():
    return render_template('bar_graph.html')

@app.route('/home_page')
def home_page():
    return render_template('home_page.html',data = data)

@app.route('/nearest_disasters')
def nearest_disasters():
    if len(data['user_disaster_distance']['data_index']) == 0:
        return render_template("session_expired.html")
    return render_template('nearest_disasters.html',data = data)

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=periodic_task, trigger='interval', minutes=30)
scheduler.start()

if __name__ == '__main__':
    try:
        webbrowser.open('http://127.0.0.1:5000')
        app.run()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()