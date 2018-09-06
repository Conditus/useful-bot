from flask import Flask, json, request
import pandas as pd
import requests
import re

token = "9434682c67a5493b8f3aea4be18e961d456403bf57343f728ae13aa5348e28555a187c5d43e58a2afcd31"
confirmation_token = "45a1b7c1"
api_version = "5.84"
group_id = "170910335"

app = Flask(__name__)

commads_list = [
		"!ping","!пинг",
		"!everyone","!все",
		"!getConv","!дай ид конфы",
		# "!","!",
		]

path = "http://www.ifmo.ru/ru/schedule/0/{}/schedule.htm"
group = "w3205"

weekdays = {
	"пн" : "1day",
	"вт" : "2day",
	"ср" : "3day",
	"чт" : "4day",
	"пт" : "5day",
	"сб" : "6day"
}

isWeekOdd = {
	"чётная":False,
	"нечётная":True,
	"четная":False,
	"нечетная":True
}

@app.route("/", methods=["POST"])
def processing():
	is_command = r"[!]\S*"
	api_request_string = "https://api.vk.com/method/{}"															# default request string
	request_params = {																							# dict of required params for request
		"group_id":group_id,			# group id
		"access_token":token,			# group access token
		"v":api_version					# VK api version
	}	
	data = json.loads(request.data)																				# loading POST-data into json structure
	if ("type" not in data):																					# if no from vk - return deny-string
		return "not vk"
	if (data["type"] == "confirmation"):																		# if want to confirm - return confirmation string
		return confirmation_token
	elif (data["type"] == "message_new"):																		# if got a message - answer
		bot_request = data["object"]["text"].lower()															# lowercasing message
		request_params["peer_id"] = data["object"]["peer_id"]													# adding a dialog id to request dict
		if (bot_request[0] != "!"):
			if ("блять" in bot_request):																		# checking spelling
				request_params["message"] = "Вообще-то, правильно будет бляДь"
				requests.get(api_request_string.format("messages.send"), params = request_params)

			elif ("похуй" in bot_request):
				request_params["message"] = "Мне тоже!"
				requests.get(api_request_string.format("messages.send"), params = request_params)
		else:
			if (re.search(is_command, bot_request)[0] not in commads_list):										# finding a command in command list by RegExp
				request_params["message"] = "Неизвестная команда!(Unknown command!)"
				requests.get(api_request_string.format("messages.send"), params = request_params)

			elif (bot_request == "!getconv" or bot_request == "!дай ид конфы"):									# asking bot about conversation id
				request_params["message"] = "Conversetion id is : {}".format(data["object"]["peer_id"])
				requests.get(api_request_string.format("messages.send"), params = request_params)

			elif (bot_request == "!everyone" or bot_request == "!все"):											# mentioning everyone at conversation
				mention_list = []
				request_params["peer_id"] = data["object"]["peer_id"]
				request_params["fields"] = "id, first_name"
				users = json.loads(requests.get(api_request_string.format("messages.getConversationMembers"), params = request_params).content)
				users = users["response"]["profiles"]
				for user in users:
					mention_list.append("{}({})".format(user["id"],user["first_name"]))
				request_params["message"] = ", @id".join(map(lambda id:str(id),mention_list))
				request_params["message"] = "@id{}".format(request_params["message"])
				requests.get(api_request_string.format("messages.send"), params = request_params)

			elif (bot_request == "!ping" or bot_request == "!пинг"):							# pinging bot to test is it alive
				request_params["message"] = "Pong!"
				requests.get(api_request_string.format("messages.send"), params = request_params)

			elif (bot_request == "!schedule" or bot_request == "!расписание"):
				weekOdd = isWeekOdd["нечетная"]
				day = "вт"
				schedule = "\n"
				subjectsList = []

				r = requests.get("http://www.ifmo.ru/ru/schedule/0/{}/schedule.htm".format(group)).text
				r = '<tbody><tr><th class="day">'.join(r.split('<tbody><th class="day">'))
				tables = pd.read_html(r, attrs={"id": "{}".format(weekdays[day])})
				for place, subj in zip(tables[0][1],tables[0][3]):
					if type(place) != float:
						subjectsList.append(place+"; "+subj)
						# if ("ул.Ломоносова, д.9, лит. А" in place) :
						# 	place = place.replace("ул.Ломоносова, д.9, лит. А","")
						# if (weekOdd):
						# 	if ("нечетная неделя" in place) :
						# 		place = place.replace("нечетная неделя  ","")
						# 	if ("нечетная неделя" in subj) :
						# 		subj = subj.replace("нечетная неделя  ","")
						# 	subjectsList.append(place+"; "+subj)
						# else:
						# 	if ("четная неделя" in place) :
						# 		place = place.replace("четная неделя  ","")
						# 	if ("четная неделя" in subj) :
						# 		subj = subj.replace("четная неделя  ","")
						# 	subjectsList.append(place+"; "+subj)
				request_params["message"] = schedule.join(subjectsList)
				requests.get(api_request_string.format("messages.send"), params = request_params)
	return "ok"