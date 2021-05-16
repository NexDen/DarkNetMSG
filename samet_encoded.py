from tkinter.scrolledtext import ScrolledText
import pyrebase
from tkinter import * 
from rgb_to_hex import *
from plyer import notification
config = {
    "apiKey": "AIzaSyDSIZTdvKgzCd4LshG4glyUui6rKnQpgm8",
    "authDomain": "pygame-oyun.firebaseapp.com",
    "databaseURL": "https://pygame-oyun-default-rtdb.europe-west1.firebasedatabase.app",
    "projectId": "pygame-oyun",
    "storageBucket": "pygame-oyun.appspot.com",
    "messagingSenderId": "818086106839",
    "appId": "1:818086106839:web:806f3f46efe9c45fcfc292",
    "measurementId": "G-VW3TKKRZ5Y"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()


def encode(giriş) -> str:
    o = ""
    for i in giriş:
        o+= "%x" % ord(i)
    return o


def decode(giriş) -> str:
    o = ""
    b = [giriş[i:i+2] for i in range(0, len(giriş), 2)]
    for i in b:
        o += chr(int(i,16))
    return o


mesajlar = []
def stream_handler(message):
    #print(message["event"]) # put
    #print(message["path"]) # /-K7yGTTEp7O549EzTYtI
    #print(message["data"]) # {'title': 'Pyrebase', "body": "etc..."}

    if message["data"] != "/":
        mesajlar.append(message["data"]["mesaj"])
        uzunluk = len(mesajlar) - 1

    print(f"Gelen mesaj: {mesajlar[uzunluk]}")


def gönder(event=None):
    global giriş_giden_mesaj
    global mesajlaşma
    global konuşulacak_kişi
    if giriş_giden_mesaj.get() != "":
        db.child("gelen_mesaj").child(f"{konuşulacak_kişi}").set({"mesaj":encode(giriş_giden_mesaj.get())})
        mesajlaşma.config(state="normal")
        mesajlaşma.insert(END, f"{giriş_giden_mesaj.get()}     \n","right")
        mesajlaşma.tag_configure("right",justify="right")
        mesajlaşma.config(state="disabled")
        giriş_giden_mesaj.delete(0, "end")
        mesajlaşma.see("end")
    

ilk_mesaj = True
def mesaj_al(message):
    global ilk_mesaj
    global mesajlaşma
    global konuşulacak_kişi
    global isim_al
    #print(message["event"]) # put
    #print(message["path"]) # /-K7yGTTEp7O549EzTYtI
    #print(message["data"]) # {'title': 'Pyrebase', "body": "etc..."}

    if ilk_mesaj:
        ilk_mesaj = False
    elif not ilk_mesaj:
        if message["data"] != "/":
            mesajlar.append(decode(message["data"]["mesaj"]))
            uzunluk = len(mesajlar) - 1

        print(f"{konuşulacak_kişi}: {mesajlar[uzunluk]}")
        mesajlaşma.config(state="normal")
        mesajlaşma.insert(END, f"  {konuşulacak_kişi}: {mesajlar[uzunluk]}\n")
        mesajlaşma.config(state="disabled")
        mesajlaşma.see("end")
        if not pencere_mesaj.focus_displayof(): # pencere odaklı mı değil mi
            notification.notify(
                title=konuşulacak_kişi,
                message=mesajlar[uzunluk],
                timeout=15,
            )


aktifler = []
anahtar_ilk_aktif = True
def aktif_kişi_al(kişi):
    global aktifler
    global anahtar_ilk_aktif

    if anahtar_ilk_aktif == True:
        aktifler_al = db.child("aktif_kullanıcılar").get()
        for kullanıcı in aktifler_al.each():
            if kullanıcı.key() != isim_al and kullanıcı.key() != "":
                aktifler.append(kullanıcı.key())
        anahtar_ilk_aktif = False
    
    try:  # bunda da hata verme artık
        kişi_ekle = kişi["path"].replace("/","")
    except:
        pass

    if kişi_ekle in aktifler:
        aktifler.remove(kişi_ekle)
    else:
        aktifler.append(kişi_ekle)
    print(aktifler)

    aktif_liste.delete(0,"end")
    for i in aktifler:
        if i != "/" and i != "":
            aktif_liste.insert(END,i)



def çıkış():
    db.child("aktif_kullanıcılar").child(f"{isim_al}").remove() # aktif kullanıcılardan siliyor
    pencere_mesaj.destroy()
    quit()


def kişi_seç():
    global konuşulacak_kişi
    try:
        konuşulacak_kişi = aktif_liste.get(aktif_liste.curselection())
        print(f"Konuşulacak Kişi: {konuşulacak_kişi}")

        yazı_konuşulan_kişi = Label(pencere_mesaj,text=f"{konuşulacak_kişi}"
        ,font=("Segoe UI",13,"bold"),bg=hex(36,36,40),fg=hex(30,200,30))
        yazı_konuşulan_kişi.place(x=200,y=15)

        gelenler = db.child("gelen_mesaj").child(f"{isim_al}").stream(mesaj_al) # bunu sakın burdan alma
    except:
        print("Lütfen konuşmak için bir kullanıcı seçin")


def mesajlaşma_giriş():
    global yazışılıcak_kişi
    global giriş_giden_mesaj
    global mesajlaşma
    global aktif_liste
    global pencere_mesaj


    #my_stream = db.child("gelen_mesaj").child(f"{kişi}").stream(stream_handler)
       

    pencere_mesaj = Tk()
    pencere_mesaj.geometry("800x500")
    pencere_mesaj.title("DarkNet")
    pencere_mesaj.configure(bg=hex(36,36,40))

    mesajlaşma_pencere = Frame(pencere_mesaj,bg=hex(60,60,60),width=400,height=150)
    mesajlaşma_pencere.place(x=190,y=51)


    mesajlaşma = ScrolledText(mesajlaşma_pencere,width=70,height=18
            ,font=("Calibri",12,"normal"),borderwidth=0
            ,bg=hex(60,60,60),fg="white",highlightthickness=0) # ana mesajlaşma alanı

    mesajlaşma.pack(padx=10, pady=10, fill="both", expand=True)
    mesajlaşma.config(state="disabled")


    giriş_giden_mesaj = Entry(pencere_mesaj,width=70
    ,font=("Segoe UI",13,"normal"),bg=hex(90,90,90),fg="white",relief="flat",borderwidth=7)
    giriş_giden_mesaj.place(x=20,y=440)

    buton_gönder = Button(pencere_mesaj,text="Gönder ->"
    ,font=("Segoe UI",9,"bold"),width=15,height=2,relief="flat",bg=hex(80,80,105),fg=hex(230,230,230),cursor="hand2",command=gönder)
    buton_gönder.place(x=670,y=439)

    buton_konuş = Button(pencere_mesaj,text="Konuş",font=("Segoe UI",9,"bold")
    ,width=24,height=2,relief="flat",bg=hex(80,80,105),fg=hex(230,230,230),cursor="hand2",command=kişi_seç)
    buton_konuş.place(x=10,y=395)

    
    aktif_izle = db.child("aktif_kullanıcılar").stream(aktif_kişi_al)

    aktif_kullanıcılar = []
    aktif_kullanıcılar_al = db.child("aktif_kullanıcılar").get()
    for kullanıcı in aktif_kullanıcılar_al.each():
        if kullanıcı.key() != isim_al:
            aktif_kullanıcılar.append(kullanıcı.key())
    
    yazı_aktif_kullanıcılar = Label(pencere_mesaj,text="AKTİF KULLANICILAR"
        ,font=("Segoe UI",12,"bold"),fg="white",bg=hex(36,36,40))
    yazı_aktif_kullanıcılar.place(x=12,y=21)

    frame_aktif_kullanıcılar = Frame(pencere_mesaj,width=300,height=320,bg=hex(56,56,60))
    frame_aktif_kullanıcılar.place(x=10,y=51)

    scrollbar = Scrollbar(frame_aktif_kullanıcılar)
    scrollbar.pack( side = RIGHT, fill = Y ) # scrollbar

    aktif_liste = Listbox(frame_aktif_kullanıcılar,width=17,height=16, yscrollcommand = scrollbar.set
            ,font=("Calibri",12,"normal"),borderwidth=0
            ,bg=hex(56,56,60),fg=hex(230,230,230),highlightthickness=0)
    aktif_liste.pack(padx=10, pady=10, fill="both", expand=True)


    giriş_giden_mesaj.bind("<Return>",gönder)
    pencere_mesaj.protocol("WM_DELETE_WINDOW",çıkış)  # çıkış yapıldığında durumu çevrimdışı yap

    mainloop()




def giriş_yap():
    global isim_giriş
    global isim_al
    isim_al = isim_giriş.get()
    #db.child("kullanıcılar").child(f"{isim_al}").set({"kayıtlı":"."})
    kullanıcılar_al = db.child("kullanıcılar").get()

    kullanıcılar = []
    for kullanıcı in kullanıcılar_al.each():
        #print(kullanıcı.key(),end="") # kullanıcı isimleri
        kullanıcılar.append(kullanıcı.key())

    if isim_al in kullanıcılar:
        print("Giriş Yapıldı!")
        db.child("aktif_kullanıcılar").child(f"{isim_al}").set({"aktif":"aktif"})
        pencere_giriş.destroy()
        mesajlaşma_giriş()
    else:
        print("Böyle bir hesap bulunamadı")


def kayıt_ol():
    if isim_kayıt.get() != "":
        db.child("kullanıcılar").child(f"{isim_kayıt.get()}").set({"aktif":"True"})
        print("Kayıt Olundu!")
        pencere_kayıt.destroy()
        pencere_giriş_yap()



def pencere_kayıt_ol():
    global isim_kayıt
    global pencere_kayıt
    pencere_giriş.destroy()
    pencere_kayıt = Tk()
    pencere_kayıt.geometry("500x300")
    pencere_kayıt.title("DarkNet | Kayıt Ol")

    yazı_kayıt_ol = Label(pencere_kayıt,text="KAYIT OL",font=("Segoe UI",14,"bold"))
    yazı_kayıt_ol.place(x=40,y=30)

    isim_kayıt = Entry(pencere_kayıt,width=25,font=("Segoe UI",12,"normal"))
    isim_kayıt.place(x=40,y=80)

    buton_tamam = Button(pencere_kayıt,text="TAMAM",font=("Segoe UI",12,"bold"),width=15,height=2,command=kayıt_ol)
    buton_tamam.place(x=40,y=130)

def pencere_giriş_yap():
    global isim_giriş
    global pencere_giriş
    pencere_giriş = Tk()
    pencere_giriş.geometry("500x300")
    pencere_giriş.title("DarkNet | Giriş Yap")

    yazı_kayıt_ol = Label(pencere_giriş,text="GİRİŞ YAP",font=("Segoe UI",14,"bold"))
    yazı_kayıt_ol.place(x=40,y=30)

    isim_giriş = Entry(pencere_giriş,width=25,font=("Segoe UI",12,"normal"))
    isim_giriş.place(x=40,y=80)

    buton_tamam = Button(pencere_giriş,text="TAMAM",font=("Segoe UI",12,"bold"),width=15,height=2,command=giriş_yap)
    buton_tamam.place(x=40,y=130)

    buton_kayıt_ol_soru = Button(pencere_giriş,text="Hesabınız yok mu? Buraya tıklayarak kayıt olun"
    ,font=("Segoe UI",10,"normal"),width=50,height=2,command=pencere_kayıt_ol)
    buton_kayıt_ol_soru.place(x=40,y=200)

    mainloop()



pencere_giriş_yap()