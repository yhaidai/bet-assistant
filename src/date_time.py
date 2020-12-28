from datetime import datetime, timedelta


def correct_year(f):
    def wrapper(*args):
        result = f(*args)
        if datetime.now() - result > timedelta(days=1):
            result = result.replace(year=datetime.now().year + 1)
        return result

    return wrapper


def correct_timezone(f):
    def wrapper(*args):
        result = f(*args)
        result = result + timedelta(hours=2)
        return result

    return wrapper


class DateTime(datetime):
    @classmethod
    @correct_year
    def from_parimatch_str(cls, src):
        src += str(cls.today().year)
        return super(DateTime, cls).strptime(src, '%d/%m%H:%M%Y')

    @classmethod
    @correct_timezone
    @correct_year
    def from_1xbet_str(cls, src):
        return super(DateTime, cls).strptime(src, '%d.%m.%Y (%H:%M)')

    @classmethod
    @correct_year
    def from_ggbet_str(cls, src):
        today = cls.today()
        src = src.replace('Today', ' '.join([today.strftime('%b'), str(today.day)]))
        src += str(today.year)
        return super(DateTime, cls).strptime(src, '%H:%M\n%b %d%Y')

    @classmethod
    @correct_year
    def from_favorit_str(cls, src):
        today = cls.today()
        if ' ' not in src:
            src = ' '.join([str(today.day), today.strftime('%b'), src])
        src += str(today.year)
        result = super(DateTime, cls).strptime(src, '%d %b%H:%M%Y')
        if result.hour == 0 and result.minute == 0:
            result += timedelta(days=1)
        return result

    @classmethod
    @correct_timezone
    @correct_year
    def from_marathon_str(cls, src):
        today = cls.today()
        if ' ' not in src:
            src = ' '.join([str(today.day), today.strftime('%b'), src])

        try:
            result = super(DateTime, cls).strptime(src, '%d %b %Y %H:%M')
        except ValueError:
            src += str(today.year)
            result = super(DateTime, cls).strptime(src, '%d %b %H:%M%Y')

        return result
