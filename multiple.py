import os
from threading import Thread


def start():
	os.system("python main.py")

if __name__ == '__main__':
	for x in range(10):
		Thread(target = start).start()