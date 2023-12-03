from difflib import SequenceMatcher

from fuzzywuzzy import fuzz, process

SCOPUS_BIB_FILEPATH = "scopus.bib"
WOS_BIB_FILEPATH = "wos.bib"
OUTPUT_JOINED_FILEPATH = "Test.bib"


def similarity(a, b) -> float:
    """Return similarity between 2 strings"""
    return SequenceMatcher(None, a, b).ratio()


def find_similar_match(a, b, threshold=0.9) -> list:
    """Find string b in a - while the strings being different"""
    corpus_lst = a.split()
    substring_lst = b.split()

    nonalpha = re.compile(r"[^a-zA-Z]")
    start_indices = [
        i for i, x in enumerate(corpus_lst) if nonalpha.sub("", x) == substring_lst[0]
    ]
    end_indices = [
        i for i, x in enumerate(corpus_lst) if nonalpha.sub("", x) == substring_lst[-1]
    ]

    rebuild_substring = " ".join(substring_lst)
    max_sim = 0
    for start_idx in start_indices:
        for end_idx in end_indices:
            corpus_search_string = " ".join(corpus_lst[start_idx:end_idx])
            sim = similarity(corpus_search_string, rebuild_substring)
            if sim > max_sim:
                result = [start_idx, end_idx]

    return result


addeditems = 0
modifiedentries = 0
modify = False
foundoneoranother = 0

uniT = {
    "SO": ["journal", "journal", "journal"],
    "AB": ["abstract", "abstract", "abstract"],
    "C1": ["affiliation", "affiliation", "affiliation"],
    "CR": ["references", "cited-references", "cited references"],
    "DI": ["doi", "doi", "DOI"],
    "DE": ["author_keywords", "keywords", "keywords"],
    "ID": ["keywords", "keywords-plus", "keywords plus"],
    "NR": ["note", "cited-references", "cited reference count"],
    "WC": ["abbrev_source_title", "web-of-science-categories", "science categories"],
    "PY": ["year", "year", "publication year"],
}

scopusTitleList3 = []

# Processing Scopus bib and tranbsforming it to dict with scopus format
scopusList3 = []
currentelement = ["", {}]
custkey = ""

print("Processing Scopus bib file...")

with open(SCOPUS_BIB_FILEPATH, "r") as scopusfile:
    for line in scopusfile:
        if line[0] == "@":
            currentelement[0] = (
                currentelement[0]
                .replace("inproceedings", "CONFERENCE")
                .replace("article", "ARTICLE")
            )
            try:
                currentelement[1]["note"] = currentelement[1]["note"].replace(
                    "{", "{cited by" + currentelement[1]["Times-Cited"] + "; "
                )
                currentelement[1]["url"] = "https://doi.org/" + currentelement[1][
                    "doi"
                ].replace("DOI = {", "").replace("},\n", "")
            except Exception as e:
                pass

            lang = ""
            doctype = ""
            year = 2001
            try:
                lang = currentelement[1]["language"]
                doctype = currentelement[1]["type"]
                year = int(
                    currentelement[1]["year"].replace("{", "").replace("},\n", "")
                )
            except Exception as e:
                pass

            if (
                not (
                    "Polish" in lang
                    or "Spanish" in lang
                    or "Chinese" in lang
                    or "French" in lang
                )
                and not ("N=34" in doctype)
                and not ("N=25" in doctype)
                and (year > 2000)
                and (
                    "Article" in doctype
                    or "Conference" in doctype
                    or "Proceeding" in doctype
                )
            ):
                scopusList3.append(currentelement)
                if currentelement[0] != "":
                    scopusTitleList3.append(currentelement[1]["title"])

            currentelement = ["", {}]
            currentelement[0] = line.replace("\t", "")
            continue
        else:
            splitted = line.replace("\t", "").replace("},\n", "},").split(" = ", 1)
            if splitted == ["\ufeff\n"] or splitted == ["\n"]:
                continue
            # if custkey == 'references':
            # 	print(custkey)
            if len(splitted) > 1:
                # if splitted[0] == 'references':
                # 	print(custkey)
                line = splitted[1]
                custkey = (
                    splitted[0]
                    .replace("Author", "author")
                    .replace("Title", "title")
                    .replace("Booktitle", "journal")
                    .replace("Year", "year")
                    .replace("DOI", "doi")
                    .replace("Note", "note")
                    .replace("Affiliation", "affiliation")
                    .replace("Abstract", "abstract")
                    .replace("Keywords-Plus", "keywords")
                    .replace("Keywords", "author_keywords")
                    .replace("Funding-Acknowledgement", "funding_details")
                    .replace("Funding-Text", "funding_text")
                    .replace("Cited-References", "references")
                    .replace("Title", "title")
                    .replace("Publisher", "publisher")
                    .replace("ISBN", "isbn")
                    .replace("Language", "language")
                    .replace("Type", "document_type")
                    .replace("ISSN", "issn")
                    .replace("Volume", "volume")
                    .replace("Journal", "journal")
                    .replace("Pages", "pages")
                    .replace("Article-Number", "art_number")
                    .replace("Title", "title")
                )

                if custkey == "source":
                    continue

                if custkey == "references":
                    line = splitted[1].replace(".\n", ";").replace(".}", "}")
                currentelement[1][custkey] = line
            else:
                if custkey == "references":
                    line = (
                        line.replace(".\n", ";").replace(".}", "}").replace("   ", " ")
                    )
                if custkey == "source":
                    continue
                currentelement[1][custkey] = currentelement[1][custkey] + line
    # Last element
    try:
        currentelement[1]["note"] = currentelement[1]["note"].replace(
            "{", "{cited by" + currentelement[1]["Times-Cited"] + "; "
        )
        currentelement[1]["url"] = "https://doi.org/" + currentelement[1][
            "doi"
        ].replace("DOI = {", "").replace("},\n", "")
    except Exception as e:
        pass

    scopusList3.append(currentelement)
    if currentelement[0] != "":
        scopusTitleList3.append(currentelement[1]["title"])
    scopusList3 = scopusList3[1:]
