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
    with open(filepath, 'r', encoding='utf-8-sig') as f:
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

    prev_date, prev_weekday = None, None

    with open(csv_path, 'r', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['detected_date', 'weekday']
        for i, row in enumerate(reader):
            text = row.get('display_text', '')
            detected_date, weekday = convert_japanese_date(text)

            if detected_date:
                prev_date, prev_weekday = detected_date, weekday
                result_lines.append(f"Line {i+1}: {detected_date} ({weekday}) ← {text[:50]}...")
            elif prev_date:
                detected_date, weekday = prev_date, prev_weekday
                result_lines.append(f"Line {i+1}: Using previous line's date {detected_date} ({weekday}) ← {text[:50]}...")
            else:
                result_lines.append(f"Line {i+1}: No date / failed to extract ← {text[:50]}...")
                continue

            if is_in_missing_periods(detected_date, periods):
                row['detected_date'] = detected_date.isoformat()
                row['weekday'] = weekday
                matched_rows.append(row)

    with open(result_txt_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(result_lines))

    if matched_rows:
        with open(missed_csv_path, 'w', newline='', encoding='utf-8-sig') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(matched_rows)
        print(f"✅ Saved {len(matched_rows)} rows matching missing periods: {missed_csv_path}")
    else:
        print("✅ No data matched missing periods.")

    print(f"📄 Saved result log: {result_txt_path}")

if __name__ == '__main__':
    for i in range(2, 32):  # Change to range(19, 32) for 19–31
        csv_path = f'C:/Users/Administrator/Documents/Workspace/SearchSystemSubMissedCheck/resource/bankcrupcy01/{i}.csv'
        missing_period_path = 'C:/Users/Administrator/Documents/Workspace/SearchSystemSubMissedCheck/resource/missing_period.txt'
        missed_csv_path = f'C:/Users/Administrator/Documents/Workspace/SearchSystemSubMissedCheck/result/missed_data(破産)_01_{i}.csv'
        result_txt_path = f'C:/Users/Administrator/Documents/Workspace/SearchSystemSubMissedCheck/resource/result_{i}.txt'

        print(f"📂 Checking file: {csv_path}")
        try:
            filter_missed_data_and_log(csv_path, missing_period_path, missed_csv_path, result_txt_path)
        except Exception as e:
            print(f"❌ Error processing file {i}.csv: {e}")
