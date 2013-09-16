import re
import os

from flask import Flask, render_template, request, send_from_directory, jsonify
from bs4 import BeautifulSoup
import requests


app = Flask(__name__)
app.config['asset_url'] = 'http://s3.amazonaws.com/okcreeper_assets/'

def login():
    credentials = {'username': 'creepyqs@gmail.com',
                   'password': 'hUB1PWbnPNkLZ5R'}
    s = requests.Session()
    r = s.post('https://www.okcupid.com/login', data=credentials)
    if 'creepyqs' not in r.text or r.status_code != 200:
        abort(500)
    return s

session_cookie = login().cookies['session']

def get_session():
    s = requests.Session()
    s.cookies.update({'session': session_cookie})
    return s

@app.route('/')
def index():
    return render_template('okcreeper.html',
                           asset_url=app.config['asset_url'])

@app.route('/creep/.json')
@app.route('/creep/<username>.json')
def creep(username=None):

    if username == None:
        return jsonify({'error':"You have to enter a username"})

    response = {}
    username = username.strip()

    if username.lower() == 'creepyqs':
        return jsonify({'error':"I'm sorry, Dave. I'm afraid I can't do that."})

    s = get_session()

    r = s.get('http://www.okcupid.com/profile/%s' % username, timeout=10, stream=False)
    soup = BeautifulSoup(r.text, "lxml")
    if soup.title.string == 'OkCupid |  Account not found':
        return jsonify({'error':"Sorry, no one with that username exists"})

    # Get proper capitalization
    response['username'] = soup.find('p', class_='username').string
    response['info'] = soup.find('p', class_='info').string.strip()

    try:
        replies = re.search(r'<p>Replies <span class="([\w]+)">([^<]+)</span></p>', r.text)
        replies = (replies.group(1), replies.group(2))
        response['replies'] = {}
        response['replies']['color'] = replies[0]
        response['replies']['message'] = replies[1]
    except: pass

    response['details'] = []
    for dt in soup.find_all('dt'):
        detail_name = dt.string

        if 'Last Online' in detail_name:
            try:
                detail_value = dt.find_next_sibling('dd').find('span').string
            except:
                detail_value = u'Online now!'
        else:
            detail_value = dt.find_next_sibling('dd').string

        response['details'].append({'name':detail_name, 'value':detail_value})

    response['essays'] = []
    for a in soup.find_all('a', class_='essay_title'):
        essay_title = a.contents[0]
        # The "I'm looking for" essay is a special case
        if 'looking for' in essay_title: 
            continue
        essay_content = a.find_next_sibling('div').contents[1].encode_contents().decode('utf-8')
        essay_content = essay_content.replace("&lt;br/&gt", "<br>").strip()
        essay_content = re.sub('href="/', 'href="http://www.okcupid.com/',
                               essay_content)

        response['essays'].append({'title': essay_title,
                                   'content': essay_content})

    looking_for = soup.find('div', class_='what_i_want')
    try:
        response['looking_for'] = [li.string.strip() for li in looking_for.ul.find_all('li')]
    except: pass

    # extract photos
    r = s.get('http://www.okcupid.com/profile/%s/photos' % username, timeout=10, stream=False)
    soup = BeautifulSoup(r.text, "lxml")
    response['photos'] = []
    for div in soup.find_all('div', class_='img'):
        response['photos'].append(div.img['src'])        

    return jsonify(**response)

@app.route('/questions/<username>/<int:page_marker>.json')
def questions(username, page_marker):
    response = {'questions': [], 'more': True}

    s = get_session()
    username = username.strip().lower()

    questions = []
    low = 1 + page_marker * 10

    for i in range(3):
        r = s.get('http://www.okcupid.com/profile/{}/questions?low={}&i_care=1'.format(username, low), timeout=10, stream=False)
        if 'answered any public questions' in r.text:
            response['more'] = False
            break
        if low == 1:
            response['total_questions'] = re.search(r'([\d]+) questions</p>', r.text).group(1)
        response['questions'].extend(extract_questions(r.text))
        low += 10

    return jsonify(**response)

def extract_questions(text):
    questions = []
    soup = BeautifulSoup(text, "lxml")
    for span in soup.find_all('span', id=re.compile('^answer_target_')):
        a = str(span.string).strip()
        if a != 'Answer publicly to see my public answer' and a != '':
            q = span.parent.find_previous_sibling('p', class_='qtext').string
            question = {'question': q, 'answer': a}
            try:
                question['explanation'] = span.find_next_sibling('span', class_='note').string
            except: pass
            questions.append(question)
    return questions