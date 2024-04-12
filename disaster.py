from gdacs.api import GDACSAPIReader
from gdacs.api import GDACSAPIError
from flask import Flask,json,render_template,request,jsonify,session
import plotly.graph_objects as go
import plotly.express as px
from collections import Counter
import mysql.connector
import webbrowser

connection = mysql.connector.connect(
    host = "localhost",
    user = "yash559",
    password = "1234",
    database = "disaster"
)

cursor = connection.cursor()

app = Flask(__name__,template_folder="templates")

data = {'latitude' : [],'longitude' : [],'country_names' : [],
            'disaster_type' : [],'is_current' : [],
            'disaster_names' : [],'exact_description' : [],
            'alert_level' : [],'alert_color' : [],
            'from_date' : [],'time' : [],'severity_text' : [],
            'icon' : [],'legend_icon_names' : [],'legend_icon_pics' : [],
            'event_type' : [],'event_id' : []}

@app.route('/')
def info():
    try:
        client = GDACSAPIReader()
        geojson_obj = client.latest_events()
    except GDACSAPIError as error:
        return render_template('error.html',error = error)

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
        description = description.split(' ')
        data['legend_icon_names'].append(description[0].split(' ')[0])


        print('exact description = ',properties['htmldescription'])
        data['exact_description'].append(properties['htmldescription'])
        
        print('icon = ',properties['icon'])
        
        print('iconoverall = ',properties['iconoverall'])
        data['icon'].append(properties['iconoverall'])

        print('eventtype = ',properties['eventtype'])
        data['event_type'].append(properties['eventtype'])

        print('eventid = ',properties['eventid'])
        data['event_id'].append(properties['eventid'])
        
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
            disaster_alert_count[description[0]]['green'] += 1

        elif 'Orange' in alert_level:
            data['alert_color'].append('bg-warning')
            disaster_alert_count[description[0]]['orange'] += 1
        
        else:
            data['alert_color'].append('bg-danger')
            disaster_alert_count[description[0]]['red'] += 1
        
        print('alert score = ',properties['alertscore'])
        print('episode alert level = ',properties['episodealertlevel'])
        print('episode alert score = ',properties['episodealertscore'])
        print('is temporary = ',properties['istemporary'])
        print('is current = ',properties['iscurrent'])
        data['is_current'].append(properties['iscurrent'])
        
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
    data['disaster_type'] = data['legend_icon_names']
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
            data['legend_icon_names'][i] += ' Cyclone'
        
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

    #separating disasters based on their alert level for graph plotting
    green_disasters,orange_disasters,red_disasters = [],[],[]

    for disaster_color in disaster_alert_count.values():
        green_disasters.append(disaster_color['green'])
        orange_disasters.append(disaster_color['orange'])
        red_disasters.append(disaster_color['red'])
   
   #creating different traces of graphs individually for red,orange and green alerts
    green_bar_trace = go.Bar(name = 'green alert level',
                             x = list(disaster_count_pie_chart.keys()),
                             y = green_disasters,
                             text = green_disasters,
                             marker_color = 'green',
                             textposition = 'auto')
    
    orange_bar_trace = go.Bar(name = 'orange alert level',
                              x = list(disaster_count_pie_chart.keys()),
                              y = orange_disasters,
                              text = orange_disasters,
                              marker_color = 'darkorange',
                              textposition = "auto")
    
    red_bar_trace = go.Bar(name = 'red alert level',
                           x = list(disaster_count_pie_chart.keys()),
                           y = red_disasters,
                           text = red_disasters,
                           marker_color = 'red',
                           textposition = 'auto')
    #crearing layout mainly for x and y axis titles
    layout = go.Layout(
        title = "Graph for Disasters Occuring currently",
        xaxis = dict(title = "Disasters"),
        yaxis = dict(title = "Count")
    )
    
    #plotting of bar graph and pie chart bar graph is of stack type
    bar_figure = go.Figure(data = [green_bar_trace,orange_bar_trace,red_bar_trace],layout=layout)
    bar_figure.update_layout(barmode = 'stack')

    pie_figure.write_html('templates/pie_chart.html')
    bar_figure.write_html('templates/bar_graph.html')
    print(type(data['event_id'][0]))
    return render_template('sign_up.html')

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

