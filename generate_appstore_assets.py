#!/usr/bin/env python3
"""
DemoScope iOS App Store Custom Product Page Asset Generator
============================================================
Generates localized promotional screenshots for iPhone and iPad.
Custom Product Page focus: Teleprompter feature.

Usage:
    python3 generate_appstore_assets.py

Output:
    AppStoreAssets/
      iPhone/<lang>/  (4 images per language)
      iPad/<lang>/    (4 images per language)
"""

import subprocess
import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter


# ─────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PORTRAIT_DIR = os.path.join(BASE_DIR, "Portrait")
OUTPUT_DIR = os.path.join(BASE_DIR, "AppStoreAssets")

CLIPS = ["woman_1", "man_1", "woman_2", "man_2"]


# ─────────────────────────────────────────────
# FRAME TIMESTAMPS  (min:sec to grab from each video)
# ─────────────────────────────────────────────
FRAME_TIMESTAMPS = {
    "woman_1": "0:01",
    "man_1":   "0:01",
    "woman_2": "0:01",
    "man_2":   "0:01",
}


# ─────────────────────────────────────────────
# APP STORE SCREENSHOT SIZES
# ─────────────────────────────────────────────
IPHONE_SIZE = (1284, 2778)    # 6.7" portrait
IPAD_SIZE   = (2064, 2752)    # 12.9" 6th gen portrait


# ─────────────────────────────────────────────
# PHONE MOCKUP
# ─────────────────────────────────────────────
PHONE_ASPECT = 2.076               # height / width (iPhone 15 Pro)
PHONE_BODY_COLOR = (28, 28, 30)    # Space black
PHONE_BODY_RADIUS_PCT = 0.14       # Corner radius as % of phone width
PHONE_BEZEL_PCT = 0.022            # Bezel as % of phone width
PHONE_ISLAND_W_PCT = 0.30          # Dynamic island width as % of screen
PHONE_ISLAND_H_PCT = 0.014         # Dynamic island height as % of screen
PHONE_BORDER_PCT = 0.014           # Colored border as % of phone width


# ─────────────────────────────────────────────
# VISUAL DESIGN
# ─────────────────────────────────────────────
BG_GRADIENTS = {
    "woman_1": ((255, 107, 107), (255, 160, 137)),   # Coral
    "man_1":   ((46, 196, 182),  (86, 227, 215)),    # Teal
    "woman_2": ((139, 92, 246),  (178, 147, 255)),    # Violet
    "man_2":   ((245, 158, 11),  (252, 196, 55)),     # Amber
}

LABEL_BLOCK_COLOR = (0, 0, 0, 210)   # Dark label behind headline text
TEXT_COLOR = (255, 255, 255, 255)
TEXT_SHADOW = (0, 0, 0, 90)


# ─────────────────────────────────────────────
# FONTS
# ─────────────────────────────────────────────
LATIN_FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
CJK_FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
THAI_FONT = "/usr/share/fonts/opentype/tlwg/Loma-Bold.otf"
HINDI_FONT = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
CJK_INDICES = {}


