# The following code sends an email with daily transaction summary of your league
# This is especially useful as ESPN does not currently have detailed summaries on the app and allows you to see who bid for whom (only for FAAB leagues)


from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import os	
import datetime
import smtplib


#builds a reference dictionary of team names
def Team_Name_Reference(leagueID):
	reference = {}
	for i in range(1,15):	
		my_url = 'http://games.espn.com/fba/clubhouse?leagueId='+str(leagueID)+'&teamId='+str(i)+'&seasonId=2018'
		uClient = uReq(my_url)
		page_html = uClient.read()
		uClient.close()
		page_soup = soup(page_html, "html.parser")
		team_containers = page_soup.findAll(attrs={"class": "team-name"})
		team_containers = team_containers[0].text.strip()
		begin = team_containers.index('(')
		end = team_containers.index(')')
		key = ''
		team_name = ''
		for i in range(begin+1, end):
			key = key + (team_containers[i])
		for i in range(begin-1):
			team_name = team_name + team_containers[i]
		reference[team_name] = [key]
	return reference

#personal league page = 28388
team_dictionary = Team_Name_Reference(28388)

#scrapes today's transactions and details
def Daily_Transactions_ESPN():
	date = datetime.datetime.today() 
	end_year = date.strftime("%Y")
	end_month = date.strftime("%m")
	end_day = date.strftime("%#d")
	my_url = 'http://games.espn.com/fba/recentactivity?leagueId=28388&seasonId=2018&activityType=2&startDate=20171002&endDate='+end_year+end_month+end_day+'&teamId=-1&tranType=-2'
	uClient = uReq(my_url)
	page_html = uClient.read()
	uClient.close()
	page_soup = soup(page_html, "html.parser")
	transactions = page_soup.findAll("tr")


	m = date.strftime("%b")
	d = date.strftime("%#d")
	message = ''


	for i in range(len(transactions)):
		try:
			player_dropped = ''
			player_added = ''
			dollar_amount = ''
			team = ''
			transaction_details = transactions[i].text.split()
			_from_ = transaction_details.index('from')
			_for_ = transaction_details.index('for')
			_added_ = transaction_details.index('added')
			_dropped_ = transaction_details.index('dropped')		
			_to_ = transaction_details.index('to')

			if transaction_details[1] == m and transaction_details[2][0:len(transaction_details[2])-5] == d:

				if transaction_details[5] == 'dropped':
					for x in range(_dropped_ + 1, _to_ - 2):
						if x == _to_ - 3:
							player_dropped += transaction_details[x][:len(transaction_details[x])-1]
						else:
							player_dropped += transaction_details[x] + ' '

				if transaction_details[5] == 'added':
					for x in range(_dropped_ + 1, _for_ -4):
						if x == _for_ - 5:
							player_dropped += transaction_details[x][:len(transaction_details[x])-1]
						else:
							player_dropped += transaction_details[x] + ' '

				for x in range(_added_ + 1, _from_ - 2):
					if x == _from_ - 3:
						player_added += transaction_details[x][:len(transaction_details[x])-1]
					else:
						player_added += transaction_details[x] + ' '
			
				z = transaction_details[len(transaction_details) - 3]	
				for x in range(len(z)):
					if z[x].isdigit() == True:
						dollar_amount += z[x]

				team_name_container = transaction_details[4]

				for x in range(8,len(team_name_container)):
					team += team_name_container[x]
						
				message += 'Team ' + team + ' has added ' + player_added + ' and dropped ' + player_dropped + ' for $' + dollar_amount + '\n\n'		
		except:
			continue
	return message

#shows all the failed transactions (i.e. waiver that had a higher bid or higher priority)
def Failed_Transactions_ESPN():
	date = datetime.datetime.today()
	m = date.strftime("%m")
	d = date.strftime("%d")
	y = date.strftime("%Y")
	my_url = 'http://games.espn.com/fba/waiverreport?leagueId=28388&date='+str(y)+str(m)+str(d)
	
	uClient = uReq(my_url)
	page_html = uClient.read()
	uClient.close()
	page_soup = soup(page_html, "html.parser")
	transactions_container = page_soup.findAll(attrs={"class":"games-fullcol games-fullcol-extramargin"})
	transactions = transactions_container[0].findAll("tr")

	b = ''

	for i in range(1,len(transactions)):
		x = transactions[i].text.split()
		try:
			y = x.index('Reason:')
		except: 
			continue

		team = str(x[0]) + ' ' + str(x[1])

		dollar = ''
		z = x[y-1]
		for i in range(len(z)):
			if z[i].isdigit() == True:
				dollar = dollar + z[i]

		b = b + ('Team ' + str(team_dictionary[team][0])+ ' placed an unsuccessful bid on ' + x[x.index('Reason:')-5] + ' ' + x[x.index('Reason:')-4][:len(x[x.index('Reason:')-4])-1] + ' for $' +  dollar + "\n\n")
	return b

#checks if there are any transactions today
def Check_Transactions_ESPN():
	if len(Daily_Transactions_ESPN()) == 0:
		return False
	else:
		return True	

#sends summary  to email
def Send_Email():
	date = datetime.datetime.today()
	m = date.strftime("%m")
	d = date.strftime("%d")
	y = date.strftime("%Y")
	sender = '##########'
	password = '##########'
	receivers = ['##########']
	subject = 'Daily FAAB Transaction Summary for ' + y + '-' + m + '-' + d
	if Check_Transactions_ESPN() == False: #no transactions occured
		body = 'Good Afternoon, \n\n There were no FAAB transactions today \n\n Reminber to set your lineups!'
	if Check_Transactions_ESPN() == True: 
		body = 'Good Afternoon,' + '\n\n' + Daily_Transactions_ESPN()  + Failed_Transactions_ESPN() + '\n' + 'Remember to set your lineups!'  

	message = '\r\n'.join([
				'To: %s' % receivers,
				'From: %s' % sender,
				'Subject: %s' % subject,
				'', body
				])

	mail = smtplib.SMTP('smtp.gmail.com',587)

	mail.ehlo()

	mail.starttls()

	mail.login(sender, password)

	mail.sendmail(sender, receivers, message)

	mail.close()

Send_Email()


