"""台大節次對照表（依使用者提供的課表截圖整理）與 115-1 學期行事曆"""

from datetime import date, timedelta

PERIODS = {

    "0": ("07:10", "08:00"),
    "1": ("08:10", "09:00"),
    "2": ("09:10", "10:00"),
    "3": ("10:20", "11:10"),
    "4": ("11:20", "12:10"),
    "5": ("12:20", "13:10"),
    "6": ("13:20", "14:10"),
    "7": ("14:20", "15:10"),
    "8": ("15:30", "16:20"),
    "9": ("16:30", "17:20"),
    "10": ("17:30", "18:20"),
    "A": ("18:25", "19:15"),
    "B": ("19:20", "20:10"),
    "C": ("20:15", "21:05"),
    "D": ("21:10", "22:00"),
}

# 節次的先後順序（用來判斷連堂、找「下一節」）
ORDER = list(PERIODS.keys())


# ===== 115-1 學期行事曆（台大教務處 115 學年度行事曆，115/9/8 更正版）=====
SEMESTER_START = date(2026, 9, 7)      # 第 1 週星期一（9/7 上課開始）
LAST_WEEK = 16                          # 第 16 週＝期末考週（12/21–12/25）

# 沒有正常上課的日子：放假或停課
NO_CLASS_DAYS = {
    date(2026, 9, 25): "中秋節",
    date(2026, 9, 28): "教師節",
    date(2026, 10, 9): "國慶日遇例假日補假",
    date(2026, 10, 10): "國慶日",
    date(2026, 10, 26): "臺灣光復節遇例假日補假",
    date(2026, 11, 20): "全校運動會（停課）",
    date(2026, 11, 21): "全校運動會（停課）",
    date(2026, 12, 25): "行憲紀念日",
    date(2027, 1, 1): "開國紀念日",
}
# 上課但情況特殊的週（驗證時分開看）
SPECIAL_WEEKS = {8: "期中考週", 16: "期末考週"}


def week_of(d):
    """日期 → 第幾週（第 1 週從 SEMESTER_START 開始）；學期外回傳 None"""
    w = (d - SEMESTER_START).days // 7 + 1
    return w if 1 <= w <= LAST_WEEK else None


def day_type(d):
    """回傳 (是否正常上課, 說明)。週末、放假、停課、學期外都算不上課"""
    if d.isoweekday() > 5:
        return False, "週末"
    if d in NO_CLASS_DAYS:
        return False, NO_CLASS_DAYS[d]
    w = week_of(d)
    if w is None:
        return False, "學期外"
    return True, SPECIAL_WEEKS.get(w, "")


if __name__ == "__main__":
    for p, (start, end) in PERIODS.items():
        print(f"第 {p:>2} 節  {start}–{end}")
