import telebot
import json
from datetime import date, timedelta


print("Start bot")
bot = telebot.TeleBot('7113688837:AAHyn6jpFYyySu8dEGuu0Go-lfndXFLUJ5Y')
Dialog_status = {} # СЛоварь для хранения статуса диалога (добавляет этапность диалога)

#функция сохранения диалога
def save_dialog(data): #получает json в котором хранится диалог с конкретным ЮЗЕРОМ
	Text = ""
	i=0
	for i in range(len(data)):
		buf = data[i] #Построчно читаем json попутно записывая в String сообщения (\n) перевод строки
		Text += "Human - " + buf["Human"] +"\n"+ "Bot - " + buf["Bot"] +"\n"
	with open("Result.txt", "w") as text_file:
		text_file.write(Text) #Сохраняем наш String в файлик


def informat_date_to_format(json_obj):
	informat_date = json_obj["date"].split(".")
	formated_date = (int(informat_date[2]), int(informat_date[1]), int(informat_date[0]))
	format_date = date(formated_date[0], formated_date[1], formated_date[2])
	return format_date



def auto_delete_deads():
	with open('file_dead.json') as file_dead:
		deads = json.load(file_dead) #считали весь джейсон с файла
	all_deads = deads.get("all_deads")
	user_deads = deads.get("user_deads")
	result_js = {} #,то, куда мы все будем перезаписывать
	new_all_deads = []
	for count in range(len(all_deads)):
		format_date = informat_date_to_format(all_deads[count]) #вызов функции котрая отформатиреут дату
		today = date.today()
		if today <= format_date:
			new_all_deads.append(all_deads[count]) #оставляем все даты котрые больше или равны сегодняшней
	result_js["all_deads"] = new_all_deads
	new_user_deads = []
	for count in range(len(user_deads)):
		format_date = informat_date_to_format(user_deads[count])
		today = date.today()
		if today <= format_date:
			new_user_deads.append(user_deads[count])
	result_js["user_deads"] = new_user_deads 


	with open('file_dead.json', 'w') as file_n: #записываем в файл обратно
		file_n.write(str(result_js))