#this is the event data which is sent from js by ajax
@app.route('/processing',methods = ['GET','POST'])
def processing():
    global eventdata
    eventdata = request.json
    return jsonify(eventdata)

#This is the data collected from above

@app.route('/more_info')
def more_info():
    client = GDACSAPIReader()
    event = client.get_event(event_id = str(eventdata['id']),event_type = eventdata['type'])
    print('Title = ',event['title'])
    print('description = ',event['description'])
    print('image url in enclosure = ',event['enclosure']['@url'])
    print('event name = ',event['gdacs:eventname'])
    print('published date = ',event['pubDate'])
    print('from date = ',event['gdacs:fromdate'])
    print('To date = ',event['gdacs:todate'])
    print('icon = ',event['gdacs:icon'])
    print('Alert level = ',event['gdacs:alertscore'])
    print('Population = ',event['gdacs:population'])
    print('Severity = ',event['gdacs:severity'])
    print('Resources = ',event['gdacs:resources'])
    resource = event['gdacs:resources']['gdacs:resource']
    print('duration in weeks = ',event['gdacs:durationinweek'])

    if(eventdata['type'] == 'EQ'):
        earthquake_images = []

        for details in resource:
            if(details['@id'] == 'overviewmap'):
                details['gdacs:description'] = "This population density overview map offers a comprehensive depiction of the distribution of population across a 100-kilometer radius"
                earthquake_images.append(details)

            elif(details['@id'] == 'neic_pager'):
                earthquake_images.append(details)
        
            elif(details['@id'] == 'populationmap_cached'):
                details['gdacs:description'] = "The Population density map zoomed Overview"
                earthquake_images.append(details)

            elif(details['@id'] == 'shakemap_populationmap_static_v01'):
                details['gdacs:description'] = "This Shakemap provides comprehensive visual representation of seismic activity and its potential impact on densely populated areas within the region."
                earthquake_images.append(details)

            elif(details['@id'] == 'shakemap_populationmap_overview_static_v01'):
                earthquake_images.append(details)

            elif(details['@id'] == 'shake_preliminary_image'):
                details['gdacs:description'] = "This rapid impact image provides a comprehensive snapshot of the aftermath of this earthquake event, offering crucial insights into the extent and severity of its impact on affected regions."
                earthquake_images.append(details)

        return render_template('earthquake_info.html',event = event,earthquake_images = earthquake_images)
    
    elif(eventdata['type'] == 'TC'):
        cyclone_images = []

        for details in resource:
            
            if(details['@id'] == 'storm_surge_maxheight'):
                details['gdacs:description'] = "This storm surge max height shows how high the water level rises above normal during this tropical cyclone"
                cyclone_images.append(details)

            elif(details['@id'] == 'storm_surge_animation'):
                details['gdacs:description'] = "This storm surge animation shows how the water level rises and falls along the coast during this tropical cyclone"
                cyclone_images.append(details)
        
        return render_template('cyclone_info.html',event = event,cyclone_images = cyclone_images)
    
    elif(eventdata['type'] == 'FL'):

        flood_images = []
        for details in resource:
            if(details['@id'] == 'overviewmap_cached'):
                details['gdacs:description'] = "This flood overview map provides a comprehensive visual representation of areas affected by this flooding within this specific region"
                flood_images.append(details)
        
        return render_template('flood_info.html',event = event,flood_images = flood_images)
    
    elif(eventdata['type'] == 'VO'):

        eruption_images = []
        for details in resource:
            if(details['@id'] == 'overview_map_cached'):
                eruption_images.append(details)

        eruption_images['@url'] = eruption_images['@url'][:-5] + '2' + eruption_images['@url'][-4:]

        return render_template('eruption_info.html',event = event,eruption_images = eruption_images)
    
    elif(eventdata['type'] == 'DR'):

        return render_template('drought_info.html',event = event)
    
    else:

        return render_template('fires_info.html',event = event)

    
@app.route('/sign_up',methods = ["POST"])
def sign_up():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    contact = request.form['contact']

    insert_query = "INSERT INTO login_details (username,password,email,contact) VALUES (%s,%s,%s,%s)"

    cursor.execute(insert_query,(username,password,email,contact))

    connection.commit()
    cursor.close()
    connection.close()

    return render_template('home_page.html',data = data)

webbrowser.open('http://127.0.0.1:5000')
app.run(debug = True)
