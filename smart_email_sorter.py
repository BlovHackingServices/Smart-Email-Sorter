from sys import exit
from colorama import Fore, Style
from os.path import isdir, isfile, expanduser
from time import time, time_ns
from os import makedirs
from re import search
from colorama import init
from dns import resolver
from validate_email import validate_email
from multiprocessing import freeze_support
from multiprocessing.pool import ThreadPool
from functools import partial
from threading import Lock

lock = Lock();

def get_truthy():
	return ('yes', 'no')

def run_lookup():
	render_intro()

	while True:
		request = request_intro()
		if request.upper() in map(str.upper, get_truthy()):
			if request.upper() == 'NO':
				exit()
			else:
				break
		else:
			show_error('Invalid input, enter yes/NO.')
			continue

	while True:
		filename = request_file().strip('"')

		if filename == '':
			show_error('File is required, try again.')
			continue
		elif isdir(filename):
			show_error('File cannot be a directory, try again.')
			continue
		elif not isfile(filename):
			show_error('File does not exist, try again.')
			continue
		else:
			break

	while True:
		folder = request_dir().strip('"')

		if folder == '':
			show_error('Folder is required, try again.')
			continue
		elif isfile(folder):
			show_error('Folder cannot be a file, try again.')
			continue
		elif not isdir(folder):
			show_error('Folder does not exist, try again.')
			continue
		else:
			break

	while True:
		thread = request_thread()

		if thread == '':
			show_error('Thread is required, try again.')
			continue
		elif not thread.isnumeric():
			show_error('Invalid input, enter a number.')
			continue
		else:
			thread_int = int(thread)

			if thread_int not in range(1, 101):
				show_error('Invalid input, enter a number from 1-100.')
				continue
			else:
				break

	try:
	  print('Opening file:', filename)
	  with open(filename) as f:
	    emails = [line.strip() for line in f if line.strip() != '']
	except:
	  show_error('Error while opening: '+ filename+ '\nSupported files are txt or csv')
	  sys.exit('IO error')
	else:
	  show_success(str(len(emails)) + ' email addresses loaded... starting lookup')

	print('Waiting...\n')
	start_time = time()
	print('Lookup started...\n')
	do_lookup(emails, folder, thread)
	end_time = time()
	render_stat(start_time, end_time)

def rw_input(prompt, prefill=''):
	try:
		from pyautogui import typewrite
		print(prompt)
		typewrite(prefill)
		return input()
	except(ImportError, KeyError):
		from readline import set_startup_hook, insert_text
		set_startup_hook(lambda: insert_text(prefill))
	
	try:
		return input(prompt)
	finally:
		set_startup_hook()

def render_intro():
	print(Fore.RED + '''
 __              __  ___     ___                       __   __   __  ___  ___  __  
/__`  |\\/|  /\\  |__)  |     |__   |\\/|  /\\  | |       /__` /  \\ |__)  |  |__  |__) 
.__/  |  | /~~\\ |  \\  |     |___  |  | /~~\\ | |___    .__/ \\__/ |  \\  |  |___ |  \\ 
                                                                                   
''' + Fore.GREEN + '''								v0.0.1 by DmitriBlov
''' + Fore.BLUE + '''
About
+++++''' + Style.RESET_ALL + '''
This program is a command-line software used to speedily sort email addresses by their webmail login page, MX, NS, CNAME, TXT, and PTR DNS records. It is distributed as freeware
''' + Fore.BLUE + '''
Contact
+++++++''' + Style.RESET_ALL + '''
To reach out to us for feedback, reports, feature requests, etc. Use the contact details below

Telegram: https://t.me/DmitriBlov
Skype: live:.cid.e47b29ce4dfd6ec6
Discord: dmitriblov
Telegram Channel: https://t.me/BlovHackingServices
''' + Fore.BLUE + '''
Disclaimer
++++++++++''' + Style.RESET_ALL + '''
DmitriBlov or developers at BlovHackingServices will not be held responsible for any misuse of this software. If usage violates the laws of your country or more, do not use this software''' + Fore.YELLOW + '''
--------------------------------------------------------------------------------''' + Style.RESET_ALL + '''
If you like what this software does and/or how it helps you, please consider donating to support our effort and to keep newer versions of this software free. We really appreciate your donations

Bitcoin: bc1q60zfh5zz5qk83e4xu6dh34fnfhkzuplt7nywga
Bitcoin Cash: qreq3z08u4jdwcgg2hf2ry4m850w8qq8uyxtkvy2hf
Ethereum: 0xF13DeAcC1D363D9D955051313b71Edde1a505496
USDT: 0xF13DeAcC1D363D9D955051313b71Edde1a505496
Litecoin: ltc1qtsd5knqly48jujp9gryamfzf0hdfpqfpfe6r8m
	''')

