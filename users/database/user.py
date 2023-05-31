from database.db import *
from fastapi.responses import JSONResponse
from botocore.exceptions import ClientError
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from uuid import uuid4
from passlib.hash import sha256_crypt
import json

def check_user(user: dict):

	if str(user["user_code"]) != "***":

		return 404, "Erken erişim kodu hatalı, uygulamayı beta aşamasında kullanabilmeniz için erken erişim kodu temin edin."


	if (len(user["user_name"]) < 3 or len(user["user_name"]) > 29) or (len(user["user_surname"]) < 3 or len(user["user_surname"])>29):

		return 404, "İsim veya Soyisim hatalı."

	elif len(user["user_phone"])==11:

		return 404, "Telefon numaranız 11 karakterli olmalıdır."

	elif len(user["user_email"]) > 39:

		return 404, "Mail adresiniz 40 karakterden büyük olamaz."

	mail_uzanti = user["user_email"].split("@")[1]
	mailBas = user["user_email"].split("@")[0]
	mailBas = mailBas.replace(".","")
	mailUser = mailBas + "@" + mail_uzanti

	if ("gmail.com" == mail_uzanti) or ("hotmail.com" == mail_uzanti) or ("outlook.com" == mail_uzanti) or ("icloud.com" == mail_uzanti) or ("yandex.com" == mail_uzanti):

		pass

	else:

		return 404, "Proje beta aşamasında olduğu için sadece gmail.com, hotmail.com, outlook.com, icloud.com ve yandex.com uzantılı mailler ile kayıt işlemi yapabilirsiniz."

	if len(user["user_password"]) < 8 or len(user["user_password"]) > 29:

		return 404, "Şifreniz 8 ile 30 karakter arasında olmalıdır."


	try:

		cursor.execute(
			'SELECT * FROM tbl_users WHERE user_email=%s or user_phone=%s', (mailUser, user["user_phone"],))
		user = cursor.fetchall()
		user_id = user[0][0]

		return 404, "Kayıt başarısız. Bu mail veya telefon numarasıyla oluşturulmuş bir hesap bulunmaktadır."

	except:

		return 1, ""


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


def create_user(user: dict):

	try:

		flag = check_user(user)

		if flag[0]!=1:

			return JSONResponse(content=flag[1], status_code=flag[0])

		token = generate_confirmation_token(user["user_email"])

		token = "https://verification.hepsitrend.tech/confirm/"+token

		strHtml = """
			
<p>Hoş geldin! Üye olduğunuz için teşekkürler. Hesabınızı etkinleştirmek için lütfen bu bağlantıyı takip edin.</p>
<p>Doğrulama bağlantısı (Bağlantının geçerlilik süresi 30 dakikadır): <a href="{}">{}</a></p>
<br>
<p><a href="https://hepsitrend.tech/">hepsitrend.tech</a> | <a href="https://ahmetfurkandemir.com/">Ahmet Furkan Demir</a></p>
<br>
<br>
""".format(token, token)

		konu = "Mail Doğrulama"
		ileti = strHtml
		#gonderenMail = "hepsitrendtech@yandex.com"
		gonderenMail = "***@yandex.com"
		#sifre = "***"
		sifre = "***"
		gonderilenMail = user["user_email"]
		message = MIMEMultipart()
		message["From"] = gonderenMail
		message["To"] = gonderilenMail
		message["Subject"] = konu
		message["Bcc"] = gonderilenMail
		message.attach(MIMEText(ileti, "html"))
		yazi = message.as_string()
		context = ssl.create_default_context()

		with smtplib.SMTP_SSL("smtp.yandex.com", 465, context=context) as server:
			server.login(gonderenMail, sifre)
			server.sendmail(gonderenMail, gonderilenMail, yazi)


		password=sha256_crypt.encrypt(user["user_password"])

		cursor.execute(
			'INSERT INTO tbl_users(user_name, user_surname, user_email, user_phone, user_password, user_search_count, user_premium, user_confirmed, user_count_attack, user_isdeleted) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
			(user["user_name"], user["user_surname"], user["user_email"], user["user_phone"], password, 20, 0, 0, 0, 0,))
		conn.commit()


	except ClientError as e:

		return JSONResponse(content=e.response["error"], status_code=500)

	return JSONResponse(content="Kayıt işlemi başarılı. Hesabınızı aktif edebilmemiz için lütfen mail kutunuzu kontrol ediniz.", status_code=201)


