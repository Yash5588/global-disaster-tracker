from gdacs.api import GDACSAPIReader
from gdacs.api import GDACSAPIError
from flask import Flask,render_template,jsonify,redirect,request,url_for
from flask import Blueprint

more_info_bp = Blueprint('more_info',__name__)

#this is the event data which is sent from js by ajax from home_page.html
@more_info_bp.route('/processing',methods = ['GET','POST'])
def processing():
    global eventdata
    eventdata = request.json
    return jsonify(eventdata)

#This is the data collected from above
@more_info_bp.route('/more_info')
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
                details['gdacs:description'] = "This overview map provides a comprehensive depiction of the recent volcanic eruption, capturing critical information to aid in understanding the extent and impact of the event."
                eruption_images.append(details)
        if(len(eruption_images) != 0):
            eruption_images[0]['@url'] = eruption_images[0]['@url'][:-5] + '2' + eruption_images[0]['@url'][-4:]

        return render_template('eruption_info.html',event = event,eruption_images = eruption_images)
    
    elif(eventdata['type'] == 'DR'):

        return render_template('drought_info.html',event = event)
    
    else:

        return render_template('fires_info.html',event = event)