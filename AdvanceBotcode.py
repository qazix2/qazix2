import discord
from discord.ext import commands
from discord.ext import tasks
import sqlite3
import time
import random
import requests
from bs4 import BeautifulSoup
from threading import Thread
import asyncio

print ('power by "Advance GG"')

bot = commands.Bot(command_prefix = '!', intents = discord.Intents.all())
bot.remove_command('help')

db = sqlite3.connect('serverds.db')
cursor = db.cursor()

@bot.event
async def on_ready():
	print('Logged on as AdvanceBot!')

	cursor.execute('''CREATE TABLE IF NOT EXISTS users (
		name TEXT,
		id INT,
		cash BIGINT,
		xp INT,
		lvl INT,
		rep INT,
		work TEXT,
		limit_work INT,
		time_job TEXT,
		wait TEXT,
		server_id INT,
		busines TEXT,
		busines_balance BIGINT
	)''')

	db.commit()
	
	cursor.execute('''CREATE TABLE IF NOT EXISTS role_shop (
		role_id INT,
		id INT,
		cost BIGINT,
		name TEXT
	)''')

	db.commit()

	cursor.execute('''CREATE TABLE IF NOT EXISTS works (
		name TEXT,
		cost BIGINT,
		role INT,
		server_id INT
	)''')

	db.commit()

	cursor.execute('''CREATE TABLE IF NOT EXISTS bank (
		user_name TEXT,
		user_id INT,
		amount BIGINT,
		place TEXT,
		guild_id INT,
		stuff BIGINT
	)''')

	db.commit()

	cursor.execute('''CREATE TABLE IF NOT EXISTS cells (
		name TEXT,
		cost BIGINT,
		cap BIGINT
	)''')

	db.commit()

	cursor.execute('''CREATE TABLE IF NOT EXISTS businesses (
		name TEXT,
		cost BIGINT,
		profit BIGINT
	)''')

	db.commit()

	for guild in bot.guilds:
		server = guild.members
		for member in server:
			print(member.id, member.name)
			if cursor.execute(f"SELECT id FROM users WHERE id = {member.id} AND server_id = {guild.id}").fetchone() is None:
				cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0, 1, 0, 'None', 0, '00:00:00', 'None', {guild.id}, 'None', 0)")
				db.commit()
			if cursor.execute(f"SELECT user_id FROM bank WHERE user_id = {member.id}").fetchone() is None:
				cursor.execute(f"INSERT INTO bank VALUES ('{member}', {member.id}, 0, 'None', {guild.id}, 0)")
				db.commit()
			else:
				pass

	businesses_list = ("сервера sa-mp", 10000, 50), ("шаурмечная", 50000, 100), ("магазин", 150000, 200), ("ночной клуб", 300000, 300), ("аукцион спорткаров", 600000, 900), ("автосалон", 1000000, 1500), ("торговля оружием", 1500000, 2500), ("нефтевышка", 2500000, 3000), ("аэропорт", 3300000, 3500), ("авто-завод", 4500000, 4300), ("АЭС", 5120000, 5000), ("букмекерская контора", 6500000, 6500), ('компания "Роскосмос"', 12120000, 12000)
	print(cursor.execute(f"SELECT busines_balance FROM users WHERE id = {759835312880484432}").fetchone()[0])
	print(cursor.execute(f"SELECT busines FROM users WHERE id = {759835312880484432}").fetchone()[0])
	db.commit()
	print('Bot connected!')


@bot.event
async def on_member_join(member):
	if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
		cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0, 1, 0, 'None', 0, '00:00:00', 'None', {guild.id}, 'None', 0)")
		db.commit()
	if cursor.execute(f"SELECT user_id FROM bank WHERE user_id = {member.id}").fetchone() is None:
		cursor.execute(f"INSERT INTO bank VALUES ('{member}', {member.id}, 0, 'None', {guild.id}, 0)")
		db.commit()
	else:
		pass


