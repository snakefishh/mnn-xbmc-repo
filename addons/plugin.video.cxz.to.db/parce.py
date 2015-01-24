def readpersons(params):
	import sqlite3
	con = sqlite3.connect(addon_data_path+'/directors.db')
	cur = con.cursor()
	cur.execute("CREATE TABLE directors (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, name VARCHAR(50), url VARCHAR(50))")
	con.commit()

	url = 'http://cxz.to/films/group/director/?all&letter=%s'
	alf =u'abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщэюя'
	#alf =u'а'

	for letter in alf:
		page = 0
		while True:
			url_ = url%(letter.encode('UTF-8'))
			if page>0:
				url_+='&page='+str(page)

			time.sleep(2)
			Data =Get_url(url_)
			Soup = BeautifulSoup(Data)
			content = Soup.find('div', 'l-content-center')
			content = content.find('table')
			if content:
				names = content.findAll('a')
				for name in names:
					cur.execute('INSERT INTO directors VALUES (NULL, "%s", "%s");'%(name.string, name['href']))
			NextPage = Soup.find('a', 'next-link')
			if NextPage:
				page+=1
			else:
				break
	con.commit()
	con.close()

def readpersons1(params):
	import sqlite3
	con = sqlite3.connect(addon_data_path+'/casts.db')
	cur = con.cursor()
	cur.execute("CREATE TABLE casts (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, name VARCHAR(50), url VARCHAR(50))")
	con.commit()

	url = 'http://cxz.to/films/group/cast/?all&letter=%s'
	alf =u'абвгдеёжзийклмнопрстуфхцчшщэюяabcdefghijklmnopqrstuvwxyz'
	#alf ='а'

	for letter in alf:
		page = 0
		while True:
			print letter.encode('UTF-8')+str(page)
			url_ = url%(letter.encode('UTF-8'))
			if page>0:
				url_+='&page='+str(page)

			time.sleep(2)
			Data =Get_url(url_)
			Soup = BeautifulSoup(Data)
			content = Soup.find('div', 'l-content-center')
			content = content.find('table')
			if content:
				names = content.findAll('a')
				for name in names:
					try:
						cur.execute('INSERT INTO casts VALUES (NULL, "%s", "%s");'%(name.string, name['href']))
					except:
						print 'Ошибка ', name.string.encode('UTF-8')
			NextPage = Soup.find('a', 'next-link')
			if NextPage:
				page+=1
			else:
				break
	con.commit()
	con.close()