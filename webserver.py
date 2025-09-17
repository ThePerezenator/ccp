from flask import Flask, redirect, render_template, request, current_app as app
import sqlite
import os
import string

port = "5000"
path = "/ccp"


app = Flask(__name__, static_folder='static')

#headings for tables
setlist_headings = ("Song", "​", "Artist", "Release")
main_headings = ("Setlist", "")

#main home page
#users can create a new setlist, or open or delete an existing one
@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        setlist = request.form["setlist"]
        if setlist:
            sqlite.add_setlist(setlist)
    if request.args.get('delete') != None:
        setlist = request.args.get('delete')
        try:
            print(f"{path}/{setlist}")
            os.remove(f"{path}/Setlists/{setlist}")
            print(f"DELETED {setlist}")
            return redirect(f"{request.url_root}")
        except:
            print(f"ERROR DELETING {setlist}")

    main_data = zip(os.listdir(f"{path}/Setlists"), )
    return render_template("index.html", main_data=main_data, main_headings=main_headings)

@app.route("/healthcheck/", methods=["GET"])
def healthcheck():
    print("Healthcheck!")
    return "200", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port, debug=True)