@bot.command(aliases = ['баланс', 'кэш'])
async def balance(ctx, member: discord.Member = None):
	if member is None:
		cursor.execute(f"SELECT cash FROM users WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
		await ctx.send("Баланс пользователя {0} составляет {1} пуллов".format(ctx.author.mention, cursor.fetchone()[0]))
		print(ctx.guild.id)
		db.commit()
	else:
		cursor.execute(f"SELECT cash FROM users WHERE id = {member.id} AND server_id = {ctx.guild.id}")
		data_cash = cursor.fetchone()[0]
		await ctx.send("Баланс пользователя {0} составляет {1} пуллов".format(member.mention, data_cash))
		db.commit()


@bot.command(aliases = ['магазин'])
async def shop_roles(ctx):
	embed = discord.Embed(title = "Магазин ролей")

	for role in cursor.execute(f"SELECT role_id, cost FROM role_shop WHERE id = {ctx.guild.id}"):
		if ctx.guild.get_role(role[0]) != None:
			if ctx.guild.get_role(role[0]).name.startswith('$') == False:
				embed.add_field(
					name = f"Стоимость - {role[1]} пуллов",
					value = f"Вы получите роль {ctx.guild.get_role(role[0]).mention}",
					inline = False
				)
			else:
				embed.add_field(
					name = f"Стоимость - {role[1]} репутации",
					value = f"Вы получите роль {ctx.guild.get_role(role[0]).mention}",
					inline = False
				)

	db.commit()

	await ctx.send(embed = embed)


@bot.command(aliases = ['купить'])
async def buy_role(ctx, *, role: discord.Role = None):
	if role is None:
		await ctx.send('Укажите роль, которую хотите купить')
	elif role.name.startswith('$') == False:
		if role in ctx.author.roles:
			await ctx.send('Данная роль уже есть у вас!')
		elif cursor.execute(f"SELECT cost FROM role_shop WHERE role_id = {role.id}").fetchone()[0] > cursor.execute(f"SELECT cash FROM users WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}").fetchone()[0]:
			await ctx.send(':no_entry_sign: У вас не достаточно средств для покупки данной роли!')
		else:
			await ctx.author.add_roles(role)
			cost_role = cursor.execute(f"SELECT cost FROM role_shop WHERE role_id = {role.id}").fetchone()[0]
			cursor.execute(f"UPDATE users SET cash = cash - {cost_role} WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
			db.commit()
			await ctx.send(f'Вы успешно приобрели роль {role.name}')
	else:
		if role in ctx.author.roles:
			await ctx.send('Данная роль уже есть у вас!')
		elif cursor.execute(f"SELECT cost FROM role_shop WHERE role_id = {role.id}").fetchone()[0] > cursor.execute(f"SELECT rep FROM users WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}").fetchone()[0]:
			await ctx.send(':no_entry_sign: У вас не достаточно репутации для покупки данной роли!')
		else:
			await ctx.author.add_roles(role)
			cost_role = cursor.execute(f"SELECT cost FROM role_shop WHERE role_id = {role.id}").fetchone()[0]
			cursor.execute(f"UPDATE users SET rep = rep - {cost_role} WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
			db.commit()
			await ctx.send(f'Вы успешно приобрели роль {role.name}')


@bot.command(aliases = ['реп', 'репутация'])
async def rep(ctx, member: discord.Member = None):
	if member is None:
		cursor.execute(f"SELECT rep FROM users WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
		await ctx.send(f"Репутация пользователя {ctx.author.mention} составляет {cursor.fetchone()[0]}")
	else:
		cursor.execute(f"SELECT rep FROM users WHERE id = {member.id} AND server_id = {ctx.guild.id}")
		await ctx.send(f"Репутация пользователя {member.mention} составляет {cursor.fetchone()[0]}")

	db.commit()


@bot.command(aliases = ['ранг', 'ранк'])
async def rank(ctx, member: discord.Member = None):
	if member is None:
		cursor.execute(f"SELECT xp FROM users WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
		dataxp = cursor.fetchone()[0]
		cursor.execute(f"SELECT lvl FROM users WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
		datalvl = cursor.fetchone()[0]

		embed = discord.Embed(title = "Ранг", description = f'''xp пользователя {ctx.author.mention} - {dataxp}

			lvl пользователя {ctx.author.mention} - {datalvl}
			''')

		await ctx.send(embed = embed)

		db.commit()

	else:
		cursor.execute(f"SELECT xp FROM users WHERE id = {member.id} AND server_id = {ctx.guild.id}")
		dataxp = cursor.fetchone()[0]
		cursor.execute(f"SELECT lvl FROM users WHERE id = {member.id} AND server_id = {ctx.guild.id}")
		datalvl = cursor.fetchone()[0]

		embed = discord.Embed(title = "Ранг", description = f'''xp пользователя {member.mention} - {dataxp}

			lvl пользователя {member.mention} - {datalvl}
			''')

		await ctx.send(embed = embed)

		db.commit()


@bot.command(aliases = ['добавить_р'])
@commands.has_role('Senior веб разработчик(10ур.)')
async def add_role(ctx, name: discord.Role = None, cost: int = None):
	if name is None:
		await ctx.send("Укажите название роли!")
	elif cost is None:
		await ctx.send("Укажите стоимость роли!")
	elif cost < 0:
		await ctx.send("Стоимость не может быть меньше 0!")
	else:
		if cursor.execute(f"SELECT name FROM role_shop WHERE id = {ctx.guild.id}").fetchall():
			name_str = str(name)
			if tuple(name_str.split()) in cursor.execute(f"SELECT name FROM role_shop WHERE id = {ctx.guild.id}").fetchall():
				await ctx.send("Данная роль уже есть в магазине ролей!")
			else:
				cursor.execute(f"INSERT INTO role_shop VALUES({name.id}, {ctx.guild.id}, {cost}, '{name}')")
				await ctx.send(f"Роль {name.mention} успешно добавлена в магазин!")
				db.commit()
		else:
			cursor.execute(f"INSERT INTO role_shop VALUES({name.id}, {ctx.guild.id}, {cost}, '{name}')")
			await ctx.send(f"Роль {name.mention} успешно добавлена в магазин!")
			db.commit()


@bot.command(aliases = ['удалить_р'])
async def delete_role(ctx, name: discord.Role = None):
	if name is None:
		await ctx.send("Укажите название роли!")
	else:
		cursor.execute(f"DELETE FROM role_shop WHERE name = '{name}' AND id = {ctx.guild.id}")
		db.commit()
		await ctx.send("Роль успешна удалена из магазина!")


@bot.command(aliases = ['добавить_п'])
@commands.has_role('Senior веб разработчик(10ур.)')
async def add_work(ctx, name: str = None, cost: int = None, role: discord.Role = None):
	if name is None:
		await ctx.send("Укажите название профессии!")
	elif cost is None:
		await ctx.send("Укажите стоимость профессии!")
	elif role is None:
		await ctx.send("Укажите название роли, с достижением которой можно приобрести данную роль!")
	elif cost <= 0:
		await ctx.send("Стоимость не может быть меньше 0 или равна 0!")
	else:
		if cursor.execute(f"SELECT name FROM works WHERE server_id = {ctx.guild.id}").fetchall():
			if tuple(name.split()) in cursor.execute(f"SELECT name FROM works WHERE server_id = {ctx.guild.id}").fetchall():
				await ctx.send("Профессия с данным названием уже есть!")
			else:
				cursor.execute("INSERT INTO works VALUES('{}', {}, {}, {})".format(name, cost, role.id, ctx.guild.id))
				await ctx.send("Профессия успешно добавлена в список")
				db.commit()
		else:
			cursor.execute("INSERT INTO works VALUES('{}', {}, {}, {})".format(name, cost, role.id, ctx.guild.id))
			await ctx.send("Профессия успешно добавлена в список")
			db.commit()


@bot.command(aliases = ['удалить_п'])
@commands.has_role('Senior веб разработчик(10ур.)')
async def delete_work(ctx, name: str = None):
	if name is None:
		await ctx.send("Укажите название профессии!")
	else:
		cursor.execute(f"DELETE FROM works WHERE name = '{name}' AND server_id = {ctx.guild.id}")
		db.commit()
		await ctx.send("Профессия успешна удалена из списка!")

@bot.command(aliases = ['профессии'])
async def all_works(ctx, work1: str = None):
	if work1 is None:
		embed = discord.Embed(title = "Профессии")

		for work in cursor.execute(f"SELECT name, cost, role FROM works WHERE server_id = {ctx.guild.id}"):
			embed.add_field(
				name = f"Стоимость - {work[1]} пуллов, Требуемая роль - {ctx.guild.get_role(work[2])}",
				value = f"Вы получите профессию {work[0]}",
				inline = False
			)

		await ctx.send(embed = embed)
	else:
		if tuple(work1.split()) == cursor.execute(f"SELECT work FROM users WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}").fetchone():
			await ctx.send("Данная профессия уже есть у вас!")
		elif len(cursor.execute(f"SELECT name FROM works WHERE name = '{work1}' AND server_id = {ctx.guild.id}").fetchall()) > 0:
			if ctx.guild.get_role(cursor.execute(f"SELECT role FROM works WHERE name = '{work1}' AND server_id = {ctx.guild.id}").fetchone()[0]) in ctx.author.roles:
				if cursor.execute(f"SELECT cost FROM works WHERE name = '{work1}'").fetchone()[0] > cursor.execute(f"SELECT cash FROM users WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}").fetchone()[0]:
					await ctx.send(":no_entry_sign: У вас не достаточно средств, для покупки данной профессии!")
					db.commit()
				else:
					cursor.execute(f"UPDATE users SET work = '{work1}' WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
					cost_work = cursor.execute(f"SELECT cost FROM works WHERE name = '{work1}' AND server_id = {ctx.guild.id}").fetchone()[0]
					cursor.execute(f"UPDATE users SET cash = cash - {cost_work} WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
					cursor.execute(f"UPDATE users SET limit_work = 8 WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
					db.commit()
					await ctx.send(f"Вы успешно приобрели профессию {work1}")
			else:
				await ctx.send(":no_entry_sign: У вас нет требуемой роли для покупки данной профессии! Загляните в магазин ролей")
		else:
			await ctx.send("Данной профессии нет в списке!")


@bot.command(aliases = ['курс', 'Курс'])
async def course(ctx):
	url = 'https://quote.rbc.ru/ticker/101039'
	headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0.0; AUM-L41 Build/HONORAUM-L41; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/80.0.3987.149 Mobile Safari/537.36 GSA/11.1.9.21.arm64'}
	response = requests.get(url)

	soap = BeautifulSoup(response.content, 'html.parser')
	html_convert = soap.find("span", {"class": "chart__info__sum"})
	convert = html_convert.text[1:]

	embed = discord.Embed(title = "Курс", description = f"1 реп - {convert} пуллов")

	await ctx.send(embed = embed)

	return convert


@bot.command(pass_context=True)
async def change_limit(ctx):
	await bot.wait_until_ready()
	print('True')
	cursor.execute(f"UPDATE users SET wait = 'True' WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
	db.commit()
	i = 0
	while i == 0:
		await asyncio.sleep(60)
		await ctx.send('Ваши попытки работать пополнились!')
		cursor.execute(f"UPDATE users SET limit_work = 8 WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
		cursor.execute(f"UPDATE users SET wait = 'False' WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
		db.commit()
		i += 1


@bot.command(aliases = ['работать'])
async def event_work(ctx):
	if cursor.execute(f"SELECT work FROM users WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}").fetchone()[0] != 'None':
		limit1 = cursor.execute(f"SELECT limit_work FROM users WHERE id = {ctx.author.id} AND {ctx.author.id}").fetchone()[0]
		if limit1 != 0:
			job_user = cursor.execute(f"SELECT work FROM users WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}").fetchone()[0]
			salary = cursor.execute(f"SELECT cost FROM works WHERE  name = '{job_user}' AND server_id = {ctx.guild.id}").fetchone()[0] // 50
			cursor.execute(f"UPDATE users SET limit_work = limit_work - 1 WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
			limit2 = cursor.execute(f"SELECT limit_work FROM users WHERE id = {ctx.author.id} AND {ctx.author.id}").fetchone()[0]
			db.commit()

			rand_compar = random.randint(1, 2)
			if rand_compar == 1:
				rand_salary = random.randint(salary, salary + 10)
				cursor.execute(f"UPDATE users SET cash = cash + {rand_salary} WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
				db.commit()
				await ctx.send(f'''{ctx.author.mention}, вы заработали {rand_salary} пуллов :money_mouth:
Попыток работать осталось - {limit2}
			''')
			elif rand_compar == 2:
				rand_salary2 = random.randint(salary - 9, salary)
				if rand_salary2 < 0:
					rand_salary2 = 0
					print('меньше 0!')
				cursor.execute(f"UPDATE users SET cash = cash + {rand_salary2} WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
				db.commit()
				await ctx.send(f'''{ctx.author.mention}, вы заработали {rand_salary2} пуллов :money_mouth:
Попыток работать осталось - {limit2}
			''')

			db.commit()

		else:
			await ctx.send(f"У вас 0 попыток работать!")

			if cursor.execute(f"SELECT wait FROM users WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}").fetchone()[0] == 'False' or cursor.execute(f"SELECT wait FROM users WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}").fetchone()[0] == 'None':
				bot.loop.create_task(change_limit(ctx))
			else:
				pass
	else:
		await ctx.send('Чтобы работать, вам нужно приобрести профессию! Загляни в список профессий при помощи команды "!профессии"')


@bot.command(aliases = ['обмен', 'обменять'])
async def exchange(ctx, amount : float = None, currency : str = None):
	if amount is None:
		await ctx.send("Укажите сумму для обмена: в пуллах, или репутации!")
	elif currency == None:
		await ctx.send('Укажите валюту, которую хотите обменять буквой "п" - пуллы, или "р" - репутация!')
	else:
		if currency != 'п' and currency != 'р':
			await ctx.send('Валюта: "п" - пуллы, "р" - репутация!')
		else:
			url = 'https://quote.rbc.ru/ticker/101039'
			response = requests.get(url)
			soap = BeautifulSoup(response.content, 'html.parser')
			html_convert = soap.find("span", {"class": "chart__info__sum"})
			convert = html_convert.text[1:]
			convert = convert.replace(" ", "")
			if ',' in convert:
				convert = convert.replace(',', '.')
			else:
				pass

			if currency == 'п':
				if cursor.execute(f"SELECT cash FROM users WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}").fetchone()[0] < amount:
					await ctx.send(":no_entry_sign: У вас недостаточно средств для обмена!")
				elif amount < float(convert):
					await ctx.send(":no_entry_sign: Курс выше указанной вами суммы!")
				elif amount == 0:
					await ctx.send("Сумма для обмена не может быть равна 0!")
				else:
					result_exch = amount // float(convert)
					cursor.execute(f"UPDATE users SET cash = cash - {amount - (amount - round(float(convert)) * result_exch)} WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
					cursor.execute(f"UPDATE users SET rep = rep + {int(result_exch)} WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
					db.commit()
					await ctx.send(f"Обмен успешно совершён! Вы получили {int(result_exch)} репутации")

			elif currency == 'р':
				if cursor.execute(f"SELECT rep FROM users WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}").fetchone()[0] < amount:
					await ctx.send(":no_entry_sign: У вас недостаточно репутации для обмена!")
				elif amount == 0:
					await ctx.send("Репутация для обмена не может быть равна 0!")
				else:
					result_exch = amount * float(convert)
					cursor.execute(f"UPDATE users SET rep = rep - {amount} WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
					cursor.execute(f"UPDATE users SET cash = cash + {result_exch} WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
					db.commit()
					await ctx.send(f"Обмен успешно совершён! Вы п0олучили {int(result_exch)} пуллов")


@bot.command(aliases = ['казино'])
async def casino(ctx, amount: int = False):
	if amount is None:
		await ctx.send("Укажите сумму, которую хотите поставить в казино!")
	elif amount == 0:
		await ctx.send("Сумма не может быть равна нулю 0!")
	elif amount > cursor.execute(f"SELECT cash FROM users WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}").fetchone()[0]:
		await ctx.send("У вас нет данной суммы на вашем балансе!")
	else:
		win_rand = random.randint(1, 3)
		if win_rand == 1:
			cursor.execute(f"UPDATE users SET cash = cash + {amount} WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
			await ctx.send(f'''{ctx.author.mention}, вы выйграли {amount} пуллов''')
			db.commit()
		else:
			lose_rand = random.randint(1, 4)
			if lose_rand == 1:
				result = amount * 0.25
				cursor.execute(f"UPDATE users SET cash = cash - {result} WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
				db.commit()
				await ctx.send(f"{ctx.author.mention}, вы проиграли {result} пуллов")
			elif lose_rand == 2:
				result = amount * 0.50
				cursor.execute(f"UPDATE users SET cash = cash - {result} WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
				db.commit()
				await ctx.send(f"{ctx.author.mention}, вы проиграли {result} пуллов")
			elif lose_rand == 3:
				result = amount * 0.75
				cursor.execute(f"UPDATE users SET cash = cash - {result} WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
				db.commit()
				await ctx.send(f"{ctx.author.mention}, вы проиграли {result} пуллов")
			elif lose_rand == 4:
				result = amount
				cursor.execute(f"UPDATE users SET cash = cash - {result} WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
				db.commit()
				await ctx.send(f"{ctx.author.mention}, вы проиграли {result} пуллов")


@bot.command(aliases = ['кубик'])
async def Cube(ctx, number: int = None):
	if number is None:
		await ctx.send("Укажите число от 1 до 6!")
	elif number > 6:
		await ctx.send("Укажите число от 1 до 6!")
	else:
		rand_cube = random.randint(1, 6)
		if number == rand_cube:
			await ctx.send(f"{ctx.author.mention}, вы угадали! Ваш приз 5000 пуллов")
			cursor.execute(f"UPDATE users SET cash = cash - 5000 WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
			db.commit()
		else:
			await ctx.send(f"Вы не угадали! Число было {rand_cube}")


@bot.command(aliases = ['банк'])
async def bank(ctx, action = None, amount: int = None):
	cell_bank = cursor.execute(f"SELECT place FROM bank WHERE user_id = {ctx.author.id} AND guild_id = {ctx.guild.id}").fetchone()[0]
	if action is None and amount is None:
		amount_bank = cursor.execute(f"SELECT amount FROM bank WHERE user_id = {ctx.author.id}").fetchone()[0]
		embed = discord.Embed(title = "Банк", description = f"{ctx.author.name}, ваш баланс в банке {amount_bank} пуллов")

		for cell in cursor.execute(f"SELECT * FROM cells"):
			embed.add_field(
				name = f'Стоимость - {cell[1]} пуллов, Вместимость - {cell[2]} пуллов',
				value = f"Вы получите ячейку '{cell[0]}'",
				inline = False
			)

		await ctx.send(embed = embed)

	elif action != None and action != 'положить' and action != 'снять':
		await ctx.send("Действия с банком: положить, снять!")

	if action == 'снять':
		print("Yest")
		if action == 'снять' and cursor.execute(f"SELECT amount FROM bank WHERE user_id = {ctx.author.id} AND guild_id = {ctx.guild.id}") == 0:
			await ctx.send("Ваш баланс в банке: 0 пуллов!")
		elif action == 'снять' and amount is None:
			await ctx.send("Укажите сумму, которую хотите снять с банка!")
		elif action == 'снять' and cursor.execute(f"SELECT amount FROM bank WHERE user_id = {ctx.author.id} AND guild_id = {ctx.guild.id}").fetchone()[0] < amount:
			print('True12344')
			await ctx.send(f"{ctx.author.name}, на вашем балансе в банке не достаточно средств!")
		else:
			cursor.execute(f"UPDATE bank SET amount = amount - {amount} WHERE user_id = {ctx.author.id} AND guild_id = {ctx.guild.id}")
			db.commit()
			cursor.execute(f"UPDATE users SET cash = cash + {amount} WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
			db.commit()
			await ctx.send(f"{ctx.author.name}, вы успешно сняли с банка {amount} пуллов!")


	if action == 'положить' and amount is None:
		await ctx.send("Укажите сумму, которую хотите положить в банк!")
	elif action == 'положить' and cell_bank == 'None':
		await ctx.send("Сначала приобретите ячейку на определённую сумму в свой банк!")
	elif cursor.execute(f"SELECT cash FROM users WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}").fetchone()[0] < amount:
		await ctx.send(f"{ctx.author.name}, на вашем балансе недостаточно средств!")
	elif action == 'положить' and cell_bank != 'None' and cursor.execute(f"SELECT cap FROM cells WHERE name = '{cell_bank}'").fetchone()[0] < amount or cursor.execute(f"SELECT cap FROM cells WHERE name = '{cell_bank}'").fetchone()[0] - cursor.execute(f"SELECT amount FROM bank WHERE user_id = {ctx.author.id} AND guild_id = {ctx.guild.id}").fetchone()[0] < amount:
		await ctx.send("В вашей ячейке в банке не достаточно места для данной суммы!")
	elif action == 'положить' and cell_bank != 'None' and cursor.execute(f"SELECT cap FROM cells WHERE name = '{cell_bank}'").fetchone()[0] >= amount:
		cursor.execute(f"UPDATE bank SET amount = amount + {amount} WHERE user_id = {ctx.author.id} AND guild_id = {ctx.guild.id}")
		db.commit()
		cursor.execute(f"UPDATE users SET cash = cash - {amount} WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
		db.commit()
		await ctx.send(f"{ctx.author.name}, на ваш счёт в банке зачисленно {amount} пуллов")

@bot.command(aliases = ['ячейка'])
async def buy_cell(ctx, name = None):
	if name is None:
		await ctx.send("Укажите название ячейки, которую хотите приобрести!")
	elif tuple(name.split()) not in cursor.execute(f"SELECT name FROM cells").fetchall():
		await ctx.send("Данной ячейки нет!")
	elif cursor.execute(f"SELECT cash FROM users WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}").fetchone()[0] < cursor.execute(f"SELECT cost FROM cells WHERE name = '{name}'").fetchone()[0]:
		await ctx.send("У вас недостаточно средств для покупки данной ячейки!")
	else:
		cost_cell = cursor.execute(f"SELECT cost FROM cells WHERE name = '{name}'").fetchone()[0]
		cursor.execute(f"UPDATE bank SET place = '{name}' WHERE user_id = {ctx.author.id} AND guild_id = {ctx.guild.id}")
		db.commit()
		cursor.execute(f"UPDATE users SET cash = cash - {cost_cell} WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
		db.commit()
		await ctx.send(f"Вы успешно приобрели ячейку '{name}'")


@bot.command(pass_context = True)
async def change_busines_balance(ctx, name):
	await bot.wait_until_ready()
	while cursor.execute(f"SELECT busines FROM users WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}").fetchone()[0] != 'None':
		await asyncio.sleep(60)
		print("Plus")
		profit_bus = cursor.execute(f"SELECT profit FROM businesses WHERE name = '{name}'").fetchone()[0]
		cursor.execute(f"UPDATE users SET busines_balance = busines_balance + {profit_bus} WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
		db.commit()


@bot.command(aliases = ['бизнесы'])
async def businesses(ctx, *, name: str = None):
	names_businesses_list = cursor.execute(f"SELECT name FROM businesses").fetchall()
	if name == None:
		embed = discord.Embed(title = "Бизнесы")
		businesses = cursor.execute(f"SELECT * FROM businesses")
		for busines in businesses:
			embed.add_field(
				name = f"Стоимость - {busines[1]}, прибыль - {busines[2]}/час",
				value = f"Вы получите бизнес {busines[0]}"
			)

		await ctx.send(embed=embed)
	elif name != None:
		names_businesses = []
		for item in names_businesses_list:
			names_businesses.append(item[0])

		if name in names_businesses:
			if cursor.execute(f"SELECT busines FROM users WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}").fetchone()[0] != 'None':
				await ctx.send(f"{ctx.author.name}, сначала продайте свой старый бизнес!")
			else:
				if cursor.execute(f"SELECT cash FROM users WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}").fetchone()[0] < cursor.execute(f"SELECT cost FROM businesses WHERE name = '{name}'").fetchone()[0]:
					await ctx.send("У вас недостаточно средств для покупки данного бизнеса!")
				elif cursor.execute(f"SELECT busines FROM users WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}").fetchone()[0] == name:
					await ctx.send(f"{ctx.author.name}, данный бизнес уже есть у вас!")
				else:
					cursor.execute(f"UPDATE users SET busines = '{name}' WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
					db.commit()
					cost_bis = cursor.execute(f"SELECT cost FROM businesses WHERE name = '{name}'").fetchone()[0]
					cursor.execute(f"UPDATE users SET cash = cash - {cost_bis} WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
					db.commit()
					await ctx.send(f"{ctx.author.name}, вы успешно приобрели бизнес {name}")

					bot.loop.create_task(change_busines_balance(ctx, name))
		else:
			await ctx.send(f"Данного бизнеса нет в списке!")


@bot.command(aliases = ['промокод'])
async def Promo_1(ctx, name):
	if name == "first_rep":
		cursor.execute(f"UPDATE users SET rep = rep + 1 WHERE id = {ctx.author.id}")

@bot.command(aliases = ['промо'])
async def Promo_2(ctx, name):
	if name == "first_pull":
		cursor.execute(f"UPDATE users SET cash = cash + 1000000 WHERE id = {ctx.author.id}")


@bot.command(aliases = ['перевести'])
async def Transfer(ctx, member: discord.Member = None, amount: int = None, currency = None):
	if member is None:
		await ctx.send("Укажите пользователя, которому хотите перевести определённую сумму!")
	elif amount is None:
		await ctx.send("Укажите сумму, которую хотите перевести!")
	elif amount < 0:
		await ctx.send("Сумма перевода не может быть меньше нуля!")
	elif currency is None:
		await ctx.send("Укажите валюту: 'п' - пуллы, 'р' - репы")
	elif currency != None and currency != 'п' and currency != 'р':
		await ctx.send("Валюта: 'п' - пуллы, 'р' - репы")
	else:
		if currency == 'п':
			if cursor.execute(f"SELECT cash FROM users WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}").fetchone()[0] < amount:
				await ctx.send(f"{ctx.author.name}, на вашем балансе недостаточно средств для перевода данной суммы!")
			else:
				cursor.execute(f"UPDATE users SET cash = cash - {amount} WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
				db.commit()
				cursor.execute(f"UPDATE users SET cash = cash + {amount} WHERE id = {member.id} AND server_id = {ctx.guild.id}")
				db.commit()
				await ctx.send(f"{ctx.author.name}, вы успешно перевели {amount} пуллов пользователю {member.name}")

		elif currency == 'р':
			if cursor.execute(f"SELECT rep FROM users WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}").fetchone()[0] < amount:
				await ctx.send(f"{ctx.author.name}, на вашем балансе недостаточно репутации для перевода данной суммы!")
			else:
				cursor.execute(f"UPDATE users SET rep = rep - {amount} WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
				db.commit()
				cursor.execute(f"UPDATE users SET rep = rep + {amount} WHERE id = {member.id} AND server_id = {ctx.guild.id}")
				db.commit()
				await ctx.send(f"{ctx.author.name}, вы успешно перевели {amount} репутации пользователю {member}")


@bot.command(aliases = ["бизнес"])
async def busines(ctx, action = None):
	if cursor.execute(f"SELECT busines FROM users WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}").fetchone()[0] == 'None':
		await ctx.send(f"{ctx.author.name}, у вас нет бизнеса!")
	else:
		if action is None:
			bus_name = cursor.execute(f"SELECT busines FROM users WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}").fetchone()[0] #change the server ID value
			profit_bus2 = cursor.execute(f"SELECT profit FROM businesses WHERE name = '{bus_name}'").fetchone()[0]
			balance = cursor.execute(f"SELECT busines_balance FROM users WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}").fetchone()[0]
			embed = discord.Embed(title = "Бизнес", description = f'''Бизнес - {bus_name}
	Прибыль - {profit_bus2} пуллов/час
	На счёте - {balance} пуллов
			''')

			await ctx.send(embed = embed)

		elif action != None and action != "снять" and action != "продать":
			await ctx.send('Действия с бизнесом: снять, продать')
		elif action == 'снять':
			if cursor.execute(f"SELECT busines_balance FROM users WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}").fetchone()[0] == 0:
				await ctx.send(f"{ctx.author.name}, на счёте вашего бизнеса 0 пуллов!")
			else:
				balance = cursor.execute(f"SELECT busines_balance FROM users WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}").fetchone()[0]
				cursor.execute(f"UPDATE users SET cash = cash + {balance} WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
				db.commit()
				cursor.execute(f"UPDATE users SET busines_balance = 0 WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
				db.commit()
				await ctx.send(f"{ctx.author.name}, вы сняли с бизнеса {balance} пуллов")
		elif action == 'продать':
			bus_name2 = cursor.execute(f"SELECT busines FROM users WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}").fetchone()[0]
			cost_bis2 = cursor.execute(f"SELECT cost FROM businesses WHERE name = '{bus_name2}'").fetchone()[0]
			cursor.execute(f"UPDATE users SET busines = 'None' WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
			db.commit()
			cursor.execute(f"UPDATE users SET cash = cash + {cost_bis2 / 2} WHERE id = {ctx.author.id} AND server_id = {ctx.guild.id}")
			db.commit()
			await ctx.send(f"{ctx.author.name}, вы успешно продали бизнес {bus_name2}")


@bot.command(aliases = ['инвестиции'])
async def investment(ctx, action = None, *, company: str = None):
	if action is None:
		url = 'https://invest.yandex.ru/catalog/stock/msft/?utm_source=serp&utm_medium=stock_wizard'
		response = requests.get(url)

		soap2 = BeautifulSoup(response.content, 'html.parser')
		html_convert2 = soap2.find("div", {"class": "NoU3BzJNsF2eLlvl7PTcX"})
		convert2 = html_convert2.text
		convert2_right = convert2.replace("$", "")
		micros_stocks = convert2_right
		#2
		url = 'https://invest.yandex.ru/catalog/stock/tsla/?utm_source=serp&utm_medium=stock_wizard'
		response2 = requests.get(url)

		soap3 = BeautifulSoup(response2.content, 'html.parser')
		html_convert3 = soap3.find("div", {"class": "NoU3BzJNsF2eLlvl7PTcX"})
		convert3 = html_convert3.text
		convert3_right = convert3.replace("$", "")
		tesla_stocks = convert3_right

		url = 'https://invest.yandex.ru/catalog/stock/googl/?utm_source=serp&utm_medium=stock_wizard'
		response3 = requests.get(url)

		soap4 = BeautifulSoup(response3.content, 'html.parser')
		html_convert4 = soap4.find("div", {"class": "NoU3BzJNsF2eLlvl7PTcX"})
		convert4 = html_convert4.text
		convert4_right = convert4.replace("$", "")
		google_stocks = convert4_right

		url = 'https://invest.yandex.ru/catalog/stock/amzn/?utm_source=serp&utm_medium=stock_wizard'
		response4 = requests.get(url)

		soap5 = BeautifulSoup(response4.content, 'html.parser')
		html_convert5 = soap5.find("div", {"class": "NoU3BzJNsF2eLlvl7PTcX"})
		convert5 = html_convert5.text
		convert5_right = convert5.replace("$", "")
		amzn_stocks = convert5_right

		url = 'https://invest.yandex.ru/catalog/stock/aapl/?utm_source=serp&utm_medium=stock_wizard'
		response5 = requests.get(url)

		soap6 = BeautifulSoup(response5.content, 'html.parser')
		html_convert6 = soap6.find("div", {"class": "NoU3BzJNsF2eLlvl7PTcX"})
		convert6 = html_convert6.text
		convert6_right = convert6.replace("$", "")
		apple_stocks = convert6_right

		url = 'https://invest.yandex.ru/catalog/stock/intc/?utm_source=serp&utm_medium=stock_wizard'
		response6 = requests.get(url)

		soap7 = BeautifulSoup(response6.content, 'html.parser')
		html_convert7 = soap7.find("div", {"class": "NoU3BzJNsF2eLlvl7PTcX"})
		convert7 = html_convert7.text
		convert7_right = convert7.replace("$", "")
		intel_stocks = convert7_right

		url = 'https://invest.yandex.ru/catalog/stock/axp/?utm_source=serp&utm_medium=stock_wizard'
		response7 = requests.get(url)

		soap8 = BeautifulSoup(response7.content, 'html.parser')
		html_convert8 = soap8.find("div", {"class": "NoU3BzJNsF2eLlvl7PTcX"})
		convert8 = html_convert8.text
		convert8_right = convert8.replace("$", "")
		axp_stocks = convert8_right

		url = 'https://invest.yandex.ru/catalog/stock/ma/?utm_source=serp&utm_medium=stock_wizard'
		response8 = requests.get(url)

		soap9 = BeautifulSoup(response8.content, 'html.parser')
		html_convert9 = soap9.find("div", {"class": "NoU3BzJNsF2eLlvl7PTcX"})
		convert9 = html_convert9.text
		convert9_right = convert9.replace("$", "")
		mas_stocks = convert9_right


		stocks = (("Microsoft", micros_stocks), ("Tesla", tesla_stocks), ("Google", google_stocks), ("Amazon", amzn_stocks), ("Intel", intel_stocks), ("American Express", axp_stocks), ("Mastercard", mas_stocks), ("Apple", apple_stocks))
		embed = discord.Embed(title = "Инвестиции", description = "Компании в которые вы можете инвестировать")
		for stock in stocks:
			embed.add_field(
				name = f"Стоимость акции - {stock[1]} пуллов",
				value = f"Компания - {stock[0]}",
				inline = False
			)

		await ctx.send(embed = embed)

bot.run('NzkyMzcwNzY4MTI2Mjc5NzAw.X-cuyA.D3Az_DzZDYOof-HMOPUeesQe6AI')