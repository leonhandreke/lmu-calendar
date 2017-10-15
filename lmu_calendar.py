import requests
import flask
import lxml.html


app = flask.Flask(__name__)

@app.route("/stundenplan/<semester_id>")
def get_stundenplan(semester_id):
    username = flask.request.args.get("username")
    password = flask.request.args.get("password")

    if not (username and password):
        flask.abort(403)

    session = requests.Session()
    session.post("https://lsf.verwaltung.uni-muenchen.de/qisserver/rds?state=user&type=1&category=auth.login&startpage=portal.vm&breadCrumbSource=portal",
                 data={"asdf": username, "fdsa": password})

    # Register requested semester in session
    session.get("https://lsf.verwaltung.uni-muenchen.de/qisserver/rds?state=user&type=0&k_semester.semid={semester_id}&idcol=k_semester.semid&idval={semester_id}&purge=n&getglobal=semester".format(semester_id=semester_id))

    r = session.get("https://lsf.verwaltung.uni-muenchen.de/qisserver/rds?state=wplan&act=show&show=plan&P.subc=plan&navigationPosition=functions%2CscheduleLoggedin&breadcrumb=schedule&topitem=functions&subitem=scheduleLoggedin")
    page = lxml.html.fromstring(r.content)

    ical_download_buttons = page.xpath('.//a[contains(text(), "Stundenplan als iCal-Datei herunterladen")]')
    if not ical_download_buttons:
        return '', 204  # No Content

    ical_response = session.get(ical_download_buttons[0].get("href"))

    response = flask.Response(ical_response.content)
    response.headers["Cache-Control"] = "max-age=7200, private, must-revalidate"
    return response
