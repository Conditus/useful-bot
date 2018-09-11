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
