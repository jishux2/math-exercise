from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple

try:
    from zoneinfo import ZoneInfo  # Python 3.9+
    _CN_TZ = ZoneInfo("Asia/Shanghai")
except Exception:
    # 回退到固定东八区（无IANA数据库时）
    _CN_TZ = timezone(timedelta(hours=8))

def get_utc_now() -> datetime:
    """获取当前UTC时间（aware）"""
    return datetime.now(timezone.utc)

def get_cn_now(aware: bool = False) -> datetime:
    """获取当前中国时区时间。

    Args:
        aware: 为True返回带tzinfo的aware时间；为False返回naive本地时间（默认）。
    """
    now = datetime.now(_CN_TZ)
    return now if aware else now.replace(tzinfo=None)

def cn_today_start_end(aware: bool = False) -> Tuple[datetime, datetime]:
    """获取中国时区“今天”的起止时间。

    Returns:
        (start, end): 当天00:00:00 和 23:59:59.999999
    """
    now = get_cn_now(aware=True)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    if aware:
        return start, end
    return start.replace(tzinfo=None), end.replace(tzinfo=None)

def cn_today_date() -> datetime.date:
    """获取中国时区“今天”的日期对象。"""
    return get_cn_now(aware=True).date()

def format_duration(seconds: int) -> str:
    """
    格式化持续时间
    例如：将 3665 秒转换为 "1小时1分钟5秒"
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}小时")
    if minutes > 0:
        parts.append(f"{minutes}分钟")
    if remaining_seconds > 0 or not parts:
        parts.append(f"{remaining_seconds}秒")
    
    return "".join(parts)

def is_same_day(dt1: datetime, dt2: datetime) -> bool:
    """检查两个日期是否是同一天"""
    return dt1.date() == dt2.date()
