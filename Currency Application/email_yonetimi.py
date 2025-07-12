import os
import re
import random
import string
import logging
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import auth, credentials
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailYonetimi:
    def __init__(self):
        # .env dosyasından email ayarlarını yükle
        load_dotenv()
        
        # Doğrulama kodları için sözlük
        self.dogrulama_kodlari = {}

        # Firebase Admin başlat
        if not firebase_admin._apps:
            cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS', 'Firebase-config.json'))
            firebase_admin.initialize_app(cred)
            
        # Loglama ayarları
        logging.basicConfig(
            filename='email_logs.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Email şablonları
        self.email_templates = {
            'verification': {
                'subject': 'Email Doğrulama',
                'template': """
                <html>
                    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px;">
                            <h2 style="color: #333;">Email Doğrulama</h2>
                            <p>Merhaba,</p>
                            <p>Email adresinizi doğrulamak için aşağıdaki butona tıklayın:</p>
                            <div style="text-align: center; margin: 30px 0;">
                                <a href="{link}" style="background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                    Email Adresimi Doğrula
                                </a>
                            </div>
                            <p>Veya aşağıdaki linki tarayıcınıza kopyalayın:</p>
                            <p style="word-break: break-all; color: #666;">{link}</p>
                            <p style="color: #666; font-size: 0.9em;">Bu link 1 saat süreyle geçerlidir.</p>
                            <p style="color: #666; font-size: 0.9em;">Eğer bu işlemi siz yapmadıysanız, lütfen bu emaili dikkate almayın.</p>
                        </div>
                    </body>
                </html>
                """
            }
        }

        # Email gönderme ayarları
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.sender_email = os.getenv('SENDER_EMAIL')

    def set_email_template(self, template_name, subject, template):
        """Yeni email şablonu ekle veya mevcut şablonu güncelle"""
        self.email_templates[template_name] = {
            'subject': subject,
            'template': template
        }
        logging.info(f"Email şablonu güncellendi: {template_name}")

    def email_kontrol(self, email):
        # Daha kapsamlı email formatı kontrolü
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not email:
            return False, "Email adresi boş olamaz!"
        
        if not re.match(pattern, email):
            return False, f"Geçersiz email formatı: {email}\nÖrnek format: kullanici@domain.com"
        
        return True, "Email formatı geçerli"

    def dogrulama_kodu_olustur(self):
        # 6 haneli random kod oluştur
        return ''.join(random.choices(string.digits, k=6))

    def dogrulama_kodu_gonder(self, email):
        # Email formatı kontrolü
        format_gecerli, mesaj = self.email_kontrol(email)
        if not format_gecerli:
            return False, mesaj

        # Yeni doğrulama kodu oluştur
        kod = self.dogrulama_kodu_olustur()
        son_gecerlilik = datetime.now() + timedelta(minutes=5)
        
        # Kodu kaydet
        self.dogrulama_kodlari[email] = {
            'kod': kod,
            'son_gecerlilik': son_gecerlilik
        }

        
        return True, "Doğrulama kodu oluşturuldu ve konsola yazdırıldı."

    def dogrulama_kodu_kontrol(self, email, kod):
        # Email için kayıtlı kod var mı kontrol et
        if email not in self.dogrulama_kodlari:
            return False, "Doğrulama kodu bulunamadı. Lütfen yeni kod talep edin."
        
        kayit = self.dogrulama_kodlari[email]
        
        # Kodun süresi geçmiş mi kontrol et
        if datetime.now() > kayit['son_gecerlilik']:
            del self.dogrulama_kodlari[email]
            return False, "Doğrulama kodunun süresi dolmuş. Lütfen yeni kod talep edin."
        
        # Kodu kontrol et
        if kod == kayit['kod']:
            # Başarılı doğrulama sonrası kodu sil
            del self.dogrulama_kodlari[email]
            return True, "Doğrulama başarılı!"
        else:
            return False, "Geçersiz doğrulama kodu!"

    def email_gonder(self, to_email, subject, body):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'html'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Email gönderme hatası: {str(e)}")
            return False

    def send_custom_email(self, email, link, template_name='verification', max_retries=3):
        
        if template_name not in self.email_templates:
            error_msg = f"Şablon bulunamadı: {template_name}"
            logging.error(error_msg)
            return False, error_msg

        template = self.email_templates[template_name]
        sender_email = os.getenv('GMAIL_ADDRESS')
        app_password = os.getenv('GMAIL_APP_PASSWORD')

        if not sender_email or not app_password:
            error_msg = "Gmail ayarları eksik. Lütfen .env dosyasını kontrol edin."
            logging.error(error_msg)
            return False, error_msg

        for attempt in range(max_retries):
            try:
                # MIME ayarları
                message = MIMEMultipart()
                message["From"] = sender_email
                message["To"] = email
                message["Subject"] = template['subject']
                
                # Şablonu formatla
                html_content = template['template'].format(link=link)
                message.attach(MIMEText(html_content, "html"))
                
                # SMTP_SSL ile güvenli bağlantı kur ve email gönder
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    server.login(sender_email, app_password)
                    server.sendmail(sender_email, email, message.as_string())
                
                success_msg = f"E-posta başarıyla gönderildi: {email}"
                logging.info(success_msg)
                return True, success_msg
                
            except smtplib.SMTPAuthenticationError:
                error_msg = "SMTP kimlik doğrulama hatası. Lütfen Gmail ayarlarınızı kontrol edin."
                logging.error(error_msg)
                return False, error_msg
                
            except smtplib.SMTPException as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2  # Her denemede bekleme süresini artır
                    logging.warning(f"E-posta gönderimi başarısız (deneme {attempt + 1}/{max_retries}). {wait_time} saniye sonra tekrar denenecek.")
                    time.sleep(wait_time)
                    continue
                error_msg = f"E-posta gönderilemedi: {str(e)}"
                logging.error(error_msg)
                return False, error_msg
                
            except Exception as e:
                error_msg = f"Beklenmeyen hata: {str(e)}"
                logging.error(error_msg)
                return False, error_msg

    def dogrulama_linki_gonder(self, email):
        try:
            # Kullanıcıyı bul veya oluştur
            try:
                user = auth.get_user_by_email(email)
            except auth.UserNotFoundError:
                user = auth.create_user(email=email)
            
            # Firebase'den doğrulama linki oluştur
            verification_link = auth.generate_email_verification_link(email)
            
            # Özel e-posta gönderme fonksiyonunu kullan
            success, message = self.send_custom_email(email, verification_link)
            return success, message
                
        except Exception as e:
            return False, f"Doğrulama e-postası gönderilemedi: {str(e)}"

    def email_dogrulandi_mi(self, email):
        try:
            user = auth.get_user_by_email(email)
            return user.email_verified
        except Exception:
            return False 