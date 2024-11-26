import pandas as pd
from flask import Flask, request, jsonify
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# データの読み込み
file_path = '/mnt/data/order_books.csv'
order_books_df = pd.read_csv(file_path)

# 日付をdatetime型に変換
order_books_df['time'] = pd.to_datetime(order_books_df['time'], format='%Y-%m-%d %H:%M:%S %z')

def calculate_ohlc(code, year, month, day, hour):
    """
    指定された銘柄コードと時刻に基づいてOHLCを計算する
    """
    # 指定された時間帯のデータを抽出
    start_time = datetime(year, month, day, hour, 0, 0)
    end_time = datetime(year, month, day, hour, 59, 59)
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

@app.route('/v1/q3-3/agent', methods=['POST'])
def agent_endpoint():
    """
    POST /v1/q3-3/agent エンドポイント
    """
    data = request.get_json()
    target = data.get('target')

    if not target:
        return jsonify({"error": "target is required"}), 400

    # 仮想的に3回リクエストを処理
    responses = []
    for i in range(3):
        code = "FTHD"
        year, month, day, hour = 2021, 12, 22, 10 + i  # 例: 各リクエストで異なる時間
        ohlc = calculate_ohlc(code, year, month, day, hour)
        if ohlc:
            responses.append(ohlc)
        else:
            return jsonify({"error": "No data found for the given parameters"}), 404

    # 結果を返却
    return jsonify(responses), 200

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
    app.run(debug=True)