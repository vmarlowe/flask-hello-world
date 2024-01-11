from flask import Flask, request, render_template_string
import requests
import os
from dotenv import load_dotenv

load_dotenv()  

app = Flask(__name__)

us_states = [
    ("Alabama", "AL"), ("Alaska", "AK"), ("Arizona", "AZ"),
    ("Arkansas", "AR"), ("California", "CA"), ("Colorado", "CO"),
    ("Connecticut", "CT"), ("Delaware", "DE"), ("Florida", "FL"),
    ("Georgia", "GA"), ("Hawaii", "HI"), ("Idaho", "ID"),
    ("Illinois", "IL"), ("Indiana", "IN"), ("Iowa", "IA"),
    ("Kansas", "KS"), ("Kentucky", "KY"), ("Louisiana", "LA"),
    ("Maine", "ME"), ("Maryland", "MD"), ("Massachusetts", "MA"),
    ("Michigan", "MI"), ("Minnesota", "MN"), ("Mississippi", "MS"),
    ("Missouri", "MO"), ("Montana", "MT"), ("Nebraska", "NE"),
    ("Nevada", "NV"), ("New Hampshire", "NH"), ("New Jersey", "NJ"),
    ("New Mexico", "NM"), ("New York", "NY"), ("North Carolina", "NC"),
    ("North Dakota", "ND"), ("Ohio", "OH"), ("Oklahoma", "OK"),
    ("Oregon", "OR"), ("Pennsylvania", "PA"), ("Rhode Island", "RI"),
    ("South Carolina", "SC"), ("South Dakota", "SD"), ("Tennessee", "TN"),
    ("Texas", "TX"), ("Utah", "UT"), ("Vermont", "VT"),
    ("Virginia", "VA"), ("Washington", "WA"), ("West Virginia", "WV"),
    ("Wisconsin", "WI"), ("Wyoming", "WY")
]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
   
        city = request.form.get('city')
        state = request.form.get('state')
        zipcode = request.form.get('zipcode')
        neighborhood = request.form.get('neighborhood')


        print(f"City: {city}, State: {state}, Zip: {zipcode}, Neighborhood: {neighborhood}")


        query_parts = [f"province:{state}"]
        if city:
            query_parts.append(f"(city:{city})")
        if zipcode:
            query_parts.append(f"(postalCode:{zipcode})")
        if neighborhood:
            query_parts.append(f"(neighborhoods:\"{neighborhood}\" OR subdivision:\"{neighborhood}\")")
        
        query = " AND ".join(query_parts)

    
        print(f"Constructed query: {query}")

        return get_data(query)
    else:
  
        state_options = ''.join([f'<option value="{abbr}">{name}</option>' for name, abbr in us_states])
        return f'''
            <html>
                <head>
                    <title>Property Search</title>
                </head>
                <body>
                    <h1>Do you want to boost your Sphere campaign and target specific neighborhoods in your city?</h1>
                    <p>Enter the neighborhoods you want to target and we will add as many of the matching addreses we can find into your audience!</p>
                    <form method="post">
                        City: <input type="text" name="city"><br>
                        State: <select name="state">{state_options}</select><br>
                        Zip Code: <input type="text" name="zipcode"><br>
                        Neighborhood Name: <input type="text" name="neighborhood"><br>
                        <input type="submit" value="Submit">
                    </form>
                </body>
            </html>
        '''

def get_data(query):
    url = "https://api.datafiniti.co/v4/properties/search"
    payload = {
        "view": "default",
        "num_records": 10,
        "query": query,
        "download": False
    }
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {os.getenv('DATAFINITI_API_KEY')}",
        "content-type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        num_found = data.get('num_found', 0)

     
        formatted_addresses = [
            f"{record.get('address', 'No address available')}, {record.get('city', 'No city')}, {record.get('province', 'No province')}, {record.get('postalCode', 'No postal code')}"
            for record in data.get('records', [])
        ]

        html_content = f'<h1>Total Address to be Added to your Audience: {num_found}</h1>'
        html_content += '<h2>Sample of 10 Addresses:</h2>'
        html_content += '<ul>'
        for address in formatted_addresses:
            html_content += f'<li>{address}</li>'
        html_content += '</ul>'
        html_content += '<br><a href="/"><button>Do Another Search</button></a>'

        return render_template_string(html_content)
    else:
        return render_template_string("<p>Error fetching data from API.</p>")

if __name__ == '__main__':
    app.run(debug=True)
