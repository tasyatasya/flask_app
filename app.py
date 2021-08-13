import json
import random
import os
from flask import Flask, request, render_template, abort
from uuid import uuid4
import sqlite3
from werkzeug.utils import redirect

from bank_api import ask_money, verify_transaction

app = Flask(__name__)


def load_users():
    with open('users.json', 'r') as file:
        users = json.load(file)
    return users


def save_users(users):
    with open('users.json', 'w') as file:
        json.dump(users, file)


@app.route('/')
def index():
    users = load_users()
    session_id = str(uuid4())
    users[session_id] = {
        "telegram_id": "",
        "votes_left": 10,
        "transaction_id": -1,
        "is_paid": False,
        "current_person": -1,
        "voted_to": []
    }
    save_users(users)
    return render_template('index.html', session_id=session_id)


@app.route('/<session_id>/pay', methods=['GET'])
def pay(session_id):
    users = load_users()

    if session_id not in users:
        abort(404)
    return render_template('pay.html', session_id=session_id)


@app.route('/<session_id>/pay', methods=['POST'])
def do_pay(session_id):
    users = load_users()

    if session_id not in users:
        abort(404)
    telegram_id = request.form.get('telegram_id')
    try:
        telegram_id = int(telegram_id)
    except:
        return render_template('pay.html', session_id=session_id, error='Введите номер счета')

    users[session_id]['telegram_id'] = telegram_id
    answer = ask_money(telegram_id, 50, "GoTo HOT 5")


    if 'error' in answer:
        return render_template('pay.html', session_id=session_id,
                               error='Не удалось провести оплату: {}'.format(answer['error']))
    else:
        users[session_id]['transaction_id'] = answer['transaction_id']
        save_users(users)
        return redirect('/{}/verify'.format(session_id))


@app.route('/<session_id>/verify', methods=['GET'])
def verify(session_id):
    users = load_users()
    if session_id not in users:
        abort(404)
    return render_template('verify.html', session_id=session_id)


@app.route('/<session_id>/verify', methods=['POST'])
def do_verify(session_id):
    users = load_users()
    if session_id not in users or 'transaction_id' not in users[session_id]:
        abort(404)
    code = request.form.get('code')
    try:
        code = int(code)
    except:
        return render_template('verify.html', session_id=session_id, error='Введите код подтверждения')

    answer = verify_transaction(users[session_id]['transaction_id'], code)
    print(users[session_id]['transaction_id'])
    if 'error' in answer:
        return render_template('verify.html', session_id=session_id,
                               error='Не удалось провести оплату: {}'.format(answer['error']))
    else:
        users[session_id]['is_paid'] = True
        save_users(users)
        return redirect('/{}/vote'.format(session_id))


@app.route('/<session_id>/vote', methods=['GET'])
def vote(session_id):
    users = load_users()
    if 'is_paid' not in users[session_id] or not users[session_id]['is_paid']:
        abort(403)

    if users[session_id]["votes_left"] == 0:
        return redirect("/top")

    connection = sqlite3.connect('database.sqlite')
    cursor = connection.execute('select * from Persons')  # ORDER BY votes DESC LIMIT 5

    person = random.choice(list(filter(lambda x: x[0] not in users[session_id]['voted_to'], cursor.fetchall())))
    users[session_id]['voted_to'].append(person[0])

    users[session_id]["current_person"] = person[0]
    # проверить оплатил ли пользователь голосование - done
    # если голосов не осталось - редирект на топ - done
    # взять из базы всех участников и выбрать рандомного - done
    # сохранить за кого голосуем в current_person в словаре - done
    # вывести страницу с голованием и двумя кнопками
    save_users(users)
    return render_template('vote.html', image=person[1])


@app.route('/<session_id>/vote', methods=['POST'])
def do_vote(session_id):
    users = load_users()

    if 'is_paid' not in users[session_id] or not users[session_id]['is_paid']:
        abort(403)

    users[session_id]["votes_left"] -= 1
    if request.form.get('vote') == '🔥':
        current_id = users[session_id]["current_person"]

        connection = sqlite3.connect('database.sqlite')

        connection.execute("INSERT INTO Votes (telegram_id, voted_to_id) VALUES (?,?)",
                           (users[session_id]['telegram_id'], current_id))

        cursor = connection.execute("SELECT * FROM Persons WHERE id = ?", (current_id,))
        votes = cursor.fetchone()[2] + 1
        connection.execute("UPDATE Persons SET votes = ? WHERE id = ?", (votes, current_id))

        connection.commit()
    save_users(users)
    return redirect('/{}/vote'.format(session_id))


@app.route('/top')
def top():
    connection = sqlite3.connect('database.sqlite')
    cursor = connection.execute('select * from Persons ORDER BY votes DESC LIMIT 5')  #
    persons = cursor.fetchall()

    return render_template("top.html", persons=persons)


if __name__ == "__main__":
    try:
        port = int(os.getenv('PORT'))
    except:
        port = 5000
    app.run(threaded=True, port=port)