@bot.message_handler(content_types=['text'])
def get_text_messages(message):
	id_user = message.from_user.id # считали айди юзера
	chat_id = message.chat.id
	print(id_user)
	status = 0 #не ждет рподолжения диалога

	if str(chat_id) in Dialog_status:
		status = Dialog_status.get(str(chat_id)) #Если диалог уже идет - считали статус
	else:
		Dialog_status[str(chat_id)] = 0 #Если только начался - ставим ожидание начала


	with open('j_cnvs.json') as j_cnvs:
		cnvr = json.load(j_cnvs) #считали весь джейсон с файла
	if(cnvr.get(str(id_user))):
		Json_Array = cnvr[str(id_user)] #считали весь диалог конкретного юзера
	else:
		Json_Array = [] #либо создали новый диалог для нового юзера

	json_buf = {}


	bot_msg = "" #Сюда запишем ответ бота

	with open('file_dead.json') as file_dead:
		deads = json.load(file_dead) #считали весь джейсон с файла
	all_deads = deads.get("all_deads")
	user_deads = deads.get("user_deads")

	json_buf_all_deads = {}
	json_buf_user_deads = {}

	if message.text != "":
		json_buf["Human"] = message.text  # Если человек отправил текст - записали фразу человека

	print(status)
	print(Dialog_status)
	print("Text = ",message.text)
	if status == 0:
		if message.text == "Привет":
			bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?")
			bot_msg = "Привет, чем я могу тебе помочь?"
			status = 0
		elif message.text == "/help":
			bot.send_message(message.chat.id, "Чтобы сохранить сообщение напиши /save \n Чтобы вписать новый дедлайн напиши /add \n Чтобы просмотреть свои текущие дедлайны напиши /dd \n Чтобы посмотреть дедлайны группы, напиши /alldd \n")
			bot_msg = "Чтобы сохранить сообщение напиши /save \n Чтобы вписать новый дедлайн напиши /add \n Чтобы просмотреть свои текущие дедлайны напиши /dd \n Чтобы посмотреть дедлайны группы, напиши /alldd \n"
			status = 0
		elif message.text == "/save":
			save_dialog(Json_Array)
			bot.send_message(message.chat.id,"Успешно сохранено")
			bot_msg = "Успешно сохранено"
			status = 0
		elif message.text == "/del":
			print(auto_delete_deads())
		elif message.text == "/add":
			bot.send_message(message.chat.id, "Напиши в 1 строке дату в формате дд.мм.гггг, а на другой строке - то, что нужно сделать, и на третьей строке - уровень доступа (все/никто)\n(Для отмены напиши - нет)")
			bot_msg = "Напиши в 1 строке дату в формате дд.мм.гггг, а на другой строке - то, что нужно сделать, и на третьей строке - уровень доступа (все/никто)\n(Для отмены напиши - нет)"

			Dialog_status[str(chat_id)] = 1 #Смена статуса на статус ожидания ввода дедлайна
			status = 1
		elif message.text == "/alldd":
			for msg in all_deads: #Вывод всех дедлайнов (для всех)
				print(msg)
				bot.send_message(message.chat.id, msg["date"] +" "+msg["deads"])
				bot_msg += msg["date"] +" "+msg["deads"] + "\n"
		elif message.text == "/dd":
			for msg_user in user_deads: #Вывод дедлайнов пользователя
				if str(id_user) == msg_user["id_user"]:
					print(msg_user)
					bot.send_message(message.from_user.id, msg_user["date"] +" "+msg_user["deads"])
					bot_msg += msg_user["date"] +" "+msg_user["deads"] + "\n"
		else:
			bot.send_message(message.chat.id,"Я тебя не понял, отправь мне /help")
			bot_msg = "Я тебя не понял, отправь мне /help"
	elif status == 1: #Считывает дедлайн
		if message.text != ("нет" or "Нет"):
			buf = message.text[1:len(message.text)+1].split("\n") #разбили строки по переносу строчки
			if buf[2] == ("все" or "Все"):
				json_buf_all_deads["deads"] = buf[1]
				json_buf_all_deads["date"] = buf[0]
				all_deads.append(json_buf_all_deads)
				Dialog_status[str(chat_id)] = 0 #Возвращаем статус обратно в начало диалога
				bot.send_message(message.chat.id, "Дедлайн успешно добавлен")
				bot_msg = "Дедлайн успешно добавлен"
			else:
				json_buf_user_deads["deads"] = buf[1]
				json_buf_user_deads["date"] = buf[0]
				json_buf_user_deads["id_user"] = str(id_user)
				user_deads.append(json_buf_user_deads)
				Dialog_status[str(chat_id)] = 0 #Возвращаем статус обратно в начало диалога
				bot.send_message(message.chat.id, "Дедлайн успешно добавлен")
				bot_msg = "Дедлайн успешно добавлен"
		else:
			Dialog_status[str(chat_id)] = 0 #Возвращаем статус обратно в начало диалога
			bot.send_message(message.chat.id, "Действие отменено")
			bot_msg = "Действие отменено"

	json_buf["Bot"] = bot_msg #записали ответ бота




	Json_Array.append(json_buf) #Добавили в наш json новое сообщение от пользователя

	cnvr[str(id_user)] = Json_Array #перезаписали диалог для конкретного ползователя (в качестве параметра идет айди пльзователя)
	#print(cnvr)
	deads["all_deads"] = all_deads #Перезаписали дедлайны
	deads["user_deads"] = user_deads #Перезаписали дедлайны
	#print(deads)

	with open('j_cnvs.json','w') as f:
		json.dump(cnvr, f, ensure_ascii=False) #записали апгрейднутый json в файлик, радуемс, пьем чай

	with open('file_dead.json', 'w') as ff:
		json.dump(deads, ff, ensure_ascii=False)






bot.polling(none_stop=True, interval=0)