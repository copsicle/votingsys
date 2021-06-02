from basic.models import Voter
from random import randrange
import datetime

start_date = datetime.date(1940, 1, 1)
end_date = datetime.date(2003, 2, 1)
time_between_dates = end_date - start_date
days_between_dates = time_between_dates.days
eligible = 605
voted = 448
image = "6d0fbd5b-1770-4969-8191-c5b3a1489742"

while eligible != 0:
    num = str(randrange(10000000, 40000000))
    if num == "21264828":
        continue
    eligible -= 1
    count = -1
    id_sum = 0
    for let in num:
        count += 1
        if let == 0:
            continue
        inc_num = int(let) * ((count % 2) + 1)
        id_sum += inc_num
        if inc_num > 9:
            id_sum -= 9
    if (id_sum % 10) != 0:
        num += str(10 - (id_sum % 10))
    else:
        num += "0"
    random_number_of_days = randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)
    if voted != 0:
        voted -= 1
        vo = Voter(pid=num, voted=True, birth=random_date, image=image)
    else:
        vo = Voter(pid=num, birth=random_date, image=image)
    vo.save()
