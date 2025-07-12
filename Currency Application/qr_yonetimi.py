import os
import pyotp
import qrcode
from datetime import datetime

class QRYonetimi:
    def __init__(self):
        self.qr_codes_dir = "qr_codes"
        if not os.path.exists(self.qr_codes_dir):
            os.makedirs(self.qr_codes_dir)

    def qr_kod_olustur(self, email, kullanici_adi, user_id):
        # Secret key oluştur
        secret_key = pyotp.random_base32()
        
        # TOTP nesnesi oluştur
        totp = pyotp.TOTP(secret_key)
        
        # QR kod için URI oluştur
        provisioning_uri = totp.provisioning_uri(
            name=user_id,  # Email yerine User ID kullan
            issuer_name="Doviz Uygulamasi"
        )
        
        # QR kodu oluştur
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=6,
            border=2,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        # Email adresini güvenli dosya adına dönüştür
        safe_email = email.replace('@', '_at_').replace('.', '_dot_')
        
        # QR kodu resim olarak kaydet
        qr_image = qr.make_image(fill_color="black", back_color="white")
        qr_path = os.path.join(self.qr_codes_dir, f"{safe_email}_qr.png")
        qr_image.save(qr_path)
        
        return secret_key, qr_path

    def dogrulama_kodu_kontrol(self, secret_key, kod):
        if not secret_key:
            return False, "Google Authenticator ayarlanmamış!"
        
        try:
            # Kodun sadece rakamlardan oluştuğunu kontrol et
            if not kod.isdigit():
                return False, "Doğrulama kodu sadece rakamlardan oluşmalıdır!"
            
            # TOTP nesnesi oluştur
            totp = pyotp.TOTP(secret_key)
            
            # Doğrulama yap
            if totp.verify(kod):
                return True, "Doğrulama başarılı!"
            else:
                return False, "Geçersiz doğrulama kodu! Lütfen Google Authenticator'dan aldığınız güncel kodu girin."
        except Exception as e:
            return False, f"Doğrulama hatası: {str(e)}" 