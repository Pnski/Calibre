from calibre.utils.date import parse_date

def _parse_date(date_str:str, log=None):
    """
    Parse RanobeDB date str (YYYYMMDD format) to datetime.

    :param date_int: Date as string (e.g., 20240115)
    :param log: Log object
    :return: datetime object or None
    """
    
    try:
        return parse_date(date_str)
    except Exception as e:
        if log:
            log.warning('Failed to parse date %s: %s' % (date_str, str(e)))

    return None

def parse_book_number(m,prefix=None, width=2):
    if width > len(m.group(2)) != 0:
        num = m.group(2).zfill(width)
    else:
        num = m.group(2)
    chosen_prefix = (prefix + " ") if len(prefix) > 0 else m.group(1)
    
    return chosen_prefix + num