# ─────────────────────────────────────────────
# LOCALIZED MARKETING COPY
# ─────────────────────────────────────────────
COPY = {
    "en-US": [
        ("Nail Every\nTake",
         "Professional teleprompter at your fingertips"),
        ("Speak With\nConfidence",
         "Read your script naturally on camera"),
        ("Sound Like\na Pro",
         "Professional tools, now in your pocket"),
        ("Effortless\nExecutive Presence",
         "Put your best self forward, every time"),
    ],
    "fr": [
        ("Réussissez\nChaque Prise",
         "Téléprompteur pro à portée de main"),
        ("Parlez Avec\nAssurance",
         "Lisez votre texte naturellement"),
        ("Parlez\nComme un Pro",
         "Des outils pro dans votre poche"),
        ("Un Charisme\nSans Effort",
         "Montrez le meilleur de vous-même"),
    ],
    "de": [
        ("Jede Aufnahme\nPerfekt",
         "Profi-Teleprompter griffbereit"),
        ("Selbstbewusst\nSprechen",
         "Ihr Skript natürlich vor der Kamera"),
        ("Wie ein Profi\nKlingen",
         "Profi-Werkzeuge in Ihrer Tasche"),
        ("Mühelose\nPräsenz",
         "Zeigen Sie Ihre beste Seite"),
    ],
    "ja": [
        ("完璧なテイクを\n毎回実現",
         "プロ仕様テレプロンプターをあなたの手に"),
        ("自信を持って\n話そう",
         "カメラの前で自然に原稿を読む"),
        ("プロのように\n話す",
         "プロのツールをポケットの中に"),
        ("エグゼクティブの\n存在感を楽々と",
         "いつでも最高の自分を見せよう"),
    ],
    "ko": [
        ("매 테이크를\n완벽하게",
         "전문 텔레프롬프터 손끝에서 바로"),
        ("자신감 있게\n말하세요",
         "카메라 앞에서 자연스럽게 대본 읽기"),
        ("프로처럼\n말하기",
         "전문가 도구를 주머니 속에"),
        ("손쉬운\n리더십 존재감",
         "매번 최고의 모습을 보여주세요"),
    ],
    "zh-Hans": [
        ("完美\n每一条",
         "专业提词器触手可及"),
        ("自信\n开口说",
         "在镜头前自然读稿"),
        ("像专业人士\n一样表达",
         "专业工具尽在掌中"),
        ("从容展现\n领导力",
         "随时展现最好的自己"),
    ],
    "zh-Hant": [
        ("完美\n每一條",
         "專業提詞器觸手可及"),
        ("自信\n開口說",
         "在鏡頭前自然讀稿"),
        ("像專業人士\n一樣表達",
         "專業工具盡在掌中"),
        ("從容展現\n領導力",
         "隨時展現最好的自己"),
    ],
    "pt-BR": [
        ("Acerte Cada\nTomada",
         "Teleprompter profissional na ponta dos dedos"),
        ("Fale Com\nConfiança",
         "Leia seu roteiro naturalmente"),
        ("Fale Como\num Profissional",
         "Ferramentas profissionais no seu bolso"),
        ("Presença Executiva\nSem Esforço",
         "Mostre o melhor de si, sempre"),
    ],
    "es-ES": [
        ("Clava Cada\nToma",
         "Teleprompter profesional en tus manos"),
        ("Habla Con\nConfianza",
         "Lee tu guion con naturalidad ante la cámara"),
        ("Habla Como\nun Profesional",
         "Herramientas profesionales en tu bolsillo"),
        ("Presencia Ejecutiva\nSin Esfuerzo",
         "Da lo mejor de ti, siempre"),
    ],
    "es-MX": [
        ("Clava Cada\nToma",
         "Teleprompter profesional en tus manos"),
        ("Habla Con\nConfianza",
         "Lee tu guion con naturalidad ante la cámara"),
        ("Habla Como\nun Profesional",
         "Herramientas profesionales en tu bolsillo"),
        ("Presencia Ejecutiva\nSin Esfuerzo",
         "Da lo mejor de ti, siempre"),
    ],
    "it": [
        ("Perfetto a\nOgni Ripresa",
         "Teleprompter professionale a portata di mano"),
        ("Parla Con\nSicurezza",
         "Leggi il copione in modo naturale"),
        ("Parla Come\nun Professionista",
         "Strumenti professionali in tasca"),
        ("Presenza Impeccabile\nSenza Sforzo",
         "Dai il meglio di te, sempre"),
    ],
    "nl-NL": [
        ("Elke Take\nPerfect",
         "Professionele teleprompter binnen handbereik"),
        ("Spreek Met\nZelfvertrouwen",
         "Lees je script natuurlijk voor de camera"),
        ("Klink Als\neen Pro",
         "Professionele tools in je zak"),
        ("Moeiteloze\nUitstraling",
         "Laat je van je beste kant zien"),
    ],
    "ru": [
        ("Идеальный\nДубль",
         "Профессиональный телесуфлёр у вас в руках"),
        ("Говорите\nУверенно",
         "Читайте сценарий естественно на камеру"),
        ("Говорите\nКак Профессионал",
         "Профессиональные инструменты в вашем кармане"),
        ("Лёгкая\nХаризма",
         "Покажите лучшую версию себя"),
    ],
    "tr": [
        ("Her Çekimde\nMükemmel",
         "Profesyonel prompter parmaklarınızın ucunda"),
        ("Özgüvenle\nKonuşun",
         "Metninizi kamera önünde doğal okuyun"),
        ("Profesyonel\nGibi Konuşun",
         "Profesyonel araçlar artık cebinizde"),
        ("Zahmetsiz\nLiderlik Aurası",
         "Her zaman en iyi halinizi gösterin"),
    ],
    "sv": [
        ("Spika Varje\nTagning",
         "Professionell teleprompter i fickan"),
        ("Tala Med\nSjälvförtroende",
         "Läs ditt manus naturligt framför kameran"),
        ("Låt Som\nett Proffs",
         "Professionella verktyg i din ficka"),
        ("Naturlig\nLedarskapsaura",
         "Visa din bästa sida, varje gång"),
    ],
    "da": [
        ("Perfekt Hver\nGang",
         "Professionel teleprompter lige ved hånden"),
        ("Tal Med\nSelvsikkerhed",
         "Læs dit manuskript naturligt foran kameraet"),
        ("Lyd Som\nen Professionel",
         "Professionelle værktøjer i din lomme"),
        ("Ubesværet\nUdstråling",
         "Vis dig fra din bedste side, hver gang"),
    ],
    "fi": [
        ("Joka Otto\nTäydellinen",
         "Ammattimainen teleprompteri käden ulottuvilla"),
        ("Puhu\nItseVarmasti",
         "Lue käsikirjoituksesi luonnollisesti kameran edessä"),
        ("Kuulosta\nAmmattilaiselta",
         "Ammattityökalut taskussasi"),
        ("Vaivatonta\nKarismaa",
         "Näytä parhaat puolesi joka kerta"),
    ],
    "no": [
        ("Spiker Hvert\nTak",
         "Profesjonell teleprompter rett i lommen"),
        ("Snakk Med\nSelvsikkerhet",
         "Les manuset naturlig foran kameraet"),
        ("Hør Ut Som\nen Proff",
         "Profesjonelle verktøy i lommen din"),
        ("Uanstrengt\nUtstråling",
         "Vis deg fra din beste side, hver gang"),
    ],
    "pl": [
        ("Perfekcyjne\nUjęcie",
         "Profesjonalny teleprompter na wyciągnięcie ręki"),
        ("Mów\nz Pewnością",
         "Czytaj scenariusz naturalnie przed kamerą"),
        ("Mów Jak\nProfesjonalista",
         "Profesjonalne narzędzia w Twojej kieszeni"),
        ("Naturalny\nAutorytet",
         "Pokaż się z najlepszej strony za każdym razem"),
    ],
    "id": [
        ("Sempurna di\nSetiap Ambilan",
         "Teleprompter profesional di ujung jari Anda"),
        ("Bicara Dengan\nPercaya Diri",
         "Baca naskah secara alami di depan kamera"),
        ("Bicara Seperti\nProfesional",
         "Alat profesional kini di saku Anda"),
        ("Karisma\nTanpa Usaha",
         "Tampilkan yang terbaik dari diri Anda"),
    ],
    "vi": [
        ("Hoàn Hảo\nMọi Cảnh Quay",
         "Máy nhắc chữ chuyên nghiệp trong tầm tay"),
        ("Nói Với\nSự Tự Tin",
         "Đọc kịch bản tự nhiên trước máy quay"),
        ("Nói Như\nChuyên Gia",
         "Công cụ chuyên nghiệp trong túi bạn"),
        ("Phong Thái\nLãnh Đạo",
         "Thể hiện phiên bản tốt nhất của bạn"),
    ],
    "ms": [
        ("Sempurna Setiap\nRakaman",
         "Teleprompter profesional di hujung jari"),
        ("Berucap Dengan\nKeyakinan",
         "Baca skrip secara semula jadi di hadapan kamera"),
        ("Berucap Seperti\nProfesional",
         "Alat profesional kini di poket anda"),
        ("Karisma Tanpa\nUsaha",
         "Tonjolkan yang terbaik daripada diri anda"),
    ],
    "uk": [
        ("Ідеальний\nДубль",
         "Професійний телесуфлер у ваших руках"),
        ("Говоріть\nВпевнено",
         "Читайте сценарій природно перед камерою"),
        ("Говоріть\nЯк Професіонал",
         "Професійні інструменти у вашій кишені"),
        ("Легка\nХаризма",
         "Покажіть найкращу версію себе"),
    ],
    "el": [
        ("Τέλειο Κάθε\nΛήψη",
         "Επαγγελματικός τηλεπροβολέας στα χέρια σας"),
        ("Μιλήστε Με\nΑυτοπεποίθηση",
         "Διαβάστε το σενάριό σας φυσικά στην κάμερα"),
        ("Ακουστείτε Σαν\nΕπαγγελματίας",
         "Επαγγελματικά εργαλεία στην τσέπη σας"),
        ("Αβίαστη\nΠαρουσία",
         "Δείξτε τον καλύτερό σας εαυτό, κάθε φορά"),
    ],
    "ro": [
        ("Perfect la\nFiecare Dublă",
         "Teleprompter profesional la îndemâna ta"),
        ("Vorbește Cu\nÎncredere",
         "Citește-ți scenariul natural în fața camerei"),
        ("Vorbește Ca\nun Profesionist",
         "Instrumente profesionale în buzunarul tău"),
        ("Prezență\nFără Efort",
         "Arată ce ai mai bun, de fiecare dată"),
    ],
    "hu": [
        ("Minden Felvétel\nTökéletes",
         "Professzionális súgógép a kezedben"),
        ("Beszélj\nMagabiztosan",
         "Olvasd a szöveged természetesen a kamera előtt"),
        ("Beszélj\nMint egy Profi",
         "Profi eszközök a zsebedben"),
        ("Természetes\nKisugárzás",
         "Mutasd a legjobb formád, mindig"),
    ],
    "cs": [
        ("Dokonalý\nKaždý Záběr",
         "Profesionální teleprompter na dosah ruky"),
        ("Mluvte\nSebevědomě",
         "Čtěte scénář přirozeně před kamerou"),
        ("Mluvte Jako\nProfesionál",
         "Profesionální nástroje ve vaší kapse"),
        ("Přirozená\nPrezence",
         "Ukažte to nejlepší ze sebe pokaždé"),
    ],
    "ca": [
        ("Clava Cada\nPresa",
         "Teleprompter professional a l'abast de la mà"),
        ("Parla Amb\nConfiança",
         "Llegeix el teu guió amb naturalitat davant la càmera"),
        ("Parla Com\nun Professional",
         "Eines professionals a la teva butxaca"),
        ("Presència\nSense Esforç",
         "Mostra el millor de tu, sempre"),
    ],
    "hr": [
        ("Savršen Svaki\nKadar",
         "Profesionalni teleprompter na dohvat ruke"),
        ("Govorite\nSamopouzdano",
         "Čitajte scenarij prirodno pred kamerom"),
        ("Zvučite Kao\nProfesionalac",
         "Profesionalni alati u vašem džepu"),
        ("Prirodna\nKarizma",
         "Pokažite najbolju verziju sebe svaki put"),
    ],
    "sk": [
        ("Dokonalý\nKaždý Záber",
         "Profesionálny teleprompter na dosah ruky"),
        ("Hovorte\nSebavedome",
         "Čítajte scenár prirodzene pred kamerou"),
        ("Hovorte Ako\nProfesionál",
         "Profesionálne nástroje vo vašom vrecku"),
        ("Prirodzená\nCharizma",
         "Ukážte to najlepšie zo seba zakaždým"),
    ],
    "th": [
        ("สมบูรณ์แบบ\nทุกเทค",
         "เทเลพรอมเตอร์มืออาชีพในมือคุณ"),
        ("พูดอย่าง\nมั่นใจ",
         "อ่านสคริปต์อย่างเป็นธรรมชาติหน้ากล้อง"),
        ("พูดอย่าง\nมืออาชีพ",
         "เครื่องมือระดับมืออาชีพในกระเป๋าคุณ"),
        ("บุคลิกผู้นำ\nอย่างง่ายดาย",
         "แสดงตัวตนที่ดีที่สุดของคุณทุกครั้ง"),
    ],
    "hi": [
        ("हर टेक\nपरफेक्ट",
         "पेशेवर टेलीप्रॉम्प्टर आपकी उंगलियों पर"),
        ("आत्मविश्वास से\nबोलें",
         "कैमरे के सामने स्वाभाविक रूप से स्क्रिप्ट पढ़ें"),
        ("प्रो की तरह\nबोलें",
         "पेशेवर उपकरण अब आपकी जेब में"),
        ("सहज नेतृत्व\nप्रभाव",
         "हमेशा अपना सर्वश्रेष्ठ दिखाएं"),
    ],
}


