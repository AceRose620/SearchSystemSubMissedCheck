import os
import re
from datetime import datetime, timedelta

# CSVファイルが格納されているディレクトリのパス
CSV_DIR = "C:/Users/Administrator/Documents/Workspace/Search System/db/current/bankcrupcy"  # ここをCSVファイルのディレクトリに置き換えてください
# ファイル名の形式: output_YYYY-MM-DD_YYYY-MM-DD_破産.csv
pattern = re.compile(r"output_(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})_破産\.csv")

# 期間リストを収集
periods = []

for filename in os.listdir(CSV_DIR):
    match = pattern.match(filename)
    if match:
        start_str, end_str = match.groups()
        start_date = datetime.strptime(start_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_str, "%Y-%m-%d")
        periods.append((start_date, end_date))

# 開始日でソート
periods.sort()

# 欠損期間の検出
missing_periods = []
for i in range(1, len(periods)):
    prev_end = periods[i - 1][1]
    curr_start = periods[i][0]
    expected_start = prev_end + timedelta(days=1)
    if curr_start != expected_start:
        missing_periods.append((expected_start.strftime("%Y-%m-%d"), (curr_start - timedelta(days=1)).strftime("%Y-%m-%d")))

# 結果の表示
print("⛔ 欠損している期間:")
for start, end in missing_periods:
    print(f"{start} ～ {end}")