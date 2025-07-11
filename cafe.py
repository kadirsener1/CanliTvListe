import requests
import re
import os

def find_working_sporcafe(start=5, end=15):
    print("🧭 sporcafe domainleri taranıyor...")
    headers = {"User-Agent": "Mozilla/5.0"}

    for i in range(start, end + 1):
        url = f"https://www.sporcafe{i}.xyz/"
        print(f"🔍 Taranıyor: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200 and "uxsyplayer" in response.text:
                print(f"✅ Aktif domain bulundu: {url}")
                return response.text, url
        except:
            print(f"⚠️ Hata: {url}")
            continue

    print("❌ Aktif domain bulunamadı.")
    return None, None

def find_dynamic_player_domain(page_html):
    match = re.search(r'https?://(main\.uxsyplayer[0-9a-zA-Z\-]+\.click)', page_html)
    if match:
        return f"https://{match.group(1)}"
    return None

def extract_base_stream_url(html):
    match = re.search(r'this\.adsBaseUrl\s*=\s*[\'"]([^\'"]+)', html)
    if match:
        return match.group(1)
    return None

def build_m3u8_links(stream_domain, referer, channel_ids):
    m3u8_links = []
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": referer
    }

    for cid in channel_ids:
        try:
            url = f"{stream_domain}/index.php?id={cid}"
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                base_url = extract_base_stream_url(response.text)
                if base_url:
                    full_url = f"{base_url}{cid}/playlist.m3u8"
                    print(f"✅ {cid} için M3U8 bulundu: {full_url}")
                    m3u8_links.append((cid, full_url))
                else:
                    print(f"❌ baseStreamUrl alınamadı: {cid}")
            else:
                print(f"❌ Yanıt alınamadı: {cid}")
        except Exception as e:
            print(f"⚠️ Hata ({cid}): {e}")
    return m3u8_links

def write_m3u_file(m3u8_links, filename="1.m3u", referer=""):
    if not os.path.exists(filename):
        print("⛔ Dosya bulunamadı. Yeni dosya oluşturulamaz çünkü eski içerik korunmalı.")
        return

    with open(filename, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)

        if line.startswith("#EXTINF") and 'tvg-id="' in line:
            tvg_id_match = re.search(r'tvg-id="([^"]+)"', line)
            if tvg_id_match:
                kanal_id = tvg_id_match.group(1)
                matched = next(((cid, url) for cid, url in m3u8_links if cid == kanal_id), None)

                if matched:
                    i += 1
                    if i < len(lines) and lines[i].startswith("#EXTVLCOPT:http-referrer"):
                        i += 1
                    if i < len(lines) and lines[i].startswith("http"):
                        i += 1

                    new_lines.append(f"#EXTVLCOPT:http-referrer= {referer}")
                    new_lines.append(matched[1])
                    continue
        i += 1

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))
    print(f"✅ Güncelleme tamamlandı: {filename}")

# tvg-id ile eşleşecek kanal ID'leri
channel_ids = [
    "sbeinsports-1",
    "sbeinsports-2",
    "sbeinsports-3",
    "sbeinsports-4",
    "sbeinsports-5",
    "sbeinsportsmax-1",
    "sbeinsportsmax-2",
    "sssport",
    "sssport2",
    "ssmartspor",
    "ssmartspor2",
    "stivibuspor-1",
    "stivibuspor-2",
    "stivibuspor-3",
    "stivibuspor-4",
    "sbeinsportshaber",
    "saspor",
    "seurosport1",
    "seurosport2",
    "sf1",
    "sdazn1",
    "sdazn2",
    "sufcfightpass",
    "smotorsporttv",
    "smotorvisiontv",
    "stabiispor",
    "sssportplus1"
]

# Ana işlem
html, referer_url = find_working_sporcafe()

if html:
    stream_domain = find_dynamic_player_domain(html)
    if stream_domain:
        print(f"\n🔗 Yayın domaini bulundu: {stream_domain}")
        m3u8_list = build_m3u8_links(stream_domain, referer_url, channel_ids)
        if m3u8_list:
            write_m3u_file(m3u8_list, referer=referer_url)
        else:
            print("❌ Hiçbir yayın linki oluşturulamadı.")
    else:
        print("❌ Yayın domaini bulunamadı.")
else:
    print("⛔ Aktif yayın alınamadı.")
