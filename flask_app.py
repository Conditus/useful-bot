# coding: utf-8
#!/usr/bin/env python
from flask import Flask, json, request
import pandas
import datetime
import requests
import regex as re
import rsa
import time


def getEncryptedValue(keyName):
    with open("/home/Veritaris/mysite/encryptedData/{}/{}.privatekey".format(keyName, keyName), mode = 'rb') as privatefile:
        keydata = privatefile.read()
    PrivateKey = rsa.PrivateKey.load_pkcs1(keydata)
    with open("/home/Veritaris/mysite/encryptedData/{}/{}.publikkey".format(keyName, keyName), mode = 'rb') as pubfile:
        keydata = pubfile.read()
    PublicKey = rsa.PublicKey.load_pkcs1(keydata)
    with open("/home/Veritaris/mysite/encryptedData/{}/{}.encoded".format(keyName, keyName), "rb") as keyFile:
        key = str(rsa.decrypt(keyFile.read(), PrivateKey).decode())
    return key

secretKey = getEncryptedValue("secretKey")
accessToken = getEncryptedValue("accessToken")
confirmationToken = getEncryptedValue("confirmationToken")

##  ##     ####      ##     ##
##  ##    ##  ##     ##  ## ##
##  ##    ##  ##     ###### ##
 ####     ##  ##         ## ##
  ##       ####  ##      ## ######

#----------------------------- A list of usable commands -----------------------------#
commandsList = [
        "!ping","!пинг",
        "!everyone","!все",
        "!getconv","!дай ид конфы",
        "!schedule","!расписание", 
        "!setdefault","!настройка",
        "!groupcreate","!группасоздать",
        "!groups","!группы"
]

restrictedGroupNamesList = [
    "group","групп"
]

apiRequestString = "https://api.vk.com/method/{}"

with open("/home/Veritaris/mysite/serverData/serverSettings.json", "r") as serverSettingsFile:
    serverSettings = json.load(serverSettingsFile)  
serverInfo = serverSettings["serverInfo"]
reactionsList = serverSettings["reactionsList"]

requestParams = {
        "group_id":serverInfo["groupID"],
        "access_token":accessToken,
        "v":serverInfo["apiVersion"]
}

app = Flask(__name__)
@app.route("/", methods=["POST"])

def processing():
    requestData = json.loads(request.data)
    requestData["secret"].encode()
    if (secretKey == requestData["secret"]):
        with open("/home/Veritaris/mysite/serverData/serverSettings.json", "r") as serverSettingsFile:
            serverSettings = json.load(serverSettingsFile)
        serverInfo = serverSettings["serverInfo"]
        reactionsList = serverSettings["reactionsList"]

        if ("type" not in requestData):
            return "not vk"

        elif (requestData["type"] == "confirmation"): 
            return confirmationToken

        elif (requestData["type"] == "message_new"):
            if (requestData["object"]["text"] != ""):
                botRequest = requestData["object"]["text"].lower()                                                      # contains full text message
                requestParams["peer_id"] = requestData["object"]["peer_id"]                                             # id of message sender
                unixtime = requestData["object"]["date"]                                                                # UNIXTIME of message
                if (("server:prod" in requestData["object"]["text"]) or ("s:p" in requestData["object"]["text"])):
                    pass
                else:
                    botRequest = botRequest.replace(" s:p", "")                                                
                    if (botRequest[0] != "!"):
                        if(reactions(botRequest, reactions)):
                            requests.post(apiRequestString.format("messages.send"), data = requestParams)
                    else:
                        commands(botRequest, requestData, serverSettings, unixtime)
                        requests.post(apiRequestString.format("messages.send"), data = requestParams)
        return "ok"
    else:
        return "Пошёл нахуй отсюдова!"

