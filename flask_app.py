# coding: utf-8
#!/usr/bin/env python
from flask import Flask, json, request
import pandas
import datetime
import requests
import regex as re


#----------------------------- A list of usable commands -----------------------------#
commandsList = [
        "!ping","!пинг",
        "!everyone","!все",
        "!getconv","!дай ид конфы",
        "!schedule","!расписание",
        "!setdefault","!настройка"
]

apiRequestString = "https://api.vk.com/method/{}"

with open("/home/Veritaris/mysite/settings.json", "r") as SD:
        serverData = json.load(SD)
serverInfo = serverData["serverInfo"]
reactionsList = serverData["reactionsList"]
requestParams = {
        "group_id":serverInfo["groupID"],
        "access_token":serverInfo["accessToken"],
        "v":serverInfo["apiVersion"]
}

app = Flask(__name__)
@app.route("/", methods=["POST"])

def processing():
    requestData = json.loads(request.data)

# ---------------------------------- Initialising server data every time when message got ------------------------------
    with open("/home/Veritaris/mysite/settings.json", "r") as SD:
        serverData = json.load(SD)
    serverInfo = serverData["serverInfo"]
    reactionsList = serverData["reactionsList"]

    if ("type" not in requestData):
        return "not vk"

    if (requestData["type"] == "confirmation"):
        return serverInfo["confirmationToken"]

    elif (requestData["type"] == "message_new"):
        botRequest = requestData["object"]["text"].lower()
        requestParams["peer_id"] = requestData["object"]["peer_id"]
        if (botRequest[0] != "!"):
            if(reactions(botRequest, reactions)):
                requests.post(apiRequestString.format("messages.send"), data = requestParams)
        else:
            commands(botRequest, requestData, serverData)
            requests.post(apiRequestString.format("messages.send"), data = requestParams)
    return "ok"

def commands(botRequest, responseData, serverData):
    if (re.search(serverData["templates"]["isCommand"], botRequest)[0] not in commandsList):
        requestParams["message"] = "Неизвестная команда!(Unknown command!)"

    elif (botRequest == "!getconv" or botRequest == "!дай ид конфы"):
        requestParams["message"] = "Conversetion id is : {}".format(responseData["object"]["peer_id"])

    elif (botRequest == "!everyone" or botRequest == "!все"):
        mention(responseData)

    elif (botRequest == "!ping" or botRequest == "!пинг"):
        requestParams["message"] = "Pong!"

    elif (re.search(serverData["templates"]["isCommand"], botRequest)[0] == "!расписание"):
        schedule(botRequest, responseData, serverData)

    elif (re.search(serverData["templates"]["isCommand"], botRequest)[0] == "!настройка"):
        changeSettings(botRequest, responseData, serverData)

def reactions(botRequest, reactions):
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

def changeSettings(botRequest, responseData, serverData):
    noKeywordsMessage = "Используй: \n!настройка <[команда для настройки] либо ['список']> <параметры настройки>"
    scheduleSettingsMessage = """🔧Настройка для команды !расписание: \n!настройка !расписание <группа> -
    сохранить <группа> для текущей беседы"""
    everyoneSettingsMessage = """🔧Настройка для команды !все: \n!настройка !все кроме : <список Имя Фамилия через
    запятую>"""
    requestList = botRequest.split()
    requestList.remove("!настройка")
    if (len(requestList) == 0):
        requestParams["message"] = noKeywordsMessage
    elif (botRequest == "!настройка список"):
        requestParams["message"] = "{} \n{}".format(scheduleSettingsMessage, everyoneSettingsMessage)
    elif (botRequest == "!настройка !расписание"):
        requestParams["message"] = scheduleSettingsMessage
    elif (botRequest == "!настройка !все"):
        requestParams["message"] = everyoneSettingsMessage
    else:
        if ("!расписание" in requestList):
            requestList.remove("!расписание")
            group = str(requestList[0])
            if (group not in list(serverData["convsWithGroups"].keys())):
                conversationID = responseData["object"]["peer_id"]
                serverData["convsWithGroups"]["{}".format(conversationID)] = str(group.upper())
                with open("/home/Veritaris/mysite/settings.json", "w") as SD:
                    json.dump(serverData, SD)
                requestParams["message"] = "Настройка успешно сохранена!\nТеперь можно использовать \"!расписание <день>\""


def mention(responseData):
    mention_list = []
    requestParams["peer_id"] = responseData["object"]["peer_id"]
    requestParams["fields"] = "id, first_name"
    users = json.loads(requests.get(apiRequestString.format("messages.getConversationMembers"),
            params = requestParams).content)
    users = users["response"]["profiles"]
    for user in users:
        mention_list.append("{}({})".format(user["id"],user["first_name"]))
    requestParams["message"] = ", @id".join(map(lambda id:str(id),mention_list))
    requestParams["message"] = "@id{}".format(requestParams["message"])

def schedule(botRequest, responseData, serverData):
    noKeywordsMessage = "Используй:\n!расписание <группа> <Пн/Вт/Ср/Чт/Пт/Сб>"
    # no_keywords_message = "Используй :\n!расписание <группа> [завтра] [чётный/нечётный/четный/нечетный] [Пн/Вт/Ср/Чт/Пт/Сб] [дд.мм.гггг]"
    schedule = "\n"
    subjectsList = []
    requestList = botRequest.split()
    requestList.remove("!расписание")
    try:
        group = re.search(r'[ABKOPXUVMNCTWLYZ]\d{4}\D?', botRequest, flags = re.IGNORECASE)[0].rstrip()
    except TypeError:
        try:
            conversationID = str(responseData["object"]["peer_id"])
            if (conversationID in list(serverData["convsWithGroups"].keys())):
                group = serverData["convsWithGroups"]["{}".format(conversationID)]
                requestList.append(group)
        except TypeError:
            pass
    if (len(requestList) == 0):
        requestParams["message"] = noKeywordsMessage
    else:
        requestList.remove(group)
        if ("завтра" in requestList):
            day = serverData["weeksData"]["weekdaysNumbers"][str(datetime.datetime.today().weekday())]
            requestList.remove("завтра")
        elif ("сегодня" in requestList):
            day = serverData["weeksData"]["weekdaysNumbers"][str(datetime.datetime.today().weekday() - 1)]
            requestList.remove("сегодня")
        else:
            day = re.search(serverData["templates"]["weekdayTemplate"], requestList[0])[0]
        r = requests.get("http://www.ifmo.ru/ru/schedule/0/{}/schedule.htm".format(group.upper())).text
        r = '<tbody><tr><th class="today day">'.join(r.split('<tbody><th class="today day">'))
        r = '<tbody><tr><th class="day">'.join(r.split('<tbody><th class="day">'))
        try:
            tables = pandas.read_html(r, attrs = {"id": "{}".format(serverData["weeksData"]["weekdaysNames"][day])})
            for place, subj in zip(tables[0][1], tables[0][3]):
                if type(place) != float:
                    subjectsList.append("⚠"+str(place)+"; "+str(subj))
            requestParams["message"] = "Расписание группы {} на {}: \n{}".format(group.upper(), day, schedule.join(subjectsList))
        except ValueError:
            requestParams["message"] = "Расписание не найдено 😓"