# ─────────────────────────────────────────────
# TELEPROMPTER SAMPLE TEXT  (per-clip, per-language)
#   woman_1 → Business / entrepreneurship coach
#   man_1   → Online educator / course creator
#   woman_2 → Fitness / wellness coach
#   man_2   → Tech podcaster / reviewer
# ─────────────────────────────────────────────
PROMPTER_TEXT = {
    "woman_1": {
        "en-US": [
            "and that's why a strong brand identity",
            "matters more than ever. Let me share",
            "my top three strategies for growth…",
        ],
        "fr": [
            "et c'est pourquoi une identité de marque",
            "compte plus que jamais. Laissez-moi",
            "partager mes trois stratégies de croissance…",
        ],
        "de": [
            "und deshalb ist eine starke Markenidentität",
            "wichtiger denn je. Lassen Sie mich",
            "drei Wachstumsstrategien teilen…",
        ],
        "ja": [
            "だからこそ強いブランドが",
            "今まで以上に重要なのです。では",
            "成長戦略を3つご紹介します…",
        ],
        "ko": [
            "그래서 강력한 브랜드 정체성이",
            "그 어느 때보다 중요합니다.",
            "성장 전략 세 가지를 공유할게요…",
        ],
        "zh-Hans": [
            "这就是为什么强大的品牌形象",
            "比以往任何时候都更重要。",
            "让我分享三个增长策略…",
        ],
        "zh-Hant": [
            "這就是為什麼強大的品牌形象",
            "比以往任何時候都更重要。",
            "讓我分享三個增長策略…",
        ],
        "pt-BR": [
            "e é por isso que uma identidade de marca",
            "importa mais do que nunca. Vou",
            "compartilhar três estratégias de crescimento…",
        ],
        "es-ES": [
            "y por eso una identidad de marca fuerte",
            "importa más que nunca. Déjame",
            "compartir mis tres estrategias de crecimiento…",
        ],
        "es-MX": [
            "y por eso una identidad de marca fuerte",
            "importa más que nunca. Déjame",
            "compartir mis tres estrategias de crecimiento…",
        ],
        "it": [
            "ed è per questo che un'identità di marca forte",
            "conta più che mai. Lasciate che condivida",
            "le mie tre strategie di crescita…",
        ],
        "nl-NL": [
            "en daarom is een sterke merkidentiteit",
            "belangrijker dan ooit. Laat me",
            "drie groeistrategieën met je delen…",
        ],
        "ru": [
            "именно поэтому сильная идентичность бренда",
            "важна как никогда. Позвольте",
            "поделиться тремя стратегиями роста…",
        ],
        "tr": [
            "işte bu yüzden güçlü bir marka kimliği",
            "her zamankinden daha önemli. Sizinle",
            "üç büyüme stratejimi paylaşayım…",
        ],
        "sv": [
            "och det är därför en stark varumärkesidentitet",
            "är viktigare än någonsin. Låt mig dela",
            "mina tre bästa tillväxtstrategier…",
        ],
        "da": [
            "og det er derfor en stærk brandidentitet",
            "er vigtigere end nogensinde. Lad mig",
            "dele tre vækststrategier med jer…",
        ],
        "fi": [
            "ja siksi vahva brändi-identiteetti",
            "on tärkeämpää kuin koskaan. Kerron",
            "kolme parasta kasvustrategiaani…",
        ],
        "no": [
            "og det er derfor en sterk merkevareidentitet",
            "betyr mer enn noensinne. La meg dele",
            "mine tre beste vekststrategier…",
        ],
        "pl": [
            "i dlatego silna tożsamość marki",
            "jest ważniejsza niż kiedykolwiek. Pozwólcie,",
            "że podzielę się trzema strategiami wzrostu…",
        ],
        "id": [
            "dan itulah mengapa identitas merek yang kuat",
            "lebih penting dari sebelumnya. Izinkan saya",
            "berbagi tiga strategi pertumbuhan…",
        ],
        "vi": [
            "và đó là lý do bản sắc thương hiệu",
            "quan trọng hơn bao giờ hết. Hãy để tôi",
            "chia sẻ ba chiến lược tăng trưởng…",
        ],
        "ms": [
            "dan itulah sebabnya identiti jenama yang kuat",
            "lebih penting berbanding sebelum ini.",
            "Izinkan saya kongsi tiga strategi pertumbuhan…",
        ],
        "uk": [
            "саме тому сильна ідентичність бренду",
            "важлива як ніколи. Дозвольте",
            "поділитися трьома стратегіями зростання…",
        ],
        "el": [
            "γι' αυτό μια ισχυρή ταυτότητα brand",
            "μετράει περισσότερο από ποτέ. Επιτρέψτε μου",
            "να μοιραστώ τρεις στρατηγικές ανάπτυξης…",
        ],
        "ro": [
            "și de aceea o identitate puternică de brand",
            "contează mai mult ca niciodată. Permiteți-mi",
            "să vă împărtășesc trei strategii de creștere…",
        ],
        "hu": [
            "ezért egy erős márkaidentitás",
            "fontosabb, mint valaha. Hadd osszam meg",
            "a három legjobb növekedési stratégiámat…",
        ],
        "cs": [
            "a proto je silná identita značky",
            "důležitější než kdy dříve. Dovolte mi",
            "sdílet tři strategie růstu…",
        ],
        "ca": [
            "i per això una identitat de marca forta",
            "importa més que mai. Deixeu-me",
            "compartir tres estratègies de creixement…",
        ],
        "hr": [
            "i zato je snažan identitet brenda",
            "važniji nego ikada. Dopustite da",
            "podijelim tri strategije rasta…",
        ],
        "sk": [
            "a preto je silná identita značky",
            "dôležitejšia ako kedykoľvek. Dovoľte mi",
            "zdieľať tri stratégie rastu…",
        ],
        "th": [
            "นั่นคือเหตุผลที่อัตลักษณ์แบรนด์ที่แข็งแกร่ง",
            "สำคัญมากกว่าที่เคย ให้ผม",
            "แชร์สามกลยุทธ์การเติบโต…",
        ],
        "hi": [
            "और इसीलिए एक मजबूत ब्रांड पहचान",
            "पहले से कहीं ज्यादा मायने रखती है।",
            "मेरी तीन विकास रणनीतियां सुनिए…",
        ],
    },
    "man_1": {
        "en-US": [
            "the key to effective lesson design",
            "is breaking concepts into smaller steps.",
            "Let me walk you through an example…",
        ],
        "fr": [
            "la clé d'un cours efficace, c'est",
            "de découper les concepts en étapes.",
            "Voyons un exemple concret…",
        ],
        "de": [
            "der Schlüssel zu gutem Unterricht",
            "ist es, Konzepte aufzuteilen.",
            "Schauen wir uns ein Beispiel an…",
        ],
        "ja": [
            "効果的なレッスン設計の鍵は",
            "概念を小さなステップに分けること。",
            "具体例を見ていきましょう…",
        ],
        "ko": [
            "효과적인 수업 설계의 핵심은",
            "개념을 작은 단계로 나누는 것입니다.",
            "예시를 함께 살펴볼까요…",
        ],
        "zh-Hans": [
            "有效课程设计的关键",
            "是将概念拆分为小步骤。",
            "让我们看一个具体的例子…",
        ],
        "zh-Hant": [
            "有效課程設計的關鍵",
            "是將概念拆分為小步驟。",
            "讓我們看一個具體的例子…",
        ],
        "pt-BR": [
            "a chave para um ensino eficaz é",
            "dividir conceitos em etapas menores.",
            "Vamos ver um exemplo prático…",
        ],
        "es-ES": [
            "la clave para un diseño de lección eficaz",
            "es dividir los conceptos en pasos más pequeños.",
            "Veamos un ejemplo práctico…",
        ],
        "es-MX": [
            "la clave para un diseño de lección eficaz",
            "es dividir los conceptos en pasos más pequeños.",
            "Veamos un ejemplo práctico…",
        ],
        "it": [
            "la chiave per una lezione efficace",
            "è scomporre i concetti in piccoli passi.",
            "Vediamo un esempio concreto…",
        ],
        "nl-NL": [
            "de sleutel tot effectief lesontwerp",
            "is concepten opdelen in kleinere stappen.",
            "Laat me een voorbeeld doorlopen…",
        ],
        "ru": [
            "ключ к эффективному построению урока —",
            "разбивать концепции на маленькие шаги.",
            "Давайте разберём пример…",
        ],
        "tr": [
            "etkili ders tasarımının anahtarı",
            "kavramları küçük adımlara bölmektir.",
            "Bir örnek üzerinden gidelim…",
        ],
        "sv": [
            "nyckeln till effektiv lektionsdesign",
            "är att bryta ner koncept i mindre steg.",
            "Låt mig visa ett exempel…",
        ],
        "da": [
            "nøglen til effektivt lektionsdesign",
            "er at opdele koncepter i mindre trin.",
            "Lad mig vise jer et eksempel…",
        ],
        "fi": [
            "tehokkaan opetuksen avain on",
            "jakaa käsitteet pienempiin vaiheisiin.",
            "Katsotaan esimerkkiä yhdessä…",
        ],
        "no": [
            "nøkkelen til effektiv leksjonsdesign",
            "er å dele opp konsepter i mindre steg.",
            "La meg vise dere et eksempel…",
        ],
        "pl": [
            "kluczem do skutecznego nauczania",
            "jest dzielenie pojęć na mniejsze kroki.",
            "Pokażę wam to na przykładzie…",
        ],
        "id": [
            "kunci desain pelajaran yang efektif",
            "adalah memecah konsep menjadi langkah kecil.",
            "Mari kita lihat contohnya…",
        ],
        "vi": [
            "chìa khóa để thiết kế bài học hiệu quả",
            "là chia nhỏ khái niệm thành các bước.",
            "Hãy cùng xem một ví dụ…",
        ],
        "ms": [
            "kunci reka bentuk pelajaran yang berkesan",
            "ialah memecahkan konsep kepada langkah kecil.",
            "Mari kita lihat satu contoh…",
        ],
        "uk": [
            "ключ до ефективного уроку —",
            "розбити концепції на менші кроки.",
            "Давайте розглянемо приклад…",
        ],
        "el": [
            "το κλειδί για αποτελεσματικά μαθήματα",
            "είναι να σπάτε τις έννοιες σε μικρά βήματα.",
            "Ας δούμε ένα παράδειγμα…",
        ],
        "ro": [
            "cheia unui design eficient al lecției",
            "este să împarți conceptele în pași mici.",
            "Hai să vedem un exemplu concret…",
        ],
        "hu": [
            "a hatékony oktatás kulcsa az,",
            "hogy a fogalmakat kis lépésekre bontjuk.",
            "Nézzünk egy példát együtt…",
        ],
        "cs": [
            "klíčem k efektivnímu návrhu lekcí",
            "je rozdělit koncepty do menších kroků.",
            "Podívejme se na příklad…",
        ],
        "ca": [
            "la clau per a un disseny de lliçó eficaç",
            "és dividir els conceptes en passos petits.",
            "Vegem un exemple pràctic…",
        ],
        "hr": [
            "ključ učinkovitog dizajna lekcije",
            "je razbiti koncepte u manje korake.",
            "Pogledajmo jedan primjer…",
        ],
        "sk": [
            "kľúčom k efektívnemu návrhu lekcií",
            "je rozdeliť koncepty na menšie kroky.",
            "Pozrime sa na príklad…",
        ],
        "th": [
            "กุญแจสำคัญของการออกแบบบทเรียนที่ดี",
            "คือการแบ่งแนวคิดเป็นขั้นตอนเล็กๆ",
            "มาดูตัวอย่างกันเลย…",
        ],
        "hi": [
            "प्रभावी पाठ डिज़ाइन की कुंजी है",
            "अवधारणाओं को छोटे चरणों में बांटना।",
            "चलिए एक उदाहरण देखते हैं…",
        ],
    },
    "woman_2": {
        "en-US": [
            "your form is everything. Keep your core",
            "engaged and shoulders back. Now let's",
            "move into our next set of reps…",
        ],
        "fr": [
            "la posture est primordiale. Gardez les",
            "abdos engagés, épaules en arrière.",
            "Passons à la série suivante…",
        ],
        "de": [
            "die Haltung ist alles. Bauchmuskeln",
            "anspannen, Schultern zurück. Weiter",
            "zur nächsten Übungsreihe…",
        ],
        "ja": [
            "フォームがすべてです。体幹を",
            "意識して肩を引いてください。",
            "次のセットに移りましょう…",
        ],
        "ko": [
            "자세가 전부입니다. 코어에 힘주고",
            "어깨를 뒤로 당기세요. 자, 이제",
            "다음 세트로 넘어갈게요…",
        ],
        "zh-Hans": [
            "姿势是关键。保持核心收紧，",
            "肩膀向后打开。现在",
            "我们进入下一组训练…",
        ],
        "zh-Hant": [
            "姿勢是關鍵。保持核心收緊，",
            "肩膀向後打開。現在",
            "我們進入下一組訓練…",
        ],
        "pt-BR": [
            "a postura é tudo. Mantenha o core",
            "ativado e os ombros para trás.",
            "Vamos para a próxima série…",
        ],
        "es-ES": [
            "tu postura lo es todo. Mantén el core",
            "activado y los hombros atrás. Ahora",
            "pasemos a la siguiente serie…",
        ],
        "es-MX": [
            "tu postura lo es todo. Mantén el core",
            "activado y los hombros atrás. Ahora",
            "pasemos a la siguiente serie…",
        ],
        "it": [
            "la postura è tutto. Mantieni il core",
            "attivato e le spalle indietro. Ora",
            "passiamo alla serie successiva…",
        ],
        "nl-NL": [
            "je houding is alles. Houd je core",
            "aangespannen en schouders naar achteren.",
            "Nu naar de volgende set…",
        ],
        "ru": [
            "осанка — это всё. Держите пресс",
            "напряжённым, плечи назад. А теперь",
            "переходим к следующему подходу…",
        ],
        "tr": [
            "duruşunuz her şeydir. Karın kaslarınızı",
            "sıkın ve omuzları gerin. Şimdi",
            "bir sonraki sete geçelim…",
        ],
        "sv": [
            "din hållning är allt. Håll core",
            "aktiverad och axlarna bakåt. Nu",
            "går vi vidare till nästa set…",
        ],
        "da": [
            "din holdning er alt. Hold din core",
            "aktiveret og skuldrene tilbage. Nu",
            "går vi videre til næste sæt…",
        ],
        "fi": [
            "ryhtisi on kaikki kaikessa. Pidä keskivartalo",
            "tiukkana ja hartiat takana. Nyt",
            "siirrytään seuraavaan sarjaan…",
        ],
        "no": [
            "holdningen din er alt. Hold kjernen",
            "aktivert og skuldrene tilbake. Nå",
            "går vi videre til neste sett…",
        ],
        "pl": [
            "postawa to podstawa. Napnij mięśnie",
            "brzucha i cofnij ramiona. Teraz",
            "przechodzimy do kolejnej serii…",
        ],
        "id": [
            "postur tubuh adalah segalanya. Jaga otot inti",
            "tetap aktif dan bahu ke belakang. Sekarang",
            "mari lanjut ke set berikutnya…",
        ],
        "vi": [
            "tư thế là tất cả. Giữ cơ bụng",
            "siết chặt và vai mở rộng. Bây giờ",
            "hãy chuyển sang hiệp tiếp theo…",
        ],
        "ms": [
            "postur badan anda adalah segalanya. Pastikan",
            "otot teras aktif dan bahu ke belakang.",
            "Sekarang mari ke set seterusnya…",
        ],
        "uk": [
            "ваша постава — це все. Тримайте прес",
            "напруженим, плечі назад. А тепер",
            "переходимо до наступного підходу…",
        ],
        "el": [
            "η στάση του σώματος είναι τα πάντα.",
            "Κρατήστε τον κορμό σφιχτό και τους ώμους πίσω.",
            "Πάμε στο επόμενο σετ…",
        ],
        "ro": [
            "postura este totul. Menține abdomenul",
            "contractat și umerii trași înapoi. Acum",
            "trecem la următoarea serie…",
        ],
        "hu": [
            "a tartásod a legfontosabb. Tartsd feszesen",
            "a törzsed és húzd hátra a vállad.",
            "Most jön a következő szett…",
        ],
        "cs": [
            "postoj je základ. Držte břišní svaly",
            "zpevněné a ramena vzad. A teď",
            "přejdeme k další sérii…",
        ],
        "ca": [
            "la postura ho és tot. Mantingueu el core",
            "activat i les espatlles enrere. Ara",
            "passem a la sèrie següent…",
        ],
        "hr": [
            "držanje je sve. Držite trbušne mišiće",
            "zategnute i ramena unatrag. Sada",
            "prijeđimo na sljedeći set…",
        ],
        "sk": [
            "postoj je základ. Držte brušné svaly",
            "spevnené a ramená dozadu. A teraz",
            "prejdeme na ďalšiu sériu…",
        ],
        "th": [
            "ท่าทางคือทุกอย่าง ให้แกนกลางลำตัว",
            "กระชับและไหล่เปิดออก ตอนนี้",
            "มาเข้าสู่เซตถัดไปกันเลย…",
        ],
        "hi": [
            "आपकी मुद्रा ही सब कुछ है। कोर को",
            "सक्रिय रखें और कंधे पीछे। अब",
            "अगले सेट पर चलते हैं…",
        ],
    },
    "man_2": {
        "en-US": [
            "and that's what makes this chip so fast.",
            "But the real question is whether",
            "it justifies the price. Let's find out…",
        ],
        "fr": [
            "et c'est ce qui rend cette puce rapide.",
            "Mais la vraie question est de savoir",
            "si le prix est justifié. Analysons ça…",
        ],
        "de": [
            "und das macht diesen Chip so schnell.",
            "Aber die eigentliche Frage ist, ob",
            "der Preis gerechtfertigt ist…",
        ],
        "ja": [
            "このチップが高速な理由はそこです。",
            "しかし本当の疑問は、この",
            "価格に見合うかどうかです…",
        ],
        "ko": [
            "그게 이 칩이 빠른 이유입니다.",
            "하지만 진짜 질문은",
            "가격 대비 가치가 있는가입니다…",
        ],
        "zh-Hans": [
            "这就是这颗芯片如此快的原因。",
            "但真正的问题是，",
            "它的价格是否值得…",
        ],
        "zh-Hant": [
            "這就是這顆晶片如此快的原因。",
            "但真正的問題是，",
            "它的價格是否值得…",
        ],
        "pt-BR": [
            "e é isso que torna este chip tão rápido.",
            "Mas a verdadeira pergunta é se",
            "o preço se justifica. Vamos analisar…",
        ],
        "es-ES": [
            "y eso es lo que hace a este chip tan rápido.",
            "Pero la verdadera pregunta es si",
            "justifica el precio. Averigüémoslo…",
        ],
        "es-MX": [
            "y eso es lo que hace a este chip tan rápido.",
            "Pero la verdadera pregunta es si",
            "justifica el precio. Averigüémoslo…",
        ],
        "it": [
            "ed è questo che rende il chip così veloce.",
            "Ma la vera domanda è se",
            "il prezzo è giustificato. Scopriamolo…",
        ],
        "nl-NL": [
            "en dat is wat deze chip zo snel maakt.",
            "Maar de echte vraag is of",
            "de prijs gerechtvaardigd is. Laten we kijken…",
        ],
        "ru": [
            "именно это делает этот чип таким быстрым.",
            "Но настоящий вопрос в том,",
            "оправдывает ли он свою цену…",
        ],
        "tr": [
            "işte bu çipi bu kadar hızlı yapan şey bu.",
            "Ama asıl soru, fiyatını",
            "haklı çıkarıp çıkarmadığı. Bakalım…",
        ],
        "sv": [
            "och det är det som gör chipet så snabbt.",
            "Men den verkliga frågan är om",
            "priset är motiverat. Låt oss ta reda på det…",
        ],
        "da": [
            "og det er det, der gør denne chip så hurtig.",
            "Men det virkelige spørgsmål er, om",
            "prisen er berettiget. Lad os finde ud af det…",
        ],
        "fi": [
            "ja se tekee tästä sirusta niin nopean.",
            "Mutta todellinen kysymys on,",
            "onko hinta perusteltu. Selvitetään…",
        ],
        "no": [
            "og det er det som gjør denne brikken så rask.",
            "Men det virkelige spørsmålet er om",
            "prisen er berettiget. La oss finne ut…",
        ],
        "pl": [
            "i to sprawia, że ten chip jest tak szybki.",
            "Ale prawdziwe pytanie brzmi, czy",
            "cena jest tego warta. Sprawdźmy…",
        ],
        "id": [
            "dan itulah yang membuat chip ini begitu cepat.",
            "Tapi pertanyaan sebenarnya adalah apakah",
            "harganya sepadan. Mari kita cari tahu…",
        ],
        "vi": [
            "và đó là điều khiến con chip này nhanh đến vậy.",
            "Nhưng câu hỏi thực sự là liệu",
            "giá cả có xứng đáng không. Hãy cùng tìm hiểu…",
        ],
        "ms": [
            "dan itulah yang menjadikan cip ini begitu pantas.",
            "Tetapi persoalan sebenarnya ialah sama ada",
            "harganya berbaloi. Mari kita ketahui…",
        ],
        "uk": [
            "саме це робить цей чип таким швидким.",
            "Але справжнє питання — чи",
            "виправдовує він свою ціну…",
        ],
        "el": [
            "αυτό κάνει αυτό το τσιπ τόσο γρήγορο.",
            "Αλλά το πραγματικό ερώτημα είναι αν",
            "δικαιολογεί την τιμή του. Ας το δούμε…",
        ],
        "ro": [
            "și asta face acest cip atât de rapid.",
            "Dar adevărata întrebare este dacă",
            "prețul este justificat. Să aflăm…",
        ],
        "hu": [
            "és ez teszi ezt a chipet ilyen gyorssá.",
            "De az igazi kérdés az, hogy",
            "megéri-e az árát. Nézzük meg…",
        ],
        "cs": [
            "a to dělá tento čip tak rychlým.",
            "Ale skutečná otázka je, zda",
            "jeho cena je oprávněná. Pojďme zjistit…",
        ],
        "ca": [
            "i això és el que fa aquest xip tan ràpid.",
            "Però la veritable pregunta és si",
            "el preu es justifica. Descobrim-ho…",
        ],
        "hr": [
            "i to je ono što ovaj čip čini tako brzim.",
            "Ali pravo pitanje je hoće li",
            "cijena opravdati ulaganje. Provjerimo…",
        ],
        "sk": [
            "a to robí tento čip takým rýchlym.",
            "Ale skutočná otázka je, či",
            "jeho cena je opodstatnená. Poďme zistiť…",
        ],
        "th": [
            "นั่นคือสิ่งที่ทำให้ชิปตัวนี้เร็วมาก",
            "แต่คำถามที่แท้จริงคือว่า",
            "มันคุ้มค่ากับราคาหรือเปล่า มาดูกัน…",
        ],
        "hi": [
            "और यही इस चिप को इतना तेज बनाता है।",
            "लेकिन असली सवाल यह है कि क्या",
            "इसकी कीमत उचित है। चलिए पता करते हैं…",
        ],
    },
}