def commands(botRequest, responseData, serverSettings, unixtime):
    with open("/home/Veritaris/mysite/serverData/subGroups.json", "r") as subGroupsFile:
        subGroupsJSON = json.load(subGroupsFile)
        subGroups = subGroupsJSON["{}".format(responseData["object"]["peer_id"])]

    if (botRequest == "!getconv" or botRequest == "!дай ид конфы"):
        requestParams["message"] = "Conversetion id is : {}".format(responseData["object"]["peer_id"])

    elif (botRequest == "!everyone" or botRequest == "!все"):
        mention(responseData)

    elif (botRequest == "!ping" or botRequest == "!пинг"):
        timeDelta = (datetime.datetime.now()-datetime.datetime.fromtimestamp(unixtime)).total_seconds()
        requestParams["message"] = "Pong! {}s".format(timeDelta)

    elif (re.search(serverSettings["templates"]["isCommand"], botRequest)[0] == "!расписание"):
        schedule(botRequest, responseData, serverSettings)

    elif (re.search(serverSettings["templates"]["isCommand"], botRequest)[0] == "!наsстройка"):
        changeSettings(botRequest, responseData, serverSettings)

    elif (re.search(serverSettings["templates"]["groupsEn"], botRequest) != None):
        if (re.search(serverSettings["templates"]["groupsEn"], botRequest)[0] == "!groupcreate"):
            conversationSubgroupsCreate(botRequest, responseData, restrictedGroupNamesList)

    elif (re.search(serverSettings["templates"]["groupsRu"], botRequest) != None):
        if (re.search(serverSettings["templates"]["groupsRu"], botRequest)[0] == "!группасоздать"):
            conversationSubgroupsCreate(botRequest, responseData, restrictedGroupNamesList)

    elif (botRequest == "!группы"):
        returnGroupsList(list(subGroups.keys()))

    elif (botRequest == "!groups"):
        returnGroupsList(list(subGroups.keys()))

    elif (any(subGroup in botRequest for subGroup in subGroups.keys())):
        subGroupMention(botRequest, subGroups, responseData)

    elif (re.search(serverSettings["templates"]["isCommand"], botRequest)[0] not in commandsList):
        requestParams["message"] = "Неизвестная команда!(Unknown command!)"

def reactions(botRequest, reactions):
    isReaction = False
    if ("похуй" in botRequest):
        requestParams["message"] = "Мне тоже!"
        isReaction = True
    if ("дай деняк" in botRequest):
        requestParams["message"] = "И мне!"
        isReaction = True
    return isReaction

def changeSettings(botRequest, responseData, serverSettings):
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
            with open("/home/Veritaris/mysite/serverData/serverData/convGroups.json", "r") as convGroupsFile:
                convGroups = json.load(convGroupsFile)
            requestList.remove("!расписание")
            group = str(requestList[0])
            if (group not in list(convGroups.keys())):
                conversationID = responseData["object"]["peer_id"]
                convGroups["{}".format(conversationID)] = str(group.upper())
                with open("/home/Veritaris/mysite/serverData/convGroups.json", "w") as convGroupsFile:
                    json.dump(convGroups, convGroupsFile)
                requestParams["message"] = """Настройка успешно сохранена!\nТеперь можно использовать 
                \"!расписание <день>\""""

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

