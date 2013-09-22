from flask import Flask

app = Flask(__name__)

@app.route('/')
def default():
    pass

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        pass
    else:
        pass

@app.route('/logout')
def logout():
    pass

@app.route('/idea')
def random_idea():
    pass

@app.route('/idea/create', methods = ['POST'])
def create_idea():
    pass

@app.route('/idea/<int:idea_id>')
def read_idea(idea_id):
    pass

@app.route('/pin/<int:idea_id>')
def pin_idea(idea_id):
    pass

@app.route('/ideas')
def read_ideas():
    pass

@app.route('/user/<username>/ideas')
def ideas_for_user(username):
    # if current user, show pinned ideas
    pass

@app.route('/idea/<int:idea_id>/post', methods = ['POST'])
def post_to_idea(idea_id):

if __name__ == '__main__':
    app.run()
