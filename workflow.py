from datetime import datetime, timedelta
import httpx
from google.cloud import storage
import streamlit as st
from urllib.parse import urlparse
from pathlib import Path

def process_csv_workflow():
    now = datetime.now()
    first_day_of_this_month = now.replace(day=1)
    last_month = first_day_of_this_month - timedelta(days=1)
    yyyymm = last_month.strftime("%Y%m")

    bucket_name = "elenmikasa"
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    
    # 共通の保存先フォルダー
    common_folder = "eria_jukyu_last_month"

    # 処理対象の電力会社リスト
    companies = {
        "hepco": {
            "name": "北海道電力(HEPCO)",
            "url": f"https://www.hepco.co.jp/network/con_service/public_document/supply_demand_results/csv/eria_jukyu_{yyyymm}_01.csv",
        },
        "tepco": {
            "name": "東京電力(TEPCO)",
            "url": f"https://www.tepco.co.jp/forecast/html/images/eria_jukyu_{yyyymm}_03.csv",
        }
    }

    header_mapping = {
        "DATE": "date",
        "TIME": "time",
        "エリア需要": "area_demand",
        "原子力": "nuclear",
        "火力(LNG)": "thermal_lng",
        "火力(石炭)": "thermal_coal",
        "火力(石油)": "thermal_oil",
        "火力(その他)": "thermal_other",
        "火力出力制御量": "thermal_output_control",
        "水力": "hydro",
        "地熱": "geothermal",
        "バイオマス": "biomass",
        "バイオマス出力制御量": "biomass_output_control",
        "太陽光発電実績": "solar_generation",
        "太陽光出力制御量": "solar_output_control",
        "風力発電実績": "wind_generation",
        "風力出力制御量": "wind_output_control",
        "揚水": "pumped_storage",
        "蓄電池": "battery",
        "連系線": "interconnection",
        "その他": "other",
        "合計": "total",
    }

    # 各社の処理を順番に実行
    for company_key, info in companies.items():
        url = info["url"]
        company_name = info["name"]
        file_name = Path(urlparse(url).path).name

        st.markdown(f"--- \n### 🏢 {company_name}")

        # 1. 外部サイトからCSVをダウンロード
        try:
            with httpx.Client(follow_redirects=True) as client:
                response = client.get(url)
                response.raise_for_status()
                csv_content = response.content
        except Exception as e:
            st.error(f"CSVのダウンロードに失敗しました: {e}")
            continue

        # 2. GCS直下にオリジナルのCSVを一時保存（プレフィックスなし）
        blob = bucket.blob(file_name)
        blob.upload_from_string(csv_content, content_type="text/csv")
        st.info(f"1. GCS直下に一時保存しました: `gs://{bucket_name}/{file_name}`")

        # 3. CSVを読み込んで加工処理
        raw_data = blob.download_as_bytes()
        try:
            text_content = raw_data.decode("cp932")
        except UnicodeDecodeError:
            text_content = raw_data.decode("utf-8", errors="ignore")

        lines = text_content.splitlines()
        lines = lines[1:]  # 2行目以降のデータだけを残す
        if len(lines) < 2:
            st.error("CSVファイルの行数が不足しています。")
            continue

        original_header = lines[0]
        cols = [col.strip() for col in original_header.split(",")]

        converted_cols = []
        unknown_cols = []

        for col in cols:
            if col in header_mapping:
                converted_cols.append(header_mapping[col])
            else:
                unknown_cols.append(col)
                converted_cols.append(col) 

        if unknown_cols:
            st.warning(f"⚠️ 新しいカラムを検知しました: {unknown_cols}")

        converted_header = ",".join(converted_cols)
        lines[0] = converted_header  

        processed_text = "\n".join(lines) + "\n"
        utf8_bytes = processed_text.encode("utf-8")

        # 4. 加工したファイルを共通フォルダーに保存（プレフィックスなし）
        converted_file_name = file_name.replace(yyyymm, "last_month").replace(".csv", "_converted_header.csv")
        destination_path = f"{common_folder}/{converted_file_name}"
        
        dest_blob = bucket.blob(destination_path)
        dest_blob.upload_from_string(utf8_bytes, content_type="text/csv; charset=utf-8")

        st.success(f"2. 加工して共通フォルダーに保存しました！\n`gs://{bucket_name}/{destination_path}`")