def request_intro():
	return input('Would you like to proceed? (yes/NO):')

def request_file():
	show_success('Supported email list seperator is a newline')
	return input('Enter email list file (you can drag and drop file here):')

def request_dir():
	return rw_input('Enter save directory (you can drag and drop folder here):', expanduser('~\\Documents'))

def request_thread():
	return rw_input('Enter lookup thread (integer 1-100):', '20')

def show_error(msg:str):
	print(Fore.RED + '\n' + msg + '\n' + Style.RESET_ALL)

def show_success(msg:str):
	print(Fore.GREEN + '\n' + msg + '\n' + Style.RESET_ALL)

def process_lookup(lock, folder, email):
	print('Looking up', email + '...')
	email = email.lower()

	if validate_email(email_address=email, check_format=True, check_blacklist=False, check_dns=False, check_smtp=False):
		split = email.split('@', 1)
		domain = split[1]
		mx_error = False
		mx = ''

		try:
			m = resolver.resolve(domain, 'MX')
			mx = (m[0].to_text()).lower()
		except:
			mx_error = True

		try:
			a = resolver.resolve(domain, 'A')
		except:
			if (mx_error == True):
				path = folder + '\\bad.txt'
				with lock:
					with open(path, 'a') as f:
						f.write(email + '\n')
				print(email, 'is a bad email address... [skipped]')
		else:
			mx_folder = folder + '\\MX'
			if not isdir(mx_folder):
				makedirs(mx_folder)

			if mx:
				print(domain, 'MX record is:', mx)

				if search(r'\.google\.com', mx) and search(r'\@gmail\.', email):
					path = mx_folder + '\\gmail.txt'
				elif search(r'\.google\.com', mx) and search(r'\@googlemail\.', email):
					path = mx_folder + '\\googlemail.txt'
				elif search(r'\.google\.com', mx):
					path = mx_folder + '\\google_workspace.txt'
				elif search(r'\.outlook\.com', mx) and search(r'\@hotmail\.', email):
					path = mx_folder + '\\hotmail.txt'
				elif search(r'\.outlook\.com', mx) and search(r'\@live\.', email):
					path = mx_folder + '\\live.txt'
				elif search(r'\.outlook\.com', mx) and search(r'\@msn\.', email):
					path = mx_folder + '\\msn.txt'
				elif search(r'\.outlook\.com', mx) and search(r'\@outlook\.', email):
					path = mx_folder + '\\outlook.txt'
				elif search(r'\.outlook\.com', mx) and search(domain.replace('-', '').replace('.', '-'), mx):
					path = mx_folder + '\\office365.txt'
				elif search(r'\.yahoodns\.net', mx) and search(r'\@yahoo\.', email):
					path = mx_folder + '\\yahoo.txt'
				elif search(r'\.yahoodns\.net', mx) and search(r'\@ymail\.', email):
					path = mx_folder + '\\ymail.txt'
				elif search(r'\.yahoodns\.net', mx) and search(r'\@aol\.', email):
					path = mx_folder + '\\aol.txt'
				elif search(r'\.yahoodns\.net', mx) and search(r'\@frontiernet\.', email):
					path = mx_folder + '\\frontiernet.txt'
				elif search(r'\.yahoodns\.net', mx) and search(r'\@sky\.com', email):
					path = mx_folder + '\\sky.com.txt'
				elif search(r'\.yahoodns\.net', mx) and search(r'\@verizon\.', email):
					path = mx_folder + '\\verizon.txt'
				elif search(r'\.yahoodns\.net', mx) and search(r'\@rocketmail\.', email):
					path = mx_folder + '\\rocketmail.txt'
				elif search(r'\.yahoodns\.net', mx) and search(r'\@aim\.', email):
					path = mx_folder + '\\aim.txt'
				elif search(r'\.orange\.fr', mx) and search(r'\@wanadoo\.', email):
					path = mx_folder + '\\wanadoo.txt'
				elif search(r'\.orange\.fr', mx) and search(r'\@orange\.', email):
					path = mx_folder + '\\orange.txt'
				elif search(r'\.icloud\.com', mx) and search(r'\@mac\.', email):
					path = mx_folder + '\\mac.txt'
				elif search(r'\.icloud\.com', mx) and search(r'\@me\.com', email):
					path = mx_folder + '\\me.com.txt'
				elif search(r'\.icloud\.com', mx) and search(r'\@icloud\.', email):
					path = mx_folder + '\\icloud.txt'
				elif search(r'\.cloudfilter\.net', mx) and search(r'\@cox\.net', email):
					path = mx_folder + '\\cox.net.txt'
				elif search(r'\.cloudfilter\.net', mx) and search(r'\@shaw\.ca', email):
					path = mx_folder + '\\shaw.ca.txt'
				elif search(r'\.prodigy\.net', mx) and search(r'\@att\.net', email):
					path = mx_folder + '\\att.net.txt'
				elif search(r'\.prodigy\.net', mx) and search(r'\@bellsouth\.net', email):
					path = mx_folder + '\\bellsouth.net.txt'
				elif search(r'\.prodigy\.net', mx) and search(r'\@sbcglobal\.net', email):
					path = mx_folder + '\\sbcglobal.net.txt'
				elif search(r'\.skymail\.net\.br', mx) and search(r'\@ig\.com\.br', email):
					path = mx_folder + '\\ig.com.br.txt'
				elif search(r'\.terra\.com', mx) and search(r'\@terra\.com\.br', email):
					path = mx_folder + '\\terra.com.br.txt'
				elif search(r'\.sfr\.fr', mx) and search(r'\@sfr\.fr', email):
					path = mx_folder + '\\sfr.fr.txt'
				elif search(r'\.sfr\.fr', mx) and search(r'\@neuf\.fr', email):
					path = mx_folder + '\\neuf.fr.txt'
				elif search(r'\.sfr\.fr', mx) and search(r'\@club-internet\.fr', email):
					path = mx_folder + '\\club-internet.fr.txt'
				elif search(r'\.tim\.it', mx) and search(r'\@alice\.it', email):
					path = mx_folder + '\\alice.it.txt'
				elif search(r'\.virginmedia\.com', mx) and search(r'\@blueyonder\.co\.uk', email):
					path = mx_folder + '\\blueyonder.co.uk.txt'
				elif search(r'\.virginmedia\.com', mx) and search(r'\@ntlworld\.com', email):
					path = mx_folder + '\\ntlworld.com.txt'
				elif search(r'\.kpnmail\.nl', mx) and search(r'\@hetnet\.nl', email):
					path = mx_folder + '\\hetnet.nl.txt'
				elif search(r'\.kpnmail\.nl', mx) and search(r'\@planet\.nl', email):
					path = mx_folder + '\\planet.nl.txt'
				elif search(r'\.ziggo\.nl', mx) and search(r'\@chello\.nl', email):
					path = mx_folder + '\\chello.nl.txt'
				elif search(r'\.ziggo\.nl', mx) and search(r'\@home\.nl', email):
					path = mx_folder + '\\home.nl.txt'
				elif search(r'\.free\.fr', mx) and search(r'\@free\.fr', email):
					path = mx_folder + '\\free.fr.txt'
				elif search(r'\.free\.fr', mx) and search(r'\@aliceadsl\.fr', email):
					path = mx_folder + '\\aliceadsl.fr.txt'
				elif search(r'\.openwave\.ai', mx) and search(r'\@optonline\.net', email):
					path = mx_folder + '\\optonline.net.txt'
				elif search(r'\.ellb\.ch', mx) and search(r'\bluewin-ch', mx):
					path = mx_folder + '\\bluewin.ch.txt'
				elif search(r'\.spamexperts\.com', mx):
					path = mx_folder + '\\zonnet.nl.txt'
				elif search(r'\.telenet-ops\.be', mx):
					path = mx_folder + '\\telenet.be.txt'
				elif search(r'\.yahoo\.co\.jp', mx):
					path = mx_folder + '\\yahoo.co.jp.txt'
				elif search(r'\.virgilio\.it', mx):
					path = mx_folder + '\\virgilio.it.txt'
				elif search(r'\.tiscali\.it', mx):
					path = mx_folder + '\\tiscali.it.txt'
				elif search(r'\.laposte\.net', mx):
					path = mx_folder + '\\laposte.net.txt'
				elif search(r'\.charter\.net', mx):
					path = mx_folder + '\\charter.net.txt'
				elif search(r'\.rambler\.ru', mx):
					path = mx_folder + '\\rambler.ru.txt'
				elif search(r'\.t-online\.de', mx):
					path = mx_folder + '\\t-online.de.txt'
				elif search(r'\.freenet\.de', mx):
					path = mx_folder + '\\freenet.de.txt'
				elif search(r'\.tin\.it', mx):
					path = mx_folder + '\\tin.it.txt'
				elif search(r'\.tiscali\.co\.uk', mx):
					path = mx_folder + '\\tiscali.co.uk.txt'	
				elif search(r'\.vodafonemail\.de', mx):
					path = mx_folder + '\\arcor.de.txt'
				elif search(r'\.centurylink\.net', mx):
					path = mx_folder + '\\centurytel.net.txt'
				elif search(r'\.optusnet\.com\.au', mx):
					path = mx_folder + '\\optusnet.com.au.txt'
				elif search(r'\.untd\.com', mx):
					path = mx_folder + '\\juno.com.txt'
				elif search(r'\.comcast\.net', mx):
					path = mx_folder + '\\comcast.txt'
				elif search(r'\.rediff\.akadns\.net', mx):
					path = mx_folder + '\\rediffmail.txt'
				elif search(r'\.windstream\.net', mx):
					path = mx_folder + '\\windstream.txt'
				elif search(r'\.sympatico\.ca', mx):
					path = mx_folder + '\\sympatico.ca.txt'
				elif search(r'\.proximus\.be', mx):
					path = mx_folder + '\\skynet.be.txt'
				elif search(r'\.gmx\.net', mx):
					path = mx_folder + '\\gmx.txt'
				elif search(r'\.web\.de', mx):
					path = mx_folder + '\\web.de.txt'
				elif search(r'\.bigpond\.com', mx):
					path = mx_folder + '\\bigpond.txt'
				elif search(r'\.libero\.it', mx):
					path = mx_folder + '\\libero.it.txt'
				elif search(r'\.uol\.com\.br', mx):
					path = mx_folder + '\\uol.com.br.txt'
				elif search(r'\.bol\.com\.br', mx):
					path = mx_folder + '\\bol.com.br.txt'
				elif search(r'\.mail\.ru', mx):
					path = mx_folder + '\\mail.ru.txt'
				elif search(r'\.anazana\.com', mx):
					path = mx_folder + '\\anazana.txt'
				elif search(r'\.icoremail\.net', mx):
					path = mx_folder + '\\coremail.txt'
				elif search(r'\.earthlink-vadesecure\.net', mx):
					path = mx_folder + '\\earthlink.net.txt'
				elif search(r'\.aliyun\.com|\.alibaba\.com', mx):
					path = mx_folder + '\\aliyun.txt'
				elif search(r'\.263\.net', mx):
					path = mx_folder + '\\263.txt'
				elif search(r'\.1and1\.', mx):
					path = mx_folder + '\\1and1.txt'
				elif search(r'\.hinet\.', mx):
					path = mx_folder + '\\hinet.txt'
				elif search(r'\.iinet\.net\.au', mx):
					path = mx_folder + '\\iinet.txt'
				elif search(r'\.mail\.com', mx):
					path = mx_folder + '\\mail.com.txt'
				elif search(r'\.mimecast\.', mx):
					path = mx_folder + '\\mimecast.txt'
				elif search(r'\.registrar-servers\.com', mx):
					path = mx_folder + '\\namecheap.txt'
				elif search(r'\.myregisteredsite\.com', mx):
					path = mx_folder + '\\networksolutions.txt'
				elif search(r'\.secureserver\.net', mx):
					path = mx_folder + '\\godaddy.txt'
				elif search(r'\.163\.com|\.netease\.com', mx):
					path = mx_folder + '\\163.txt'
				elif search(r'\.pphosted\.com', mx):
					path = mx_folder + '\\pphosted.txt'
				elif search(r'\.qq\.com', mx):
					path = mx_folder + '\\qq.txt'
				elif search(r'\.emailsrvr\.com', mx):
					path = mx_folder + '\\rackspace.txt'
				elif search(r'\.synaq\.', mx):
					path = mx_folder + '\\synaq.txt'
				elif search(r'\.yandex\.ru', mx):
					path = mx_folder + '\\yandex.ru.txt'
				elif search(r'\.zmail\.', mx):
					path = mx_folder + '\\zmail.txt'
				elif search(r'\.zoho\.com', mx):
					path = mx_folder + '\\zoho.txt'
				elif search(r' ' + domain + r'\.', mx):
					path = mx_folder + '\\only_domain.txt'
				elif search(r' mail\.' + domain + r'\.', mx):
					path = mx_folder + '\\mail.domain.txt'
				elif search(domain, mx):
					path = mx_folder + '\\has_domain.txt'
				else:
					path = mx_folder + '\\others.txt'
			else:
				print(domain, 'has no MX record')
				path = mx_folder + '\\no_record.txt'

			with lock:
				with open(path, 'a') as f:
					f.write(email + '\n')
			print('Added', email, 'to', path)
	else:
		path = folder + '\\invalid.txt'
		with lock:
			with open(path, 'a') as f:
				f.write(email + '\n')
		print(email, 'is an invalid email address... [skipped]')

def do_lookup(emails, folder, thread):
	resolver.default_resolver = resolver.Resolver(configure=False)
	resolver.default_resolver.nameservers = ['8.8.8.8']

	folder += '\\SmartEmailSorter\\' + str(time_ns())
	if not isdir(folder):
		makedirs(folder)
	
	print('------------------------------------------------')

	lock = Lock()
	
	with ThreadPool(processes=int(thread)) as pool:
		pool.map(partial(process_lookup, lock, folder), emails)
	
	print('------------------------------------------------')

def render_stat(start_time, end_time):
	print(f'Finished in {end_time - start_time} seconds')

if __name__ == '__main__':
	freeze_support()
	init()
	run_lookup()