LANGUAGES = list(COPY.keys())


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def detect_cjk_indices():
    """Auto-detect CJK font variant indices in the .ttc file."""
    global CJK_INDICES
    lang_map = {"JP": "ja", "KR": "ko", "SC": "zh-Hans", "TC": "zh-Hant"}
    for i in range(30):
        try:
            font = ImageFont.truetype(CJK_FONT, 20, index=i)
            family = font.getname()[0]
            if "Mono" in family:
                continue
            for code, lang_key in lang_map.items():
                if code in family and lang_key not in CJK_INDICES:
                    CJK_INDICES[lang_key] = i
        except (OSError, IOError):
            break
    print(f"  CJK font indices detected: {CJK_INDICES}")


def extract_frame(video_path, timestamp="0:00"):
    """Extract a frame at the given min:sec timestamp as a PIL Image."""
    tmp = video_path + ".tmp_frame.png"
    cmd = [
        "ffmpeg", "-y",
        "-ss", timestamp,
        "-i", video_path,
        "-vframes", "1", "-q:v", "1", tmp,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr[-500:]}")
    img = Image.open(tmp).convert("RGB")
    os.remove(tmp)
    return img


def gradient_bg(w, h, color_top, color_bottom):
    """Create a vertical gradient background."""
    col = Image.new("RGB", (1, h))
    px = col.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        px[0, y] = tuple(int(a + (b - a) * t) for a, b in zip(color_top, color_bottom))
    return col.resize((w, h), Image.NEAREST)


