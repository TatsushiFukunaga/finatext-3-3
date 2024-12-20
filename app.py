from flask import Flask, request, jsonify, redirect
import pandas as pd
from datetime import datetime
import logging
from pytz import timezone

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

file_path = 'order_books.csv'
# file_path = 'order_books_example.csv'
df = pd.read_csv(file_path)

df['time'] = pd.to_datetime(df['time'].str.replace(' JST', '', regex=False), format='%Y-%m-%d %H:%M:%S %z')
df['price'] = df['price'].astype(float)

def calculate_ohlc(code, year, month, day, hour):
    jst = timezone("Asia/Tokyo")
    # start_time と end_time を tz-aware にする
    start_time = jst.localize(datetime(year, month, day, hour, 0, 0))
    end_time = jst.localize(datetime(year, month, day, hour, 59, 59))

    mask = (
        (df['code'] == code) &
        (df['time'] >= start_time) &
        (df['time'] <= end_time)
    )
    filtered_data = df[mask]

    open_price = filtered_data.iloc[0]['price']
    high_price = filtered_data['price'].max()
    low_price = filtered_data['price'].min()
    close_price = filtered_data.iloc[-1]['price']

    return {
        "open": int(open_price),
        "high": int(high_price),
        "low": int(low_price),
        "close": int(close_price)
    }

@app.route('/candle', methods=['GET'])
def candle_endpoint():
    """
    GET /candle エンドポイント
    """
    code = request.args.get('code')
    year = int(request.args.get('year'))
    month = int(request.args.get('month'))
    day = int(request.args.get('day'))
    hour = int(request.args.get('hour'))

    ohlc = calculate_ohlc(code, year, month, day, hour)
    if ohlc:
        logging.info(f"Calculated OHLC: {ohlc}")
        return jsonify(ohlc), 200
    else:
        return jsonify({"error": "No data found for the given parameters"}), 404

@app.route('/flag', methods=['PUT'])
def flag_endpoint():
    """
    PUT /flag エンドポイント
    """
    data = request.get_json()
    flag = data.get('flag')

    if flag:
        logging.info(f"Received flag: {flag}")
        return jsonify({"flag_received": flag})
    else:
        logging.warning("Missing flag in the request")
        return jsonify({"error": "Missing flag"}), 400

if __name__ == '__main__':
    app.run()