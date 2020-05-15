try:
	import requests as rq
except ImportError:
	print("This app needs the \"requests\" to be installed on your system. Please install it.")
import time
import re
import sys

def getIntInput(t):
	tmp = input(t)
	if not tmp.isdigit():
		return None
	return int(tmp)

def connect(s,name, passwd):
	try:
		r = s.post("http://{}.minitroopers.fr/login".format(name.replace(' ','-')), data=({'login':name, 'pass':passwd} if passwd else {"login":name})) #Truthfully, name doesn't have to be in url
	except:
		return None
	if "correct" in r.history[0].cookies["ssid"]:
		return None
	return r

def getChk(r):
	start = r.history[0].cookies["ssid"].find("keyy6:")
	return r.history[0].cookies["ssid"][start+6:start+12]

def playAllAttacks(s, r, chk, ennemy=None):
	results = []
	print("Battles:")
	r = s.get(r.url[:-3]+"/b/opp")
	for i in range(3):
		print("\tAttack n°{}: Pending...".format(i), end='\r', flush=True)
		if ennemy:
			attackurl = r.url[:-3] + "battle"
			a = s.post(attackurl, data={"friend":ennemy,"chk":chk})
		else:
			T = s.cookies["ssid"]
			start = T.find("oppsli") #See the keepnote book. Attackable opponents are in a list in the cookie
			end = T.find("i", start+6)
			opp = T[start+6:end]
			attackurl = r.url[:-3]+"battle?opp={};chk={}".format(opp, chk)
			a = s.get(attackurl)
		time.sleep(1)
		results.append("remport" in a.history[0].cookies["ssid"])
		print("\tAttack n°{}: {}".format(i, "Victory!  " if results[-1] else "Defeat.   "), flush=True)
	return sum(results)+3

def isMissionUnlocked(r):
	start = r.content.find(b'/b/mission')
	return start != -1
def isRaidUnlocked(r):
	start = r.content.find(b'/b/raid')
	return start != -1

def unlockMission(s,r,chk):
	s.get(r.url[:-2]+"unlock?mode=miss;chk={}".format(chk))

def playMission(s, r, chk):
	print("Mission:")
	attackurl = r.url[:-3]+"/b/mission?chk={}".format(chk)
	for i in range(3):
		print("\tAttempt n°{}: Pending...".format(i), end='\r', flush=True)
		a = s.get(attackurl)
		time.sleep(1)
		if "remport" in a.history[0].cookies["ssid"]:
			print("\tAttempt n°{}: {}".format(i, "Victory!  "), flush=True)
			return 4
		else:
			print("\tAttempt n°{}: {}".format(i, "Defeat.   "), flush=True)
	return 0

def playRaid(s, r, chk):
	print("Raid:")
	attackurl = r.url[:-3]+"/b/raid?chk={}".format(chk)
	stage = 0
	while True:
		a = s.get(attackurl)
		stage += 1
		print("\tStage: {}. Raiding...".format(stage), flush=True, end='\r')
		time.sleep(1)
		if "remport" not in a.history[0].cookies["ssid"]:
			break
	print("\tStage: {}. Raid has ended.".format(stage))
	return 4*stage

def getCredits(r):
	start = r.content.find(b'class="money"')
	start = r.content.find(b"\n", start)
	end = r.content.find(b"\n", start+1)
	money = int(r.content[start+1:end])
	return money

def farmPlayer(name, passwd, D):
	s = rq.Session()
	gain = 0
	print("--------\nPlayer: " + name, flush = True)
	if passwd=="#MANUALPASS#":
		print("This account is locked by a password. Please modify it manually if you want to farm this account.")
		return
	r = connect(s, name, passwd)
	if not r:
		print("Incorrect playername or password: {}, {}.\n".format(name, passwd if passwd else "<No password>"))
		return
	chk = getChk(r)
	if not b"/b/opp" in r.content:
		print("This account needs a password ! (or it was already farmed today)")
		return
	credits = getCredits(r)
	gain += playAllAttacks(s, r, chk, D["ennemy"]) if "ennemy" in D else playAllAttacks(s, r, chk)
	print() #Get to the next line
	if isMissionUnlocked(r): 
		gain += playMission(s, r, chk)
	else: 
		print("Mission: Not unlocked.",end = '')
		if "buyMission" in D and D["buyMission"].lower() == "true" and credits+gain >= 5:
			unlockMission(s,r, chk)
			print("\nMissions were unlocked. (buyMission config)")
			gain += -5
			gain += playMission(s,r,chk)
	print()
	if isRaidUnlocked(r): 
		gain += playRaid(s, r, chk)
	else: 
		print("Raid: Not unlocked.")
	print("\n{} total gain: {} credits (=> {} total).\n".format(name,gain,credits+gain))


def farmList():
	D = readconfigfile()

	Players = getAccounts()	

	for n, p in Players:
		farmPlayer(n,p,D)

	print("[END] Farm ended sucessfully.")


def readconfigfile():
	D = {}
	try:
		with open("config.txt",'r') as f:
			for line in f:
				if line[0] == '#':
					continue
				line = line.strip()
				m = re.match(r"^(\w*)=(.*)$", line)
				if m :
					D[m.group(1)] = m.group(2)
	except:
		print("[!] Config file not found. Assuming default parameters.")
		try:
			with open("config.txt",'w') as f:
				f.write("#Default config file, change it for your needs\n\n")
				f.write("#write a name to attack the same ennemy each time, or leave it blanc to choose randomly\n")
				f.write("ennemy=\n\n")
				f.write("#if this option is true, it checks if it can buy the access to Missions (which is worth over time)\n")
				f.write("buyMission=False\n\n")
				f.write("#Select the log level (1 = minimal, 2 = full) [WIP]\n")
				f.write("logLevel=2")
		except Exception as e:
			print("[!!!] Could not create a config file. Error: "+e)
		else:
			print("[+] A config file with default parameters has been created.")
	else:
		print("[+] Parameters read from config file.")
	return D

