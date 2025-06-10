import re
import datetime
from flask import session
import mysql.connector
import difflib

faq = {
    "apa itu telkom university": "Telkom University adalah kampus swasta yang berada di 4 lokasi yaitu Bandung sebagai pusatnya, Surabaya, Jakarta, Purwokerto",
    "dimana lokasi telkom university": "Telkom University terletak di 4 lokasi yaitu Bandung sebagai pusatnya, Surabaya, Jakarta, Purwokerto Saat ini anda trdaftar sebagai mahasiswa di Telkom University Surabaya.",
    "apa saja program studi yang tersedia": "Beberapa prodi di antaranya Informatika, Sistem Informasi, Teknik Telekomunikasi, dan Manajemen Bisnis."
}

deskripsi_prodi = {
    "informatika": "Teknik Informatika mempelajari tentang pengembangan perangkat lunak, algoritma, dan sistem cerdas.",
    "sistem informasi": "Sistem Informasi menjembatani antara teknologi dan bisnis, fokus pada pengelolaan informasi.",
    "teknik telekomunikasi": "Teknik Telekomunikasi fokus pada sistem komunikasi seperti jaringan dan sinyal digital."
}

basic_intents = {
    "halo": "Halo juga! Ada yang bisa saya bantu?",
    "hi": "Hai! Ada yang ingin kamu tanyakan?",
    "terima kasih": "Sama-sama! 😊",
    "siapa kamu": "Saya adalah chatbot dari Telkom University untuk membantu menjawab pertanyaanmu. Silahkan bertanya!"
}

hari_mapping = {
    "monday": "senin",
    "tuesday": "selasa",
    "wednesday": "rabu",
    "thursday": "kamis",
    "friday": "jumat",
    "saturday": "sabtu",
    "sunday": "minggu"
}

def find_closest_question(user_input):
    matches = difflib.get_close_matches(user_input, faq.keys(), n=1, cutoff=0.6)
    return matches[0] if matches else None

def get_response(user_input):
    cleaned_input = re.sub(r'[^\w\s]', '', user_input.lower())
    hari_ditanya = None

    for hari in hari_mapping.values():
        if hari in cleaned_input:
            hari_ditanya = hari
            break

    if "hari ini" in cleaned_input:
        today_en = datetime.datetime.today().strftime('%A').lower()
        hari_ditanya = hari_mapping.get(today_en)

    elif "besok" in cleaned_input:
        besok = datetime.datetime.today() + datetime.timedelta(days=1)
        hari_besok = besok.strftime('%A').lower()
        hari_ditanya = hari_mapping.get(hari_besok)

    if any(word in cleaned_input for word in ["jadwal", "kuliah", "hari", "besok"]):
        try:
            user = session.get('user')
            if user:
                conn = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="data_mahasiswa"
                )
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT jadwal_mata_kuliah FROM users WHERE id = %s", (user['id'],))
                result = cursor.fetchone()
                cursor.close()
                conn.close()

                if result and result['jadwal_mata_kuliah']:
                    jadwal = result['jadwal_mata_kuliah'].splitlines()

                    if hari_ditanya:
                        jadwal_hari = [j for j in jadwal if hari_ditanya in j.lower()]
                        if jadwal_hari:
                            return f"Jadwal hari {hari_ditanya.capitalize()}:\n" + "\n".join(jadwal_hari)
                        else:
                            return f"Tidak ada kuliah pada hari {hari_ditanya.capitalize()}."
                    else:
                        return f"Berikut jadwal kuliah Anda:\n" + "\n".join(jadwal)
                else:
                    return "Maaf, jadwal kuliah Anda tidak ditemukan."
            else:
                return "Anda belum login."
        except Exception as e:
            return f"Terjadi kesalahan saat mengambil jadwal: {str(e)}"

    for phrase, reply in basic_intents.items():
        if phrase in cleaned_input:
            return reply

    for prodi, deskripsi in deskripsi_prodi.items():
        if f"apa itu {prodi}" in cleaned_input:
            return deskripsi

    faq_match = find_closest_question(cleaned_input)
    if faq_match:
        return faq[faq_match]

    return "Maaf, saya tidak mengerti pertanyaan Anda."
