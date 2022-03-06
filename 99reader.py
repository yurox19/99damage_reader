from enum import Enum
from io import StringIO
from bs4 import BeautifulSoup
import requests
import json
import csv
import argparse

url_ff		= "https://faceitfinder.com/stats/"
url_vl		= "https://vaclist.net/api/account?q="
url_99		= ""
teams		= []
players		= []
pick_ban 	= []

arg_csv		= False
arg_team	= False
arg_match	= False

parser		= argparse.ArgumentParser(description="simple python tool to gather informations about 99damage teams or matches")
url_group	= parser.add_mutually_exclusive_group(required=True)
print_group	= parser.add_mutually_exclusive_group()
url_group.add_argument("-m", "--match", action="store_true", help="use 99damage match url")
url_group.add_argument("-t", "--team", action="store_true", help="use 99damage team url")
print_group.add_argument("-c", "--csv", action="store_true", help="print output as csv")
print_group.add_argument("-p", "--print", action="store_true", help="print output as readable list")
args		= parser.parse_args()

header_99 = {
	"User-Agent":					"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
	"Accept":						"*/*",
	"Accept-Language":				"en-US,en",
	"Accept-Encoding":				"gzip, deflate, br",
	"Content-Type":					"application/x-www-form-urlencoded; charset=UTF-8",
	"X-Requested-With":				"XMLHttpRequest",
	"Origin":						"https://liga.99damage.de",
	"DNT":							"1",
	"Connection":					"keep-alive",
	"Referer":						url_99,
	"Sec-Fetch-Dest":				"empty",
	"Sec-Fetch-Mode":				"cors",
	"Sec-Fetch-Site":				"same-origin",
	"Cache-Control":				"max-age=0",
	"TE":							"trailers"
}

header_ff = {
	"authority":					"faceitfinder.com",
	"sec-ch-ua":					"Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"97\", \"Chromium\";v=\"97\"",
	"sec-ch-ua-mobile":				"?0",
	"sec-ch-ua-platform":			"Windows",
	"upgrade-insecure-requests":	"1",
	"dnt":							"1",
	"user-agent":					"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
	"accept":						"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
	"sec-fetch-site":				"same-origin",
	"sec-fetch-mode":				"navigate",
	"sec-fetch-user":				"?1",
	"sec-fetch-dest":				"document",
	"accept-language":				"en,en-US"
}

class Maps(Enum):
	__order__ = "de_dust2 de_inferno de_nuke de_mirage de_overpass de_vertigo de_ancient"
	de_dust2		= 88
	de_inferno		= 90
	de_nuke			= 91
	de_mirage		= 94
	de_overpass		= 295
	de_vertigo		= 417
	de_ancient		= 454

class Player:
	def __init__(self, name_99, id_steam, name_steam = None, vac_ban = None, game_ban = None, faceit_elo = None, faceit_kd = None, faceit_rating = None, faceit_matches = None):
		self.name_99			= name_99
		self.id_steam			= id_steam
		self.name_steam			= name_steam
		self.vac_ban			= vac_ban
		self.game_ban			= game_ban
		self.faceit_elo			= faceit_elo
		self.faceit_kd			= faceit_kd
		self.faceit_rating		= faceit_rating
		self.faceit_matches		= faceit_matches

class PickBan:
	def __init__(self, team, action, map):
		self.team	= team
		self.action	= action
		self.map	= map

class Team:
	def __init__(self, name, final_score = None, map1_score = None, map2_score = None, team_players = None):
		self.name				= name
		self.final_score		= final_score
		self.map1_score			= map1_score
		self.map2_score			= map2_score
		self.players			= team_players

def findPlayer(id_steam):
	for idx, player in enumerate(players):
		if player.id_steam == id_steam:
			return idx

def steamid_to_64bit(steamid):
	steam64id = 76561197960265728
	id_split = steamid.split(":")
	steam64id += int(id_split[2]) * 2
	if id_split[1] == "1":
		steam64id += 1
	return steam64id

