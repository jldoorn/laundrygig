import sqlite3
import datetime

dbconn = sqlite3.connect('laundry.db')
cur = dbconn.cursor()
price = 5

def create_user(room, building, PUID=None, fname=None, lname=None, email=None):
    query = '''
    INSERT INTO person(room, building, puid, fname, lname, email)
    VALUES(?, ?, ?, ?, ?, ?)
    '''
    cur.execute(query, (room, building, PUID, fname, lname, email))
    
    query = '''
    INSERT INTO credit(user, balance) VALUES (?, ?)
    '''
    cur.execute(query, (cur.lastrowid, 0))
    dbconn.commit()

def check_user_exists(user_id):
    query = '''
    SELECT * FROM person WHERE user = ?
    '''
    cur.execute(query, (user_id,))
    resp = cur.fetchall()
    if len(resp) > 0:
        return True
    else:
        return False

def get_user_balance(user_id):
    query = '''
    SELECT balance FROM credit WHERE user=?
    '''
    cur.execute(query, (user_id,))
    return cur.fetchall()[0][0]


# multiple jobs could be submitted with insufficient funds
# think about incentives (bribes?) to get load done quicker
def new_job(user_id, num_bags):
    if not check_user_exists(user_id):
        return False
    
    user_balance = get_user_balance(user_id)
    if user_balance < price * num_bags:
        return False

    query = '''
    INSERT INTO pending_job(requester, bags, request_time)
    VALUES(?, ?, ?)
    '''
    cur.execute(query, (user_id, num_bags, int(datetime.datetime.now().timestamp())))
    dbconn.commit()
    return True
