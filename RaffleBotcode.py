import discord
from discord.ext import commands
import sqlite3
import json
import random
import time

bot = commands.Bot(command_prefix = '.', intents = discord.Intents.all())
bot.remove_command('help')

db = sqlite3.connect('serverds.db')
cursor1 = db.cursor()

db2 = sqlite3.connect('rafflesds.db')
cursor2 = db2.cursor()

members_dict = dict()

@bot.event
async def on_ready():
	print('Logged on as RaffleBot')

	cursor2.execute('''CREATE TABLE IF NOT EXISTS users2(
		name TEXT,
		id INT,
		server2_id INT
		)''')

	db2.commit()

	cursor2.execute('''CREATE TABLE IF NOT EXISTS raffles(
		name TEXT,
		cost BIGINT,
		members INT,
		id INT,
		author TEXT
		)''')
	db2.commit()

	for guild in bot.guilds:
		server = guild.members
		for member in server:
			print(member.id, member.name)
			if cursor2.execute(f"SELECT id FROM users2 WHERE id = {member.id} AND server2_id = {guild.id}").fetchone() is None:
				cursor2.execute(f"INSERT INTO users2 VALUES ('{member.name}', {member.id}, {guild.id})")
				db2.commit()
			else:
				pass

	diction = {'Кейс3': ['Name1', 'Name2']}

	f = open('raffles_members.txt')
	cont_str = f.read()
	cont = json.loads(cont_str)
	print(cont)
	print(type(cont))
	f.close()
	print('Bot connected!')


@bot.command(aliases = ['добавить'])
async def add_raffle(ctx, name = None, cost: int = None):
	if name is None:
		await ctx.send("Укажите название розыгрыша!")
	elif cost is None:
		await ctx.send("Укажите стоимость розыгрыша!")
	else:
		cursor2.execute(f"INSERT INTO raffles VALUES ('{name}', {cost}, 0, {ctx.guild.id}, '{ctx.author.name}')")
		db2.commit()
		await ctx.send("Розыгрыш успешно добавлен! Вы можете подвести результаты в любое время командой '.разыграть'")


@bot.command(aliases = ['розыгрыши'])
async def raffles(ctx):
	embed = discord.Embed(title = 'Розыгрыши')
	for raf in cursor2.execute(f"SELECT * FROM raffles WHERE id = {ctx.guild.id}"):
		embed.add_field(
			name = f"Стоимость участия - {raf[1]}, участников - {raf[2]}, автор - {raf[4]}",
			value = f"Название розыгрыша - {raf[0]}",
			inline = False			
		)

	await ctx.send(embed = embed)


@bot.command(aliases = ['удалить'])
async def delete_raffle(ctx, name = None):
	print(cursor2.execute(f"SELECT author FROM raffles WHERE name = '{name}' AND id = {ctx.guild.id}").fetchone())
	if name is None:
		await ctx.send("Укажите название розыгрыша, который хотите удалить!")
	else:
		if cursor2.execute(f"SELECT name FROM raffles WHERE name = '{name}' AND id = {ctx.guild.id}").fetchone() is None:
			await ctx.send("Данного розыгрыша нет на вашем сервере!")
		else:
			if cursor2.execute(f"SELECT author FROM raffles WHERE name = '{name}' AND id = {ctx.guild.id}").fetchone()[0] != ctx.author.name:
				await ctx.send("Вы можете удалять только вами созданные розыгрыши!")
			else:
				cursor2.execute(f"DELETE FROM raffles WHERE name = '{name}' AND id = {ctx.guild.id}")
				db2.commit()
				await ctx.send("Розыгрыш успешно удалён!")