scopusfile.close()

print("Processed Scopus bib file...")
print("Processing Wos bib file...")

# Processing WOS bib and tranbsforming it to dict with scopus format
wosList3 = []
currentelement = ["", {}]
custkey = ""

with open(WOS_BIB_FILEPATH, "r") as wosfile:
    for line in wosfile:
        if line[0] == "@":
            currentelement[0] = (
                currentelement[0]
                .replace("inproceedings", "CONFERENCE")
                .replace("article", "ARTICLE")
            )
            try:
                currentelement[1]["note"] = currentelement[1]["note"].replace(
                    "{", "{cited by" + currentelement[1]["Times-Cited"] + "; "
                )
                currentelement[1]["url"] = "https://doi.org/" + currentelement[1][
                    "doi"
                ].replace("DOI = {", "").replace("},\n", "")
            except Exception as e:
                pass

            lang = ""
            doctype = ""
            year = 2001
            try:
                lang = currentelement[1]["language"]
                doctype = currentelement[1]["document_type"]
                year = int(
                    currentelement[1]["year"].replace("{", "").replace("},\n", "")
                )
            except Exception as e:
                pass

            if (
                not (
                    "Polish" in lang
                    or "Spanish" in lang
                    or "Chinese" in lang
                    or "French" in lang
                )
                and not ("N=34" in doctype)
                and not ("N=25" in doctype)
                and (year > 2000)
                and (
                    "Article" in doctype
                    or "Conference" in doctype
                    or "Proceeding" in doctype
                )
            ):
                wosList3.append(currentelement)

            currentelement = ["", {}]
            currentelement[0] = line
            continue
        else:
            splitted = line.split(" = ", 1)
            if splitted == ["\ufeff\n"]:
                continue
            if len(splitted) > 1:
                line = splitted[1]
                custkey = (
                    splitted[0]
                    .replace("Author", "author")
                    .replace("Title", "title")
                    .replace("Booktitle", "journal")
                    .replace("Year", "year")
                    .replace("DOI", "doi")
                    .replace("Note", "note")
                    .replace("Affiliation", "affiliation")
                    .replace("Abstract", "abstract")
                    .replace("Keywords-Plus", "keywords")
                    .replace("Keywords", "author_keywords")
                    .replace("Funding-Acknowledgement", "funding_details")
                    .replace("Funding-Text", "funding_text")
                    .replace("Cited-References", "references")
                    .replace("Title", "title")
                    .replace("Publisher", "publisher")
                    .replace("ISBN", "isbn")
                    .replace("Language", "language")
                    .replace("Type", "document_type")
                    .replace("ISSN", "issn")
                    .replace("Volume", "volume")
                    .replace("Journal", "journal")
                    .replace("Pages", "pages")
                    .replace("Article-Number", "art_number")
                    .replace("Title", "title")
                )

                if custkey == "source" or custkey[0].isupper():
                    continue
                if custkey == "references":
                    line = splitted[1].replace(".\n", ";").replace(".}", "}")
                currentelement[1][custkey] = line
            else:
                if custkey == "references":
                    line = (
                        line.replace(".\n", ";").replace(".}", "}").replace("   ", " ")
                    )
                if custkey == "source" or custkey[0].isupper():
                    continue
                currentelement[1][custkey] = currentelement[1][custkey] + line
    # Last element
    try:
        currentelement[1]["note"] = currentelement[1]["note"].replace(
            "{", "{cited by" + currentelement[1]["Times-Cited"] + "; "
        )
        currentelement[1]["url"] = "https://doi.org/" + currentelement[1][
            "doi"
        ].replace("DOI = {", "").replace("},\n", "")
    except Exception as e:
        pass
    wosList3.append(currentelement)
    wosList3 = wosList3[1:]
