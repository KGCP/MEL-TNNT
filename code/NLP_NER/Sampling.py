from NLP_NER.EntityRecognition import NER
from NLP_NER.EntityRecognition import NERUtils
import random
import json
import platform
import MEL


# ==================================================================================================
class SamplingUtils:
    CONFIG_JSON_DIR_ = \
        "E:/_GitHub/KGCP/MEL-TNNT/code/NLP_NER/" if (platform.system() == 'Windows') else\
        "/data/mapping-services/NLP_NER/"
    CONFIG_JSON_FILE = "sampling-config.json"
    with open(CONFIG_JSON_DIR_ + CONFIG_JSON_FILE, "r") as _config_json_f:
        _config = json.loads(_config_json_f.read())

    datasets = _config["dataset"]
    constant = _config["sampling_constant"]


# ==================================================================================================
class Sampling:
    @staticmethod
    def sampleByExtension(files, extensions, models):
        for folder in files:
            extension_files = []

            for ext in extensions:
                extension = []
                for file in folder:
                    if file["General-Metadata"]["EXTENSION"].lower() in ext:
                        extension.append(file)
                extension_files.append(extension)

            outputs = []
            for sorted_files in extension_files:
                for i in range(round(len(sorted_files) * SamplingUtils.constant)):

                    NLP_NER = {}
                    index = random.randrange(len(sorted_files) - 1)

                    if ('text-analysis' in sorted_files[index]["Specific-Metadata"]):
                        doc_0 = {}
                        doc_0["filename"] = sorted_files[index]["General-Metadata"]["FILENAME"]

                        if (sorted_files[index]["General-Metadata"]["EXTENSION"] == "csv"): # only CSV | doesn't apply to XLSX
                            text = NER.csv_preprocess(sorted_files[index])
                            NLP_NER["doc-0"] = NER.get_csv_ner_from_models(text, doc_0, models)
                        else:
                            text = NER.get_text_values(sorted_files[index])
                            NLP_NER["doc-0"] = NER.get_ner_from_models(text, doc_0, models)

                        if (sorted_files[index]["General-Metadata"]["EXTENSION"] == "msg"):

                            attachment_texts = NER.get_attachment_texts(sorted_files[index])
                            for i in range(len(attachment_texts)):
                                attachment = {}
                                attachment["filename"] = attachment_texts[i]["filename"]
                                attachment_text = attachment_texts[i]["text"]
                                NLP_NER[f"doc-{i + 1}"] = NER.get_ner_from_models(attachment_text, attachment, models)

                        elif (sorted_files[index]["General-Metadata"]["EXTENSION"] == "zip"):
                            print()

                    outputs.append(NLP_NER)

        return outputs


    @staticmethod
    def sampleByFileLength(object, models):

        file_size_below_100000 = []
        file_size_below_1000000 = []
        file_size_above = []
        all_files = []
        for file in object["docs"]:
            file_length = file["General-Metadata"]["FILELENGTH"]
            if file_length < 100000:
                file_size_below_100000.append(file)
            elif file_length < 1000000:
                file_size_below_1000000.append(file)
            else:
                file_size_above.append(file)

        outputs = []
        all_files.append(file_size_below_100000)
        all_files.append(file_size_below_1000000)
        all_files.append(file_size_above)

        for file_list in all_files:
            for i in range(round(len(file_list) * SamplingUtils.constant)):
                NLP_NER = {}
                index = random.randrange(len(file_list) - 1)

                if ('text-analysis' in file_list[index]["Specific-Metadata"]):
                    doc_0 = {}
                    doc_0["filename"] = file_list[index]["General-Metadata"]["FILENAME"]

                    if (file_list[index]["General-Metadata"]["EXTENSION"] == "csv"):
                        text = NER.csv_preprocess(file_list[index])
                        NLP_NER["doc-0"] = NER.get_csv_ner_from_models(text, doc_0, models)
                    else:
                        text = NER.get_text_values(file_list[index])
                        NLP_NER["doc-0"] = NER.get_ner_from_models(text, doc_0, models)

                    if (file_list[index]["General-Metadata"]["EXTENSION"] == "msg"):

                        attachment_texts = NER.get_attachment_texts(file_list[index])
                        for i in range(len(attachment_texts)):
                            attachment = {}
                            attachment["filename"] = attachment_texts[i]["filename"]
                            attachment_text = attachment_texts[i]["text"]
                            NLP_NER[f"doc-{i + 1}"] = NER.get_ner_from_models(attachment_text, attachment,
                                                                              models)

                    elif (file_list[index]["General-Metadata"]["EXTENSION"] == "zip"):
                        print()
                outputs.append(NLP_NER)

        return outputs


    @staticmethod
    def get_samples_by_length(docs, constant):
        file_list_by_len = []
        file_size_below_100000  = [file for file in docs if file["General-Metadata"]["FILELENGTH"] < 100000]
        file_size_below_1000000 = [file for file in docs if
                                   file["General-Metadata"]["FILELENGTH"] < 1000000 and file["General-Metadata"][
                                       "FILELENGTH"] >= 100000]
        file_size_above = [file for file in docs if file["General-Metadata"]["FILELENGTH"] >= 1000000]
        all_files = []
        all_files.append(file_size_below_100000)
        all_files.append(file_size_below_1000000)
        all_files.append(file_size_above)

        for file_list in all_files:
            files = []
            for i in range(round(len(file_list) * constant)):
                index = random.randrange(len(file_list) - 1)
                files.append(file_list[index])
            file_list_by_len.append(files)
        return file_list_by_len


    @staticmethod
    def get_samples_by_doc_Structure(docs, constant):
        pass


    @staticmethod
    def get_samples_by_extension(docs, constant, extensions):
        file_list = []
        files_by_extension = []
        for ext in extensions:
            files = [i for i in docs if i["General-Metadata"]["EXTENSION"].lower() == ext]
            files_by_extension.append(files)

        for ext in files_by_extension:
            ext_list = []
            for i in range(round(len(ext) * constant)):
                index = random.randrange(len(ext) - 1)
                ext_list.append(ext[index])
            file_list.append(ext_list)
        return file_list


    @staticmethod
    def get_folders_and_extensions(object):
        n = 0
        paths = []
        extensions = []
        for file in object["docs"]:
            n += 1
            if file["General-Metadata"]["PARENT"] not in paths and file["General-Metadata"]["PARENT"]:
                paths.append(file["General-Metadata"]["PARENT"])
            if file["General-Metadata"]["EXTENSION"].lower() not in extensions:
                extensions.append(file["General-Metadata"]["EXTENSION"].lower())
        print(*extensions)

        return paths, extensions


    @staticmethod
    def get_files_by_folder(file_paths, object):
        n = 0
        all_files = []
        for path in file_paths:
            folder = []
            for x in object["docs"]:
                if path in x["General-Metadata"]["PARENT"]:
                    folder.append(x)
            all_files.append(folder)
            n += len(folder)
        return all_files