def delete_user(user: dict):

	try:

		cursor.execute(
			'SELECT user_password FROM tbl_users WHERE user_email=%s', (user["user_email"], ))
		userSn = cursor.fetchall()
		user_passwordd = userSn[0][0]

	except:

		return JSONResponse(content="Hatalı mail, hesap silme başarısız", status_code=404)

	try:

		password=sha256_crypt.encrypt(user["user_password"])

		if sha256_crypt.verify(user["user_password"], user_passwordd) != True:

			cursor.execute(
				'update tbl_users set user_count_attack=user_count_attack+1 where user_email=%s',
				(user["user_email"],))
			conn.commit()

			return JSONResponse(content="Hatalı şifre, hesap silme başarısız", status_code=404)


		cursor.execute(
			'update tbl_users set user_isdeleted=1 where user_email=%s',
			(user["user_email"], ))
		conn.commit()

		return JSONResponse(content="Hesap silme işlemi başarılı, sizi özleyeceğiz...", status_code=202)

	except ClientError as e:

		return JSONResponse(content=e.response["error"], status_code=500)

def update_user(user: dict):

	try:

		cursor.execute(
			'SELECT user_password FROM tbl_users WHERE user_email=%s and user_isdeleted=0', (user["user_email"], ))
		userSn = cursor.fetchall()
		user_passwordd = userSn[0][0]

	except:

		return JSONResponse(content="Hatalı mail, hesap güncelleme başarısız", status_code=404)

	try:

		
		password=sha256_crypt.encrypt(user["user_password"])

		if sha256_crypt.verify(user["user_password"], user_passwordd) != True:

			cursor.execute(
				'update tbl_users set user_count_attack=user_count_attack+1 where user_email=%s',
				(user["user_email"],))
			conn.commit()

			return JSONResponse(content="Hatalı şifre, hesap güncelleme başarısız", status_code=404)


		if (len(user["user_name"]) < 3 or len(user["user_name"]) > 29) or (len(user["user_surname"]) < 3 or len(user["user_surname"])>29):

			return JSONResponse(content="İsim veya Soyisim hatalı.", status_code=404)


		if len(user["user_password"]) < 8 or len(user["user_password"]) > 29:

			return JSONResponse(content="Şifreniz 8 ile 30 karakter arasında olmalıdır.", status_code=404)


		cursor.execute(
			'update tbl_users set user_name=%s, user_surname=%s, user_password=%s  WHERE user_email=%s',
			(user["user_name"], user["user_surname"], password, user["user_email"],))
		conn.commit()

		return JSONResponse(content="Kullanıcı güncelleme başarılı.", status_code=202)

	except ClientError as e:

		return JSONResponse(content=e.response["error"], status_code=500)

def login_user(user: dict):

	try:

		cursor.execute(
			'SELECT user_id, user_password, user_confirmed FROM tbl_users WHERE user_email=%s and user_isdeleted=0', (user["user_email"], ))
		userSn = cursor.fetchall()

		user_id = userSn[0][0]
		user_passwordd = userSn[0][1]
		user_confirmed = userSn[0][2]

		if user_confirmed==0:

			cursor.execute(
				'update tbl_users set user_count_attack=user_count_attack+1 where user_email=%s',
				(user["user_email"],))
			conn.commit()

			return None, -99

		if sha256_crypt.verify(user["user_password"], user_passwordd) != True:

			cursor.execute(
				'update tbl_users set user_count_attack=user_count_attack+1 where user_email=%s',
				(user["user_email"],))
			conn.commit()

			return False, -99

		return True, int(user_id)

	except:

		return False, -99


def get_user_id(id: int):

	try:

		cursor.execute(
			'SELECT * FROM tbl_users WHERE user_id=%s and user_isdeleted=0 and user_confirmed=1', (id,))
		user = cursor.fetchone()

		dictt = {"user_id": user[0], "user_name": user[1], "user_surname": user[2], "user_email": user[3], "user_phone": user[4],
				 "user_password": user[5], "user_search_count": user[6], "user_premium": user[7], "user_confirmed": user[8], 
				 "user_count_attack": user[9], "user_isdeleted": user[10], "user_token": user[11]}

		return JSONResponse(content=dictt , status_code=200)

	except:

		return JSONResponse(content="Kullanıcı bulunamadı." , status_code=404)
	

