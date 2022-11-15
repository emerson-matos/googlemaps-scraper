from datetime import timedelta

def parse_relative_date(curr_date, string_date):
    split_date = string_date.split(' ')

    n = split_date[0]
    delta = split_date[1]

    if delta == 'ano':
        return curr_date - timedelta(days=365)
    elif delta == 'anos':
        return curr_date - timedelta(days=365 * int(n))
    elif delta == 'mes':
        return curr_date - timedelta(days=30)
    elif delta == 'meses':
        return curr_date - timedelta(days=30 * int(n))
    elif delta == 'semana':
        return curr_date - timedelta(weeks=1)
    elif delta == 'semanas':
        return curr_date - timedelta(weeks=int(n))
    elif delta == 'dia':
        return curr_date - timedelta(days=1)
    elif delta == 'dias':
        return curr_date - timedelta(days=int(n))
    elif delta == 'hora':
        return curr_date - timedelta(hours=1)
    elif delta == 'horas':
        return curr_date - timedelta(hours=int(n))
    elif delta == 'minuto':
        return curr_date - timedelta(minutes=1)
    elif delta == 'minutos':
        return curr_date - timedelta(minutes=int(n))
    elif delta == 'momentos':
        return curr_date - timedelta(seconds=1)