#!/usr/bin/env python
from flask import Flask, json, request
import pandas
import datetime
import requests
import regex as re

# This is a server settings file

#------------------------------ An group-access token -----------------------------#
token = "d72481f00c65b68013d31f43a9cc4a7d8496ac4b7fd6ae2749e69b3fe5a8f575ce38cbaac8d9c4b55c81a"
#----------------------------- A token to confirm that server works normally -----------------------------#
confirmation_token = "45a1b7c1"
#----------------------------- Version of VKApi -----------------------------#
api_version = "5.84"
#----------------------------- Bot version -----------------------------#
bot_version = "0.3"
#----------------------------- The id of group -----------------------------#
group_id = "170910335"

#----------------------------- Dicts with weekdays -----------------------------#
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

#----------------------------- Boolean week -----------------------------#g
isWeekOdd = {
	"чётная":False,
	"нечётная":True,
	"четная":False,
	"нечетная":True,
	"чёт":False,
	"нечёт":True,
	"чет":False,
	"нечет":True
}

#----------------------------- A list of usable commands -----------------------------#
commads_list = [
		"!ping","!пинг",
		"!everyone","!все",
		"!getConv","!дай ид конфы",
		"!schedule","!расписание"
		]

weekday_template = r"пн|вт|ср|чт|пт|сб|вс"
is_command = "[!]\\S*"
api_request_string = "https://api.vk.com/method/{}"

request_params = {
		"group_id":group_id,
		"access_token":token,
		"v":api_version
	}

weekday_template = r"пн|вт|ср|чт|пт|сб|вс"
isCommand = r"[!]\S*"

app = Flask(__name__)
@app.route("/", methods=["POST"])

def processing():
	data = json.loads(request.data)
	if ("type" not in data):
		return "not vk"
	if (data["type"] == "confirmation"):
		return confirmation_token
	elif (data["type"] == "message_new"):
		bot_request = data["object"]["text"].lower()
		request_params["peer_id"] = data["object"]["peer_id"]
		if (bot_request[0] != "!"):
			if(reactions(bot_request)):
				requests.post(api_request_string.format("messages.send"), data = request_params)
		else:
			commands(bot_request, data)
			requests.post(api_request_string.format("messages.send"), data = request_params)
	return "ok"

def commands(bot_request, response_data):
	if (re.search(isCommand, bot_request)[0] not in commads_list):
		request_params["message"] = "Неизвестная команда!(Unknown command!)"

	elif (bot_request == "!getconv" or bot_request == "!дай ид конфы"):
		request_params["message"] = "Conversetion id is : {}".format(response_data["object"]["peer_id"])

	elif (bot_request == "!everyone" or bot_request == "!все"):
		mention(response_data)

	elif (bot_request == "!ping" or bot_request == "!пинг"):
		request_params["message"] = "Pong!"

	elif (re.search(isCommand, bot_request)[0] == "!расписание"):
		schedule(bot_request, response_data)

def reactions(bot_request):
	isReaction = False
	if ("блять" in bot_request):
		request_params["message"] = "Вообще-то, правильно будет бляДь"
		isReaction = True
	elif ("похуй" in bot_request):
		request_params["message"] = "Мне тоже!"
		isReaction = True
	return isReaction

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
			tables = pandas.read_html(r, attrs={"id": "{}".format(weekdays_names[day])})
			for place, subj in zip(tables[0][1],tables[0][3]):
				if type(place) != float:
					subjectsList.append("⚠"+str(place)+"; "+str(subj))
			request_params["message"] = "Расписание группы {} на {}: \n{}".format(group.upper(), day, schedule.join(subjectsList))
		except ValueError:
			request_params["message"] = "Расписание не найдено 😓"

