import os
from xml.etree import ElementTree
import shutil
import logging
# from tkinter import Entry, Button, Tk, Label, TOP, LEFT, RIGHT
import tkinter
from tkinter import messagebox

# NS = {"eaed": "http://schemas.uwv.nl/UwvML/Berichten/EAEDRegielaag-RegistrerenDocumentRequest-v0300"}
NS = {"regres": "http://schemas.uwv.nl/Regresvoorblad-v0100"}
SOURCEFILEDIR = "C:/Users/pestam/PycharmProjects/metedataExtractor/resources/dummy/0609CV9600VBL3037_005"

TARGETFILEDIR = "C:/Users/pestam/PycharmProjects/metedataExtractor/targetmapje"
# XMLITEMS = {"titel": "GegevensleveringDocBundeling/Document/Titel",
#             "dagtekening": "GegevensleveringDocBundeling/Document/DatDagtekeningDocument",
#             "naam_dir": "GegevensleveringDocBundeling/Document/Bestand/NaamDirectory",
#             "naam_bestand": "GegevensleveringDocBundeling/Document/Bestand/NaamBestand",
#             "bsn": "GegevensleveringDocBundeling/Personen/PersoonBelanghebbende/"
#                    "NatuurlijkPersoon/Burgerservicenr",
#             }

XMLITEMS = {"Dossiernummer": "Dossiernummer",
            "Categorie": "Categorie",
            "Volgnummer": "Volgnummer"}
FILENAMECONSTRUCTOR = {"keys": ["Dossiernummer", "Categorie", "Volgnummer"],
                       "separator": "/",
                       "extension": "pdf"}


def klaar():

    messagebox.showinfo(title="Info",
                        message=f"Dit bestand staat in de map {os.getcwd()} Klaar! ")

    tk.destroy()

def copy_files(sourcefiledirectory: str, targetfiledirectory: str):
    """

    :param sourcefiledirectory:
    :param targetfiledirectory:
    :return:
    """
    sourcefiledirectory = SOURCEFILEDIR if len(sourcefiledirectory) == 0 else sourcefiledirectory
    targetfiledirectory = TARGETFILEDIR if len(targetfiledirectory) == 0 else targetfiledirectory
    xml_filename_list = list_xml_files_in_dir(sourcefiledirectory)
    number_of_files_copied = 0
    for xml_filename in xml_filename_list:
        logging.info(f"Parsing file {xml_filename}")
        metadata_dictionary = parse_xml(xml_filename, XMLITEMS)
        logging.info(f"Generating target filename")
        constructed_targetfilename = construct_filename_from_metadata(metadata_dictionary)

        if "naam_dir" in metadata_dictionary:
            if "naam_bestand" in metadata_dictionary:
                logging.info(f"Copying file {metadata_dictionary['naam_dir']}/{metadata_dictionary['naam_bestand']} "
                             f"to {targetfiledirectory}/{constructed_targetfilename}")
                copy_file(sourcefiledir=sourcefiledirectory, sourcefilename=metadata_dictionary['naam_bestand'],
                          targetfiledir=targetfiledirectory,
                          targetfilename=constructed_targetfilename)
                copy_file(sourcefiledir=metadata_dictionary["naam_dir"],
                          sourcefilename=metadata_dictionary["naam_bestand"],
                          targetfiledir=targetfiledirectory, targetfilename=constructed_targetfilename)
                number_of_files_copied += 1
            else:
                error_message = "No bestandsnaam for source pdf found in xml"
                messagebox.showerror(title="Error", message=error_message)
                raise SystemExit(error_message)

        else:
            error_message = "No directory for source pdf found in xml"
            messagebox.showerror(title="Error", message=error_message)
            raise SystemExit(error_message)
    messagebox.showinfo(title="Info",
                        message=f"Klaar! {number_of_files_copied} bestanden gekopieerd naar {targetfiledirectory}")
    tk.destroy()


def list_xml_files_in_dir(path: str) -> list:
    """
    This function lists al xml files that are stored in directory path
    :param path: The path to the location where the xml files are stored
    :return: a list of the names of all xml files in the given directory
    """
    if os.path.exists(path):
        xmlfilesinpath = [item for item in os.listdir(path) if item.endswith(".xml")]
    else:
        error_message = f"Directory {path} does not exist"
        messagebox.showerror(title="Error", message=error_message)
        raise SystemExit(error_message)

    if len(xmlfilesinpath) < 1:
        error_message = f"No xml files found in directory {path}"
        messagebox.showerror(title="Error", message=error_message)
        raise SystemExit(error_message)
    return xmlfilesinpath


