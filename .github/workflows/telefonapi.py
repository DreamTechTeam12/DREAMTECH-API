from flask import Flask, request, jsonify
import phonenumbers
from phonenumbers import NumberParseException, geocoder, carrier, timezone, PhoneNumberFormat, PhoneNumberType
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app)

# Telefon numarasının türünü döndürür
def get_number_type(parsed_number):
    number_type_mapping = {
        PhoneNumberType.MOBILE: 'Mobile',
        PhoneNumberType.FIXED_LINE: 'Fixed Line',
        PhoneNumberType.FIXED_LINE_OR_MOBILE: 'Fixed Line or Mobile',
        PhoneNumberType.VOIP: 'VoIP',
        PhoneNumberType.PERSONAL_NUMBER: 'Personal Number',
        PhoneNumberType.PAGER: 'Pager',
        PhoneNumberType.UAN: 'UAN',
        PhoneNumberType.TOLL_FREE: 'Toll-Free',
        PhoneNumberType.PREMIUM_RATE: 'Premium Rate',
        PhoneNumberType.SHARED_COST: 'Shared Cost',
        PhoneNumberType.UNKNOWN: 'Unknown'
    }
    num_type = phonenumbers.number_type(parsed_number)
    return number_type_mapping.get(num_type, 'Unknown')

@app.route('/phoneinfo', methods=['GET'])
@limiter.limit("5 per minute")  # Dakikada 5 istek
def get_phone_info():
    phone_number = request.args.get('phone')
    if not phone_number:
        return jsonify({'error': 'Phone number is required'}), 400

    try:
        # Telefon numarasını ayrıştır, varsayılan bölge kodu olarak 'TR' belirle
        parsed_number = phonenumbers.parse(phone_number, 'TR')

        # Telefon numarasının geçerli olup olmadığını kontrol et
        if not phonenumbers.is_valid_number(parsed_number):
            return jsonify({'error': 'Invalid phone number'}), 400

        # Telefon numarasının bilgilerini al
        country_code = parsed_number.country_code
        region_code = phonenumbers.region_code_for_number(parsed_number)
        country_name = geocoder.description_for_number(parsed_number, 'en')
        phone_carrier = carrier.name_for_number(parsed_number, 'en')
        time_zones = timezone.time_zones_for_number(parsed_number)
        number_type_description = get_number_type(parsed_number)
        international_format = phonenumbers.format_number(parsed_number, PhoneNumberFormat.INTERNATIONAL)
        national_format = phonenumbers.format_number(parsed_number, PhoneNumberFormat.NATIONAL)
        city = geocoder.description_for_number(parsed_number, 'en')  # Şehir veya il bilgisi

        # Yanıtı oluştur
        result = {
            'valid': True,
            'country_code': country_code,
            'region_code': region_code,
            'country_name': country_name,
            'carrier': phone_carrier,
            'time_zones': list(time_zones),
            'number_type': number_type_description,
            'international_format': international_format,
            'national_format': national_format,
            'city': city
        }
        return jsonify(result)

    except NumberParseException as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
