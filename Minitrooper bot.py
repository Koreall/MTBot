import requests as rq
import time

def connect(s,name, passwd):
	r = s.post("http://{}.minitroopers.fr/login".format(name), data=({'login':name, 'pass':passwd} if passwd else {"login":name})) #Truthfully, name doesn't have to be in url
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
		T = s.cookies["ssid"]
		start = T.find("oppsli") #See the keepnote book. Attackable opponents are in a list in the cookie
		end = T.find("i", start+6)
		ennemy = T[start+6:end]
		attackurl = r.url[:-3]+"battle?opp={};chk={}".format(ennemy, chk)
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
		a = s.get(attackurl, allow_redirects=False)
		stage += 1
		print("\tStage: {}. Raiding...".format(stage), flush=True, end='\r')
		time.sleep(1)
		if "remport" not in a.headers["Set-Cookie"]:
			break
	print("\tStage: {}. Raid has ended.".format(stage))
	return 4*stage

def farmPlayer(name, passwd):
	s = rq.Session()
	money = 0
	print("Player: " + name, flush = True)
	r = connect(s, name, passwd)
	if not r:
		print("Incorrect playername or password: {}, {}".format(name, passwd))
		return
	chk = getChk(r)
	money += playAllAttacks(s, r, chk)
	print() #Get to the next line
	if isMissionUnlocked(r): 
		money += playMission(s, r, chk)
	else: 
		print("Mission: Not unlocked.",end = '')
	print()
	if isRaidUnlocked(r): 
		money += playRaid(s, r, chk)
	else: 
		print("Raid: Not unlocked.")
	print("\n{} total gain: {} credits.\n\n".format(name,money))


def farmList(loc):
	Players=[]
	try:
		with open("mtbotlist.txt",'r') as f:
			for line in f:
				if line[0] == '#':
					continue
				start = line.find(":")
				line = line.strip()
				Players.append((line[:start],line[start+1:]) if start != -1 else (line,""))
	except Exception as e:
		raise e

	for n, p in Players:
		farmPlayer(n,p)