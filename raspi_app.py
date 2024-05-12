import hashlib
import os
import re
import sqlite3
import subprocess

from flask import Flask, redirect, render_template, request, session, url_for

# Running up a instance as app
app = Flask(__name__)

app.secret_key = os.urandom(21)
# """
# default user id (name) and password are;
#     id_pwd_hash = {'raspimin': 'raspimin'}
# """


# Password Digest
def get_digest(password):
    pwd = bytes(password, 'utf-8')
    diget = hashlib.sha224(pwd).hexdigest()
    return diget


# DB connection
def get_user_data():
    sqlite_path = 'static/db/users.sqlite'
    connection = sqlite3.connect(sqlite_path)
    cursor = connection.cursor()
    cursor.execute('SELECT name, password FROM users')
    id_pwd_hash = dict(cursor.fetchall())
    connection.close()
    return id_pwd_hash


# TopPage
@app.route('/')
def index():
    if not session.get('login'):
        return redirect(url_for('login'))
    else:
        return render_template('index.html')


# Login
@app.route('/login')
def login():
    return render_template('login.html')


# lockin check
@app.route('/logincheck', methods=['POST'])
def logincheck():
    user_id = request.form['user_id']
    pwd = request.form['password']
    session['username'] = user_id

    # make pwd hashed by "get_digest()"" function
    password = get_digest(pwd)
    id_pwd_hash = get_user_data()

    if user_id in id_pwd_hash:
        if password == id_pwd_hash[user_id]:
            session['login'] = True
        else:
            session['login'] = False
    else:
        session['login'] = False

    if session['login']:
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))


# logout
@app.route('/logout')
def logout():
    session.pop('login', None)
    return redirect(url_for('index'))


# Get IP address via "ip -4 address" command
@app.route('/get_ip_addr')
def get_ip_addr():
    ''' Get IP address via "ip -4 address" command '''

    if not session.get('login'):
        return redirect(url_for('login'))
    else:
        get_ip_addr = subprocess.run(['ip', '-4', 'address'],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        cmd_result = get_ip_addr.stdout.decode('utf-8')

        ip_addr_result = []

        cmd_result0 = cmd_result.splitlines()
        for read_line in cmd_result0:
            if re.search(r'^\s*inet', read_line):
                read_line0 = read_line.lstrip(' ').rstrip('\n').split()
                ip_addr_result.append(read_line0)

        ip_addr_result0 = []

        for read_line in ip_addr_result:
            ip_addr_result0.append((read_line[-1], read_line[1]))

        result_dict = dict(ip_addr_result0)

        return render_template('get_ip_addr.html', result=result_dict)


# Get Socket info via "ss -tu" command
@app.route('/get_socket')
def get_socket():
    ''' Get Socket info via "ss -tu" command '''

    if not session.get('login'):
        return redirect(url_for('login'))
    else:
        get_socket = subprocess.run(['ss', '-tu'],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        cmd_result = get_socket.stdout.decode('utf-8')

        socket_list = []

        cmd_result0 = cmd_result.splitlines()
        for read_line in cmd_result0:
            read_line0 = [*read_line.split(), '']
            socket_list.append(read_line0)

        socket_list1 = []

        for list_value in socket_list:
            socket_list1.append(list_value)

            if 'Netid' in list_value:
                value0 = list_value[4] + '-' + list_value[5]
                value1 = list_value[6] + '-' + list_value[7]
                socket_list1[0].insert(4, value0)
                socket_list1[0].insert(5, value1)
                socket_list1[0].remove('Local')
                socket_list1[0].remove('Peer')
                socket_list1[0].remove('Address:Port')
                socket_list1[0].remove('Address:Port')
                del socket_list1[0][-1]

        return render_template('get_socket.html', result=socket_list1)


# Get IP routing table via "route" command
@app.route('/get_route')
def get_route():
    ''' Get IP routing table via "route" command '''

    if not session.get('login'):
        return redirect(url_for('login'))
    else:
        get_route_table = subprocess.run(['route'],
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
        cmd_result = get_route_table.stdout.decode('utf-8')

        route_result = []

        cmd_result0 = cmd_result.splitlines()
        for read_line in cmd_result0:
            read_read_line0 = read_line.split()
            route_result.append(read_read_line0)

        del route_result[0]

        return render_template('get_route.html', result=route_result)


# Get SoC temparature via "vcgencmd" command
@app.route('/get_temp')
def get_temp():
    ''' Get SoC temparature via "vcgencmd" command '''

    if not session.get('login'):
        return redirect(url_for('login'))
    else:
        get_temp = subprocess.run(['vcgencmd', 'measure_temp'],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
        value0 = get_temp.stdout.decode('utf-8')
        value1 = value0.split('=')
        value2 = value1[1][:-2]
        cmd_result = f'SoC Temparature : { value2 }C \n'
        return render_template('get_temp.html', result=cmd_result)


# Get disk info via "lsbk" & "df -h" command
@app.route('/get_disk')
def get_disk():
    ''' Get disk info via "lsbk" & "df -h" command '''

    if not session.get('login'):
        return redirect(url_for('login'))
    else:
        # Get disk info via "lsblk" command
        get_block_dev = subprocess.run(['lsblk'],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
        lsblk_result = get_block_dev.stdout.decode('utf-8')

        result_list0 = []

        lsblk_result0 = lsblk_result.splitlines()
        for read_line in lsblk_result0:
            read_line0 = read_line.rstrip('\n').split()
            result_list0.append(read_line0)

        # Get disk info via "df -h" command
        get_disk_usage = subprocess.run(['df', '-h'],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
        df_result = get_disk_usage.stdout.decode('utf-8')

        result_list1 = []

        df_result0 = df_result.splitlines()
        for read_line in df_result0:
            read_line0 = read_line.rstrip('\n').split()
            result_list1.append(read_line0)

        result_list2 = []

        for read_line in result_list1:
            result_list2.append(read_line)

            if 'Filesystem' in read_line:
                h_list = read_line[5] + '-' + read_line[6]
                result_list2[0].insert(5, h_list)
                result_list2[0].remove('Mounted')
                result_list2[0].remove('on')

        return render_template('get_disk.html', lsblk_result=result_list0,
                               df_result=result_list2)


# Get memory info via "free --mega -w" command
@app.route('/get_mem')
def get_mem():
    ''' Get memory info via "free --mega -w" command '''

    if not session.get('login'):
        return redirect(url_for('login'))
    else:
        get_socket = subprocess.run(['free', '--mega', '-w'],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        cmd_result = get_socket.stdout.decode('utf-8')

        result_list = []

        cmd_result0 = cmd_result.splitlines()
        for line in cmd_result0:
            line0 = line.split()
            result_list.append(line0)

        result_list[0].insert(0, '')
        result_list[2].extend(['', '', '', ''])

        return render_template('get_mem.html', result=result_list)


# Get statistics of CPU, Mem, IO
@app.route('/get_vmstat')
def get_vmstat():
    ''' Get statistics of CPU, Mem, IO '''

    if not session.get('login'):
        return redirect(url_for('login'))
    else:
        get_socket = subprocess.run(['vmstat'],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        cmd_result = get_socket.stdout.decode('utf-8')

        result_list = []

        cmd_result0 = cmd_result.splitlines()
        for read_line in cmd_result0:
            read_line0 = read_line.split()
            result_list.append(read_line0)

        del result_list[0]

        return render_template('get_vmstat.html', result=result_list)


if __name__ == ('__main__'):
    app.run(debug=True, host='0.0.0.0', port=5050)
