from gdacs.api import GDACSAPIReader
from flask import Flask,json,render_template
import plotly.graph_objects as go
import plotly.express as px
from collections import Counter
import webbrowser

app = Flask(__name__)

data = {'latitude' : [],'longitude' : [],'country_names' : [],
            'disaster_names' : [],'exact_description' : [],
            'alert_level' : [],'alert_color' : [],
            'from_date' : [],'time' : [],'severity_text' : [],
            'icon' : [],'legend_icon_names' : [],'legend_icon_pics' : []}

@app.route('/')
def info():
    client = GDACSAPIReader()
    geojson_obj = client.latest_events()
    disaster_count = {}
    disaster_count_pie_chart = {}
    for feature in geojson_obj.features:
        print('type = ',feature['type'])
        geometry = feature['geometry']
        
        print('type = ',geometry['type'])
        
        print('coordinates = ',geometry['coordinates'][0],geometry['coordinates'][1])
        data['longitude'].append(geometry['coordinates'][0])
        data['latitude'].append(geometry['coordinates'][1])
        
        properties = feature['properties']
        
        print('name = ',properties['name'])
        disaster_name = properties['name']
        
        print('description = ',properties['description'])
        description = properties['description']
        description = description.split()
        data['legend_icon_names'].append(description[0])


        print('exact description = ',properties['htmldescription'])
        data['exact_description'].append(properties['htmldescription'])
        
        print('icon = ',properties['icon'])
        data['icon'].append(properties['icon'])
        
        print('iconoverall = ',properties['iconoverall'])
        url = properties['url']
        print('url geometry = ',url['geometry'])
        print('report = ',url['report'])
        print('details = ',url['details'])
        
        print('alert level = ',properties['alertlevel'])
        data['alert_level'].append(properties['alertlevel'])
        alert_level = properties['alertlevel']
        print(len(alert_level))

        if 'Green' in alert_level:
            data['alert_color'].append('bg-success')
        elif 'Orange' in alert_level:
            data['alert_color'].append('bg-warning')
        else:
            data['alert_color'].append('bg-danger')
        
        print('alert score = ',properties['alertscore'])
        print('episode alert level = ',properties['episodealertlevel'])
        print('episode alert score = ',properties['episodealertscore'])
        print('is temporary = ',properties['istemporary'])
        print('is current = ',properties['iscurrent'])
        
        print('country = ',properties['country'])
        country = properties['country']
        if(len(country) == 0):
            country = "OffShore"
            disaster_name += ' OffShore'
            
        data['country_names'].append(country)
        data['disaster_names'].append(disaster_name)
        
        print('from date = ',properties['fromdate'])
        date_time = properties['fromdate'].split('T')
        data['from_date'].append(date_time[0])
        data['time'].append(date_time[1])

        print('to date = ',properties['todate'])
        print('date modified = ',properties['datemodified'])
        print('iso3 = ',properties['iso3'])
        print('source = ',properties['source'])
        print('source id = ',properties['sourceid'])
        print('polygon label = ',properties['polygonlabel'])
        print('class = ',properties['Class'])
        print('the affected countries are')
        for countries in properties['affectedcountries']:
            print('iso3 = ',countries['iso3'])
            print('countryname = ',countries['countryname'])
        severitydata = properties['severitydata']
        print('severity = ',severitydata['severity'])
        print('severity text = ',severitydata['severitytext'])
        data['severity_text'].append(severitydata['severitytext'])
        print('severity unit = ',severitydata['severityunit'])
        print('\n\n')
    disaster_count = Counter(data['legend_icon_names'])
    data['legend_icon_names'] = list(set(data['legend_icon_names']))
    baselink = "https://www.gdacs.org/images/gdacs_icons/maps/"
    for i in range(len(data['legend_icon_names'])):
        if data['legend_icon_names'][i] == 'Flood':
            data['legend_icon_pics'].append(baselink + alert_level + "/FL.png")

        elif data['legend_icon_names'][i] == 'Earthquake':
            data['legend_icon_pics'].append(baselink + alert_level + "/EQ.png")

        elif data['legend_icon_names'][i] == 'Forest':
            data['legend_icon_pics'].append(baselink + alert_level + "/WF.png")
            data['legend_icon_names'][i] += ' fires'
        
        elif data['legend_icon_names'][i] == 'Tropical':
            data['legend_icon_pics'].append(baselink + alert_level + "/TC.png")
            data['legend_icon_names'][i] += ' Cyclone';
        
        elif data['legend_icon_names'][i] == 'Tsunami':
            data['legend_icon_pics'].append(baselink + alert_level + "/TS.png")

        elif data['legend_icon_names'][i] == 'Drought':
            data['legend_icon_pics'].append(baselink + alert_level + "/DR.png")

        else:
            data['legend_icon_names'][i] = 'Volcano ' + data['legend_icon_names'][i]
            data['legend_icon_pics'].append(baselink + alert_level + "/VO.png")
    #event = client.get_event(event_type='WF', event_id='1019383',episode_id = "3")
    #print(event)
    disaster_count_pie_chart['Earthquakes'] = disaster_count['Earthquake']
    disaster_count_pie_chart['Floods'] = disaster_count['Flood']
    disaster_count_pie_chart['Forest Fires'] = disaster_count['Forest']
    disaster_count_pie_chart['Tropical Cyclones'] = disaster_count['Tropical']
    disaster_count_pie_chart['Tsunamis'] = disaster_count['Tsunami']
    disaster_count_pie_chart['Droughts'] = disaster_count['Drought']
    disaster_count_pie_chart['Volcanic Eruptions'] = disaster_count['Eruption']

    #plotting of pie chart
    pie_chart_colors = ['brown','blue','darkred','grey','darkblue','lightbrown','yellow']
    pie_figure = go.Figure(
        data = [
            go.Pie(
                labels = list(disaster_count_pie_chart.keys()),
                values = list(disaster_count_pie_chart.values()),
                textinfo = "label + percent",
                insidetextorientation = 'radial',
                textfont_size = 20,
                marker=dict(colors=pie_chart_colors)
            )
        ]
    )
   
    bar_trace = go.Bar(x = list(disaster_count_pie_chart.keys()),y = list(disaster_count_pie_chart.values()),
                                   marker_color = 'rgb(55, 83, 109)')
    layout = go.Layout(
        title = "Graph for Disasters Occuring currently",
        xaxis = dict(title = "Disasters"),
        yaxis = dict(title = "Count")
    )

    bar_figure = go.Figure(data = [bar_trace],layout=layout)

    pie_figure.write_html('templates/pie_chart.html')
    bar_figure.write_html('templates/bar_graph.html')
    return render_template('home_page.html')

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
    return render_template('home_page.html')

    
webbrowser.open('http://127.0.0.1:5000')
app.run(debug = True)