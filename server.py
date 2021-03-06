from flask import Flask, redirect, render_template, request, session, url_for
import data_handler
import functions

app = Flask(__name__)
app.secret_key = '$2b$12$yxO3U5wrC1QSvVfL3xrLbu'


@app.route('/')
@app.route('/list')
def route_list():
    username = None
    if 'username' in session:
        username = session['username']

    sort_by = 'submission_time'
    sort_direction = 'DESC'
    if 'sort_by' in request.args and 'sort_direction' in request.args:
        sort_by = request.args['sort_by']
        sort_direction = request.args['sort_direction']

    questions = data_handler.get_all_data('question', sort_by, sort_direction)
    return render_template('list.html', questions=questions, sort_by=sort_by, sort_direction=sort_direction,
                           username=username)


@app.route('/question/<question_id>')
def route_question_by_id(question_id):
    username = None
    if 'username' in session:
        username = session['username']

    question = data_handler.get_data_by_question_id('question', question_id)[0]
    answers = data_handler.get_data_by_question_id('answer', question_id)

    return render_template('question.html', question=question, answers=answers, number_of_answers=len(answers),
                           username=username)


@app.route('/question/<question_id>/')
def route_question_view_count(question_id):
    data_handler.edit_view_number(question_id)

    return redirect(f'/question/{question_id}')


@app.route('/question/<question_id>/<vote>')
@functions.login_required
def route_question_vote_count(question_id, vote):

    data_handler.edit_vote_number('question', question_id, vote)

    return redirect(f'/question/{question_id}')


@app.route('/question/<question_id>/<answer_id>/<vote>')
@functions.login_required
def route_answer_vote_count(question_id, answer_id, vote):

    data_handler.edit_vote_number('answer', answer_id, vote)

    return redirect(f'/question/{question_id}')


@app.route('/add-a-question', methods=['GET', 'POST'])
@functions.login_required
def route_add_question():
    username = None
    if 'username' in session:
        username = session['username']

    if request.method == "POST":
        title = request.form['title']
        message = request.form['message']
        image = request.form['image']
        if image == "":
            image = None

        data_handler.add_question(title, message, image)
        return redirect('/')

    return render_template('add-a-question.html', username=username)


@app.route('/question/<question_id>/edit-a-question', methods=['GET', 'POST'])
@functions.login_required
def route_edit_a_question(question_id):
    question = data_handler.get_data_by_question_id('question', question_id)[0]

    if request.method == "POST":

        message = request.form['message']
        image = request.form['image']
        data_handler.edit_question('question', question_id, message, image)
        return redirect(f'/question/{question_id}')

    return render_template('edit-a-question.html', question=question)


@app.route('/question/<question_id>/delete')
@functions.login_required
def route_delete_question(question_id):
    data_handler.delete_data(question_id)
    return redirect('/')


@app.route('/question/<question_id>/new-answer', methods=["GET", "POST"])
@functions.login_required
def route_add_answer(question_id):
    question = data_handler.get_data_by_question_id('question', question_id)[0]

    if request.method == "POST":

        message = request.form['message']
        image = request.form['image']
        if image == "":
            image = None

        data_handler.add_answer(question_id, message, image)
        return redirect(f"/question/{question_id}")

    return render_template("new-answer.html", question=question)


@app.route('/search')
def search():
    search_part = request.args['search']
    questions = data_handler.search_question(search_part)
    return render_template('list.html', questions=questions)


@app.route('/<question_id>/<answer_id>/delete')
@functions.login_required
def delete_answer(question_id, answer_id):
    data_handler.delete_answer(answer_id)
    return redirect(f'/question/{question_id}')


@app.route('/<question_id>/<answer_id>/edit', methods=['GET', 'POST'])
@functions.login_required
def route_edit_answer(question_id, answer_id):
    if request.method == 'GET':
        question = data_handler.get_data_by_question_id('question', question_id)[0]
        answer = data_handler.get_answer_by_id(answer_id)[0]
        return render_template('edit-answer.html', question=question, answer=answer)

    if request.method == 'POST':
        message = request.form['message']
        image = request.form['image']
        data_handler.edit_question('answer', answer_id, message, image)
        return redirect(f'/question/{question_id}')


@app.route("/registration", methods=['GET', 'POST'])
def route_register():
    if request.method == 'GET':
        return render_template('register.html')

    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        password2 = request.form["password2"]

        if functions.username_exists(username):
            return render_template('register.html', message="The username you entered is already in use")
        elif password != password2:
            return render_template('register.html', message="Passwords do not match please fill again")
        else:
            hash_password = functions.hash_password(password)
            data_handler.register_user(username, hash_password)
            return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def route_login(invalid_login=False):
    if request.method == 'GET':
        return render_template('login.html', invalid_login=invalid_login)
    elif request.method == 'POST':
        username = request.form['username']
        plain_text_password = request.form['plain_text_password']

        if functions.username_exists(username):
            hashed_password = data_handler.get_hashed_password(username)
            if functions.verify_password(plain_text_password, hashed_password):
                session['username'] = username
                return redirect("/")
        return render_template('login.html', invalid_login=True)


@app.route('/logout')
def route_logout():
    session.pop('username', None)
    return redirect('/')


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8001,
        debug=True
    )