def schedule(botRequest, responseData, serverSettings):
    noKeywordsMessage = "Используй:\n!расписание <группа> <Пн/Вт/Ср/Чт/Пт/Сб>"
    # To realise:
    # no_keywords_message = "Используй :\n!расписание <группа> [завтра] [чётный/нечётный/четный/нечетный] [Пн/Вт/Ср/Чт/Пт/Сб] [дд.мм.гггг]"
    schedule = "\n"
    subjectsList = []
    with open("/home/Veritaris/mysite/convGroups.json", "r") as convGroupsFile:
        convGroups = json.load(convGroupsFile)
    requestList = botRequest.split()
    requestList.remove("!расписание")
    try:
        group = re.search(r'[ABKOPXUVMNCTWLYZ]\d{4}\D?', botRequest, flags = re.IGNORECASE)[0].rstrip()
    except TypeError:
        try:
            conversationID = str(responseData["object"]["peer_id"])
            if (conversationID in list(convGroups.keys())):
                group = convGroups["{}".format(conversationID)]
                requestList.append(group)
        except TypeError:
            requestParams["message"] = "Группа"
    if (len(requestList) == 0):
        requestParams["message"] = noKeywordsMessage
    else:
        try:
            requestList.remove(group)
            if ("завтра" in requestList):
                day = serverSettings["weeksData"]["weekdaysNumbers"][str(datetime.datetime.today().weekday() + 1)]
                requestList.remove("завтра")
            elif ("сегодня" in requestList):
                day = serverSettings["weeksData"]["weekdaysNumbers"][str(datetime.datetime.today().weekday())]
                requestList.remove("сегодня")
            else:
                day = re.search(serverSettings["templates"]["weekdayTemplate"], requestList[0])[0]
            r = requests.get("http://www.ifmo.ru/ru/schedule/0/{}/schedule.htm".format(group.upper())).text
            r = '<tbody><tr><th class="today day">'.join(r.split('<tbody><th class="today day">'))
            r = '<tbody><tr><th class="day">'.join(r.split('<tbody><th class="day">'))
            try:
                tables = pandas.read_html(r, attrs = {"id": "{}".format(serverSettings["weeksData"]["weekdaysNames"][day])})
                for place, subj in zip(tables[0][1], tables[0][3]):
                    if type(place) != float:
                        subjectsList.append("⚠"+str(place)+"; "+str(subj))
                requestParams["message"] = "Расписание группы {} на {}: \n{}".format(group.upper(), day, schedule.join(subjectsList))
            except ValueError:
                requestParams["message"] = "Расписание не найдено 😓"
        except UnboundLocalError:
            pass

def conversationSubgroupsCreate(botRequest, responseData, restrictedGroupNamesList):
    if ("!группасоздать" in botRequest):
        botRequest = botRequest.replace("!группасоздать", "")
    else:
        botRequest = botRequest.replace("!groupcreate", "")
    with open("/home/Veritaris/mysite/serverData/subGroups.json", "r") as subGroupsFile:
        subGroups = json.load(subGroupsFile)                                                                            # getting a JSON of all groups and conversation relatives
    conversationID = responseData["object"]["peer_id"]                                                                  # taking a conversation ID from message command
    creatorID = responseData["object"]["from_id"]                                                                       # getting id of group creator
    try:                                                                                                                # get subgroups dict if at least one exists, new dict otherwise
        subGroupsDict = subGroups["{}".format(conversationID)]                                                          # getting groups dict for conversation with set ID
    except KeyError:
        subGroupsDict = {}
    groupList = botRequest.split(" ")
    groupList.remove("")
    groupName = groupList.pop(0)
    if (len(groupList) != 0) and (True):
        if not (any(restrictedName == groupName for restrictedName in restrictedGroupNamesList)):
            subGroup = {}
            subGroup["groupName"] = str(groupName)
            subGroup["gropCreator"] = str(creatorID)
            subGroup["creationDate"] = str(time.mktime(datetime.datetime.now().timetuple()))
            subGroup["members"] = groupList
            subGroupsDict["{}".format(groupName)] = subGroup
            requestParams["message"] = "Группа {} успешно создана!".format(groupName)
            subGroups["{}".format(conversationID)] = subGroupsDict
            with open("/home/Veritaris/mysite/serverData/subGroups.json", "w") as subGroupsFile:
                json.dump(subGroups, subGroupsFile)
        else:
            requestParams["message"] = "⛔ Ошибка! Данное название группы недоступно!"
    else:
        requestParams["message"] = "⛔ Ошибка! В группе должно быть не менее двух участников!"

def subGroupMention(botRequest, subGroups, responseData):
    if (any(subGroup == botRequest[1:] for subGroup in subGroups.keys())):
        groupList = subGroups[botRequest[1:]]["members"]
        requestParams["message"] = ", @".join(map(lambda id:str(id), groupList))
        requestParams["message"] = "@{}".format(requestParams["message"])

def returnGroupsList(subGroupsJSON):
    groupsList = "\n".join(subGroupsJSON)
    requestParams["message"] = "Список групп:\n{}".format(groupsList)







