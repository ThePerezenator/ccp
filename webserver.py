from flask import Flask, render_template, current_app as app

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
    return render_template("recipie.html")


@app.route("/healthcheck/", methods=["GET"])
def healthcheck():
    print("Healthcheck!")
    return "200", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, debug=True)
