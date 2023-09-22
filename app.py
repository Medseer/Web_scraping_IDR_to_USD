from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

matplotlib.use('Agg')
app = Flask(__name__)

url_get = requests.get('https://www.exchange-rates.org/history/IDR/USD/T')
soup = BeautifulSoup(url_get.content,"html.parser")

table = soup.find('section', attrs={'class':'box history-rates-table-box'})
row = table.find_all('a', attrs={'class':'n'})

row_length = len(row)

temp = []

for i in range(1, row_length):
    
    date = table.find_all('a', attrs={'class':'n'})[i].text
    
    USD_to_IDR = table.find_all('span', attrs={'class':'n'})[i].text
    
    temp.append((date,USD_to_IDR))
    
temp = temp[::-1]

df = pd.DataFrame(temp, columns = ('date','USD_to_IDR'))

df['date']=df['date'].str.replace('-','/')
df['date']=df['date'].astype('datetime64[ns]')
df['USD_to_IDR']=df['USD_to_IDR'].str.replace('$', '',regex=False)
df['USD_to_IDR']=df['USD_to_IDR'].str.replace('=', '')
df['USD_to_IDR']=df['USD_to_IDR'].str.replace('Rp', '')
df['USD_to_IDR']=df['USD_to_IDR'].str.replace(',', '.')
df['USD_to_IDR']=df['USD_to_IDR'].str.replace(' ', '')
df['USD_to_IDR']=df['USD_to_IDR'].str[1:]
df['USD_to_IDR']=df['USD_to_IDR'].astype('float64')

@app.route("/")
def index(): 
	
	card_data = f'{df["USD_to_IDR"].mean()}'

	ax = df.plot(x='date', y='USD_to_IDR', figsize = (10,5)) 
	
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)