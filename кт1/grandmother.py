import random
bye = 0

print("ЧЕГО СКАЗАТЬ-ТО ХОТЕЛ, МИЛОК?!")

while True:
    us = input('- ')
    if us == us.upper():
        if us == 'ПОКА!':
            bye += 1
            if bye == 3:
                print('ДО СВИДАНИЯ, МИЛЫЙ!')
                break
            else:
                year = random.randint(1930, 1950)
                print(f'НЕТ, НИ РАЗУ С {year} ГОДА!')
        else:
            bye = 0
            year = random.randint(1930, 1950)
            print(f'НЕТ, НИ РАЗУ С {year} ГОДА!')
    else:
       bye = 0
       print('АСЬ?! ГОВОРИ ГРОМЧЕ, ВНУЧЕК!')