def copy_file(sourcefiledir: str, sourcefilename: str, targetfiledir: str, targetfilename: str):
    """
    This function copies a file with name sourcefilename from directory sourcefilepath to directory targetfilepath with
    name targetfilename
    :param sourcefiledir: The path to the source file
    :param sourcefilename: the name of the source file
    :param targetfiledir: The path to the target file
    :param targetfilename: The name of the target file
    :return:
    """
    if FILENAMECONSTRUCTOR["separator"] == "/":
        splittedfilename = targetfilename.split("/")
        targetfiledir = "/".join([targetfiledir] + splittedfilename[:-1])
        targetfilename = splittedfilename[-1]

    if os.path.exists(f"{sourcefiledir}/{sourcefilename}"):
        if os.path.exists(f"{targetfiledir}"):
            if os.path.exists(f"{targetfiledir}/{targetfilename}"):
                logging.warning(f"File {targetfiledir}/{targetfilename} already exists, overwriting existing file...")
            shutil.copy(f"{sourcefiledir}/{sourcefilename}", f"{targetfiledir}/{targetfilename}")
        else:
            logging.warning(f"target directory {targetfiledir} does not exists: creating target directory...")
            os.makedirs(targetfiledir, exist_ok=True)
            shutil.copy(f"{sourcefiledir}/{sourcefilename}", f"{targetfiledir}/{targetfilename}")
    else:
        logging.warning(f"source file not found {sourcefiledir}/{sourcefilename}, skipping file...")


def parse_xml(xmlfilepath: str, items_to_retrieve: dict) -> dict:
    """
    This function reads given elements from the xml file and returns a dictionary with those elements
    :param xmlfilepath: The filepath of the xml file
    :param items_to_retrieve: a dictionary with a name and location of the items to retrieve from the xml
    :return: a dictionary with the retrieved items from the xml
    """
    nskey = list(NS.keys())[0]
    result_dict = {}
    if os.path.exists(f"{SOURCEFILEDIR}/{xmlfilepath}"):
        tree = ElementTree.parse(f"{SOURCEFILEDIR}/{xmlfilepath}")
        root = tree.getroot()

        for key, value in items_to_retrieve.items():
            path = f"{nskey}:{f'/{nskey}:'.join(value.split('/'))}"

            item = root.find(path=path, namespaces=NS)
            if item is not None:
                result_dict[key] = item.text
            else:
                logging.warning(f"No data found for {key}, {value} does not exist in xml. Skipping...")
    else:
        logging.warning(f"{xmlfilepath} not found in dir {SOURCEFILEDIR}, skipping...")
    if "naam_dir" in result_dict:
        result_dict["naam_dir"] = result_dict["naam_dir"].replace("\\", "/")
        result_dict["naam_dir"] = result_dict["naam_dir"][:-1] if result_dict["naam_dir"].endswith("/") else \
            result_dict["naam_dir"]
    else:
        result_dict["naam_dir"] = SOURCEFILEDIR
    result_dict["naam_bestand"] = result_dict[
        "naam_bestand"] if "naam_bestand" in result_dict else f"{xmlfilepath.split('.')[0]}.PDF"
    return result_dict


def construct_filename_from_metadata(metadata_dict: dict) -> str:
    """
    This function generates a filename conform the FILENAMECONSTRUCTOR from the metadata_dict
    :param metadata_dict: a dictionary with metadata from the file
    :return: filename in string format
    """
    if all(item in metadata_dict.keys() for item in FILENAMECONSTRUCTOR["keys"]):
        metadata_list = [metadata_dict[key] for key in FILENAMECONSTRUCTOR["keys"]]
    else:
        error_message = f"Not all keys in FILENAMECONTRUCTOR found in xml. Required keys " \
                        f"{FILENAMECONSTRUCTOR['keys']}, available keys in xml {metadata_dict.keys()}"
        messagebox.showerror(tite="Error", message=error_message)
        raise SystemExit(error_message)

    return f"{FILENAMECONSTRUCTOR['separator'].join(metadata_list)}.{FILENAMECONSTRUCTOR['extension']}"


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    tk = tkinter.Tk()

    l1 = tkinter.Label(tk, justify=tkinter.LEFT, text="Geef de directory van de xml bestanden (C:/Users/..../...)\n"
                                                      "Als er niets wordt meegegeven zal de map uitgelezen worden "
                                                      "C:/Users/pestam/PycharmProjects/metedataExtractor/resources")
    l2 = tkinter.Label(tk, justify=tkinter.LEFT, text="Geef de directory waar de pdf bestanden moeten landen "
                                                      "(C:/Users/..../...)\n"
                                                      "Als er niets wordt meegegeven zal de map uitgelezen worden "
                                                      "C:/Users/pestam/PycharmProjects/metedataExtractor/targetdir")

    # grid method to arrange labels in respective
    # rows and columns as specified
    l1.grid(row=0, column=0, sticky=tkinter.W, pady=2)
    l2.grid(row=2, column=0, sticky=tkinter.W, pady=2)

    # entry widgets, used to take entry from user
    e1 = tkinter.Entry(tk, justify=tkinter.LEFT)
    e2 = tkinter.Entry(tk, justify=tkinter.LEFT)

    # this will arrange entry widgets
    e1.grid(row=1, column=0, pady=2)
    e2.grid(row=3, column=0, pady=2)

    btn = tkinter.Button(tk, text="Kopieer bestanden",
                         command=lambda: copy_files(sourcefiledirectory=e1.get(), targetfiledirectory=e2.get()))
    # btn = tkinter.Button(tk, text="Kopieer bestanden",
    #                      command=lambda: klaar())

    btn.grid(row=4, column=0, sticky=tkinter.W, columnspan=2)
    tk.mainloop()
