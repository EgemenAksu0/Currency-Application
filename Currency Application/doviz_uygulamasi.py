import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
from datetime import datetime
from kullanici_yonetimi import KullaniciYonetimi
import os
from PIL import Image, ImageTk
import threading

class DovizUygulamasi:
    def __init__(self, root):
        self.root = root
        self.root.title("Döviz Kuru Hesaplayıcı")
        self.root.geometry("600x700")
        self.root.configure(bg="#f0f0f0")
        
        self.kullanici_yonetimi = KullaniciYonetimi()
        self.giris_ekrani_goster()

    def sifre_goster_gizle(self, entry_widget, button_widget):
        if entry_widget['show'] == '*':
            entry_widget['show'] = ''
            button_widget.configure(text="●")  # Görünür şifre için nokta
        else:
            entry_widget['show'] = '*'
            button_widget.configure(text="○")  # Gizli şifre için boş daire

    def giris_ekrani_goster(self):
        # Mevcut widget'ları temizle
        for widget in self.root.winfo_children():
            widget.destroy()

        # Giriş ekranı başlığı
        self.baslik = tk.Label(
            self.root,
            text="Döviz Kuru Hesaplayıcı - Giriş",
            font=("Helvetica", 16, "bold"),
            bg="#f0f0f0"
        )
        self.baslik.pack(pady=20)

        # Giriş formu
        self.giris_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.giris_frame.pack(pady=20, padx=50, anchor="w")  # Sola hizala

        # Grid konfigürasyonu
        self.giris_frame.columnconfigure(0, weight=1)  # Label sütunu
        self.giris_frame.columnconfigure(1, weight=2)  # Entry sütunu

        # Kullanıcı adı
        self.kullanici_adi_label = tk.Label(
            self.giris_frame,
            text="Kullanıcı Adı:",
            font=("Helvetica", 12),
            bg="#f0f0f0",
            width=15,  # Sabit genişlik
            anchor="w"  # Sola hizala
        )
        self.kullanici_adi_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.kullanici_adi_entry = tk.Entry(
            self.giris_frame,
            font=("Helvetica", 12),
            width=30
        )
        self.kullanici_adi_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Şifre
        self.sifre_label = tk.Label(
            self.giris_frame,
            text="Şifre:",
            font=("Helvetica", 12),
            bg="#f0f0f0",
            width=15,  # Sabit genişlik
            anchor="w"  # Sola hizala
        )
        self.sifre_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        # Şifre giriş alanı ve göster/gizle butonu için frame
        self.sifre_frame = tk.Frame(self.giris_frame, bg="#f0f0f0")
        self.sifre_frame.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        self.sifre_entry = tk.Entry(
            self.sifre_frame,
            font=("Helvetica", 12),
            width=30,
            show="*"
        )
        self.sifre_entry.pack(side=tk.LEFT)

        # Şifre göster/gizle butonu
        self.sifre_goster_button = tk.Button(
            self.sifre_frame,
            text="○",
            command=lambda: self.sifre_goster_gizle(self.sifre_entry, self.sifre_goster_button),
            font=("Helvetica", 12, "bold"),
            bg="#f0f0f0",
            width=3,
            relief=tk.RAISED,
            bd=2
        )
        self.sifre_goster_button.pack(side=tk.LEFT, padx=5)

        # Giriş yöntemi seçimi
        self.giris_yontemi_frame = tk.Frame(self.giris_frame, bg="#f0f0f0")
        self.giris_yontemi_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="w")

        # Giriş yöntemi yazısı
        self.giris_yontemi_label = tk.Label(
            self.giris_yontemi_frame,
            text="Giriş Yöntemi:",
            font=("Helvetica", 12),
            bg="#f0f0f0"
        )
        self.giris_yontemi_label.pack(side=tk.LEFT, padx=5)

        # QR ile giriş butonu
        self.qr_giris_button = tk.Button(
            self.giris_yontemi_frame,
            text="QR ile Giriş",
            command=lambda: self.giris_yap("qr"),
            font=("Helvetica", 12),
            bg="#2196F3",  # Mavi renk
            fg="white",
            width=12
        )
        self.qr_giris_button.pack(side=tk.LEFT, padx=5)

        # Email ile giriş butonu
        self.email_giris_button = tk.Button(
            self.giris_yontemi_frame,
            text="Email ile Giriş",
            command=lambda: self.giris_yap("email"),
            font=("Helvetica", 12),
            bg="#2196F3",  # Mavi renk
            fg="white",
            width=12
        )
        self.email_giris_button.pack(side=tk.LEFT, padx=10)

        # Kayıt ol butonu için yeni frame
        self.kayit_frame_alt = tk.Frame(self.giris_frame, bg="#f0f0f0")
        self.kayit_frame_alt.grid(row=3, column=0, columnspan=2, pady=10)

        # Kayıt ol butonu
        self.kayit_button = tk.Button(
            self.kayit_frame_alt,
            text="Kayıt Ol",
            command=self.kayit_ekrani_goster,
            font=("Helvetica", 12),
            bg="#FFA500",  # Turuncu renk
            fg="white",
            width=12
        )
        self.kayit_button.pack(side=tk.LEFT, padx=10)  # Sola hizala

        # Şifremi Unuttum butonu
        self.sifremi_unuttum_button = tk.Button(
            self.kayit_frame_alt,
            text="Şifremi Unuttum",
            command=self.sifremi_unuttum_ekrani_goster,
            font=("Helvetica", 12),
            bg="#4CAF50",  # Yeşil renk
            fg="white",
            width=12
        )
        self.sifremi_unuttum_button.pack(side=tk.LEFT, padx=10)  # Sola hizala

    def giris_yap(self, yontem="qr"):
        kullanici_adi = self.kullanici_adi_entry.get()
        sifre = self.sifre_entry.get()

        if not kullanici_adi or not sifre:
            messagebox.showerror("Hata", "Lütfen kullanıcı adı ve şifre giriniz!")
            return

        # Giriş yöntemini kaydet
        self.giris_yontemi = yontem

        if yontem == "email":
            basarili, mesaj = self.kullanici_yonetimi.giris_yap(kullanici_adi, sifre, yontem="email")
            if basarili:
                self.email_dogrulama_ekrani_goster(kullanici_adi)
            else:
                messagebox.showerror("Hata", mesaj)
        else:
            basarili, mesaj = self.kullanici_yonetimi.giris_yap(kullanici_adi, sifre)
            if basarili:
                messagebox.showinfo("Bilgi", "Google Authenticator ile doğrulama yapabilirsiniz.")
                self.dogrulama_ekrani_goster(kullanici_adi, "qr")
            else:
                messagebox.showerror("Hata", mesaj)

    def dogrulama_ekrani_goster(self, kullanici_adi, yontem):
        # Mevcut widget'ları temizle
        for widget in self.root.winfo_children():
            widget.destroy()

        # Doğrulama ekranı başlığı
        self.baslik = tk.Label(
            self.root,
            text="İki Faktörlü Doğrulama",
            font=("Helvetica", 16, "bold"),
            bg="#f0f0f0"
        )
        self.baslik.pack(pady=20)

        # Doğrulama formu
        self.dogrulama_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.dogrulama_frame.pack(pady=20)

        # Doğrulama mesajı
        if yontem == "qr":
            mesaj = "Google Authenticator uygulamasından aldığınız 6 haneli kodu giriniz.\nKod sadece rakamlardan oluşmalıdır."
        else:
            mesaj = "Email adresinize gönderilen 6 haneli doğrulama kodunu giriniz."

        self.mesaj_label = tk.Label(
            self.dogrulama_frame,
            text=mesaj,
            font=("Helvetica", 12),
            bg="#f0f0f0",
            wraplength=400,
            justify=tk.LEFT
        )
        self.mesaj_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Doğrulama kodu
        self.kod_label = tk.Label(
            self.dogrulama_frame,
            text="Doğrulama Kodu:",
            font=("Helvetica", 12),
            bg="#f0f0f0"
        )
        self.kod_label.grid(row=1, column=0, padx=5, pady=5)
        
        # Doğrulama kodu giriş alanı için değişken
        self.kod_var = tk.StringVar()
        self.kod_var.trace('w', self.kod_uzunluk_kontrol)  # Her değişiklikte kontrol et
        
        self.kod_entry = tk.Entry(
            self.dogrulama_frame,
            font=("Helvetica", 12),
            width=30,
            textvariable=self.kod_var
        )
        self.kod_entry.grid(row=1, column=1, padx=5, pady=5)
        self.kod_entry.focus()  # Odağı doğrudan giriş alanına ver

        # Doğrula butonu
        self.dogrula_button = tk.Button(
            self.dogrulama_frame,
            text="Doğrula",
            command=lambda: self.dogrulama_kontrol(kullanici_adi),
            font=("Helvetica", 12),
            bg="#4CAF50",
            fg="white",
            width=15
        )
        self.dogrula_button.grid(row=2, column=0, columnspan=2, pady=10)

        # QR kodu tekrar göster butonu (sadece QR yöntemi için)
        if yontem == "qr":
            self.qr_tekrar_button = tk.Button(
                self.dogrulama_frame,
                text="QR Kodu Tekrar Göster",
                command=lambda: self.qr_kodu_tekrar_goster(kullanici_adi),
                font=("Helvetica", 12),
                bg="#2196F3",
                fg="white",
                width=20
            )
            self.qr_tekrar_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Geri dön butonu
        self.geri_button = tk.Button(
            self.dogrulama_frame,
            text="Geri Dön",
            command=self.giris_ekrani_goster,
            font=("Helvetica", 12),
            bg="#2196F3",
            fg="white",
            width=15
        )
        self.geri_button.grid(row=4, column=0, columnspan=2)

        # Enter tuşu ile doğrulama
        self.root.bind('<Return>', lambda event: self.dogrulama_kontrol(kullanici_adi))

    def qr_kodu_tekrar_goster(self, kullanici_adi):
        # Kullanıcı adına göre email'i bul
        email = None
        for mail, bilgiler in self.kullanici_yonetimi.kullanici_bilgileri.items():
            if bilgiler['kullanici_adi'] == kullanici_adi:
                email = mail
                break
        
        if not email:
            messagebox.showerror("Hata", "Kullanıcı bulunamadı!")
            return

        # Kullanıcının QR kod yolunu bul
        safe_email = email.replace('@', '_at_').replace('.', '_dot_')
        qr_path = os.path.join("qr_codes", f"{safe_email}_qr.png")

        if not os.path.exists(qr_path):
            messagebox.showerror("Hata", "QR kod bulunamadı!")
            return

        # QR kodu göster
        self.qr_kodu_dogrulama_icin_goster(qr_path)

    def qr_kodu_dogrulama_icin_goster(self, qr_path):
        # QR kod penceresi
        qr_window = tk.Toplevel(self.root)
        qr_window.title("Google Authenticator QR Kodu")
        qr_window.geometry("500x600")
        qr_window.configure(bg="#f0f0f0")

        # Ana frame
        main_frame = tk.Frame(qr_window, bg="#f0f0f0")
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)

        # Başlık
        baslik = tk.Label(
            main_frame,
            text="Google Authenticator QR Kodu",
            font=("Helvetica", 14, "bold"),
            bg="#f0f0f0"
        )
        baslik.pack(pady=(0, 20))

        # Açıklama
        aciklama = tk.Label(
            main_frame,
            text="1. Google Authenticator uygulamasını açın\n2. QR kodu tarayın\n3. Uygulamada görünen kodu doğrulama ekranında kullanın",
            font=("Helvetica", 12),
            bg="#f0f0f0",
            justify=tk.LEFT
        )
        aciklama.pack(pady=10)

        # QR kod resmi
        try:
            qr_image = tk.PhotoImage(file=qr_path)
            qr_label = tk.Label(main_frame, image=qr_image, bg="#f0f0f0")
            qr_label.image = qr_image  # Referansı koru
            qr_label.pack(pady=20)
        except Exception as e:
            hata_label = tk.Label(
                main_frame,
                text=f"QR kod yüklenemedi: {str(e)}",
                font=("Helvetica", 12),
                fg="red",
                bg="#f0f0f0"
            )
            hata_label.pack(pady=20)

        # Butonlar için frame
        button_frame = tk.Frame(main_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=20)

        # Tamam butonu
        tamam_button = tk.Button(
            button_frame,
            text="Tamam",
            command=qr_window.destroy,  # Sadece pencereyi kapat, ana sayfaya dönme
            font=("Helvetica", 12),
            bg="#2196F3",
            fg="white",
            width=20
        )
        tamam_button.pack(expand=True)

    def kod_uzunluk_kontrol(self, *args):
        # Maksimum 6 karakter sınırı
        if len(self.kod_var.get()) > 6:
            self.kod_var.set(self.kod_var.get()[:6])

    def dogrulama_kontrol(self, kullanici_adi):
        kod = self.kod_entry.get()
        if not kod:
            messagebox.showerror("Hata", "Lütfen doğrulama kodunu girin!")
            return

        # Giriş yöntemini kontrol et
        if hasattr(self, 'giris_yontemi'):
            if self.giris_yontemi == "qr":
                basarili, mesaj = self.kullanici_yonetimi.qr_dogrulama_kontrol(kullanici_adi, kod)
            else:  # email
                basarili, mesaj = self.kullanici_yonetimi.dogrulama_kodu_kontrol(kullanici_adi, kod)
        else:
            messagebox.showerror("Hata", "Giriş yöntemi belirlenemedi!")
            return

        if basarili:
            self.ana_ekrani_goster()
        else:
            messagebox.showerror("Hata", mesaj)

    def email_kontrol(self, *args):
        # Email'i küçük harfe çevir
        current_text = self.email_var.get()
        if current_text != current_text.lower():
            self.email_var.set(current_text.lower())

    def email_dogrula(self, email):
        # Yaygın email sağlayıcıları
        gecerli_providerlar = [
            'gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com',
            'yandex.com', 'protonmail.com', 'icloud.com', 'mail.com',
            'aol.com', 'zoho.com', 'gmx.com', 'live.com'
        ]
        
        # Email formatı kontrolü
        if '@' not in email or '.' not in email:
            return False, "Geçersiz email formatı! Email adresi @ ve . içermelidir."
        
        # @ işaretinden sonraki kısmı al (domain)
        domain = email.split('@')[1]
        
        # Domain uzantısı kontrolü
        if not domain.endswith(('.com', '.net', '.org', '.edu', '.gov')):
            return False, "Geçersiz email uzantısı! Email .com, .net, .org, .edu veya .gov ile bitmelidir."
        
        # Email sağlayıcı kontrolü
        if domain not in gecerli_providerlar:
            return False, "Geçersiz email sağlayıcı! Lütfen yaygın bir email sağlayıcı kullanın (örn: gmail.com, hotmail.com)"
        
        return True, "Email formatı geçerli."

    def kayit_ekrani_goster(self):
        # Mevcut widget'ları temizle
        for widget in self.root.winfo_children():
            widget.destroy()

        # Kayıt ekranı başlığı
        self.baslik = tk.Label(
            self.root,
            text="Döviz Kuru Hesaplayıcı - Kayıt",
            font=("Helvetica", 16, "bold"),
            bg="#f0f0f0"
        )
        self.baslik.pack(pady=20)

        # Kayıt formu
        self.kayit_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.kayit_frame.pack(pady=20, padx=50, anchor="w")  # Sola hizala

        # Grid konfigürasyonu
        self.kayit_frame.columnconfigure(0, weight=1)  # Label sütunu
        self.kayit_frame.columnconfigure(1, weight=2)  # Entry sütunu

        # Kullanıcı adı
        self.kayit_kullanici_adi_label = tk.Label(
            self.kayit_frame,
            text="Kullanıcı Adı:",
            font=("Helvetica", 12),
            bg="#f0f0f0",
            width=15,  # Sabit genişlik
            anchor="w"  # Sola hizala
        )
        self.kayit_kullanici_adi_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.kayit_kullanici_adi_entry = tk.Entry(
            self.kayit_frame,
            font=("Helvetica", 12),
            width=30
        )
        self.kayit_kullanici_adi_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Email
        self.email_label = tk.Label(
            self.kayit_frame,
            text="Email:",
            font=("Helvetica", 12),
            bg="#f0f0f0",
            width=15,  # Sabit genişlik
            anchor="w"  # Sola hizala
        )
        self.email_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        # Email için StringVar ve kontrol
        self.email_var = tk.StringVar()
        self.email_var.trace('w', self.email_kontrol)
        
        self.email_entry = tk.Entry(
            self.kayit_frame,
            font=("Helvetica", 12),
            width=30,
            textvariable=self.email_var
        )
        self.email_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Şifre
        self.kayit_sifre_label = tk.Label(
            self.kayit_frame,
            text="Şifre:",
            font=("Helvetica", 12),
            bg="#f0f0f0",
            width=15,  # Sabit genişlik
            anchor="w"  # Sola hizala
        )
        self.kayit_sifre_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        
        # Şifre giriş alanı ve göster/gizle butonu için frame
        self.kayit_sifre_frame = tk.Frame(self.kayit_frame, bg="#f0f0f0")
        self.kayit_sifre_frame.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        self.kayit_sifre_entry = tk.Entry(
            self.kayit_sifre_frame,
            font=("Helvetica", 12),
            width=30,
            show="*"
        )
        self.kayit_sifre_entry.pack(side=tk.LEFT)

        # Şifre göster/gizle butonu
        self.kayit_sifre_goster_button = tk.Button(
            self.kayit_sifre_frame,
            text="○",
            command=lambda: self.sifre_goster_gizle(self.kayit_sifre_entry, self.kayit_sifre_goster_button),
            font=("Helvetica", 12, "bold"),
            bg="#f0f0f0",
            width=3,
            relief=tk.RAISED,
            bd=2
        )
        self.kayit_sifre_goster_button.pack(side=tk.LEFT, padx=5)

        # Şifre gereksinimleri bilgisi
        self.sifre_bilgi_label = tk.Label(
            self.kayit_frame,
            text="Şifre Gereksinimleri:\n" +
                 "• En az 8 karakter uzunluğunda olmalıdır\n" +
                 "• En az 1 büyük harf içermelidir\n" +
                 "• En az 1 küçük harf içermelidir\n" +
                 "• En az 1 rakam içermelidir\n" +
                 "• En az 1 özel karakter içermelidir (örn: ?, @, !, #, %, +, -, *)",
            font=("Helvetica", 10),
            bg="#f0f0f0",
            fg="#666666",
            justify=tk.LEFT
        )
        self.sifre_bilgi_label.grid(row=3, column=0, columnspan=2, padx=5, pady=(0, 10), sticky="w")

        # Butonlar için yeni frame
        self.kayit_butonlar_frame = tk.Frame(self.kayit_frame, bg="#f0f0f0")
        self.kayit_butonlar_frame.grid(row=4, column=0, columnspan=2, pady=20)

        # Kayıt ol butonu
        self.kayit_ol_button = tk.Button(
            self.kayit_butonlar_frame,
            text="Kayıt Ol",
            command=self.kayit_ol,
            font=("Helvetica", 12),
            bg="#4CAF50",
            fg="white",
            width=15
        )
        self.kayit_ol_button.pack(side=tk.LEFT, padx=10)

        # Geri dön butonu
        self.geri_button = tk.Button(
            self.kayit_butonlar_frame,
            text="Giriş Ekranına Dön",
            command=self.giris_ekrani_goster,
            font=("Helvetica", 12),
            bg="#2196F3",
            fg="white",
            width=15
        )
        self.geri_button.pack(side=tk.LEFT, padx=10)

    def kayit_ol(self):
        kullanici_adi = self.kayit_kullanici_adi_entry.get()
        email = self.email_entry.get()
        sifre = self.kayit_sifre_entry.get()

        if not kullanici_adi or not email or not sifre:
            messagebox.showerror("Hata", "Lütfen tüm alanları doldurun!")
            return

        # Email doğrulama
        email_gecerli, email_mesaj = self.email_dogrula(email)
        if not email_gecerli:
            messagebox.showerror("Hata", email_mesaj)
            return

        # Şifre kontrolü
        if len(sifre) < 8:
            messagebox.showerror("Hata", "Şifre en az 8 karakter uzunluğunda olmalıdır!")
            return

        # Büyük harf kontrolü
        buyuk_harf_var = False
        for karakter in sifre:
            if karakter.isupper():
                buyuk_harf_var = True
                break
        if not buyuk_harf_var:
            messagebox.showerror("Hata", "Şifre en az bir büyük harf içermelidir!")
            return

        # Küçük harf kontrolü
        kucuk_harf_var = False
        for karakter in sifre:
            if karakter.islower():
                kucuk_harf_var = True
                break
        if not kucuk_harf_var:
            messagebox.showerror("Hata", "Şifre en az bir küçük harf içermelidir!")
            return

        # Sayı kontrolü
        sayi_var = False
        for karakter in sifre:
            if karakter.isdigit():
                sayi_var = True
                break
        if not sayi_var:
            messagebox.showerror("Hata", "Şifre en az bir rakam içermelidir!")
            return

        # Özel karakter kontrolü
        ozel_karakterler = ['?', '@', '!', '#', '%', '+', '-', '*']
        ozel_karakter_var = False
        for karakter in sifre:
            if karakter in ozel_karakterler:
                ozel_karakter_var = True
                break
        if not ozel_karakter_var:
            messagebox.showerror("Hata", "Şifre en az bir özel karakter içermelidir! (örn: ?, @, !, #, %, +, -, *)")
            return

        # Email formatı kontrolü
        if '@' not in email or '.' not in email:
            messagebox.showerror("Hata", "Lütfen geçerli bir email adresi giriniz!")
            return

        basarili, mesaj = self.kullanici_yonetimi.kayit_ol(kullanici_adi, sifre, email)
        if basarili:
            # Kullanıcı ID'sini ve QR kod yolunu ayır
            user_id = mesaj.split("Kullanıcı ID'niz: ")[1].split("\n")[0]
            qr_path = mesaj.split("QR kodunuz: ")[1]
            
            # Kullanıcı ID'sini göster
            messagebox.showinfo("Kayıt Başarılı", f"Kullanıcı ID'niz: {user_id}\n\nBu ID'yi not alın, daha sonra ihtiyacınız olabilir.")
            
            # QR kodu göster
            self.qr_kod_goster(qr_path)
        else:
            messagebox.showerror("Hata", mesaj)

    def qr_kod_goster(self, qr_path):
        # QR kod penceresi
        qr_window = tk.Toplevel(self.root)
        qr_window.title("Google Authenticator QR Kodu")
        qr_window.geometry("500x600")
        qr_window.configure(bg="#f0f0f0")

        # Ana frame
        main_frame = tk.Frame(qr_window, bg="#f0f0f0")
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)

        # Başlık
        baslik = tk.Label(
            main_frame,
            text="Google Authenticator Kurulumu",
            font=("Helvetica", 14, "bold"),
            bg="#f0f0f0"
        )
        baslik.pack(pady=(0, 20))

        # Açıklama
        aciklama = tk.Label(
            main_frame,
            text="1. Google Authenticator uygulamasını indirin\n2. QR kodu tarayın\n3. Uygulamada görünen kodu giriş ekranında kullanın",
            font=("Helvetica", 12),
            bg="#f0f0f0",
            justify=tk.LEFT
        )
        aciklama.pack(pady=10)

        # QR kod resmi
        try:
            qr_image = tk.PhotoImage(file=qr_path)
            qr_label = tk.Label(main_frame, image=qr_image, bg="#f0f0f0")
            qr_label.image = qr_image  # Referansı koru
            qr_label.pack(pady=20)
        except Exception as e:
            hata_label = tk.Label(
                main_frame,
                text=f"QR kod yüklenemedi: {str(e)}",
                font=("Helvetica", 12),
                fg="red",
                bg="#f0f0f0"
            )
            hata_label.pack(pady=20)

        # Butonlar için frame
        button_frame = tk.Frame(main_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=20)

        # Tamam butonu
        tamam_button = tk.Button(
            button_frame,
            text="Tamam",
            command=lambda: [qr_window.destroy(), self.giris_ekrani_goster()],
            font=("Helvetica", 12),
            bg="#2196F3",
            fg="white",
            width=15
        )
        tamam_button.pack(expand=True)

    def ana_ekrani_goster(self):
        # Mevcut widget'ları temizle
        for widget in self.root.winfo_children():
            widget.destroy()

        # Para birimleri ve tam isimleri
        self.para_birimleri = {
            "USD": "Amerikan Doları",
            "EUR": "Euro",
            "TRY": "Türk Lirası",
            "GBP": "İngiliz Sterlini",
            "JPY": "Japon Yeni",
            "AUD": "Avustralya Doları",
            "CAD": "Kanada Doları",
            "CHF": "İsviçre Frangı",
            "CNY": "Çin Yuanı",
            "INR": "Hindistan Rupisi",
            "BRL": "Brezilya Reali",
            "RUB": "Rus Rublesi",
            "KRW": "Güney Kore Wonu",
            "SGD": "Singapur Doları",
            "NZD": "Yeni Zelanda Doları",
            "MXN": "Meksika Pesosu",
            "HKD": "Hong Kong Doları",
            "SEK": "İsveç Kronu",
            "NOK": "Norveç Kronu",
            "ZAR": "Güney Afrika Randı"
        }

        # API URL
        self.api_url = "https://api.exchangerate-api.com/v4/latest/USD"

        # Ana başlık
        self.baslik = tk.Label(
            self.root,
            text="Döviz Kuru Hesaplayıcı",
            font=("Helvetica", 16, "bold"),
            bg="#f0f0f0"
        )
        self.baslik.pack(pady=20)

        # Çıkış butonu
        self.cikis_button = tk.Button(
            self.root,
            text="Çıkış Yap",
            command=self.giris_ekrani_goster,
            font=("Helvetica", 10),
            bg="#f44336",
            fg="white"
        )
        self.cikis_button.pack(pady=5)

        # Miktar girişi
        self.miktar_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.miktar_frame.pack(pady=10)

        self.miktar_label = tk.Label(
            self.miktar_frame,
            text="Miktar:",
            font=("Helvetica", 12),
            bg="#f0f0f0"
        )
        self.miktar_label.pack(side=tk.LEFT, padx=5)
        
        self.miktar_entry = tk.Entry(
            self.miktar_frame,
            font=("Helvetica", 12),
            width=15
        )
        self.miktar_entry.pack(side=tk.LEFT)

        # Para birimi seçeneklerini oluştur (kısaltma ve açıklama ile)
        para_birimi_listesi = [f"{kod} - {isim}" for kod, isim in self.para_birimleri.items()]

        # Kaynak para birimi seçimi
        self.kaynak_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.kaynak_frame.pack(pady=10)
        
        self.kaynak_label = tk.Label(
            self.kaynak_frame,
            text="Kaynak Para Birimi:",
            font=("Helvetica", 12),
            bg="#f0f0f0"
        )
        self.kaynak_label.pack(side=tk.LEFT, padx=5)
        
        self.kaynak_combo = ttk.Combobox(
            self.kaynak_frame,
            values=para_birimi_listesi,
            width=30,
            state="readonly"
        )
        self.kaynak_combo.set("TRY - Türk Lirası")
        self.kaynak_combo.pack(side=tk.LEFT)

        # Hedef para birimi seçimi
        self.hedef_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.hedef_frame.pack(pady=10)
        
        self.hedef_label = tk.Label(
            self.hedef_frame,
            text="Hedef Para Birimi:",
            font=("Helvetica", 12),
            bg="#f0f0f0"
        )
        self.hedef_label.pack(side=tk.LEFT, padx=5)
        
        self.hedef_combo = ttk.Combobox(
            self.hedef_frame,
            values=para_birimi_listesi,
            width=30,
            state="readonly"
        )
        self.hedef_combo.set("USD - Amerikan Doları")
        self.hedef_combo.pack(side=tk.LEFT)

        # Hesapla butonu
        self.hesapla_button = tk.Button(
            self.root,
            text="Hesapla",
            command=self.hesapla,
            font=("Helvetica", 12),
            bg="#4CAF50",
            fg="white",
            width=15,
            height=2
        )
        self.hesapla_button.pack(pady=20)

        # Sonuç etiketi
        self.sonuc_label = tk.Label(
            self.root,
            text="",
            font=("Helvetica", 14),
            bg="#f0f0f0"
        )
        self.sonuc_label.pack(pady=10)

        # Güncelleme zamanı etiketi
        self.guncelleme_label = tk.Label(
            self.root,
            text="",
            font=("Helvetica", 10),
            bg="#f0f0f0"
        )
        self.guncelleme_label.pack(pady=5)

    def hesapla(self):
        try:
            miktar = float(self.miktar_entry.get())
            
            # Negatif sayı kontrolü
            if miktar < 0:
                messagebox.showerror("Hata", "Lütfen pozitif bir sayı giriniz!")
                return
                
            # Çok büyük sayı kontrolü
            if miktar > 1000000000:  # 1 milyar
                messagebox.showerror("Hata", "Lütfen daha küçük bir sayı giriniz!")
                return

            kaynak = self.kaynak_combo.get().split(" - ")[0]
            hedef = self.hedef_combo.get().split(" - ")[0]

            try:
                # API'den güncel kurları al
                response = requests.get(self.api_url, timeout=5)  # 5 saniye timeout
                response.raise_for_status()  # HTTP hatalarını kontrol et
                data = response.json()
                rates = data["rates"]
            except requests.exceptions.RequestException as e:
                messagebox.showerror("Bağlantı Hatası", 
                    "Döviz kurları alınamadı. Lütfen internet bağlantınızı kontrol edin.\n"
                    "Hata detayı: " + str(e))
                return

            # Dönüşüm hesaplama
            if kaynak == "USD":
                sonuc = miktar * rates[hedef]
            elif hedef == "USD":
                sonuc = miktar / rates[kaynak]
            else:
                usd_miktar = miktar / rates[kaynak]
                sonuc = usd_miktar * rates[hedef]

            # Sonucu göster
            self.sonuc_label.config(
                text=f"{miktar:,.2f} {kaynak} = {sonuc:,.2f} {hedef}"
            )

            # Güncelleme zamanını göster
            guncelleme_zamani = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            self.guncelleme_label.config(
                text=f"Son Güncelleme: {guncelleme_zamani}"
            )

        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli bir sayı giriniz!")
        except Exception as e:
            messagebox.showerror("Hata", f"Beklenmeyen bir hata oluştu: {str(e)}")

    def email_dogrulama_ekrani_goster(self, kullanici_adi):
        # Mevcut widget'ları temizle
        for widget in self.root.winfo_children():
            widget.destroy()

        self.email_dogrulama_kalan_sure = 300  # 5 dakika (saniye cinsinden)
        self.email_dogrulama_durum = False

        self.baslik = tk.Label(
            self.root,
            text="E-posta Doğrulama",
            font=("Helvetica", 16, "bold"),
            bg="#f0f0f0"
        )
        self.baslik.pack(pady=20)

        self.mesaj_label = tk.Label(
            self.root,
            text="Mailinize bir doğrulama linki gönderildi. Lütfen mailinizi kontrol edin ve linke tıklayın.",
            font=("Helvetica", 12),
            bg="#f0f0f0",
            wraplength=400,
            justify=tk.LEFT
        )
        self.mesaj_label.pack(pady=10)

        self.sure_label = tk.Label(
            self.root,
            text="Kalan süre: 05:00",
            font=("Helvetica", 12),
            bg="#f0f0f0"
        )
        self.sure_label.pack(pady=10)

        self.geri_button = tk.Button(
            self.root,
            text="Geri Dön",
            command=self.giris_ekrani_goster,
            font=("Helvetica", 12),
            bg="#2196F3",
            fg="white",
            width=15
        )
        self.geri_button.pack(pady=10)

        self.email_dogrulama_sayac_baslat(kullanici_adi)

    def email_dogrulama_sayac_baslat(self, kullanici_adi):
        def sayac():
            if self.email_dogrulama_kalan_sure > 0:
                dakika = self.email_dogrulama_kalan_sure // 60
                saniye = self.email_dogrulama_kalan_sure % 60
                self.sure_label.config(text=f"Kalan süre: {dakika:02d}:{saniye:02d}")
                # Her 5 saniyede bir doğrulama kontrolü
                if self.email_dogrulama_kalan_sure % 5 == 0:
                    if self.kullanici_yonetimi.email_dogrulandi_mi(kullanici_adi):
                        self.email_dogrulama_durum = True
                        messagebox.showinfo("Başarılı", "E-posta doğrulama işlemi tamamlandı!")
                        self.ana_ekrani_goster()
                        return
                self.email_dogrulama_kalan_sure -= 1
                self.root.after(1000, sayac)
            else:
                messagebox.showerror("Süre Doldu", "Doğrulama linkinin süresi doldu. Lütfen tekrar giriş yapın.")
                self.giris_ekrani_goster()
        sayac()

    def sifremi_unuttum_ekrani_goster(self):
        # Giriş ekranından geliniyorsa, email veya kullanıcı adı boşsa uyarı ver
        if hasattr(self, 'kullanici_adi_entry') and hasattr(self, 'email_entry'):
            kullanici_adi = self.kullanici_adi_entry.get() if hasattr(self, 'kullanici_adi_entry') else ''
            email = self.email_entry.get() if hasattr(self, 'email_entry') else ''
            if not kullanici_adi and not email:
                messagebox.showerror("Hata", "Lütfen önce giriş ekranında kullanıcı adı veya email alanını doldurun!")
                return
        # Mevcut widget'ları temizle
        for widget in self.root.winfo_children():
            widget.destroy()

        # Şifremi unuttum ekranı başlığı
        self.baslik = tk.Label(
            self.root,
            text="Şifremi Unuttum",
            font=("Helvetica", 16, "bold"),
            bg="#f0f0f0"
        )
        self.baslik.pack(pady=20)

        # Şifremi unuttum formu
        self.sifremi_unuttum_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.sifremi_unuttum_frame.pack(pady=20, padx=50, anchor="w")

        # Email girişi
        self.email_label = tk.Label(
            self.sifremi_unuttum_frame,
            text="Email:",
            font=("Helvetica", 12),
            bg="#f0f0f0",
            width=15,
            anchor="w"
        )
        self.email_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Email için StringVar ve kontrol
        self.email_var = tk.StringVar()
        self.email_var.trace('w', self.email_kontrol)

        self.email_entry = tk.Entry(
            self.sifremi_unuttum_frame,
            font=("Helvetica", 12),
            width=30,
            textvariable=self.email_var
        )
        self.email_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Butonlar için frame
        self.butonlar_frame = tk.Frame(self.sifremi_unuttum_frame, bg="#f0f0f0")
        self.butonlar_frame.grid(row=1, column=0, columnspan=2, pady=20)

        # 6 Haneli Kod Gönder butonu
        self.kod_gonder_button = tk.Button(
            self.butonlar_frame,
            text="6 Haneli Kod Gönder",
            command=self.sifre_sifirla_kod_gonder,
            font=("Helvetica", 12),
            bg="#4CAF50",
            fg="white",
            width=20
        )
        self.kod_gonder_button.pack(side=tk.LEFT, padx=10)

        # Geri dön butonu
        self.geri_button = tk.Button(
            self.butonlar_frame,
            text="Giriş Ekranına Dön",
            command=self.giris_ekrani_goster,
            font=("Helvetica", 12),
            bg="#2196F3",
            fg="white",
            width=15
        )
        self.geri_button.pack(side=tk.LEFT, padx=10)

    def sifre_sifirla_kod_gonder(self):
        email = self.email_entry.get()

        if not email:
            messagebox.showerror("Hata", "Lütfen email adresinizi girin!")
            return

        # Email doğrulama
        email_gecerli, email_mesaj = self.email_dogrula(email)
        if not email_gecerli:
            messagebox.showerror("Hata", email_mesaj)
            return

        # Kullanıcı kontrolü
        if not self.kullanici_yonetimi.kullanici_var_mi(email):
            messagebox.showerror("Hata", "Bu email adresi ile kayıtlı bir kullanıcı bulunamadı!")
            return

        # 6 haneli kod gönder
        basarili, mesaj = self.kullanici_yonetimi.sifre_sifirla_kod_gonder(email)
        if basarili:
            messagebox.showinfo("Başarılı", "Şifre sıfırlama kodu email adresinize gönderildi. Lütfen mailinizi kontrol edin.")
            self.sifre_sifirla_kod_dogrulama_ekrani_goster(email)
        else:
            messagebox.showerror("Hata", mesaj)

    def sifre_sifirla_kod_dogrulama_ekrani_goster(self, email):
        # Mevcut widget'ları temizle
        for widget in self.root.winfo_children():
            widget.destroy()

        self.baslik = tk.Label(
            self.root,
            text="Şifre Sıfırlama Kodu Doğrulama",
            font=("Helvetica", 16, "bold"),
            bg="#f0f0f0"
        )
        self.baslik.pack(pady=20)

        self.kod_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.kod_frame.pack(pady=20)

        self.kod_label = tk.Label(
            self.kod_frame,
            text="6 Haneli Kod:",
            font=("Helvetica", 12),
            bg="#f0f0f0"
        )
        self.kod_label.grid(row=0, column=0, padx=5, pady=5)

        self.kod_var = tk.StringVar()
        # Sadece rakam ve 6 karakter sınırı için validate fonksiyonu
        vcmd = (self.root.register(self.kod_entry_validate), '%P')
        self.kod_entry = tk.Entry(
            self.kod_frame,
            font=("Helvetica", 12),
            width=10,
            textvariable=self.kod_var,
            validate='key',
            validatecommand=vcmd
        )
        self.kod_entry.grid(row=0, column=1, padx=5, pady=5)
        self.kod_entry.focus()

        self.onayla_button = tk.Button(
            self.kod_frame,
            text="Onayla",
            command=lambda: self.sifre_sifirla_kod_dogrula(email),
            font=("Helvetica", 12),
            bg="#4CAF50",
            fg="white",
            width=12
        )
        self.onayla_button.grid(row=1, column=0, columnspan=2, pady=10)

        self.geri_button = tk.Button(
            self.kod_frame,
            text="Geri",
            command=self.sifremi_unuttum_ekrani_goster,
            font=("Helvetica", 12),
            bg="#2196F3",
            fg="white",
            width=12
        )
        self.geri_button.grid(row=2, column=0, columnspan=2, pady=5)

    def sifre_sifirla_kod_dogrula(self, email):
        kod = self.kod_entry.get()
        if not kod or len(kod) != 6:
            messagebox.showerror("Hata", "Lütfen 6 haneli kodu girin!")
            return
        basarili, mesaj = self.kullanici_yonetimi.sifre_sifirla_kod_dogrula(email, kod)
        if basarili:
            messagebox.showinfo("Başarılı", "Kod doğrulandı. Şimdi yeni şifrenizi belirleyebilirsiniz.")
            self.sifre_yenile_ekrani_goster(email)
        else:
            messagebox.showerror("Hata", mesaj)

    def sifre_yenile_ekrani_goster(self, email):
        # Mevcut widget'ları temizle
        for widget in self.root.winfo_children():
            widget.destroy()

        self.baslik = tk.Label(
            self.root,
            text="Yeni Şifre Belirle",
            font=("Helvetica", 16, "bold"),
            bg="#f0f0f0"
        )
        self.baslik.pack(pady=20)

        self.yenile_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.yenile_frame.pack(pady=20)

        self.sifre_label = tk.Label(
            self.yenile_frame,
            text="Yeni Şifre:",
            font=("Helvetica", 12),
            bg="#f0f0f0"
        )
        self.sifre_label.grid(row=0, column=0, padx=5, pady=5)

        self.sifre_entry = tk.Entry(
            self.yenile_frame,
            font=("Helvetica", 12),
            width=30,
            show="*"
        )
        self.sifre_entry.grid(row=0, column=1, padx=5, pady=5)

        self.onayla_button = tk.Button(
            self.yenile_frame,
            text="Şifreyi Güncelle",
            command=lambda: self.sifre_yenile(email),
            font=("Helvetica", 12),
            bg="#4CAF50",
            fg="white",
            width=15
        )
        self.onayla_button.grid(row=1, column=0, columnspan=2, pady=10)

        self.geri_button = tk.Button(
            self.yenile_frame,
            text="Giriş Ekranına Dön",
            command=self.giris_ekrani_goster,
            font=("Helvetica", 12),
            bg="#2196F3",
            fg="white",
            width=15
        )
        self.geri_button.grid(row=2, column=0, columnspan=2, pady=5)

    def sifre_yenile(self, email):
        yeni_sifre = self.sifre_entry.get()
        if not yeni_sifre or len(yeni_sifre) < 8:
            messagebox.showerror("Hata", "Şifre en az 8 karakter olmalıdır!")
            return
        basarili, mesaj = self.kullanici_yonetimi.sifre_yenile(email, yeni_sifre)
        if basarili:
            messagebox.showinfo("Başarılı", "Şifreniz başarıyla güncellendi.")
            self.giris_ekrani_goster()
        else:
            messagebox.showerror("Hata", mesaj)

    def kod_entry_validate(self, value):
        return value.isdigit() and len(value) <= 6 or value == ''

if __name__ == "__main__":
    root = tk.Tk()
    app = DovizUygulamasi(root)
    root.mainloop() 