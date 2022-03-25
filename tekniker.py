"""
Konvertering av Finlandssvenska tekniker -PDF-filer till textform
"""

import csv
import os.path

def parse_html(html_filename):
    with open(html_filename, "r") as f:
        html = f.read()
    eliminate = ['<span style="font-family: TimesNewRomanPSMT; font-size:14px">',
        '</span>', '</div>', '<br>',
        'style="position:absolute; border: textbox 1px solid; ',
        'writing-mode:lr-tb; ', 'writing-mode:False; ', 'position:absolute; ']
    for text in eliminate:
        html = html.replace(text, "")
    html = html.replace("  ", " ")
    s = ""
    sidnr = 0
    kort_rad = False
    for row in html.splitlines():
        if "<a name" in row:
            sidnr = row.split('<a name="')[1].split('"')[0]
            s += f"<!-- page {sidnr} -->\n"
            continue
        while True:
            p1 = row.find("<")
            p2 = row.find(">")
            if p1 > -1:
                row = row[0:p1] + row[p2+1:]
            else:
                break

        if len(row) > 0:
            nytt_stycke = (row[0].isupper()) and kort_rad
            if nytt_stycke:
                s += "\n<p>"
        s += row + "\n"
        kort_rad = (len(row) < 50)
    return s


def htmlhead(title): 
    return f"""
<html><head>
<meta charset="UTF-8">
<title>{title}</title>""" + \
"""
 <style>
  a {text-decoration: none;}
  p {font-family: Vollkorn, Georgia; font-size: 12pt; }
  h1 {font-family: Vollkorn, Georgia; font-size: 18pt; }
  h2 {font-family: Vollkorn, Georgia; font-size: 14pt; }
 </style>
</head>

<body style="margin:100px">
"""


def create_fabo_dict(csv_filnamn):
    with open(csv_filnamn) as fp:
        reader = csv.reader(fp, delimiter=",")
        next(reader, None)  # skip the headers
        fabo_lista = [row for row in reader]
    fabor = {}
    for fabo in fabo_lista:
        filnamn, namn, startsida, skip1, skip2, slutsida, forfattare = fabo
        fabor[filnamn] = {'namn': namn, 'startsida': int(startsida), 
                'slutsida': int(slutsida), 'skip1': int(skip1), 'skip2': int(skip2),
                'forfattare': forfattare}
    return fabor


def create_fabo_files(fabor, parsat, katalog, bok):
    for filnamn in fabor:
        fabo = fabor[filnamn]
        namn = fabo['namn']
        startsida = fabo['startsida']
        slutsida = fabo['slutsida'] + 1
        skip1 = fabo['skip1']
        skip2 = fabo['skip2']
        forfattare = fabo['forfattare']
        s = htmlhead(namn)
        s += f"<h1>{namn}</h1>\n"
        s += f"<h2>Författare: {forfattare}</h2>\n"
        nr = bok.split(".")[0][-1]
        nr = int(nr) * "I"
        s += f"<p><em>Utdrag ur Finlandssvenska tekniker {nr}, sidorna {startsida}-{slutsida}</em>\n\n"
        s += f'<p><img src="{filnamn}.jpg" align=right style="width: 50%"/>'
        del1 = parsat.split(f"<!-- page {startsida} -->")[1]
        del1 = del1.split(f"<!-- page {skip1} -->")[0]
        del2 = parsat.split(f"<!-- page {skip2} -->")[1]
        del2 = del2.split(f"<!-- page {slutsida} -->")[0]
        s += del1 + del2
        utfil_namn = os.path.join(katalog, filnamn + ".html")
        with open(utfil_namn, "w") as fh:
            fh.write(s)
            print(f"Skrev {utfil_namn}")

def word_stat(text, skiplist):
    for word in skiplist:
        text = text.replace(word, "")
    list_words = text.split()
    sorted_word_list = sorted(list_words) #, key=str.lower)
    #sorted_word_list = sorted_word_list.append('<EOF>')
    word_stat_list = []
    last_word = ""
    c = 0
    for word in sorted_word_list:
        if last_word != "":
            if word != last_word:
                word_stat_list.append([last_word,c])
                c = 0
        c += 1
        last_word = word
    word_stat_list.sort(key = lambda row: row[1], reverse=True)
    return word_stat_list


def save_list_of_lists(lofl, filename):
    s = ""
    for inner_l in lofl:
        t = ""
        for leaf in inner_l:
            t += str(leaf)+","
        s += t[:-1] + "\n"
    with open(filename, "w") as fh:
        fh.write(s)
    return f"Skrev {filename} totalt {len(s)} tecken"
