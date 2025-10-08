from datetime import datetime
def time_ago(dt):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'yesterday', '3 months ago',
    'just now', etc
    """
    if not dt:
        return ""
    
    now = datetime.utcnow()
    
    if isinstance(dt, str):
        # Try to parse the datetime string
        try:
            dt = datetime.strptime(dt, '%Y-%m-%dT%H:%M:%SZ')
        except (ValueError, TypeError):
            return dt  # Return as is if can't parse
    
    diff = now - dt if isinstance(dt, datetime) else now - datetime.fromtimestamp(dt)
    
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return 'just now'
    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return f"{second_diff} seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return f"{second_diff // 60} minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return f"{second_diff // 3600} hours ago"
    if day_diff == 1:
        return "yesterday"
    if day_diff < 7:
        return f"{day_diff} days ago"
    if day_diff < 31:
        weeks = day_diff // 7
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    if day_diff < 365:
        months = day_diff // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    years = day_diff // 365
    return f"{years} year{'s' if years > 1 else ''} ago"
