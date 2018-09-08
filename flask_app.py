#!/usr/bin/env python
from flask import Flask, json, request
import pandas as pd
import datetime
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
		"!schedule","!расписание"
		]

path = "http://www.ifmo.ru/ru/schedule/0/{}/schedule.htm"
group = "w3205"

weekdays_names = {
	"пн" : "1day",
	"вт" : "2day",
	"ср" : "3day",
	"чт" : "4day",
	"пт" : "5day",
	"сб" : "6day",
	"вс" : "7day"
}

weekdays_numbers = {
	"0" : "1day",
	"1" : "2day",
	"2" : "3day",
	"3" : "4day",
	"4" : "5day",
	"5" : "6day"
}

isWeekOdd = {
	"чётная":False,
	"нечётная":True,
	"четная":False,
	"нечетная":True
}

weekday_template = r"пн|вт|ср|чт|пт|сб|вс"																# weekdays template	
is_command = r"[!]\S*"																					# a command template
api_request_string = "https://api.vk.com/method/{}"														# default request string
request_params = {																						# dict of required params for request
		"group_id":group_id,			# group id
		"access_token":token,			# group access token
		"v":api_version					# VK api version
	}

def test(bot_request):
	schedule = "\n"
	subjectsList = []
	no_keywords_message = "Используй :\n!расписание <группа> <Пн/Вт/Ср/Чт/Пт/Сб>"
	# no_keywords_message = "Используй :\n!расписание <группа> [завтра] [чётный/нечётный/четный/нечетный] [Пн/Вт/Ср/Чт/Пт/Сб] [дд.мм.гггг]"
	weekOdd = isWeekOdd["нечетная"]
	schedule = "\n"
	subjectsList = []
	try:
		group = re.search(r'[ABKOPXUVMNCTWLYZ]\d{4}\D?', bot_request, flags=re.IGNORECASE)[0].rstrip()
	except TypeError:
		pass
	request_list = bot_request.split()
	request_list.remove("!расписание")
	if (len(request_list) == 0):
		request_params["message"] = no_keywords_message
	else:
		request_list.remove(group)
		if ("завтра" in request_list):
			day = weekdays_numbers[str(datetime.datetime.today().weekday())]
			request_list.remove("завтра")
		else:
			day = re.search(weekday_template, request_list[0])[0]
		r = requests.get("http://www.ifmo.ru/ru/schedule/0/{}/schedule.htm".format(group.upper())).text
		r = '<tbody><tr><th class="today day">'.join(r.split('<tbody><th class="today day">'))
		r = '<tbody><tr><th class="day">'.join(r.split('<tbody><th class="day">'))
		try:
			tables = pd.read_html(r, attrs={"id": "{}".format(weekdays_names[day])})
			for place, subj in zip(tables[0][1],tables[0][3]):
				if type(place) != float:
					subjectsList.append("⚠"+str(place)+"; "+str(subj))
			print("Расписание группы {} на {}: \n{}".format(group.upper(), day, schedule.join(subjectsList)))
		except ValueError:
			print("Расписание не найдено 😓")

# test("!расписание w3205 ср")

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

def reactions(bot_request):
	if ("блять" in bot_request):
		request_params["message"] = "Вообще-то, правильно будет бляДь"
	elif ("похуй" in bot_request):
		request_params["message"] = "Мне тоже!"

def mention(response_data):
	mention_list = []
	request_params["peer_id"] = response_data["object"]["peer_id"]
	request_params["fields"] = "id, first_name"
	users = json.loads(requests.get(api_request_string.format("messages.getConversationMembers"), params = request_params).content)
	users = users["response"]["profiles"]
	for user in users:
		mention_list.append("{}({})".format(user["id"],user["first_name"]))
	request_params["message"] = ", @id".join(map(lambda id:str(id),mention_list))
	request_params["message"] = "@id{}".format(request_params["message"])

def schedule(bot_request, response_data):
	no_keywords_message = "Используй :\n!расписание <группа> <Пн/Вт/Ср/Чт/Пт/Сб>"
	# no_keywords_message = "Используй :\n!расписание <группа> [завтра] [чётный/нечётный/четный/нечетный] [Пн/Вт/Ср/Чт/Пт/Сб] [дд.мм.гггг]"
	weekOdd = isWeekOdd["нечетная"]
	schedule = "\n"
	subjectsList = []
	try:
		group = re.search(r'[ABKOPXUVMNCTWLYZ]\d{4}\D?', bot_request, flags=re.IGNORECASE)[0].rstrip()
	except TypeError:
		pass
	request_list = bot_request.split()
	request_list.remove("!расписание")
	if (len(request_list) == 0):
		request_params["message"] = no_keywords_message
	else:
		request_list.remove(group)
		if ("завтра" in request_list):
			day = weekdays_numbers[str(datetime.datetime.today().weekday())]
			request_list.remove("завтра")
		else:
			day = re.search(weekday_template, request_list[0])[0]
		r = requests.get("http://www.ifmo.ru/ru/schedule/0/{}/schedule.htm".format(group.upper())).text
		r = '<tbody><tr><th class="today day">'.join(r.split('<tbody><th class="today day">'))
		r = '<tbody><tr><th class="day">'.join(r.split('<tbody><th class="day">'))
		try:
			tables = pd.read_html(r, attrs={"id": "{}".format(weekdays_names[day])})
			for place, subj in zip(tables[0][1],tables[0][3]):
				if type(place) != float:
					subjectsList.append("⚠"+str(place)+"; "+str(subj))
			request_params["message"] = "Расписание группы {} на {}: \n{}".format(group.upper(), day, schedule.join(subjectsList))
		except ValueError:
			request_params["message"] = "Расписание не найдено 😓"

def commands(bot_request, response_data):
	if (re.search(is_command, bot_request)[0] not in commads_list):										# finding a command in command list by RegExp
		request_params["message"] = "Неизвестная команда!(Unknown command!)"
	elif (bot_request == "!getconv" or bot_request == "!дай ид конфы"):									# asking bot about conversation id
		request_params["message"] = "Conversetion id is : {}".format(data["object"]["peer_id"])
	elif (bot_request == "!everyone" or bot_request == "!все"):											# mentioning everyone at conversation
		mention(response_data)
	elif (bot_request == "!ping" or bot_request == "!пинг"):											# pinging bot to test is it alive
		request_params["message"] = "Pong!"
	elif (re.search(is_command, bot_request)[0] == "!расписание"):
		schedule(bot_request, response_data)

@app.route("/", methods=["POST"])
def processing():
	data = json.loads(request.data)																		# loading POST-data into json structure
	if ("type" not in data):																			# if no from vk - return deny-string
		return "not vk"
	if (data["type"] == "confirmation"):																# if want to confirm - return confirmation string
		return confirmation_token
	elif (data["type"] == "message_new"):																# if got a message - answer
		bot_request = data["object"]["text"].lower()													# lowercasing message
		request_params["peer_id"] = data["object"]["peer_id"]											# adding a dialog id to request dict
		if (bot_request[0] != "!"):
			reactions(bot_request)
		else:
			commands(bot_request, data)
		# requests.get(api_request_string.format("messages.send"), params = request_params)
		requests.post(api_request_string.format("messages.send"), data = request_params)

	return "ok"