def getSubAccounts(s,r):
	a = s.get(r.url[:-2]+"history")
	if a.url[-2:] == "hq":
		print(": this account needs a password. Please add it manually",end = '')
		return None
	start = a.content.find(b"<td class=\"right\"><h2>")
	end = a.content.find(b"</td>",start)
	L = re.findall(r"http:\/\/((?!data\.).+?)\.minitroopers\.fr",a.content[start:end].decode())
	return L

def recursiveAllAccounts(s,r,indent):
	node =  	' ├╴'
	vertical = 	' │ '
	last =  	' └╴'
	space = 	'   '
	children = []
	sub = getSubAccounts(s,r)
	if sub == None:
		return None
	for i,name in enumerate(sub):
		print("\n",indent,node if i != len(sub)-1 else last,name,end='', sep='')
		tmp = rq.session()
		L = recursiveAllAccounts(tmp,connect(tmp, name, ""),indent + (vertical if i != len(sub)-1 else space))
		if L == None:
			children+=[(name,"#MANUALPASS#")]
		else:
			children += [(name,"")]
			children += L
	return children

def addToList(L):
	if not L:
		return
	T = list(set(L))
	names = []
	try:
		with open("mtbotlist.txt",'r+') as f:
			for line in f:
				name = line.strip().split(':')[0].lower().replace(' ','-')
				if not name:
					continue
				names.append(name)

			for player in T:
				if player[0].lower().replace(' ','-') in names:
					continue
				f.write("\n{}:{}".format(player[0].lower().replace(' ','-'),player[1]))
		print("Sucessfully added {} accounts to the list!\nPlease make sure to write passwords of the accounts that have one.".format(len(T)))
	except Exception as e:
		print("[!!!] Could not add to the list. Error: "+e)

def Menu():
	banner = r""" _____ _     _ _       _   _                      ___     ___ 
|     |_|___|_| |_ ___| |_| |_ ___ ___ ___    _ _|_  |   |   |
| | | | |   | | . | . |  _|  _| -_|  _|_ -|  | | |_| |_ _| | |
|_|_|_|_|_|_|_|___|___|_| |_| |___|_| |___|   \_/|_____|_|___|"""

	mainOptions="""
1) Add a player to the list
2) Farm an account
3) Farm all accounts
99) Quit"""


	print(banner)
	config = readconfigfile()

	while True:
		print(mainOptions)
		option = getIntInput("Select an option: ") #Case against empty strings
		if option == 1:
			AddPlayerOption()
		if option == 2:
			while True:
				sub = getIntInput("""\nDow you want to farm:
1) From input
2) From the list
99) Return
Select an option: """)
				if sub == 1:
					name = input("\nName: ")
					passwd = input("Password (empty if none): ")
					farmPlayer(name, passwd, config)
					break
				if sub == 2:
					print()
					Players = getAccounts()
					while True:
						print()
						for i, player in enumerate(Players):
							print("{}) {}".format(i+1,player[0]))
						print("{}) {}".format(len(Players)+1, "Return"))
						n = getIntInput("Select a player: ")
						if not n:
							continue
						n-=1
						if n in range(len(Players)):
							farmPlayer(Players[n][0],Players[n][1],config)
							break
						if n == len(Players):
							break
					break
				if sub == 99:
					break
		if option == 99:
			break
		if option == 3:
			farmList()

def AddPlayerOption():
	while True:
		print("""\nDo you want to add:
1) A single player
2) A player and its recruits, recursively
99) Return""")
		choice = getIntInput("Select an option: ")
		if not choice:
			continue
		
		if choice == 99:
			break
		if choice == 1:
			name = input("\nName: ")
			passwd = input("Password (empty if none): ")
			addToList([(name, passwd),])
			break
		if choice == 2:
			name = input("\nName: ")
			passwd = input("Password (empty if none): ")
			s = rq.session()
			r = connect(s,name,passwd)
			if not r:
				print("Invalid user or pass")
			print(name,end='')
			acts = recursiveAllAccounts(s,r,'')
			print()
			addToList(acts+[(name, passwd)])
			break

def getAccounts():
	Players = []
	try:
		with open("mtbotlist.txt",'r') as f:
			print("[+] Bot list found.")
			for line in f:
				if line[0] == '#':
					continue
				start = line.find(":")
				line = line.strip()
				if not line: continue
				Players.append((line[:start],line[start+1:]) if start != -1 else (line,""))
			print("[+] Bot list read. ({} accounts read)".format(len(Players)) if len(Players)>0 else "[!] Bot list empty. Please add your accounts to the list")
	except:
		print("[!] Bot list not found.")
		try:
			with open("mtbotlist.txt",'w') as f:
				f.write("#Each line is a different account\n#name:password\n#if your account do not have a password, both name or name: will work")
				print("[+] Created default bot list (mtbotlist.txt). Please add your accounts to the list.")
		except:
			print("[!] Could not create file, please add it manually or grant rights to this bot")
	
	return Players


def GetUpgradeCost(actualRank): #needs the Actual level of the trooper.
	return int(actualRank**2.5)

if __name__ == '__main__':
	Menu()
	if "-f" in sys.argv:
		pass