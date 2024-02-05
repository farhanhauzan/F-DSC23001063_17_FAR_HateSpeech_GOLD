import sqlite3
import pandas as pd

conn = sqlite3.connect("tweet.db")
cur = conn.cursor()

conn.execute("CREATE TABLE tweet_clean")
print('Table creation successful') 
conn.commit()


conn.close()
