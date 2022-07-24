#!/usr/bin/env python

from dtmf import DTMF
import os
import random

from string import digits
prefix = '06'
call_code = ['0', '1', '2', '3', '4', '5', '6', '7', '9']

solutions = []

for user in os.listdir('/home'):

    flag = prefix + random.choice(call_code) + \
        ''.join(random.choice(digits) for _ in range(8))

    solutions.append(','.join([user, flag]) + '\n')

    DTMF.to_file(
        '/home/%s/dtmf.wav' % user,
        flag,
        1,
        44100,
        True
    )

    uid = os.stat('/home/%s' % user).st_uid
    gid = os.stat('/home/%s' % user).st_gid

    os.chown('/home/%s/dtmf.wav' % user, uid, gid)

with open('dtmf_solutions.csv', 'w') as f:
    f.writelines(solutions)
