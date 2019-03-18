from flaskr import app

# start auto-scaling

app.run('0.0.0.0', port=5001, debug=False)