# ==================================================================================================
def main_sampling(_models=[NERUtils.stanford_class3_name], _dataset_names=[]):
    NER.load_models(_models)

    selector = {}
    fields = ["_id", "General-Metadata", "Specific-Metadata"]

    for dataset in SamplingUtils.datasets:
        if (_dataset_names and (dataset["name"] not in _dataset_names)):
            continue # skip...
        print(f"@dataset={dataset['name']}")
        DB = dataset["CouchDB-db"]
        SamplingUtils.constant = dataset["sampling_constant"]
        print(f"Querying all docs of database '{DB}'...")
        r = MEL.CouchDB.queryDocs(DB, selector, False, fields)
        if bool(dataset["sampling"]["by_extension"]):
            file_paths, extensions = Sampling.get_folders_and_extensions(r)
            file_lists = Sampling.get_files_by_folder(file_paths, r)
            print(file_lists)
            ext_results = Sampling.sampleByExtension(file_lists, extensions, _models)
            print(ext_results)
        if bool(dataset["sampling"]["by_file_length"]):
            len_results = Sampling.sampleByFileLength(r, _models)
            print(len_results)
        if bool(dataset["sampling"]["by_doc_structure"]):
            structure_results = Sampling.sampleByDocStructure()
            print(structure_results)


def get_samples_not_in_ner_db(_models, _datasets=[]):
    selector = {}
    fields     = ["_id", "_rev", "General-Metadata", "Use-Case$Folder"]
    fields_ner = ["_id", "_rev", "General-Metadata", "NLP-NER"]
    datasets = {}

    for dataset in SamplingUtils.datasets:
        name = dataset["name"]
        if (_datasets) and (name not in _datasets): # skipping dataset
            continue
        DB = dataset["CouchDB-db"]
        r = MEL.CouchDB.queryDocs(DB, selector, False, fields)

        # change name according to the respective ner database. changes in the sampling config file
        DB_ner = "/nlp-ner-" + DB.split("/")[1]

        r_ner = MEL.CouchDB.queryDocs(DB_ner, selector, False, fields_ner)["docs"]
        r_ner_ids = [doc["General-Metadata"]["ABSOLUTEPATH"] for doc in r_ner]

        docs        = [doc for doc in r["docs"] if doc["General-Metadata"]["ABSOLUTEPATH"] not in r_ner_ids]
        docs_in_ner = [doc for doc in r_ner     if doc["General-Metadata"]["ABSOLUTEPATH"] in r_ner_ids]
        for doc in docs_in_ner:
            for model in _models:
                # if at leaset one model in the models is not processed, the document is considered.
                if model not in doc["NLP-NER"]:
                    docs.append(doc)
                    break

        datasets[name] = {}
        samples = {}
        if bool(dataset["sampling"]["by_extension"]):
            file_paths, extensions = Sampling.get_folders_and_extensions(r)
            samples["by_extension"] = Sampling.get_samples_by_extension(docs, dataset["sampling_constant"], extensions)

        if bool(dataset["sampling"]["by_file_length"]):
            len_samples = Sampling.get_samples_by_length(docs, dataset["sampling_constant"])
            samples["by_length"] = len_samples

        if bool(dataset["sampling"]["by_doc_structure"]):
            doc_structure_samples = Sampling.get_samples_by_doc_Structure(docs, dataset["sampling_constant"])
            samples["by_doc_structure"] = doc_structure_samples

        datasets[name] = samples

    return datasets


