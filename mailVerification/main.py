from flask import Flask
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime, timedelta
from db import *

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World'

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer("***")
    now = datetime.now()
    email+="-"+now.strftime("%d/%m/%Y %H:%M:%S")
    return serializer.dumps(email, salt="***")


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer("***")
    try:
        email = serializer.loads(
            token,
            salt="***",
            max_age=expiration
        )
    except:
        return False
    return email


@app.route("/confirm/<token>")
def confirm_email(token):

    emailTemp = confirm_token(token)

    if emailTemp==False:

        return """

        <html>
  <head>
    <link href="https://fonts.googleapis.com/css?family=Nunito+Sans:400,400i,700,900&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet"
        integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">

    <title>hepsitrend.tech | Mail Doğrulama</title>

    <link rel="icon" href="https://avatars.mds.yandex.net/get-yapic/27274/WSHQwDMSKXuEcJ4jNFExzLLaoyI-1/islands-200">

  </head>
    <style>
      body {
        text-align: center;
        padding: 40px 0;
        background: #EBF0F5;
      }
        h1 {
          color: #da2020;
          font-family: "Nunito Sans", "Helvetica Neue", sans-serif;
          font-weight: 900;
          font-size: 40px;
          margin-bottom: 10px;
        }
        p {
          color: #404F5E;
          font-family: "Nunito Sans", "Helvetica Neue", sans-serif;
          font-size:20px;
          margin: 0;
        }
      i {
        color: #da2020;
        font-size: 100px;
        line-height: 200px;
        margin-left:-15px;
      }
      .card {
        background: white;
        padding: 60px;
        border-radius: 4px;
        box-shadow: 0 2px 3px #C8D0D8;
        display: inline-block;
        margin: 0 auto;
      }
    </style>
    <body>
      <div class="card">
      <div style="border-radius:200px; height:200px; width:200px; background: #F8FAF5; margin:0 auto;">
        <i class="checkmark">&#x2717;</i>
      </div>
        <h1>Başarısız</h1> 
        <p>Girilen token hatalı, hesabınız aktif edilemedi.</p>
        <br></br>

        <a href="https://hepsitrend.tech/" class="btn btn-danger" role="button">Ana sayfaya dön</a>
      </div>
    </body>
</html>

        """

    email = emailTemp.split("-")[0]
    email = str(email)

    dataTime = emailTemp.split("-")[1]
    datetime_object = datetime.strptime(dataTime ,'%d/%m/%Y %H:%M:%S')

    now = datetime.now()

    new_final_time = datetime_object + timedelta(minutes=30)

    if now>=new_final_time:

        return """

        <html>
  <head>
    <link href="https://fonts.googleapis.com/css?family=Nunito+Sans:400,400i,700,900&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet"
        integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">

    <title>hepsitrend.tech | Mail Doğrulama</title>

    <link rel="icon" href="https://avatars.mds.yandex.net/get-yapic/27274/WSHQwDMSKXuEcJ4jNFExzLLaoyI-1/islands-200">
  </head>
    <style>
      body {
        text-align: center;
        padding: 40px 0;
        background: #EBF0F5;
      }
        h1 {
          color: #da2020;
          font-family: "Nunito Sans", "Helvetica Neue", sans-serif;
          font-weight: 900;
          font-size: 40px;
          margin-bottom: 10px;
        }
        p {
          color: #404F5E;
          font-family: "Nunito Sans", "Helvetica Neue", sans-serif;
          font-size:20px;
          margin: 0;
        }
      i {
        color: #da2020;
        font-size: 100px;
        line-height: 200px;
        margin-left:-15px;
      }
      .card {
        background: white;
        padding: 60px;
        border-radius: 4px;
        box-shadow: 0 2px 3px #C8D0D8;
        display: inline-block;
        margin: 0 auto;
      }
    </style>
    <body>
      <div class="card">
      <div style="border-radius:200px; height:200px; width:200px; background: #F8FAF5; margin:0 auto;">
        <i class="checkmark">&#x2717;</i>
      </div>
        <h1>Başarısız</h1> 
        <p>Doğrulama bağlantısının süresi doldu, hesabınız aktif hale getirilemedi.</p>
        <br></br>

        <a href="https://hepsitrend.tech/" class="btn btn-danger" role="button">Ana sayfaya dön</a>
      </div>
    </body>
</html>

        """

    cursor.execute('SELECT user_id, user_confirmed FROM tbl_users WHERE user_email=%s and user_isdeleted=0',(email,))
    user = cursor.fetchall()
    print(user)
    user_id = user[0][0]
    user_confirmed = user[0][1]

    if user_confirmed==1:

        return """

        <html>
  <head>
    <link href="https://fonts.googleapis.com/css?family=Nunito+Sans:400,400i,700,900&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet"
        integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">

    <title>hepsitrend.tech | Mail Doğrulama</title>

    <link rel="icon" href="https://avatars.mds.yandex.net/get-yapic/27274/WSHQwDMSKXuEcJ4jNFExzLLaoyI-1/islands-200">
  </head>
    <style>
      body {
        text-align: center;
        padding: 40px 0;
        background: #EBF0F5;
      }
        h1 {
          color: #fe8a0c;
          font-family: "Nunito Sans", "Helvetica Neue", sans-serif;
          font-weight: 900;
          font-size: 40px;
          margin-bottom: 10px;
        }
        p {
          color: #404F5E;
          font-family: "Nunito Sans", "Helvetica Neue", sans-serif;
          font-size:20px;
          margin: 0;
        }
      i {
        color: #fe8a0c;
        font-size: 100px;
        line-height: 200px;
        margin-left:-15px;
      }
      .card {
        background: white;
        padding: 60px;
        border-radius: 4px;
        box-shadow: 0 2px 3px #C8D0D8;
        display: inline-block;
        margin: 0 auto;
      }
    </style>
    <body>
      <div class="card">
      <div style="border-radius:200px; height:200px; width:200px; background: #F8FAF5; margin:0 auto;">
        <i class="checkmark">&#9675;</i>
      </div>
        <h1>Hesabınız zaten aktif</h1> 
        <br></br>
        <a href="https://hepsitrend.tech/login" class="btn btn-warning" role="button">Giriş Yap</a>
      </div>
    </body>
</html>

        """

    cursor.execute('UPDATE tbl_users SET user_confirmed=%s WHERE user_id=%s',(1,user_id,))
    conn.commit()

    return """<html>
  <head>
    <link href="https://fonts.googleapis.com/css?family=Nunito+Sans:400,400i,700,900&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet"
        integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">

    <title>hepsitrend.tech | Mail Doğrulama</title>

    <link rel="icon" href="https://avatars.mds.yandex.net/get-yapic/27274/WSHQwDMSKXuEcJ4jNFExzLLaoyI-1/islands-200">
  </head>
    <style>
      body {
        text-align: center;
        padding: 40px 0;
        background: #EBF0F5;
      }
        h1 {
          color: #88B04B;
          font-family: "Nunito Sans", "Helvetica Neue", sans-serif;
          font-weight: 900;
          font-size: 40px;
          margin-bottom: 10px;
        }
        p {
          color: #404F5E;
          font-family: "Nunito Sans", "Helvetica Neue", sans-serif;
          font-size:20px;
          margin: 0;
        }
      i {
        color: #9ABC66;
        font-size: 100px;
        line-height: 200px;
        margin-left:-15px;
      }
      .card {
        background: white;
        padding: 60px;
        border-radius: 4px;
        box-shadow: 0 2px 3px #C8D0D8;
        display: inline-block;
        margin: 0 auto;
      }
    </style>
    <body>
      <div class="card">
      <div style="border-radius:200px; height:200px; width:200px; background: #F8FAF5; margin:0 auto;">
        <i class="checkmark">✓</i>
      </div>
        <h1>Başarılı</h1> 
        <p>Hesabınız aktif hale gelmiştir.</p>
        <br></br>

        <a href="https://hepsitrend.tech/login" class="btn btn-success" role="button">Giriş Yap</a>

      </div>
    </body>
</html>"""

if __name__ == '__main__':

    app.run(host="0.0.0.0", port=5006)