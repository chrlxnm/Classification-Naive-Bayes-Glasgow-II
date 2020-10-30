# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 18:42:12 2019

@author: lenovoideapad320
"""
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import ast
import operator
import math
import pandas as pd
totalData = 0

file = pd.read_excel('DATA SKRIPSI FULL.xlsx',sheet_name='lati', usecols=['pengaduan', 'kelas'])
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
    totalData += 1
print(len(kk))
print(len(ktp))
print(len(akta))
print(len(surat))
# tokenisasi
def tokenisasi(doc):
    return (doc.split(" "))
tokenisasi_kk = [tokenisasi(doc) for doc in kk]
tokenisasi_ktp = [tokenisasi(doc) for doc in ktp]
tokenisasi_akta = [tokenisasi(doc) for doc in akta]
tokenisasi_surat = [tokenisasi(doc) for doc in surat]

# stemming
factory = StemmerFactory()
stemmer = factory.create_stemmer()
stemming_kk = [[stemmer.stem(str(i))for i in doc] for doc in tokenisasi_kk]
stemming_ktp = [[stemmer.stem(str(i))for i in doc] for doc in tokenisasi_ktp]
stemming_akta = [[stemmer.stem(str(i))for i in doc] for doc in tokenisasi_akta]
stemming_surat = [[stemmer.stem(str(i))for i in doc] for doc in tokenisasi_surat]

# filtering
stopwords = []
with open("stopwords.txt") as a:
    content = a.readlines()
stopwords = [x.strip() for x in content]
def filtering(doc):
    return ([w for w in doc if w not in stopwords])
filtering_kk = [filtering(doc) for doc in stemming_kk]
filtering_ktp = [filtering(doc) for doc in stemming_ktp]
filtering_akta = [filtering(doc) for doc in stemming_akta]
filtering_surat = [filtering(doc) for doc in stemming_surat]

# mendapatkan term unik
hasil_filtering = filtering_kk,filtering_ktp,filtering_akta,filtering_surat
def terms(dokumen, termunik):
    for docs in dokumen:
        for doc in docs:
            for term in doc:
                if term not in termunik:
                    termunik.append(term)
    return (termunik)
term_unik = []
term_unik = terms(hasil_filtering, term_unik)

# menghitung jumlah term unik
jt_unik = len(term_unik)

# pembobotan raw tf
def rawtf(termunik,filtering,tf):
    for term in term_unik:
        row = []
        for doc in filtering:
            row.append(doc.count(term))
        tf.append(row)
    return tf
tf_kk = []
tf_ktp = []
tf_akta = []
tf_surat = []
tf_kk = rawtf(term_unik,filtering_kk,tf_kk)
tf_ktp = rawtf(term_unik,filtering_ktp,tf_ktp)
tf_akta = rawtf(term_unik,filtering_akta,tf_akta)
tf_surat = rawtf(term_unik,filtering_surat,tf_surat)

# jumlah setiap term pada tiap kelas
def jstk(termunik,tf,jstk):
    for i in range(0, len(termunik)):
        jstk[termunik[i]] = sum(tf[i])
    return jstk
jst_kk = {}
jst_ktp = {}
jst_akta = {}
jst_surat = {}
jst_kk = jstk(term_unik,tf_kk,jst_kk)
jst_ktp = jstk(term_unik,tf_ktp,jst_ktp)
jst_akta = jstk(term_unik,tf_akta,jst_akta)
jst_surat = jstk(term_unik,tf_surat,jst_surat)

# kemunculan term di semua dokumen
jtsd = {}
for i in range(0, len(term_unik)):
    jtsd[term_unik[i]] = sum(tf_kk[i] + tf_ktp[i] + tf_akta[i] + tf_surat[i])

# jumlah term pada suatu kelas
def count(tf_docs):
    x = []
    for doc in tf_docs:
        x.append(sum(doc))
    return sum(x)

jt_kk = count(tf_kk)
jt_ktp = count(tf_ktp)
jt_akta = count(tf_akta)
jt_surat = count(tf_surat)

# total semua term
jst = 0
jst = jt_kk + jt_ktp + jt_akta + jt_surat
'''
#Seleksi Fitur
seleksi_kk = {}
for i in range(0, len(term_unik)):
    seleksi_kk[term_unik[i]] = ((math.log10(jst_kk[term_unik[i]]+1)/math.log10(jt_kk))*(jtsd[term_unik[i]])/totalData)

seleksi_ktp = {}
for i in range(0, len(term_unik)):
    seleksi_ktp[term_unik[i]] = ((math.log10(jst_ktp[term_unik[i]]+1)/math.log10(jt_ktp))*(jtsd[term_unik[i]])/totalData)

seleksi_akta = {}
for i in range(0, len(term_unik)):
    seleksi_akta[term_unik[i]] = ((math.log10(jst_akta[term_unik[i]]+1)/math.log10(jt_akta))*(jtsd[term_unik[i]])/totalData)

seleksi_surat = {}
for i in range(0, len(term_unik)):
    seleksi_surat[term_unik[i]] = ((math.log10(jst_surat[term_unik[i]]+1)/math.log10(jt_surat))*(jtsd[term_unik[i]])/totalData)

glasgow_II = {}
for i in range(0, len(term_unik)):
    glasgow_II[term_unik[i]] = seleksi_kk[term_unik[i]] + seleksi_ktp[term_unik[i]] + seleksi_akta[term_unik[i]] + seleksi_surat[term_unik[i]]
#sorting term terseleksi
seleksi_fitur = sorted(glasgow_II.items() , reverse=True, key=lambda x: x[1])

#menghapus term yang memiliki nilai Glasgow-II terendah
persen = len(term_unik)-(len(term_unik)*0.2)
persen = int(persen)

term_unik=[]
br=0
for i in range(0,persen):
    term_unik.append(seleksi_fitur[i][0])
'''
# Naive Bayes Training
# prior
prior_kk = len(kk) / totalData
prior_ktp = len(ktp) / totalData
prior_akta = len(akta) / totalData
prior_surat = len(surat) / totalData

# likelihood
def likelihood(term_unik, jtsk, jst):
    likelihood = {}
    for term in term_unik:
        likelihood[term] = (jst[term] + 1) / (jtsk + len(term_unik))
    return likelihood

likelihood_kk = likelihood(term_unik, jt_kk, jst_kk)
likelihood_ktp = likelihood(term_unik, jt_ktp, jst_ktp)
likelihood_akta = likelihood(term_unik, jt_akta, jst_akta)
likelihood_surat = likelihood(term_unik, jt_surat, jst_surat)

# evidence
def evidence(term_unik, jtsd, totalterm):
    evidence = {}
    for term in term_unik:
        evidence[term] = jtsd[term] / totalterm
    return evidence

evidence_allterms = evidence(term_unik, jtsd, jst)

# TESTING

test = pd.read_excel('DATA SKRIPSI FULL.xlsx',sheet_name='uji', usecols=['pengaduan', 'kelas'])
test = test.to_dict(orient='record')
datatest = []
labels = []
for element in test:
    datatest.append(element['pengaduan'])
    labels.append(element['kelas'])

stem_test = [stemmer.stem(str(doc)) for doc in datatest]
token_test = [tokenisasi(dok) for dok in stem_test]
filter_test = [filtering(d) for d in token_test]

# posterior
hasil = []
for doc in filter_test:
    like_kk = 1
    like_ktp = 1
    like_akta = 1
    like_surat = 1
    evid = 1
    for kata in doc:
        if kata in term_unik:
            like_kk *= likelihood_kk[kata]
            like_ktp *= likelihood_ktp[kata]
            like_akta *= likelihood_akta[kata]
            like_surat *= likelihood_surat[kata]
            evid *= evidence_allterms[kata]

    post_kk = (prior_kk * like_kk) / evid
    post_ktp = (prior_ktp * like_ktp) / evid
    post_akta = (prior_akta * like_akta) / evid
    post_surat = (prior_surat * like_surat) / evid

    text = " ".join(doc)
    peringkat = {'KK': post_kk, 'KTP': post_ktp, 'AKTA': post_akta, 'SURAT PINDAH': post_surat}
    # print(peringkat)
    tmp = max(peringkat.items(), key=operator.itemgetter(1))[0]
    hasil.append([text, tmp])

print("Hasil Klasifikasi")
label_pred = []
for i in range(len(hasil)):
    print('Data uji ke-', i + 1, 'dikasifikasikan ke dalam kelas: ', hasil[i][1])
    label_pred.append(hasil[i][1])

#Hitung Akurasi
b=0
for i in range(len(labels)):
   if labels[i]==hasil[i][1]:
       b=b+1
akurasi = b/len(labels)
print (akurasi)
