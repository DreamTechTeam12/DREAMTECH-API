from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# IP adresi bilgilerini almak için kullanılacak servis
IP_INFO_URL = "http://ipapi.co/{}/json"

@app.route('/ipinfo', methods=['GET'])
def get_ip_info():
    ip_address = request.args.get('ip')
    if not ip_address:
        return jsonify({'error': 'IP address is required'}), 400

    try:
        response = requests.get(IP_INFO_URL.format(ip_address))
        response.raise_for_status()
        ip_info = response.json()
        return jsonify(ip_info)
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
