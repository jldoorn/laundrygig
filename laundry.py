import sqlite3
import datetime

dbconn = sqlite3.connect('laundry.db')
cur = dbconn.cursor()
price = 5
wash_dry_cost = 3
material_cost = 0.5
commission = 0.5

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

def check_job_in_queue(job_id):
    query = '''
    SELECT * FROM pending_job WHERE id = ?
    '''
    cur.execute(query, (job_id,))
    resp = cur.fetchall()
    if len(resp) > 0:
        return True
    else:
        return False

def check_job_in_active(job_id):
    query = '''
    SELECT * FROM active_job WHERE id = ?
    '''
    cur.execute(query, (job_id,))
    resp = cur.fetchall()
    if len(resp) > 0:
        return True
    else:
        return False

def get_job_bags(status, job_id):
    query = '''
    SELECT bags FROM ? WHERE id = ?
    '''
    cur.execute(query, (status, job_id))
    return cur.fetchall()[0][0]

def get_user_balance(user_id):
    query = '''
    SELECT balance FROM credit WHERE user=?
    '''
    cur.execute(query, (user_id,))
    return cur.fetchall()[0][0]

def debit_balance(user_id, debit):
    current_balance = get_user_balance(user_id)
    query = '''
    UPDATE credit
    SET balance = ? WHERE user = ?
    '''
    cur.execute(query, (current_balance - debit, user_id))
    dbconn.commit()

def add_balance(user_id, credit):
    current_balance = get_user_balance(user_id)
    query = '''
    UPDATE credit
    SET balance = ? WHERE user = ?
    '''
    cur.execute(query, (current_balance + credit, user_id))
    dbconn.commit()

def charge_requester(job_id):
    query = '''
    SELECT requester, bags FROM active_job WHERE id = ?
    '''
    cur.execute(query, (job_id,))
    ret = cur.fetchall()[0]
    debit_balance(ret[0], price * ret[1])
    return True

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

def start_job(user_id, job_id):
    if not check_job_in_queue(job_id):
        return False
    
    query = '''
    INSERT INTO active_job(requester, bags, request_time)
    SELECT p.requester, p.bags, p.request_time FROM pending_job p
    WHERE p.id = ?
    '''
    cur.execute(query, (job_id,))
    dbconn.commit()
    query = '''
    UPDATE active_job
    SET worker = ?, start_time = ?, load_charge = ?
    WHERE id = ?
    '''
    cur.execute(query, (user_id, int(datetime.datetime.now().timestamp()), price, cur.lastrowid))
    charge_requester(cur.lastrowid)
    cur.execute("DELETE FROM pending_job WHERE id = ?", (job_id,))
    dbconn.commit()


def calculate_pay_from_bags(bags):
    total_price = bags * price
    washer_fee = bags * wash_dry_cost
    soap_overhead = bags * material_cost
    worker_pay = washer_fee + soap_overhead + (bags * commission)
    laundrygig_pay = bags * commission

    return (worker_pay, laundrygig_pay)


def end_job(job_id):
    if not check_job_in_active(job_id):
        return False

    # copy active into completed
    query = '''
    INSERT INTO completed_job(requester, worker, bags, request_time, start_time, load_charge)
    SELECT a.requester, a.worker, a.bags, a.request_time, a.start_time, a.load_charge FROM active_job a
    WHERE a.id = ?
    '''
    cur.execute(query, (job_id,))
    dbconn.commit()

    bags = get_job_bags('completed_job', cur.lastrowid)

    # update end_time, gig pay, commission
    query = '''
    UPDATE completed_job
    SET end_time = ?, gig_pay = ?, commission = ?
    WHERE id = ?
    '''