def get99Response():
	if "99damage" not in url_99 and "teams" not in url_99:
		if "99damage" not in url_99 and "matches" not in url_99:
			print("invalid url")
			exit()
	else:
		if args.team:
			result_99 = requests.get(url_99)
		elif args.match:
			result_99 = requests.post("https://liga.99damage.de/ajax/leagues_match", headers = header_99, params =
			{
				"id":			url_99.split("/")[5].split("-")[0],
				"action":		"init",
				"devmode":		"1",
				"language":		"de"
			})
			return result_99.text
		return(BeautifulSoup(result_99.text, "html.parser"))

def getTeamInfo():
	teamnames = get99Response().find_all("section", "league-team-members")[0].find_all("div", "section-content")[0].find_all("ul", "content-portrait-grid-l")[0].find_all("li")
	for item in teamnames:
		players.append(Player(item.find_all("h3")[0].string, item.find_all("span")[0].string))
		getFaceitInfo(item.find_all("span")[0].string)
		getBanInfo(item.find_all("span")[0].string)

def getMatchInfo():
	team_response = json.loads(get99Response())
	for team in team_response["lineups"].values():
		for user in team:
			players.append(Player(user["name"], "".join(user["gameaccounts"])))
			getFaceitInfo("".join(user["gameaccounts"]))
			getBanInfo("".join(user["gameaccounts"]))
	html_match = BeautifulSoup(requests.get(url_99).text, "html.parser")
	scores = html_match.find_all("div", "content-match-head content-league-match-head")[0].find_all("div", "txt-info")[0].string
	map1 = scores.split("/")[0]
	map2 = scores.split("/")[1]

	teams.append(Team(team_response["draft_opp1"], team_response["score_1"], map1.split(":")[0], map2.split(":")[0], players[:5]))
	teams.append(Team(team_response["draft_opp2"], team_response["score_2"], map1.split(":")[1], map2.split(":")[1],players[5:]))
	
	pick_ban.append(PickBan(teams[0].name, "ban", Maps(team_response["draft_mapvoting_bans"][0]).name))
	pick_ban.append(PickBan(teams[1].name, "ban", Maps(team_response["draft_mapvoting_bans"][1]).name))
	pick_ban.append(PickBan(teams[1].name, "ban", Maps(team_response["draft_mapvoting_bans"][2]).name))
	pick_ban.append(PickBan(teams[0].name, "ban", Maps(team_response["draft_mapvoting_bans"][3]).name))
	pick_ban.append(PickBan(teams[1].name, "pick", Maps(team_response["draft_mapvoting_picks"][0]).name))
	pick_ban.append(PickBan(teams[0].name, "pick", Maps(team_response["draft_mapvoting_picks"][1]).name))

	for map in Maps:
		if not any(x for x in pick_ban if x.map == map.name):
			pick_ban.append(PickBan("defban", "ban", map.name))

def getFaceitInfo(id_steam):
	result_ff = requests.get(url_ff + str(steamid_to_64bit(id_steam)), headers = header_ff)
	html_ff = BeautifulSoup(result_ff.text, "html.parser")
	player_idx = findPlayer(id_steam)
	try:
		if html_ff.find_all("div", "account-container")[0].find_all("strong")[0].string == "Players not found!":
			players[player_idx].faceit_elo		= "No faceit account"
			players[player_idx].faceit_kd		= "No faceit account"
			players[player_idx].faceit_rating	= "No faceit account"
			players[player_idx].faceit_matches	= "No faceit account"
	except:
		html_ff_stats = html_ff.find_all("div", style="max-width: 900px;margin: 0 auto;")[0].find_all("div", "stats_totals_block_wrapper")
		try:
			elo		= html_ff.find_all("span", "stats_profile_elo_span")[0].string
		except:
			elo		= "ERROR"
		try:
			kd		= html_ff_stats[0].find_all("span", "stats_totals_block_main_value_span")[0].string
		except:
			kd		= "ERROR"
		try:
			rating	= html_ff_stats[2].find_all("span", "stats_totals_block_main_value_span")[0].string
		except:
			rating	= "ERROR"
		try:
			matches	= html_ff_stats[5].find_all("span", "stats_totals_block_main_value_span")[0].string
		except:
			matches	= "ERROR"
		players[player_idx].faceit_elo		= elo
		players[player_idx].faceit_kd		= kd
		players[player_idx].faceit_rating	= rating
		players[player_idx].faceit_matches	= matches