@bot.command(aliases = ['участвовать'])
async def add_member(ctx, name = None):
	f = open('raffles_members.txt')
	check_str = f.read()
	check_mem = json.loads(check_str)
	print(check_mem)
	f.close()

	if name is None:
		await ctx.send("Укажите название розыгрыша, в котором хотите участвовать!")
	else:
		if cursor2.execute(f"SELECT name FROM raffles WHERE name = '{name}' AND id = {ctx.guild.id}").fetchone() is None:
			await ctx.send("Данного розыгрыша нет на вашем сервере!")
		if f'{ctx.author.name}' in check_mem.get(f'{name}', []):
			await ctx.send("Вы уже участвуете в данном розыгрыше!")
		else:
			cash_user_tup = cursor1.execute(f"SELECT cash FROM users WHERE id = {ctx.author.id}").fetchall()
			cash_user_array = []
			for cash in cash_user_tup:
				cash_user_array.append(cash[0])
			max_cash = max(cash_user_array)

			if max_cash < cursor2.execute(f"SELECT cost FROM raffles WHERE name = '{name}' AND id = {ctx.guild.id}").fetchone()[0]:
				await ctx.send("У вас недостаточно средств, для участия в данном розыгрыше!")
			else:
				cost_raf = cursor2.execute(f"SELECT cost FROM raffles WHERE name = '{name}' AND id = {ctx.guild.id}").fetchone()[0]
				cursor1.execute(f"UPDATE users SET cash = cash - {cost_raf} WHERE id = {ctx.author.id} AND cash = {max_cash}")
				cursor2.execute(f"UPDATE raffles SET members = members + 1 WHERE name = '{name}' AND id = {ctx.guild.id}")
				db.commit()
				db2.commit()
				await ctx.send(f"{ctx.author.mention}, теперь вы участвуете в розыгрыше {name}")

				f = open('raffles_members.txt')
				cont_str = f.read()
				cont = json.loads(cont_str)
				print(cont)
				f.close()

				f = open('raffles_members.txt', 'w')
				if cont != {}:
					if f'{name}' in cont.keys():
						members_list = cont[f'{name}']
						members_list.append(f'{ctx.author.name}')
						cont[f'{name}'] = members_list

						json.dump(cont, f)

					else:
						cont[f'{name}'] = []
						members_list = cont[f'{name}']
						members_list.append(f'{ctx.author.name}')
						cont[f'{name}'] = members_list

						json.dump(cont, f)
						f.close()


@bot.command(aliases = ['разыграть'])
async def raffling(ctx, name = None):
	if name is None:
		await ctx.send("Укажите название розыгрыша, итоги которого хотите подвести!")
	elif cursor2.execute(f"SELECT name FROM raffles WHERE name = '{name}' AND id = {ctx.guild.id}").fetchone() is None:
		await ctx.send("Данного розыгрыша нет на вашем сервере!")
	elif cursor2.execute(f"SELECT author FROM raffles WHERE name = '{name}' AND id = {ctx.guild.id}").fetchone()[0] != ctx.author.name:
		await ctx.send("Вы можете разыгрывать только вами созданные розыгрыши!")
	else:
		f = open("raffles_members.txt")
		content = f.read()
		content_dict = json.loads(content)
		print(content_dict)
		necessary_raffle = content_dict[f'{name}']
		rand_winner = random.choice(necessary_raffle)
		del content_dict[f'{name}']
		f.close()

		f = open("raffles_members.txt", "w")
		json.dump(content_dict, f)
		f.close()

		cursor2.execute(f"DELETE FROM raffles WHERE name = '{name}' AND id = {ctx.guild.id}")
		db2.commit()

		await ctx.send("И таааак, кто же победил...")
		time.sleep(3)
		await ctx.send(f"{rand_winner}, поздравляю! Вы победили в розыгрыше {name}")


@bot.command(aliases = ['кик', 'Кик', 'kick', 'Kick'])
@commands.has_permissions(administrator = True)
async def kick_command(ctx, member: discord.Member = None, *, reason = None):
	if member is None:
		await ctx.send("Укажите имя пользователя, которого хотите выгнать с сервера!")
	else:
		await member.kick(reason = reason)
		await ctx.send(f"Пользователь {member.name} был изгнан с сервера пользователем {ctx.author.name}")


@bot.command(aliases = ['бан', 'Бан', 'ban', 'Ban'])
@commands.has_permissions(administrator = True)
async def ban_command(ctx, member: discord.Member = None, *, reason = None):
	if member is None:
		await ctx.send("Укажите имя пользователя, которого хотите забанить на сервере!")
	else:
		await member.ban(reason = reason)
		await ctx.send(f"Пользователь {member.name} был забанен с сервера пользователем {ctx.author.name}")

@kick_command.error
async def kick_error(ctx, error):
	if isinstance(error, discord.ext.commands.errors.MemberNotFound):
		await ctx.send(f'{ctx.author.name}, данного пользователя нет на сервере!')

bot.run('ODA5NDY3NzQwNDEzNzU1NDc1.YCVhlA.YQvFlml8a6m1EDKFewz-5t9jhBA')