def get_samples(_datasets=[]):
    selector = {}
    fields = ["_id", "_rev", "General-Metadata", "Use-Case$Folder"]
    datasets = {}
    for dataset in SamplingUtils.datasets:
        if (_datasets) and (dataset["name"] not in _datasets): # skipping dataset
            continue
        DB = dataset["CouchDB-db"]
        r = MEL.CouchDB.queryDocs(DB, selector, False, fields)

        datasets[DB] = {}
        samples = {}
        if bool(dataset["sampling"]["by_extension"]):
            file_paths, extensions = Sampling.get_folders_and_extensions(r)
            samples["by_extension"] = Sampling.get_samples_by_extension(r["docs"], dataset["sampling_constant"],
                                                                        extensions)

        if bool(dataset["sampling"]["by_file_length"]):
            len_samples = Sampling.get_samples_by_length(r["docs"], dataset["sampling_constant"])
            samples["by_length"] = len_samples

        if bool(dataset["sampling"]["by_doc_structure"]):
            doc_structure_samples = Sampling.get_samples_by_doc_Structure(r["docs"], dataset["sampling_constant"])
            samples["by_doc_structure"] = doc_structure_samples

        datasets[DB] = samples
    return datasets


# ==================================================================================================
if __name__ == "__main__":
    main_sampling(_dataset_names=["DoEE-Assessments"])
    #to get samples
    samples = get_samples()
    # to get samples which have not been previously processed for the specified ner models
    samples_not_processed = get_samples_not_in_ner_db(_models = [NERUtils.spacy_sm_name])
