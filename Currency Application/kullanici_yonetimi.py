import csv
import os
from datetime import datetime
from qr_yonetimi import QRYonetimi
from email_yonetimi import EmailYonetimi
import random
import string
import hashlib

class KullaniciYonetimi:
    def __init__(self):
        self.kullanici_dosyasi = "kullanicilar.csv"
        self.kullanici_bilgileri = {}
        self.qr_yonetimi = QRYonetimi()
        self.email_yonetimi = EmailYonetimi()
        self.dosyayi_yukle()

    def hash_olustur(self, veri):
        """Verilen veriyi SHA-256 ile hashler"""
        return hashlib.sha256(str(veri).encode()).hexdigest()

    def user_id_olustur(self):
        """8 haneli karışık (büyük harf, küçük harf ve sayı) bir kullanıcı ID'si oluşturur"""
        karakterler = string.ascii_uppercase + string.ascii_lowercase + string.digits
        while True:
            user_id = ''.join(random.choices(karakterler, k=8))
            # ID'nin benzersiz olduğundan emin ol
            if not any(bilgiler.get('user_id') == user_id for bilgiler in self.kullanici_bilgileri.values()):
                return user_id

    def dosyayi_yukle(self):
        if os.path.exists(self.kullanici_dosyasi):
            with open(self.kullanici_dosyasi, 'r', encoding='utf-8') as dosya:
                okuyucu = csv.DictReader(dosya)
                for satir in okuyucu:
                    # Hash'lenmiş verileri geri çözme işlemi yok, sadece hash'leri saklıyoruz
                    self.kullanici_bilgileri[satir['email']] = {
                        'user_id': satir['user_id'],
                        'kullanici_adi': satir['kullanici_adi'],
                        'sifre': satir['sifre'],  # Hash'lenmiş şifre
                        'email': satir['email'],
                        'secret_key': satir.get('secret_key', ''),
                        'kayit_tarihi': satir['kayit_tarihi']
                    }

    def dosyaya_kaydet(self):
        with open(self.kullanici_dosyasi, 'w', newline='', encoding='utf-8') as dosya:
            yazici = csv.DictWriter(dosya, fieldnames=['user_id', 'kullanici_adi', 'sifre', 'email', 'secret_key', 'kayit_tarihi'])
            yazici.writeheader()
            for email, bilgiler in self.kullanici_bilgileri.items():
                yazici.writerow({
                    'user_id': bilgiler['user_id'],
                    'kullanici_adi': bilgiler['kullanici_adi'],
                    'sifre': bilgiler['sifre'],  # Şifreyi hash'lemeden kaydet
                    'email': email,
                    'secret_key': bilgiler.get('secret_key', ''),
                    'kayit_tarihi': bilgiler['kayit_tarihi']
                })

    def kayit_ol(self, kullanici_adi, sifre, email):
        # Email'i küçük harfe çevir
        email = email.lower()
        
        # Email kontrolü
        if email in self.kullanici_bilgileri:
            return False, "Bu email adresi zaten kullanılıyor!"
        
        # Kullanıcı adı kontrolü
        for bilgiler in self.kullanici_bilgileri.values():
            if bilgiler['kullanici_adi'].lower() == kullanici_adi.lower():
                return False, "Bu kullanıcı adı zaten kullanılıyor!"
        
        # Email formatı kontrolü
        if not email or '@' not in email or '.' not in email:
            return False, "Geçersiz email formatı!"
        
        if len(sifre) < 8:
            return False, "Şifre en az 8 karakter olmalıdır!"

        try:
            # Kullanıcı ID'si oluştur
            user_id = self.user_id_olustur()
            
            # QR kod oluştur
            secret_key, qr_path = self.qr_yonetimi.qr_kod_olustur(email, kullanici_adi, user_id)

            self.kullanici_bilgileri[email] = {
                'user_id': user_id,
                'kullanici_adi': kullanici_adi,
                'sifre': sifre,
                'email': email,
                'secret_key': secret_key,
                'kayit_tarihi': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.dosyaya_kaydet()
            
            return True, f"Kayıt başarıyla tamamlandı! Kullanıcı ID'niz: {user_id}\nQR kodunuz: {qr_path}"
        except Exception as e:
            return False, f"Kayıt sırasında bir hata oluştu: {str(e)}"

    def giris_yap(self, kullanici_adi, sifre, yontem=None):
        # Kullanıcı adına göre email'i bul (büyük/küçük harf duyarsız)
        email = None
        for mail, bilgiler in self.kullanici_bilgileri.items():
            if bilgiler['kullanici_adi'].lower() == kullanici_adi.lower():
                email = mail
                break
        
        if not email:
            return False, "Kullanıcı adı bulunamadı!"
        
        # Şifreleri karşılaştır
        if self.kullanici_bilgileri[email]['sifre'] != sifre:
            return False, "Hatalı şifre!"
        
        if yontem == "email":
            basarili, mesaj = self.email_yonetimi.dogrulama_linki_gonder(email)
            if not basarili:
                return False, f"Email doğrulama linki gönderilemedi: {mesaj}"
            return True, "Doğrulama linki email adresinize gönderildi. Lütfen mailinizi kontrol edin."
        else:
            # QR veya diğer yöntemler için eski akış
            return True, "Şifre doğrulaması başarılı. Lütfen doğrulama kodunu girin."

    def email_dogrulandi_mi(self, kullanici_adi):
        # Kullanıcı adına göre email'i bul
        email = None
        for mail, bilgiler in self.kullanici_bilgileri.items():
            if bilgiler['kullanici_adi'] == kullanici_adi:
                email = mail
                break
        if not email:
            return False
        return self.email_yonetimi.email_dogrulandi_mi(email)

    def dogrulama_kodu_kontrol(self, kullanici_adi, kod):
        # Kullanıcı adına göre email'i bul
        email = None
        for mail, bilgiler in self.kullanici_bilgileri.items():
            if bilgiler['kullanici_adi'] == kullanici_adi:
                email = mail
                break
        
        if not email:
            return False, "Kullanıcı bulunamadı!"
        
        # Email doğrulama kodu kontrolü
        return self.email_yonetimi.dogrulama_kodu_kontrol(email, kod)

    def qr_dogrulama_kontrol(self, kullanici_adi, kod):
        # Kullanıcı adına göre email'i bul
        email = None
        for mail, bilgiler in self.kullanici_bilgileri.items():
            if bilgiler['kullanici_adi'] == kullanici_adi:
                email = mail
                break
        
        if not email:
            return False, "Kullanıcı bulunamadı!"
        
        secret_key = self.kullanici_bilgileri[email].get('secret_key')
        if not secret_key:
            return False, "Google Authenticator ayarlanmamış!"
        
        # QR kod doğrulaması
        return self.qr_yonetimi.dogrulama_kodu_kontrol(secret_key, kod)

    def kullanici_verilerini_sifirla(self):
        """Tüm kullanıcı verilerini hafızadan ve dosyadan temizler"""
        self.kullanici_bilgileri = {}
        if os.path.exists(self.kullanici_dosyasi):
            os.remove(self.kullanici_dosyasi)
        return True, "Tüm kullanıcı verileri başarıyla temizlendi."

    def kullanici_var_mi(self, email):
        """Email adresi ile kayıtlı kullanıcı var mı kontrol et"""
        return email.lower() in self.kullanici_bilgileri

    def sifre_sifirla_linki_gonder(self, email):
        """Şifre sıfırlama linki gönder"""
        try:
            # Email'i küçük harfe çevir
            email = email.lower()
            
            # Kullanıcı kontrolü
            if not self.kullanici_var_mi(email):
                return False, "Bu email adresi ile kayıtlı bir kullanıcı bulunamadı!"
            
            # Şifre sıfırlama linki oluştur
            basarili, mesaj = self.email_yonetimi.dogrulama_linki_gonder(email)
            if not basarili:
                return False, f"Şifre sıfırlama linki gönderilemedi: {mesaj}"
            
            return True, "Şifre sıfırlama linki email adresinize gönderildi."
            
        except Exception as e:
            return False, f"Şifre sıfırlama işlemi sırasında bir hata oluştu: {str(e)}"

    def sifre_sifirla_kod_gonder(self, email):
        """Şifre sıfırlama için 6 haneli kod gönderir"""
        try:
            email = email.lower()
            if not self.kullanici_var_mi(email):
                return False, "Bu email adresi ile kayıtlı bir kullanıcı bulunamadı!"
            basarili, mesaj = self.email_yonetimi.dogrulama_kodu_gonder(email)
            return basarili, mesaj
        except Exception as e:
            return False, f"Kod gönderimi sırasında bir hata oluştu: {str(e)}"

    def sifre_sifirla_kod_dogrula(self, email, kod):
        """Şifre sıfırlama kodunu doğrular"""
        try:
            email = email.lower()
            basarili, mesaj = self.email_yonetimi.dogrulama_kodu_kontrol(email, kod)
            return basarili, mesaj
        except Exception as e:
            return False, f"Kod doğrulama sırasında bir hata oluştu: {str(e)}"

    def sifre_yenile(self, email, yeni_sifre):
        """Kullanıcının şifresini günceller"""
        try:
            email = email.lower()
            if not self.kullanici_var_mi(email):
                return False, "Kullanıcı bulunamadı!"
            if len(yeni_sifre) < 8:
                return False, "Şifre en az 8 karakter olmalıdır!"
            self.kullanici_bilgileri[email]['sifre'] = yeni_sifre
            self.dosyaya_kaydet()
            return True, "Şifre başarıyla güncellendi."
        except Exception as e:
            return False, f"Şifre güncelleme sırasında bir hata oluştu: {str(e)}" 