def round_corners(img, radius):
    """Add rounded corners, returning an RGBA image."""
    img = img.convert("RGBA")
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [(0, 0), (img.width - 1, img.height - 1)], radius=radius, fill=255
    )
    img.putalpha(mask)
    return img


def get_font(lang, size):
    """Return the correct bold font for a language."""
    if lang in CJK_INDICES:
        return ImageFont.truetype(CJK_FONT, size, index=CJK_INDICES[lang])
    if lang == "th" and os.path.exists(THAI_FONT):
        return ImageFont.truetype(THAI_FONT, size)
    if lang == "hi" and os.path.exists(HINDI_FONT):
        return ImageFont.truetype(HINDI_FONT, size)
    return ImageFont.truetype(LATIN_FONT, size)


def composite_with_shadow(canvas, img, pos, offset=10, blur=20, opacity=60):
    """Paste img onto canvas with a soft drop shadow."""
    canvas = canvas.convert("RGBA")
    pad = blur * 3
    sbuf = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad), (0, 0, 0, 0))
    sfill = Image.new("RGBA", img.size, (0, 0, 0, opacity))
    if img.mode == "RGBA":
        sfill.putalpha(img.split()[3])
    sbuf.paste(sfill, (pad, pad))
    sbuf = sbuf.filter(ImageFilter.GaussianBlur(blur))

    shadow_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sx, sy = pos[0] + offset - pad, pos[1] + offset - pad
    shadow_layer.paste(sbuf, (sx, sy))
    canvas = Image.alpha_composite(canvas, shadow_layer)
    canvas.paste(img, pos, img)
    return canvas


