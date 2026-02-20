class TRGOALSManager:
    def __init__(self):
        self.httpx = Client(timeout=15, verify=False, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5)'})

    def get_dynamic_urls(self):
        try:
            redirect_content = self.httpx.get('https://eniyiyayinci.github.io/redirect/index.html').text
            domain_match = re.search(r'URL=(https:\/\/[^"]+)', redirect_content or '')
            dynamic_domain = (domain_match.group(1) if domain_match else 'https://trgoals896.xyz').rstrip('/') + '/'
            print(f"TRGOALS: Dinamik domain bulundu -> {dynamic_domain}")

            channel_content = self.httpx.get(f"{dynamic_domain}channel.html").text
            base_match = re.search(r'const\s+baseurl\s*=\s*["\']([^"\']+)["\']', channel_content or '', re.IGNORECASE)
            base_url = (base_match.group(1) if base_match else 'https://iss.trgoalshls1.shop').rstrip('/') + '/'
            print(f"TRGOALS: Base URL bulundu -> {base_url}")

            return {'dynamic_domain': dynamic_domain, 'base_url': base_url}
        except Exception as e:
            print(f"TRGOALS: Dinamik URL'ler alınırken hata: {e}")
            return {'dynamic_domain': None, 'base_url': None}

    def calistir(self):
        urls = self.get_dynamic_urls()
        if not urls.get('dynamic_domain') or not urls.get('base_url'):
            return ""

        channels = {1: "BEIN SPORTS 1 (ZIRVE)", 2: "BEIN SPORTS 1 (1)", 3: "BEIN SPORTS 1 (INAT)", 4: "BEIN SPORTS 2", 5: "BEIN SPORTS 3", 6: "BEIN SPORTS 4", 7: "BEIN SPORTS 5", 8: "BEIN SPORTS MAX 1", 9: "BEIN SPORTS MAX 2", 10: "S SPORT PLUS 1", 11: "S SPORT PLUS 2", 13: "TIVIBU SPOR 1", 14: "TIVIBU SPOR 2", 15: "TIVIBU SPOR 3", 16: "SPOR SMART 1", 17: "SPOR SMART 2", 18: "TRT SPOR 1", 19: "TRT SPOR 2", 20: "TRT 1", 21: "A SPOR", 22: "ATV", 23: "TV 8", 24: "TV 8.5", 25: "FORMULA 1", 26: "NBA TV", 27: "EURO SPORT 1", 28: "EURO SPORT 2", 29: "EXXEN SPOR 1", 30: "EXXEN SPOR 2", 31: "EXXEN SPOR 3", 32: "EXXEN SPOR 4", 33: "EXXEN SPOR 5", 34: "EXXEN SPOR 6", 35: "EXXEN SPOR 7", 36: "EXXEN SPOR 8"}
        stream_paths = {1: "yayinzirve.m3u8", 2: "yayin1.m3u8", 3: "yayininat.m3u8", 4: "yayinb2.m3u8", 5: "yayinb3.m3u8", 6: "yayinb4.m3u8", 7: "yayinb5.m3u8", 8: "yayinbm1.m3u8", 9: "yayinbm2.m3u8", 10: "yayinss.m3u8", 11: "yayinss2.m3u8", 13: "yayint1.m3u8", 14: "yayint2.m3u8", 15: "yayint3.m3u8", 16: "yayinsmarts.m3u8", 17: "yayinsms2.m3u8", 18: "yayintrtspor.m3u8", 19: "yayintrtspor2.m3u8", 20: "yayintrt1.m3u8", 21: "yayinas.m3u8", 22: "yayinatv.m3u8", 23: "yayintv8.m3u8", 24: "yayintv85.m3u8", 25: "yayinf1.m3u8", 26: "yayinnbatv.m3u8", 27: "yayineu1.m3u8", 28: "yayineu2.m3u8", 29: "yayinex1.m3u8", 30: "yayinex2.m3u8", 31: "yayinex3.m3u8", 32: "yayinex4.m3u8", 33: "yayinex5.m3u8", 34: "yayinex6.m3u8", 35: "yayinex7.m3u8", 36: "yayinex8.m3u8"}

        m3u = []
        for channel_id, channel_name in channels.items():
            if channel_id in stream_paths:
                stream_url = f"{urls['base_url']}{stream_paths[channel_id]}"
                m3u.append(f'#EXTINF:-1 group-title="TRGOALS",{channel_name}')
                m3u.append('#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5)')
                m3u.append(f'#EXTVLCOPT:http-referrer={urls["dynamic_domain"]}')
                m3u.append(stream_url)

        content = "\n".join(m3u)
        print(f"TRGOALS içerik uzunluğu: {len(content)}")
        return content
