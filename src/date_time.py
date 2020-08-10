from datetime import datetime, timedelta


class DateTime(datetime):
    @classmethod
    def from_parimatch_str(cls, src):
        src += str(cls.today().year)
        return super(DateTime, cls).strptime(src, '%d/%m%H:%M%Y')

    @classmethod
    def from_1xbet_str(cls, src):
        return super(DateTime, cls).strptime(src, '%d.%m.%Y (%H:%M)')

    @classmethod
    def from_ggbet_str(cls, src):
        today = cls.today()
        src = src.replace('Today', ' '.join([today.strftime('%b'), str(today.day)]))
        src += str(today.year)
        return super(DateTime, cls).strptime(src, '%H:%M\n%b %d%Y')

    @classmethod
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
    def from_marathon_str(cls, src):
        today = cls.today()
        if ' ' not in src:
            src = ' '.join([str(today.day), today.strftime('%b'), src])
        src += str(today.year)

        result = super(DateTime, cls).strptime(src, '%d %b %H:%M%Y')
        result += timedelta(seconds=2 * 3600)
        return result