# ─────────────────────────────────────────────
# TEXT RENDERING
# ─────────────────────────────────────────────

def draw_label_text(canvas, center_x, start_y, text, font,
                    text_fill=TEXT_COLOR, block_fill=LABEL_BLOCK_COLOR,
                    block_radius=14, pad_x=24, pad_y=8, line_gap=10):
    """Draw text with a dark label block behind each line (reference style)."""
    lines = text.split("\n")
    draw = ImageDraw.Draw(canvas)

    y_cursor = start_y
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Measure actual pixel bbox for this line
        bbox = draw.textbbox((center_x, y_cursor), line, font=font, anchor="mt")

        # Dark block wraps the actual text bbox
        bx0 = bbox[0] - pad_x
        by0 = bbox[1] - pad_y
        bx1 = bbox[2] + pad_x
        by1 = bbox[3] + pad_y
        draw.rounded_rectangle(
            [(bx0, by0), (bx1, by1)],
            radius=block_radius,
            fill=block_fill,
        )

        # Text on top of block
        draw.text((center_x, y_cursor), line, font=font,
                  fill=text_fill, anchor="mt")

        y_cursor = by1 + line_gap

    return canvas, y_cursor


def draw_text_with_shadow(canvas, pos, text, font,
                          fill=TEXT_COLOR, shadow_color=TEXT_SHADOW,
                          shadow_offset=(0, 6), shadow_blur=10,
                          anchor="mm", align="center"):
    """Draw text with a soft drop shadow."""
    canvas = canvas.convert("RGBA")

    tmp_draw = ImageDraw.Draw(canvas)
    bbox = tmp_draw.textbbox(pos, text, font=font, anchor=anchor, align=align)

    pad = shadow_blur * 3 + max(abs(shadow_offset[0]), abs(shadow_offset[1])) + 4
    bx = int(max(bbox[0] - pad, 0))
    by = int(max(bbox[1] - pad, 0))
    bw = int(min(bbox[2] + pad, canvas.width) - bx)
    bh = int(min(bbox[3] + pad, canvas.height) - by)

    sbuf = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sbuf)
    local_pos = (pos[0] - bx + shadow_offset[0], pos[1] - by + shadow_offset[1])
    sd.text(local_pos, text, font=font, fill=shadow_color, anchor=anchor, align=align)
    sbuf = sbuf.filter(ImageFilter.GaussianBlur(shadow_blur))

    slayer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    slayer.paste(sbuf, (bx, by))
    canvas = Image.alpha_composite(canvas, slayer)

    draw = ImageDraw.Draw(canvas)
    draw.text(pos, text, font=font, fill=fill, anchor=anchor, align=align)
    return canvas


