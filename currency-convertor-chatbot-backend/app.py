from flask import Flask, request, jsonify
import requests  # Importing requests to make API calls

app = Flask(__name__)

@app.route('/', methods=['POST'])
def index():
    print("Endpoint hit!")  # Debugging line
    try:
        # Retrieve JSON data from the request
        data = request.get_json()

        # Check if data is provided
        if data is None:
            return jsonify({"error": "No JSON data provided"}), 400

        # Extracting parameters from the JSON data
        unit_currency = data['queryResult']['parameters'].get('unit-currency', [{}])[0]
        source_currency = unit_currency.get('currency', '')  # Adjust as per your JSON
        amount = unit_currency.get('amount')
        target_currency = data['queryResult']['parameters'].get('currency-name')

        # Check if any parameters are missing
        if amount is None or target_currency is None or source_currency == '':
            return jsonify({"error": "Missing parameters"}), 400

        print("Source Currency:", source_currency)
        print("Amount:", amount)
        print("Target Currency:", target_currency)

        # Fetch conversion rate
        conversion_rate = fetch_conversion(source_currency, target_currency)

        if conversion_rate is None:
            return jsonify({"error": "Failed to fetch conversion rate"}), 500

        # Calculate converted amount
        converted_amount = amount * conversion_rate
        response = {
            'fulfillmentText': "{} {} is {:.2f} {}".format(amount, source_currency, converted_amount, target_currency)
        }
        return jsonify(response)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

def fetch_conversion(source, target):
    # Your API URL
    url = f"https://api.currencyapi.com/v3/latest?apikey=cur_live_hDOBnfviABg2u8ZcX28otJp0GA95tx7Z834ubhWg&currencies={source},{target}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # Adjust the response parsing according to the actual API response structure
            # Check if data['data'] contains both source and target currencies
            if 'data' in data and source in data['data'] and target in data['data']:
                return data['data'][target]['value'] / data['data'][source]['value']
            else:
                print("Currency data not found in response")
                return None
        else:
            print(f"API error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching conversion: {str(e)}")
        return None

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
