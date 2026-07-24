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