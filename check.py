import re
import csv
from datetime import date, datetime

def zenkaku_to_hankaku(s):
    return s.translate(str.maketrans('０１２３４５６７８９', '0123456789'))

def convert_japanese_date(text):
    weekday_match = re.search(r'(月曜日|火曜日|水曜日|木曜日|金曜日|土曜日|日曜日)', text)
    text_before_weekday = text[:weekday_match.start()] if weekday_match else text

    pattern = re.compile(r'(昭和|平成|令和)([0-9０-９]{3,6})')
    m = pattern.search(text_before_weekday)
    if not m:
        return None, None

    era = m.group(1)
    num_str = zenkaku_to_hankaku(m.group(2))

    try:
        if len(num_str) == 3:
            year = int(num_str[0])
            month = int(num_str[1])
            day = int(num_str[2])
        elif len(num_str) == 4:
            year = int(num_str[:2])
            month = int(num_str[2])
            day = int(num_str[3])
        elif len(num_str) == 5:
            year = int(num_str[:2])
            month = int(num_str[2])
            day = int(num_str[3:])
        elif len(num_str) == 6:
            year = int(num_str[:2])
            month = int(num_str[2:4])
            day = int(num_str[4:])
        else:
            return None, None
    except Exception:
        return None, None

    if era == '昭和':
        year += 1925
    elif era == '平成':
        year += 1988
    elif era == '令和':
        year += 2018
    else:
        return None, None

    try:
        d = date(year, month, day)
        return d, d.strftime('%A')
    except ValueError:
        return None, None

def load_missing_periods(filepath):
    periods = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.match(r"(\d{4}-\d{2}-\d{2}) ～ (\d{4}-\d{2}-\d{2})", line)
            if match:
                start = datetime.strptime(match.group(1), "%Y-%m-%d").date()
                end = datetime.strptime(match.group(2), "%Y-%m-%d").date()
                periods.append((start, end))
    return periods

def is_in_missing_periods(detected_date, periods):
    for start, end in periods:
        if start <= detected_date <= end:
            return True
    return False

def filter_missed_data_and_log(csv_path, missing_period_path, missed_csv_path, result_txt_path):
    periods = load_missing_periods(missing_period_path)
    matched_rows = []
    result_lines = []

    last_valid_date = None
    last_valid_weekday = None

    with open(csv_path, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['detected_date', 'weekday']
        for i, row in enumerate(reader):
            text = row.get('display_text', '')
            detected_date, weekday = convert_japanese_date(text)

            inherited = False
            if detected_date:
                last_valid_date = detected_date
                last_valid_weekday = weekday
            elif last_valid_date:
                detected_date = last_valid_date
                weekday = last_valid_weekday
                inherited = True
            else:
                result_lines.append(f"Line {i+1}: 日付なし / 抽出失敗 ← {text[:50]}...")
                continue  # 最初の行など、継承もできない場合はスキップ

            if inherited:
                result_lines.append(f"Line {i+1}: {detected_date} ({weekday}) ※前の行から継承 ← {text[:50]}...")
            else:
                result_lines.append(f"Line {i+1}: {detected_date} ({weekday}) ← {text[:50]}...")

            if is_in_missing_periods(detected_date, periods):
                row['detected_date'] = detected_date.isoformat()
                row['weekday'] = weekday
                matched_rows.append(row)

    with open(result_txt_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(result_lines))

    if matched_rows:
        with open(missed_csv_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(matched_rows)
        print(f"✅ 欠損期間内のデータ {len(matched_rows)} 行を保存しました: {missed_csv_path}")
    else:
        print("✅ 欠損期間内に該当するデータは見つかりませんでした。")

    print(f"📄 抽出結果を保存しました: {result_txt_path}")

# === 実行 ===
if __name__ == '__main__':
    csv_path = 'C:/Users/Administrator/Documents/Workspace/SearchSystemSubMissedCheck/resource/bankcrupcy01/26.csv'
    missing_period_path = 'C:/Users/Administrator/Documents/Workspace/SearchSystemSubMissedCheck/resource/missing_period.txt'
    missed_csv_path = 'C:/Users/Administrator/Documents/Workspace/SearchSystemSubMissedCheck/result/missed_data_01_26.csv'
    result_txt_path = 'C:/Users/Administrator/Documents/Workspace/SearchSystemSubMissedCheck/resource/result.txt'

    filter_missed_data_and_log(csv_path, missing_period_path, missed_csv_path, result_txt_path)