wosfile.close()

print("Processed Wos bib file...")
print("Adding Wos exclusives and completing...")

listwosexclusive = []
infocompletedkw = 0

for wosentry in wosList3:
    extracted, similarity = process.extractOne(
        wosentry[1]["title"], scopusTitleList3, scorer=fuzz.ratio
    )
    if similarity >= 95:
        # scopusList3[scopusTitleList3.index(extracted)]
        for key in wosentry[1].keys():
            if key not in scopusList3[scopusTitleList3.index(extracted)][1].keys():
                if "references" in key:
                    infocompletedkw = infocompletedkw + 1
                scopusList3[scopusTitleList3.index(extracted)][1][key] = wosentry[1][
                    key
                ]
    else:
        listwosexclusive.append(wosentry)
        scopusList3.append(wosentry)

print("Finished processing files... writing to disk new file...")

# write all
scopusxx = open(OUTPUT_JOINED_FILEPATH, "w")  # write mode
scopusxx.write("\n")

uniqueTitles = []
uniquerepetitions = []

for entry in scopusList3:
    scopusxx.write(entry[0])
    for key in entry[1].keys():
        if key[0] == " ":
            continue
        if key == "references":
            entry[1][key] = (
                entry[1][key]
                .lower()
                .replace(
                    "comput electron agric", "computers and electronics in agriculture"
                )
                .replace("agric syst", "agricultural systems")
            )
        if key == "title":
            uniqueTitles.append(entry[1]["title"].replace("{", "").replace("},", ""))
            uniquerepetitions.append([])
        scopusxx.write(key + "=" + entry[1][key].replace("\n", "") + "\n")
    scopusxx.write("source = {Scopus},\n}\n\n")
scopusxx.close()

print("Joint file written...")
print("Searching for references...")

import re

for entry in scopusList3:
    try:
        reference = entry[1]["references"]
    except Exception as e:
        pass
    for title in uniqueTitles:
        if title in reference:
            uniquerepetitions[uniqueTitles.index(title)].append(entry[1]["title"])
            continue

        # Allow any character between whitespace-separated "words" except ASCII
        # alphabetic characters
        ssre = re.compile(r"[^a-z]+".join(title.split()), re.IGNORECASE)

        if m := ssre.search(reference):
            # print(m.start(), m.end())
            # print(repr(m.group(0)))
            uniquerepetitions[uniqueTitles.index(title)].append(entry[1]["title"])

print("Finished searching for references...")
print("Listing references with two or more repetitions in subset...")

summaryCited = {}

for enum in range(len(uniquerepetitions)):
    if len(uniquerepetitions[enum]) < 2:
        pass
    else:
        print(uniquerepetitions[enum])
        summaryCited[uniqueTitles[enum]] = uniquerepetitions[enum]

print("FIN")