# ─────────────────────────────────────────────
# PHONE MOCKUP & TELEPROMPTER
# ─────────────────────────────────────────────

def create_screen_content(video_frame, screen_w, screen_h, lang, clip):
    """Build screen content: video scaled to width + teleprompter overlay below."""
    scale = screen_w / video_frame.width
    vid_w = screen_w
    vid_h = int(video_frame.height * scale)

    scaled = video_frame.resize((vid_w, vid_h), Image.LANCZOS)

    screen = Image.new("RGBA", (screen_w, screen_h), (0, 0, 0, 255))
    screen.paste(scaled.convert("RGBA"), (0, 0))

    screen = add_teleprompter_overlay(screen, vid_h, lang, clip)
    return screen


def add_teleprompter_overlay(screen, video_bottom, lang, clip):
    """Overlay a teleprompter UI centred at the vertical midpoint."""
    w, h = screen.size

    # Full-screen Gaussian overlay — peaks at vertical midpoint, no hard edges
    import math
    center = 0.50          # peak at screen midpoint
    sigma = 0.22           # controls how wide the darkening spreads
    peak_alpha = 130       # max darkness at center

    col = Image.new("RGBA", (1, h))
    for y in range(h):
        t = y / max(h - 1, 1)
        alpha = int(peak_alpha * math.exp(-0.5 * ((t - center) / sigma) ** 2))
        col.putpixel((0, y), (0, 0, 0, alpha))
    overlay = col.resize((w, h), Image.NEAREST)
    screen = Image.alpha_composite(screen, overlay)

    draw = ImageDraw.Draw(screen)
    lines = PROMPTER_TEXT[clip][lang]

    base_sz = int(h * 0.022)
    active_sz = int(h * 0.027)

    line_font = get_font(lang, base_sz)
    active_font = get_font(lang, active_sz)

    cx = w // 2
    line_gap = int(h * 0.058)
    # Centre the active line (line 1) at the vertical midpoint
    text_top = h // 2 - line_gap

    for i, line in enumerate(lines):
        y = text_top + i * line_gap
        if i == 1:
            draw.text((cx, y), line, font=active_font,
                      fill=(255, 255, 255, 175), anchor="mm", align="center")
            bbox = draw.textbbox((cx, y), line, font=active_font, anchor="mm")
            bar_x = bbox[0] - int(w * 0.025)
            bar_w = max(int(w * 0.006), 3)
            draw.rounded_rectangle(
                [(bar_x, bbox[1] + 2), (bar_x + bar_w, bbox[3] - 2)],
                radius=bar_w // 2,
                fill=(255, 255, 255, 130),
            )
        else:
            draw.text((cx, y), line, font=line_font,
                      fill=(255, 255, 255, 55), anchor="mm", align="center")

    return screen


