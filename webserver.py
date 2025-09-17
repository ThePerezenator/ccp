from flask import Flask, request, render_template, current_app as app
import sqlite

port = "5001"
path = "/CCP"


app = Flask(__name__, static_folder='static')

#headings for tables
setlist_headings = ("Song", "​", "Artist", "Release")
main_headings = ("Setlist", "")

#main home page
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/recipie/")
def recipie():
    if request.args.get('recipie') != None:
        recipie = request.args.get('recipie')
        recipie_data = sqlite.open({recipie})
    return render_template("recipies.html", recipie_data=recipie_data)


@app.route("/healthcheck/", methods=["GET"])
def healthcheck():
    print("Healthcheck!")
    return "200", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, debug=True)