def getBanInfo(id_steam):
	result_vl = requests.get(url_vl + str(steamid_to_64bit(id_steam)))
	if result_vl.text == "Not Found":
		players[findPlayer(id_steam)].name_steam	= "Server Error"
		players[findPlayer(id_steam)].vac_ban		= "Server Error"
		players[findPlayer(id_steam)].game_ban		= "Server Error"
	else:
		json_vl = json.loads(result_vl.text)
		players[findPlayer(id_steam)].name_steam	= json_vl["personaname"]
		players[findPlayer(id_steam)].vac_ban		= json_vl["vac_bans"]
		players[findPlayer(id_steam)].game_ban		= json_vl["game_bans"]

def printCsv():
	f = StringIO()
	csv_w = csv.writer(f, delimiter = ";", quotechar = '"', quoting = csv.QUOTE_MINIMAL)
	if args.match:
		csv_w.writerow([str(teams[0].name), "", str(teams[1].name)])
		csv_w.writerow([str(teams[0].final_score), "", str(teams[1].final_score)])
		csv_w.writerow("\n")
		for item in pick_ban:
			csv_w.writerow([str(item.team), str(item.action), str(item.map)])
		csv_w.writerow("\n")
		csv_w.writerow([str(teams[0].map1_score), str(pick_ban[4].map), str(teams[1].map1_score)])
		csv_w.writerow([str(teams[0].map2_score), str(pick_ban[5].map), str(teams[1].map2_score)])
		csv_w.writerow("\n\n")
	csv_w.writerow(["99name","steamid","steamname","vacban","gameban","faceitelo","faceitkd","hltvrating","matches"])
	for idx, player in enumerate(players):
		if args.match:
			if idx == 0:
				csv_w.writerow([str(teams[0].name)])
			if idx == 5:
				csv_w.writerow("\n\n")
				csv_w.writerow([str(teams[1].name)])
		csv_w.writerow([str(player.name_99),
							str(player.id_steam),
							str(player.name_steam),
							str(player.vac_ban),
							str(player.game_ban),
							str(player.faceit_elo),
							str(player.faceit_kd),
							str(player.faceit_rating),
							str(player.faceit_matches)])
	print(f.getvalue())

def printOut():
	if args.match:
		print(str(teams[0].name) + " " + str(teams[1].name))
		print(str(teams[0].final_score) + " " + str(teams[1].final_score))
		print("\n")
		for item in pick_ban:
			print(str(item.team) + " " + str(item.action) + " " + str(item.map))
		print("\n")
		print(str(teams[0].map1_score) + " " + str(pick_ban[4].map) + " " + str(teams[1].map1_score))
		print(str(teams[0].map2_score) + " " + str(pick_ban[5].map) + " " + str(teams[1].map2_score))
		print("\n\n")
	for idx, player in enumerate(players):
		if args.match:
			if idx == 0:
				print(str(teams[0].name))
			if idx == 5:
				print("\n\n")
				print(str(teams[1].name))
		print("###########################################")
		print("99name :\t" + str(player.name_99))
		print("steamid:\t" + str(player.id_steam))
		print("steamname:\t" + str(player.name_steam))
		print("vacban :\t" + str(player.vac_ban))
		print("gameban:\t" + str(player.game_ban))
		print("faceitelo:\t" + str(player.faceit_elo))
		print("faceitkd:\t" + str(player.faceit_kd))
		print("hltv rating:\t" + str(player.faceit_rating))
		print("matches:\t" + str(player.faceit_matches))

if args.match:
	url_99 = input("enter 99damage match url: ")
	getMatchInfo()
if args.team:
	url_99 = input("enter 99damage team url: ")
	getTeamInfo()
if args.csv:
	printCsv()
if args.print:
	printOut()