def build_phone_mockup(screen_content, phone_w, phone_h, bezel, border_color):
    """Wrap screen content in an iPhone frame with a colored accent border."""
    screen_w = phone_w - 2 * bezel
    screen_h = phone_h - 2 * bezel
    body_r = int(phone_w * PHONE_BODY_RADIUS_PCT)
    screen_r = int(body_r * 0.85)

    # Colored border wraps the phone body
    border_w = max(int(phone_w * PHONE_BORDER_PCT), 3)
    total_w = phone_w + 2 * border_w
    total_h = phone_h + 2 * border_w
    border_r = body_r + border_w

    phone = Image.new("RGBA", (total_w, total_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(phone)

    # Outer colored border
    draw.rounded_rectangle(
        [(0, 0), (total_w - 1, total_h - 1)],
        radius=border_r,
        fill=(*border_color, 255),
    )

    # Inner dark phone body
    draw.rounded_rectangle(
        [(border_w, border_w),
         (border_w + phone_w - 1, border_w + phone_h - 1)],
        radius=body_r,
        fill=(*PHONE_BODY_COLOR, 255),
    )

    # Screen content
    scaled = screen_content.resize((screen_w, screen_h), Image.LANCZOS)
    rounded = round_corners(scaled, screen_r)
    sx = border_w + bezel
    sy = border_w + bezel
    phone.paste(rounded, (sx, sy), rounded)

    # Dynamic island
    island_w = int(screen_w * PHONE_ISLAND_W_PCT)
    island_h = int(screen_h * PHONE_ISLAND_H_PCT)
    ix = sx + (screen_w - island_w) // 2
    iy = sy + int(screen_h * 0.012)
    draw = ImageDraw.Draw(phone)
    draw.rounded_rectangle(
        [(ix, iy), (ix + island_w, iy + island_h)],
        radius=island_h // 2,
        fill=(0, 0, 0, 255),
    )

    return phone


# ─────────────────────────────────────────────
# CARD GENERATOR
# ─────────────────────────────────────────────

def make_card(frame, cw, ch, clip, lang, clip_idx):
    """Generate a complete App Store screenshot card."""
    c1, c2 = BG_GRADIENTS[clip]
    tagline, subtitle = COPY[lang][clip_idx]

    # 1. Gradient background
    canvas = gradient_bg(cw, ch, c1, c2).convert("RGBA")

    # 2. Headline with dark label blocks — BIG, positioned near the top
    tag_size = int(ch * 0.050)
    tag_font = get_font(lang, tag_size)

    label_pad_x = int(cw * 0.030)
    label_pad_y = int(ch * 0.008)
    label_radius = int(ch * 0.008)
    label_gap = int(ch * 0.005)

    tag_start_y = int(ch * 0.040)
    canvas, tag_bottom_y = draw_label_text(
        canvas, cw // 2, tag_start_y, tagline, tag_font,
        pad_x=label_pad_x, pad_y=label_pad_y,
        block_radius=label_radius, line_gap=label_gap,
    )

    # 3. Subtitle — 2x size, auto-fit to card width
    sub_size = int(ch * 0.032)
    sub_font = get_font(lang, sub_size)
    max_sub_w = int(cw * 0.90)
    _tmp_d = ImageDraw.Draw(canvas)
    _sub_bb = _tmp_d.textbbox((0, 0), subtitle, font=sub_font)
    _sub_tw = _sub_bb[2] - _sub_bb[0]
    if _sub_tw > max_sub_w:
        sub_size = int(sub_size * max_sub_w / _sub_tw)
        sub_font = get_font(lang, sub_size)
    sub_y = tag_bottom_y + int(ch * 0.005)

    canvas = draw_text_with_shadow(
        canvas, (cw // 2, sub_y), subtitle, sub_font,
        fill=(255, 255, 255, 220),
        shadow_offset=(0, 3), shadow_blur=6,
        anchor="ma", align="center",
    )

    # Measure subtitle bottom for phone placement
    _d = ImageDraw.Draw(canvas)
    sub_bb = _d.textbbox((cw // 2, sub_y), subtitle, font=sub_font, anchor="ma")
    content_bottom = sub_bb[3] + int(ch * 0.018)

    # 4. Phone dimensions — wide, bleeds off bottom by ~25%
    #    Width: 92% of card (capped at 45% of card height for iPad)
    phone_w = int(min(cw * 0.92, ch * 0.45))
    phone_h = int(phone_w * PHONE_ASPECT)

    bezel = max(int(phone_w * PHONE_BEZEL_PCT), 4)
    screen_w = phone_w - 2 * bezel
    screen_h = phone_h - 2 * bezel

    # 5. Screen content (video + teleprompter)
    screen = create_screen_content(frame, screen_w, screen_h, lang, clip)

    # 6. Phone mockup with colored border
    border_color = c1
    phone = build_phone_mockup(screen, phone_w, phone_h, bezel, border_color)

    # 7. Position phone — centred, gap below subtitle, bottom bleeds off card
    phone_x = (cw - phone.width) // 2
    phone_y = content_bottom

    shadow_off = max(int(cw * 0.004), 3)
    shadow_blur_sz = max(int(cw * 0.012), 10)
    canvas = composite_with_shadow(canvas, phone, (phone_x, phone_y),
                                   offset=shadow_off, blur=shadow_blur_sz,
                                   opacity=50)

    return canvas.convert("RGB")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    print("DemoScope App Store Asset Generator")
    print("=" * 50)

    detect_cjk_indices()

    # Extract frames
    print("\n[1/3] Extracting frames from portrait videos...")
    frames = {}
    for clip in CLIPS:
        path = os.path.join(PORTRAIT_DIR, f"{clip}.mp4")
        if not os.path.exists(path):
            print(f"  SKIP: {path} not found")
            continue
        ts = FRAME_TIMESTAMPS.get(clip, "0:00")
        frames[clip] = extract_frame(path, ts)
        print(f"  OK  {clip} @ {ts}: {frames[clip].size}")

    if not frames:
        sys.exit("ERROR: No frames extracted. Check Portrait/ directory.")

    # Generate assets
    sizes = [("iPhone", IPHONE_SIZE), ("iPad", IPAD_SIZE)]
    total = len(frames) * len(LANGUAGES) * len(sizes)
    count = 0

    print(f"\n[2/3] Generating {total} images...")

    for device, (w, h) in sizes:
        for lang in LANGUAGES:
            out_dir = os.path.join(OUTPUT_DIR, device, lang)
            os.makedirs(out_dir, exist_ok=True)

            for clip_idx, clip_name in enumerate(CLIPS):
                if clip_name not in frames:
                    continue

                frame = frames[clip_name]
                card = make_card(frame, w, h, clip_name, lang, clip_idx)

                fname = f"{clip_name}_{w}x{h}.png"
                card.save(os.path.join(out_dir, fname), "PNG", optimize=True)

                count += 1
                if count % 8 == 0 or count == total:
                    print(f"  Progress: {count}/{total}")

    # Summary
    print(f"\n[3/3] Done! Generated {count} images.")
    print(f"Output: {OUTPUT_DIR}/")

    for device in ["iPhone", "iPad"]:
        device_dir = os.path.join(OUTPUT_DIR, device)
        if os.path.isdir(device_dir):
            print(f"\n  {device}/")
            for lang in sorted(os.listdir(device_dir)):
                lang_dir = os.path.join(device_dir, lang)
                n = len(os.listdir(lang_dir))
                print(f"    {lang}/ ({n} images)")


if __name__ == "__main__":
    main()
