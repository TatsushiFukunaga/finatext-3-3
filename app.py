from flask import Flask, request, jsonify
import pandas as pd
from datetime import datetime
import logging
from pytz import timezone

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# データの読み込み
file_path = 'order_books.csv'
order_books_df = pd.read_csv(file_path)

# JSTを取り除き、+0900のみ残す
order_books_df['time'] = order_books_df['time'].str.replace(' JST', '', regex=False)

# 'time'列をdatetime型に変換
order_books_df['time'] = pd.to_datetime(
    order_books_df['time'], 
    format='%Y-%m-%d %H:%M:%S %z'
)

def calculate_ohlc(code, year, month, day, hour):
    """
    指定された銘柄コードと時刻に基づいてOHLCを計算する
    """
    # タイムゾーンを定義（日本標準時）
    jst = timezone("Asia/Tokyo")

    # 指定された時間帯のデータを抽出
    start_time = datetime(year, month, day, hour, 0, 0, tzinfo=jst)
    end_time = datetime(year, month, day, hour, 59, 59, tzinfo=jst)

    mask = (
        (order_books_df['code'] == code) &
        (order_books_df['time'] >= start_time) &
        (order_books_df['time'] <= end_time)
    )
    filtered_data = order_books_df[mask]

    if filtered_data.empty:
        return None

    # OHLCを計算
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