import requests as rq
import time
import re

def connect(s,name, passwd):
	r = s.post("http://{}.minitroopers.fr/login".format(name.replace(' ','-')), data=({'login':name, 'pass':passwd} if passwd else {"login":name})) #Truthfully, name doesn't have to be in url
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

def farmPlayer(name, passwd,D):
	s = rq.Session()
	gain = 0
	print("--------\nPlayer: " + name, flush = True)
	r = connect(s, name, passwd)
	if not r:
		print("Incorrect playername or password: {}, {}".format(name, passwd))
		return
	chk = getChk(r)
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
	print("\n{} total gain: {} credits (=> {} total).\n\n".format(name,gain,credits+gain))


def farmList(loc):
	Players=[]
	D = readconfigfile()
	try:
		with open("mtbotlist.txt",'r') as f:
			print("[+] Bot list found.")
			for line in f:
				if line[0] == '#':
					continue
				start = line.find(":")
				line = line.strip()
				Players.append((line[:start],line[start+1:]) if start != -1 else (line,""))
			print("[+] Bot list read. ({} accounts read)".format(len(Players)) if len(Players)>0 else "[!] Bot list empty. Please add your accounts to the list")
	except:
		print("[!] Bot list not found.")
		try:
			with open("mtbotlist.txt",'w') as f:
				print("[+] Created default bot list (mtbotlist.txt). Please add your accounts to the list.")
		except:
			print("[!] Could not create file, please add it manually or grant rights to this bot")

	for n, p in Players:
		farmPlayer(n,p,D)

	print("[END] Bot ended sucessfully.")


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
				f.write("#Select the log level (1 = minimal, 2 = full)\n")
				f.write("logLevel=2")
		except Exception as e:
			print("[!!!] Could not create a config file. Error: "+e)
		else:
			print("[+] A config file with default parameters has been created.")
	else:
		print("[+] Parameters read from config file.")
	return D