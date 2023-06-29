import pypdf



def findInDict(needle, haystack):
    for key in haystack.keys():
        try:
            value=haystack[key]
        except:
            continue
        if key==needle:
            return value
        if isinstance(value,dict):
            x=findInDict(needle,value)
            if x is not None:
                return x
pdfobject=open("C:/Users/pestam/Desktop/DIVVA-10060_CNCPT1_VBL_SMZ_Regres_SAAS_Dossierconversie__COLOR_V1.0.pdf",'rb')
pdf=pypdf.PdfReader(pdfobject)



xfa=findInDict('/XFA', pdf.resolved_objects)
xml=xfa[5].get_object().get_data()

print(xml)