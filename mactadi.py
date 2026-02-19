

from Kekik.cli import konsol
from httpx     import Client
from parsel    import Selector
import re

class mactadi:
    def __init__(self, m3u_dosyasi):
        self.m3u_dosyasi = m3u_dosyasi
        self.httpx       = Client(timeout=10, verify=False)

    def referer_domainini_al(self):
        referer_deseni = r'#EXTVLCOPT:http-referrer=(https?://[^/]*mactadi[^/]*\.[^\s/]+)'
        with open(self.m3u_dosyasi, "r") as dosya:
            icerik = dosya.read()

        if eslesme := re.search(referer_deseni, icerik):
            return eslesme[1]
        else:
            raise ValueError("M3U dosyasında 'mactadi' içeren referer domain bulunamadı!")

    def mactadi_domaini_al(self):
        redirect_url = "https://bit.ly/m/mactadi"
        deneme = 0
        while "bit.ly" in redirect_url and deneme < 5:
            try:
                redirect_url = self.redirect_gec(redirect_url)
            except Exception as e:
                konsol.log(f"[red][!] redirect_gec hata: {e}")
                break
            deneme += 1

        if "bit.ly" in redirect_url or "error" in redirect_url:
            konsol.log("[yellow][!] 5 denemeden sonra bit.ly çözülemedi, yedek linke geçiliyor...")
            try:
                redirect_url = self.redirect_gec("https://t.co/aOAO1eIsqE")
            except Exception as e:
                raise ValueError(f"Yedek linkten de domain alınamadı: {e}")

        return redirect_url

    def redirect_gec(self, redirect_url: str):
        konsol.log(f"[cyan][~] redirect_gec çağrıldı: {redirect_url}")
        try:
            response = self.httpx.get(redirect_url, follow_redirects=True)
        except Exception as e:
            raise ValueError(f"Redirect sırasında hata oluştu: {e}")

        
        tum_url_listesi = [str(r.url) for r in response.history] + [str(response.url)]

        
        for url in tum_url_listesi[::-1]:  
            if "mactadi" in url:
                return url.strip("/")

        raise ValueError("Redirect zincirinde 'mactadi' içeren bir link bulunamadı!")

    def yeni_domaini_al(self, eldeki_domain: str) -> str:
        def check_domain(domain: str) -> str:
            if domain == "https://mactadigiris.xyz":
                raise ValueError("Yeni domain alınamadı")
            return domain

        try:
            
            yeni_domain = check_domain(self.redirect_gec(eldeki_domain))
        except Exception:
            konsol.log("[red][!] `redirect_gec(eldeki_domain)` fonksiyonunda hata oluştu.")
            try:
                
                yeni_domain = check_domain(self.mactadi_domaini_al())
            except Exception:
                konsol.log("[red][!] `mactadi_domaini_al` fonksiyonunda hata oluştu.")
                try:
                    
                    yeni_domain = check_domain(self.redirect_gec("https://t.co/MTLoNVkGQN"))
                except Exception:
                    konsol.log("[red][!] `redirect_gec('https://t.co/MTLoNVkGQN')` fonksiyonunda hata oluştu.")
                    
                    rakam = int(eldeki_domain.split("mactadi")[1].split(".")[0]) + 1
                    yeni_domain = f"https://mactadi{rakam}.xyz"

        return yeni_domain

    def m3u_guncelle(self):
        eldeki_domain = self.referer_domainini_al()
        konsol.log(f"[yellow][~] Bilinen Domain : {eldeki_domain}")

        yeni_domain = self.yeni_domaini_al(eldeki_domain)
        konsol.log(f"[green][+] Yeni Domain    : {yeni_domain}")

        kontrol_url = f"{yeni_domain}/channel.html?id=yayin1"

        with open(self.m3u_dosyasi, "r") as dosya:
            m3u_icerik = dosya.read()

        if not (eski_yayin_url := re.search(r'https?:\/\/[^\/]+\.(shop|click|workers.dev)\/?', m3u_icerik)):
            raise ValueError("M3U dosyasında eski yayın URL'si bulunamadı!")

        eski_yayin_url = eski_yayin_url[0]
        konsol.log(f"[yellow][~] Eski Yayın URL : {eski_yayin_url}")

        
        response = self.httpx.get(kontrol_url, follow_redirects=True)

        if not (yayin_ara := re.search(r'(?:var|let|const)\s+baseurl\s*=\s*"(https?://[^"]+)"', response.text)):
            secici = Selector(response.text)
            baslik = secici.xpath("//title/text()").get()
            if baslik == "404 Not Found":
                yeni_domain = eldeki_domain
                yayin_ara   = [None, eski_yayin_url]
            else:
                konsol.print(response.text)
                raise ValueError("Base URL bulunamadı!")

        yayin_url = yayin_ara[1]
        konsol.log(f"[green][+] Yeni Yayın URL : {yayin_url}")

        yeni_m3u_icerik = m3u_icerik.replace(eski_yayin_url, yayin_url)
        yeni_m3u_icerik = yeni_m3u_icerik.replace(eldeki_domain, yeni_domain)

        with open(self.m3u_dosyasi, "w") as dosya:
            dosya.write(yeni_m3u_icerik)

if __name__ == "__main__":
    guncelleyici = mactadi("1.m3u")
    guncelleyici.m3u_guncelle()
