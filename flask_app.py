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
confirmationToken = "45a1b7c1"
#----------------------------- Version of VKApi -----------------------------#
apiVersion = "5.84"
#----------------------------- Bot version -----------------------------#
botVersion = "0.3"
#----------------------------- The id of group -----------------------------#
groupId = "170910335"

#----------------------------- Dicts with weekdays -----------------------------#
weekdaysNames = {
    "пн" : "1day",
    "вт" : "2day",
    "ср" : "3day",
    "чт" : "4day",
    "пт" : "5day",
    "сб" : "6day",
    "вс" : "7day"
}

weekdaysNumbers = {
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
commandsList = [
        "!ping","!пинг",
        "!everyone","!все",
        "!getConv","!дай ид конфы",
        "!schedule","!расписание"
        ]

apiRequestString = "https://api.vk.com/method/{}"

requestParams = {
        "group_id":groupId,
        "access_token":token,
        "v":apiVersion
    }

weekdayTemplate = r"пн|вт|ср|чт|пт|сб|вс"
isCommand = r"[!]\S*"

app = Flask(__name__)
@app.route("/", methods=["POST"])

def processing():
    data = json.loads(request.data)
    if ("type" not in data):
        return "not vk"
    if (data["type"] == "confirmation"):
        return confirmationToken
    elif (data["type"] == "message_new"):
        botRequest = data["object"]["text"].lower()
        requestParams["peer_id"] = data["object"]["peer_id"]
        if (botRequest[0] != "!"):
            if(reactions(botRequest)):
                requests.post(apiRequestString.format("messages.send"), data = requestParams)
        else:
            commands(botRequest, data)
            requests.post(apiRequestString.format("messages.send"), data = requestParams)
    return "ok"

def commands(botRequest, responseData):
    if (re.search(isCommand, botRequest)[0] not in commandsList):
        requestParams["message"] = "Неизвестная команда!(Unknown command!)"

    elif (botRequest == "!getconv" or botRequest == "!дай ид конфы"):
        requestParams["message"] = "Conversetion id is : {}".format(responseData["object"]["peer_id"])

    elif (botRequest == "!everyone" or botRequest == "!все"):
        mention(responseData)

    elif (botRequest == "!ping" or botRequest == "!пинг"):
        requestParams["message"] = "Pong!"

    elif (re.search(isCommand, botRequest)[0] == "!расписание"):
        schedule(botRequest, responseData)

def reactions(botRequest):
    isReaction = False
    if ("блять" in botRequest):
        requestParams["message"] = "Вообще-то, правильно будет бляДь"
        isReaction = True
    if ("похуй" in botRequest):
        requestParams["message"] = "Мне тоже!"
        isReaction = True
    if ("дай деняк" in botRequest):
        requestParams["message"] = "И мне!"
        isReaction = True
    return isReaction

def mention(responseData):
    mention_list = []
    requestParams["peer_id"] = responseData["object"]["peer_id"]
    requestParams["fields"] = "id, first_name"
    users = json.loads(requests.get(apiRequestString.format("messages.getConversationMembers"), params = requestParams).content)
    users = users["response"]["profiles"]
    for user in users:
        mention_list.append("{}({})".format(user["id"],user["first_name"]))
    requestParams["message"] = ", @id".join(map(lambda id:str(id),mention_list))
    requestParams["message"] = "@id{}".format(requestParams["message"])

def schedule(botRequest, responseData):
    no_keywords_message = "Используй :\n!расписание <группа> <Пн/Вт/Ср/Чт/Пт/Сб>"
    # no_keywords_message = "Используй :\n!расписание <группа> [завтра] [чётный/нечётный/четный/нечетный] [Пн/Вт/Ср/Чт/Пт/Сб] [дд.мм.гггг]"
    weekOdd = isWeekOdd["нечетная"]
    schedule = "\n"
    subjectsList = []
    try:
        group = re.search(r'[ABKOPXUVMNCTWLYZ]\d{4}\D?', botRequest, flags=re.IGNORECASE)[0].rstrip()
    except TypeError:
        pass
    requestList = botRequest.split()
    requestList.remove("!расписание")
    if (len(requestList) == 0):
        requestParams["message"] = no_keywords_message
    else:
        requestList.remove(group)
        if ("завтра" in requestList):
            day = weekdaysNumbers[str(datetime.datetime.today().weekday())]
            requestList.remove("завтра")
        else:
            day = re.search(weekdayTemplate, requestList[0])[0]
        r = requests.get("http://www.ifmo.ru/ru/schedule/0/{}/schedule.htm".format(group.upper())).text
        r = '<tbody><tr><th class="today day">'.join(r.split('<tbody><th class="today day">'))
        r = '<tbody><tr><th class="day">'.join(r.split('<tbody><th class="day">'))
        try:
            tables = pandas.read_html(r, attrs={"id": "{}".format(weekdaysNames[day])})
            for place, subj in zip(tables[0][1],tables[0][3]):
                if type(place) != float:
                    subjectsList.append("⚠"+str(place)+"; "+str(subj))
            requestParams["message"] = "Расписание группы {} на {}: \n{}".format(group.upper(), day, schedule.join(subjectsList))
        except ValueError:
            requestParams["message"] = "Расписание не найдено 😓"

