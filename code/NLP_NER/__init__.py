''''
@component: Natural Language Processing - Name Entity Recognition (NLP-NER).
@author: Sandaru & Sergio.
@summary: NLP-NER task on textual content of docs. from CouchDB.
@project: AGRIF.
# History Update:
#    2020-06-03,25: internal release of version 0.1.0.
#    2020-08-26: *load_models* separated from *main* (process).
#    2020-10-26: Sampling mechanism.
#    2023-03-13: MEL import as "global".
'''


# ==================================================================================================
import MEL
import json
import NLP_NER.EntityRecognition as _NLP_NER


# ==================================================================================================
def load_models(models=[_NLP_NER.NERUtils.stanza_name]): # default: stanza
    _NLP_NER.NER.load_models(models)


def NER_main(models=[_NLP_NER.NERUtils.stanford_class3_name], docs={}):
    ''' --------------------------------------- NER ---------------------------------------
    _models = [
        _NLP_NER.NERUtils.stanford_class3_name,      _NLP_NER.NERUtils.stanford_class4_name, _NLP_NER.NERUtils.stanford_class7_name,
        _NLP_NER.NERUtils.spacy_sm_name,             _NLP_NER.NERUtils.spacy_md_name,        _NLP_NER.NERUtils.spacy_lg_name,
        _NLP_NER.NERUtils.stanza_name,               _NLP_NER.NERUtils.nltk_name,            _NLP_NER.NERUtils.bert_name,
        _NLP_NER.NERUtils.flair_name,                _NLP_NER.NERUtils.flair_ontonotes_name, _NLP_NER.NERUtils.flair_fast_name,
        _NLP_NER.NERUtils.flair_fast_ontonotes_name, _NLP_NER.NERUtils.flair_pooled_name,
        _NLP_NER.NERUtils.deeppavlov_onto_name,      _NLP_NER.NERUtils.deeppavlov_onto_bert_name,
        _NLP_NER.NERUtils.deeppavlov_conll2003_name, _NLP_NER.NERUtils.deeppavlov_conll2003_bert_name,
        _NLP_NER.NERUtils.allennlp_ner_name,         _NLP_NER.NERUtils.allennlp_finegrained_ner_name,
        _NLP_NER.NERUtils.polyglot_name
    ]
    _models = [_NLP_NER.NERUtils.spacy_sm_name]
    '''
    r = docs if ("docs" in docs) else { "docs": [docs] } # converts input into proper expected structure: r["docs"]
    MEL.Utils.output(f"{json.dumps(r, indent=4)}", _print=False)
    output = _NLP_NER.NER.ner_for_all_files(r, models)
    MEL.Utils.output(f"{json.dumps(output, indent=4)}", _print=False)
    return output


def sampling_main(models=[_NLP_NER.NERUtils.stanford_class3_name], dataset_names=[]):
    import NLP_NER.Sampling as Sampling # prevent circular referencing from MEL
    Sampling.main_sampling(models, dataset_names)


def sampling_get_samples():
    import NLP_NER.Sampling as Sampling # prevent circular referencing from MEL
    return Sampling.get_samples()


def sampling_get_samples_not_in_ner_db(datasets=[], models=[_NLP_NER.NERUtils.stanza_name]): # default: stanza
    import NLP_NER.Sampling as Sampling # prevent circular referencing from MEL
    # to get samples which have not been previously processed for the specified ner models
    return Sampling.get_samples_not_in_ner_db(_models=models, _datasets=datasets)


# ==================================================================================================
