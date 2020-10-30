from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import ast
import operator
import math
import pandas as pd
jumData = 0
dl = "L"
du = "U"
for i in range(5):
    file = pd.read_excel('DATA SKRIPSI FULL.xlsx', sheet_name=dl+str(i+1), usecols=['pengaduan', 'kelas'])
    file = file.to_dict(orient='record')
    kk, ktp, akta, surat = [], [], [], []
    for element in file:
        if element['kelas'] == 'KK':
            kk.append(element['pengaduan'])
        if element['kelas'] == 'KTP':
            ktp.append(element['pengaduan'])
        if element['kelas'] == 'AKTA':
            akta.append(element['pengaduan'])
        if element['kelas'] == 'SURAT PINDAH':
            surat.append(element['pengaduan'])
        jumData += 1


    # tokenisasi
    def tokenize(doc):
        return (doc.split(" "))


    kk_token = [tokenize(doc) for doc in kk]
    ktp_token = [tokenize(doc) for doc in ktp]
    akta_token = [tokenize(doc) for doc in akta]
    surat_token = [tokenize(doc) for doc in surat]

    # stemming
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    kk_stemmed = [[stemmer.stem(str(i)) for i in doc] for doc in kk_token]
    ktp_stemmed = [[stemmer.stem(str(i)) for i in doc] for doc in ktp_token]
    akta_stemmed = [[stemmer.stem(str(i)) for i in doc] for doc in akta_token]
    surat_stemmed = [[stemmer.stem(str(i)) for i in doc] for doc in surat_token]

    # filtering
    stopwords = []
    with open("stopwords.txt") as a:
        content = a.readlines()
    stopwords = [x.strip() for x in content]


    def filtering(doc):
        return ([w for w in doc if w not in stopwords])


    kk_filtered = [filtering(doc) for doc in kk_stemmed]
    ktp_filtered = [filtering(doc) for doc in ktp_stemmed]
    akta_filtered = [filtering(doc) for doc in akta_stemmed]
    surat_filtered = [filtering(doc) for doc in surat_stemmed]

    # mendapatkan term unik
    docFiltered = kk_filtered, ktp_filtered, akta_filtered, surat_filtered


    def term_unik(dokumen, terms):
        for docs in dokumen:
            for doc in docs:
                for term in doc:
                    if term not in terms:
                        terms.append(term)
        return (terms)


    terms = []
    terms = term_unik(docFiltered, terms)

    # menghitung jumlah term
    jum_term = len(terms)

    # pembobotan raw tf
    tf_kk = []
    tf_ktp = []
    tf_akta = []
    tf_surat = []
    for term in terms:
        row = []
        for doc in kk_filtered:
            row.append(doc.count(term))
        tf_kk.append(row)

    for term in terms:
        row = []
        for doc in ktp_filtered:
            row.append(doc.count(term))
        tf_ktp.append(row)

    for term in terms:
        row = []
        for doc in akta_filtered:
            row.append(doc.count(term))
        tf_akta.append(row)

    for term in terms:
        row = []
        for doc in surat_filtered:
            row.append(doc.count(term))
        tf_surat.append(row)

    # jumlah setiap term pada tiap kelas
    term_sum_kk = {}

    for i in range(0, len(terms)):
        term_sum_kk[terms[i]] = sum(tf_kk[i])

    term_sum_ktp = {}
    for i in range(0, len(terms)):
        term_sum_ktp[terms[i]] = sum(tf_ktp[i])

    term_sum_akta = {}
    for i in range(0, len(terms)):
        term_sum_akta[terms[i]] = sum(tf_akta[i])

    term_sum_surat = {}
    for i in range(0, len(terms)):
        term_sum_surat[terms[i]] = sum(tf_surat[i])

    # kemunculan term di semua dokumen
    term_sum_alldoc = {}
    for i in range(0, len(terms)):
        term_sum_alldoc[terms[i]] = sum(tf_kk[i] + tf_ktp[i] + tf_akta[i] + tf_surat[i])


    # jumlah term pada suatu kelas
    def count(tf_docs):
        x = []
        for doc in tf_docs:
            x.append(sum(doc))
        return sum(x)


    count_kk = count(tf_kk)
    count_ktp = count(tf_ktp)
    count_akta = count(tf_akta)
    count_surat = count(tf_surat)

    # total semua term
    term_sum = 0
    term_sum = count_kk + count_ktp + count_akta + count_surat

    # Seleksi Fitur
    seleksi_kk = {}
    for i in range(0, len(terms)):
        seleksi_kk[terms[i]] = ((math.log10(term_sum_kk[terms[i]] + 1) / math.log10(count_kk)) * (
        term_sum_alldoc[terms[i]]) / jumData)

    seleksi_ktp = {}
    for i in range(0, len(terms)):
        seleksi_ktp[terms[i]] = ((math.log10(term_sum_ktp[terms[i]] + 1) / math.log10(count_ktp)) * (
        term_sum_alldoc[terms[i]]) / jumData)

    seleksi_akta = {}
    for i in range(0, len(terms)):
        seleksi_akta[terms[i]] = ((math.log10(term_sum_akta[terms[i]] + 1) / math.log10(count_akta)) * (
        term_sum_alldoc[terms[i]]) / jumData)

    seleksi_surat = {}
    for i in range(0, len(terms)):
        seleksi_surat[terms[i]] = ((math.log10(term_sum_surat[terms[i]] + 1) / math.log10(count_surat)) * (
        term_sum_alldoc[terms[i]]) / jumData)

    glasgow_II = {}
    for i in range(0, len(terms)):
        glasgow_II[terms[i]] = seleksi_kk[terms[i]] + seleksi_ktp[terms[i]] + seleksi_akta[terms[i]] + seleksi_surat[
            terms[i]]
    # sorting term terseleksi
    seleksi_fitur = sorted(glasgow_II.items(), reverse=True, key=lambda x: x[1])

    # menghapus term yang memiliki nilai Glasgow-II terendah
    persen = len(terms) - (len(terms) * 0.2)
    persen = int(persen)

    terms = []
    br = 0
    for i in range(0, persen):
        terms.append(seleksi_fitur[i][0])

    # Naive Bayes Training
    # prior
    prior_kk = len(kk) / jumData
    prior_ktp = len(ktp) / jumData
    prior_akta = len(akta) / jumData
    prior_surat = len(surat) / jumData


    # likelihood
    def likelihood(terms, count, term_sum):
        likelihood = {}
        for term in terms:
            likelihood[term] = (term_sum[term] + 1) / (count + len(terms))
        return likelihood


    likelihood_kk = likelihood(terms, count_kk, term_sum_kk)
    likelihood_ktp = likelihood(terms, count_ktp, term_sum_ktp)
    likelihood_akta = likelihood(terms, count_akta, term_sum_akta)
    likelihood_surat = likelihood(terms, count_surat, term_sum_surat)


    # evidence
    def evidence(terms, termsumdoc, termsum):
        evidence = {}
        for term in terms:
            evidence[term] = termsumdoc[term] / termsum
        return evidence


    evidence_allterms = evidence(terms, term_sum_alldoc, term_sum)

    with open("termunik.txt", "w") as f:
        f.write(str(terms))

    with open("likelihoodkk.txt", "w") as f:
        f.write(str(likelihood_kk))

    with open("likelihoodktp.txt", "w") as f:
        f.write(str(likelihood_ktp))

    with open("likelihoodakta.txt", "w") as f:
        f.write(str(likelihood_akta))

    with open("likelihoodsurat.txt", "w") as f:
        f.write(str(likelihood_surat))

    with open("evidence.txt", "w") as f:
        f.write(str(evidence_allterms))

    with open("priorkk.txt", "w") as f:
        f.write(str(prior_kk))

    with open("priorktp.txt", "w") as f:
        f.write(str(prior_ktp))

    with open("priorakta.txt", "w") as f:
        f.write(str(prior_akta))

    with open("priorsurat.txt", "w") as f:
        f.write(str(prior_surat))

    # TESTING

    with open("termunik.txt", "r") as f:
        terms = ast.literal_eval(f.read())

    with open("priorkk.txt", "r") as f:
        prior_kk = ast.literal_eval(f.read())

    with open("priorktp.txt", "r") as f:
        prior_ktp = ast.literal_eval(f.read())

    with open("priorakta.txt", "r") as f:
        prior_akta = ast.literal_eval(f.read())

    with open("priorsurat.txt", "r") as f:
        prior_surat = ast.literal_eval(f.read())

    with open("likelihoodkk.txt", "r") as f:
        likelihood_kk = ast.literal_eval(f.read())

    with open("likelihoodktp.txt", "r") as f:
        likelihood_ktp = ast.literal_eval(f.read())

    with open("likelihoodakta.txt", "r") as f:
        likelihood_akta = ast.literal_eval(f.read())

    with open("likelihoodsurat.txt", "r") as f:
        likelihood_surat = ast.literal_eval(f.read())

    with open("evidence.txt", "r") as f:
        evidence_allterms = ast.literal_eval(f.read())
    test = pd.read_excel('DATA SKRIPSI FULL.xlsx', sheet_name=du+str(i+1), usecols=['pengaduan', 'kelas'])
    test = test.to_dict(orient='record')
    datatest = []
    labels = []
    for element in test:
        datatest.append(element['pengaduan'])
        labels.append(element['kelas'])

    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    stem_test = [stemmer.stem(str(doc)) for doc in datatest]

    tokenize = lambda doc: doc.split(" ")
    token_test = [tokenize(dok) for dok in stem_test]

    stopwords = []
    with open("stopwords.txt") as a:
        content = a.readlines()
    stopwords = [x.strip() for x in content]
    filter = lambda doc: [w for w in doc if w not in stopwords]
    filter_test = [filter(d) for d in token_test]

    # posterior
    nb_hasil = []
    for doc in filter_test:
        nb_like_kk = 1
        nb_like_ktp = 1
        nb_like_akta = 1
        nb_like_surat = 1
        evid = 1
        for kata in doc:
            if kata in terms:
                nb_like_kk *= likelihood_kk[kata]
                nb_like_ktp *= likelihood_ktp[kata]
                nb_like_akta *= likelihood_akta[kata]
                nb_like_surat *= likelihood_surat[kata]
                evid *= evidence_allterms[kata]

        nb_post_kk = (prior_kk * nb_like_kk) / evid
        nb_post_ktp = (prior_ktp * nb_like_ktp) / evid
        nb_post_akta = (prior_akta * nb_like_akta) / evid
        nb_post_surat = (prior_surat * nb_like_surat) / evid

        text = " ".join(doc)
        peringkat = {'KK': nb_post_kk, 'KTP': nb_post_ktp, 'AKTA': nb_post_akta, 'SURAT PINDAH': nb_post_surat}
        # print(peringkat)
        tmp = max(peringkat.items(), key=operator.itemgetter(1))[0]

        nb_hasil.append([text, tmp])

    print("Hasil Klasifikasi")
    label_pred = []
    for i in range(len(nb_hasil)):
        print('Data uji ke-', i + 1, 'dikasifikasikan ke dalam kelas: ', nb_hasil[i][1])
        label_pred.append(nb_hasil[i][1])
