import re
import csv
from datetime import date

# 全角数字→半角数字変換関数
def zenkaku_to_hankaku(s):
    return s.translate(str.maketrans('０１２３４５６７８９', '0123456789'))

# 和暦から西暦へ変換する関数（曜日の直前までの文字列から抽出）
def convert_japanese_date(text):
    # 曜日名（〇曜日）の位置を探す
    weekday_match = re.search(r'(月曜日|火曜日|水曜日|木曜日|金曜日|土曜日|日曜日)', text)
    if weekday_match:
        text_before_weekday = text[:weekday_match.start()]
    else:
        text_before_weekday = text

    # 和暦+数字4桁以上のパターンを検索
    pattern = re.compile(r'(昭和|平成|令和)([0-9０-９]{3,6})')
    m = pattern.search(text_before_weekday)
    if not m:
        return None

    era = m.group(1)
    num_str = zenkaku_to_hankaku(m.group(2))

    length = len(num_str)
    try:
        if length == 3:
            year = int(num_str[0])
            month = int(num_str[1])
            day = int(num_str[2])
        elif length == 4:
            year = int(num_str[:2])
            month = int(num_str[2])
            day = int(num_str[3])
        elif length == 5:
            year = int(num_str[:2])
            month = int(num_str[2])
            day = int(num_str[3:])
        elif length == 6:
            year = int(num_str[:2])
            month = int(num_str[2:4])
            day = int(num_str[4:])
        else:
            return None
    except Exception:
        return None

    # 和暦→西暦変換
    if era == '昭和':
        year += 1925
    elif era == '平成':
        year += 1988
    elif era == '令和':
        year += 2018
    else:
        return None

    try:
        return date(year, month, day)
    except ValueError:
        return None

# CSV読み込み＆日付検出＆結果保存
def extract_dates_and_save(csv_path, output_txt_path):
    results = []
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader):
            text = row.get('display_text', '')
            detected_date = convert_japanese_date(text)
            if detected_date:
                results.append(f'Line {i+1}: {detected_date}  ← {text[:50]}...')
            else:
                results.append(f'Line {i+1}: 日付なし / 抽出失敗 ← {text[:50]}...')

    with open(output_txt_path, 'w', encoding='utf-8') as f:
        for line in results:
            f.write(line + '\n')

    print(f"✅ 結果を保存しました: {output_txt_path}")

# 実行例
if __name__ == '__main__':
    csv_path = 'C:/Users/Administrator/Documents/Workspace/Search System/resource/7.csv'  # CSVファイルパスを適宜変更してください
    output_txt_path = 'C:/Users/Administrator/Documents/Workspace/Search System/result.txt'  # 保存先テキストファイルパスを適宜変更してください
    extract_dates_and_save(csv_path, output_txt_path)
