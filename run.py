from flask import Flask, redirect, render_template, request
import sqlite3
import pickle

connection = sqlite3.connect("datastore.db", check_same_thread=False)
cursor = connection.cursor()

model = pickle.load(open("dengue_prediction_model.pkl", "rb"))
scaler = pickle.load(open("Standarscaler.pkl", "rb"))

app = Flask(__name__)
@app.route("/", methods = ["POST", "GET"])
def home():
    return render_template("login.html")

@app.route("/index", methods = ["POST", "GET"])
def index():
    return render_template("index.html")

@app.route("/loginresult", methods = ["POST", "GET"])
def login():
    try:
        if request.method == "POST":
            details = request.form
            email = details["email"]
            password = details["password"]
            print(email)
            print(password)
            if email == "admin147@master.com" and password == "Admin4u$":
                return render_template("index.html")
            else:
                return redirect("/")
    except:
        return redirect("/")

@app.route("/predict", methods = ["POST", "GET"])
def predict():
    try:
        if request.method == "POST":
            cursor = connection.cursor()

            feature = request.form
            print(feature)
            city = int(feature["city"])
            year = int(feature["Year"])
            week_of_year = int(feature["Week_of_year"])
            ndvi_se = float(feature["ndvi_se"])
            precipitation_amt_mm = float(feature["precipitation_amt_mm"])
            reanalysis_dew_point_temp_k = float(feature["reanalysis_dew_point_temp_k"])
            reanalysis_precip_amt_kg_per_m2 = float(feature["reanalysis_precip_amt_kg_per_m2"])
            station_precip_mm = float(feature["station_precip_mm"])
    
            scaled = scaler.transform([[city,year,week_of_year,ndvi_se,precipitation_amt_mm,reanalysis_dew_point_temp_k,reanalysis_precip_amt_kg_per_m2,station_precip_mm,1,2]])
            print(scaled[0][0:8])
            value = model.predict([scaled[0][0:8]])[0]

            data = [city,year,week_of_year,ndvi_se,precipitation_amt_mm,reanalysis_dew_point_temp_k,reanalysis_precip_amt_kg_per_m2,station_precip_mm]

            cursor.execute('INSERT INTO Dengue_Cases_Data values(?,?,?,?,?,?,?,?,?)',(city,year,week_of_year,ndvi_se,precipitation_amt_mm,reanalysis_dew_point_temp_k,reanalysis_precip_amt_kg_per_m2,station_precip_mm, int(value)))
            connection.commit()
            for i in cursor.execute("SELECT * FROM Dengue_Cases_Data"):
                print(i)
            cursor.close()

            return render_template("result.html", value =int(value), data = data)
    except Exception as e:
        print(e)
        return redirect("/")

@app.route("/table", methods = ["POST", "GET"])
def table():
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Dengue_Cases_Data")
        r = cursor.fetchall()
        cursor.close()
        return render_template("table.html", value = r,)
    except:
        return redirect("/")

if __name__ == "__main__":
    app.run(debug= True)