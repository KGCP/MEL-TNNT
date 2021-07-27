import platform # Checking the O.S. | 'Windows' specific variables.
import json
import re
import random
import datetime
import string
import gc
import regex

import nltk
import spacy
from nltk.tag.stanford import StanfordNERTagger
import stanza
from spacy_stanza import StanzaLanguage
from NLP_NER.bert import Ner
from flair.data import Sentence
from flair.models import SequenceTagger
# Import segtok library to split the paragraph into sentences flair
from segtok.segmenter import split_single
from deeppavlov import configs, build_model

from allennlp.predictors.predictor import Predictor
import allennlp_models.tagging

from polyglot.text import Text


# ==================================================================================================
class NERUtils:
    CONFIG_JSON_DIR_ = \
        "E:/_GitHub/KGCP/MEL-TNNT/code/NLP_NER/" if (platform.system() == 'Windows') else\
        "/data/mapping-services/NLP_NER/"
    CONFIG_JSON_FILE = "NLP-NER-config.json"
    with open(CONFIG_JSON_DIR_ + CONFIG_JSON_FILE, "r") as _config_json_f:
        _config = json.loads(_config_json_f.read())

    nlp_sm = _config["spacy_sm_model"]["model"]
    nlp_md = _config["spacy_md_model"]["model"]
    nlp_lg = _config["spacy_lg_model"]["model"]
    nlp_sm_len = _config["spacy_sm_model"]["max-length"]
    nlp_md_len = _config["spacy_md_model"]["max-length"]
    nlp_lg_len = _config["spacy_lg_model"]["max-length"]
    nlp_sm_categories = _config["spacy_sm_model"]["categories"]
    nlp_md_categories = _config["spacy_md_model"]["categories"]
    nlp_lg_categories = _config["spacy_lg_model"]["categories"]

    stanford_ner_path = _config["Stanford-Ner-Path"]
    stanford_class3 = _config["stanford_class3_model"]["path"]
    stanford_class4 = _config["stanford_class4_model"]["path"]
    stanford_class7 = _config["stanford_class7_model"]["path"]

    stanford_class3_categories = _config["stanford_class3_model"]["categories"]
    stanford_class4_categories = _config["stanford_class4_model"]["categories"]
    stanford_class7_categories = _config["stanford_class7_model"]["categories"]

    stanza_max_length = _config["stanza_model"]["max-length"]
    stanza_categories = _config["stanza_model"]["categories"]

    nltk_categories = _config["nltk_model"]["categories"]
    bert_path = _config["bert_model"]["path"]
    bert_max_length = _config["bert_model"]["max_length"]
    punctuation_marks = _config["bert_model"]["punctuation_list"]
    bert_categories = _config["bert_model"]["categories"]

    flair_categories = _config["flair_model"]["categories"]
    flair_ontonotes_categories = _config["flair_ontonotes_model"]["categories"]
    flair_fast_categories = _config["flair_fast_model"]["categories"]
    flair_fast_ontonotes_categories = _config["flair_fast_ontonotes_model"]["categories"]
    flair_pooled_categories = _config["flair_pooled_model"]["categories"]
    deeppavlov_onto_categories = _config["deeppavlov_onto_model"]["categories"]
    deeppavlov_onto_bert_categories = _config["deeppavlov_onto_bert_model"]["categories"]
    deeppavlov_conll2003_categories = _config["deeppavlov_conll2003_model"]["categories"]
    deeppavlov_conll2003_bert_categories = _config["deeppavlov_conll2003_bert_model"]["categories"]
    allennlp_ner_categories = _config["allennlp_ner"]["categories"]
    allennlp_finegrained_ner_categories = _config["allennlp-finegrained-ner"]["categories"]

    datetime2string_format = _config["DateTime-to-String-Format"]

    text_file = open(_config["Text-File-Path"], "w")

    spacy_sm_name = _config["spacy_sm_model"]["name"]
    spacy_md_name = _config["spacy_md_model"]["name"]
    spacy_lg_name = _config["spacy_lg_model"]["name"]
    stanford_class3_name = _config["stanford_class3_model"]["name"]
    stanford_class4_name = _config["stanford_class4_model"]["name"]
    stanford_class7_name = _config["stanford_class7_model"]["name"]
    stanza_name = _config["stanza_model"]["name"]
    nltk_name = _config["nltk_model"]["name"]
    bert_name = _config["bert_model"]["name"]
    flair_name = _config["flair_model"]["name"]
    flair_ontonotes_name =_config["flair_ontonotes_model"]["name"]
    flair_fast_name = _config["flair_fast_model"]["name"]
    flair_fast_ontonotes_name = _config["flair_fast_ontonotes_model"]["name"]
    flair_pooled_name = _config["flair_pooled_model"]["name"]
    deeppavlov_onto_name = _config["deeppavlov_onto_model"]["name"]
    deeppavlov_onto_bert_name = _config["deeppavlov_onto_bert_model"]["name"]
    deeppavlov_conll2003_name = _config["deeppavlov_conll2003_model"]["name"]
    deeppavlov_conll2003_bert_name = _config["deeppavlov_conll2003_bert_model"]["name"]
    allennlp_ner_name = _config["allennlp_ner"]["name"]
    allennlp_finegrained_ner_name = _config["allennlp-finegrained-ner"]["name"]

    allennlp_ner_path = _config["allennlp_ner"]["path"]
    allennlp_finegrained_ner_path = _config["allennlp-finegrained-ner"]["path"]

    polyglot_name = _config["polyglot_model"]["name"]
    polyglot_categories = _config["polyglot_model"]["categories"]

    sentence_include = _config["sentence_include"]
    csv_delimiter = _config["Text-Based-File-Processing"]["CSV"]

    @staticmethod
    def garbage_collector():
        # gc.get_count() - to get the number of objects. can check before and after gc.collect() to see how much is cleaned
        collected = gc.collect()


# ==================================================================================================
class Polyglot:
    @staticmethod
    def get_polyglot_entities(text):

        dt_begin = datetime.datetime.now()
        polyglot_ner_model = {}
        text_ner = Text(text)
        polyglot_entities = []

        for sent in text_ner.sentences:
            for entity in sent.entities:
                entity_list = []
                for item in entity:
                    item_tuple = (item, entity.tag.split("-")[1])
                    entity_list.append(item_tuple)
                polyglot_entities.append(entity_list)

        entity_labels = NER.get_entity_label_lists(text, polyglot_entities, NERUtils.polyglot_categories)
        polyglot_ner_model["_output"] = entity_labels

        dt_end = datetime.datetime.now()
        polyglot_ner_model["_stats"] = NER.get_statistics(dt_begin, dt_end, entity_labels.copy())
        return polyglot_ner_model


# ==================================================================================================
class AllennlpNer:
    ner_predictor = None
    finegrained_ner_predictor = None

    @staticmethod
    def load_ner_model():
        AllennlpNer.ner_predictor = Predictor.from_path(NERUtils.allennlp_ner_path)
        AllennlpNer.ner_predictor._dataset_reader._token_indexers['token_characters']._min_padding_length = 3

    @staticmethod
    def load_finegrained_ner_model():
        AllennlpNer.finegrained_ner_predictor = Predictor.from_path(NERUtils.allennlp_finegrained_ner_path)
        AllennlpNer.finegrained_ner_predictor._dataset_reader._token_indexers['token_characters']._min_padding_length = 3

    @staticmethod
    def get_continuous_chunks(tagged_sent):
        continuous_chunk = []
        current_chunk = []

        for token, tag in tagged_sent:
            if tag != "O":
                current_chunk.append((token, tag))
            else:
                if current_chunk:  # if the current chunk is not empty
                    continuous_chunk.append(current_chunk)
                    current_chunk = []
        # Flush the final current_chunk into the continuous_chunk, if any.
        if current_chunk:
            continuous_chunk.append(current_chunk)
        return continuous_chunk

    @staticmethod
    def get_allennlp_ner(text):
        dt_begin = datetime.datetime.now()
        allennlp_ner_model = {}

        predictor = AllennlpNer.ner_predictor
        predictor.max_length =  5402555

        output = predictor.predict(text)
        concepts = output["words"]
        tags = output["tags"]

        sentence_chunks = [(concepts[i], tags[i].split("-")[1]) if len(tags[i]) > 1 else (concepts[i], tags[i]) for i in
                           range(len(concepts))]

        named_entities = AllennlpNer.get_continuous_chunks(sentence_chunks)

        entity_labels = NER.get_entity_label_lists(text, named_entities, NERUtils.allennlp_ner_categories)
        allennlp_ner_model["_output"] = entity_labels

        dt_end = datetime.datetime.now()
        allennlp_ner_model["_stats"] = NER.get_statistics(dt_begin, dt_end, entity_labels.copy())

        return allennlp_ner_model

    @staticmethod
    def get_allennlp_fine_grained_ner(text):
        dt_begin = datetime.datetime.now()
        allennlp_fine_grained_ner_model = {}

        predictor = AllennlpNer.finegrained_ner_predictor
        predictor.max_length =  5402555


        output = predictor.predict(text)
        concepts = output["words"]
        tags = output["tags"]

        sentence_chunks = [(concepts[i], tags[i].split("-")[1]) if len(tags[i]) > 1 else (concepts[i], tags[i]) for i in
                           range(len(concepts))]

        named_entities = AllennlpNer.get_continuous_chunks(sentence_chunks)

        entity_labels = NER.get_entity_label_lists(text, named_entities, NERUtils.allennlp_finegrained_ner_categories)
        allennlp_fine_grained_ner_model["_output"] = entity_labels

        dt_end = datetime.datetime.now()
        allennlp_fine_grained_ner_model["_stats"] = NER.get_statistics(dt_begin, dt_end, entity_labels.copy())

        return allennlp_fine_grained_ner_model


# ==================================================================================================
class Deeppavlov:
    onto_bert_model = None
    onto_model = None
    conll_bert_model = None
    conll_model = None

    @staticmethod
    def load_onto_bert_model():
        Deeppavlov.onto_bert_model = build_model(configs.ner.ner_ontonotes_bert)

    @staticmethod
    def load_onto_model():
        Deeppavlov.onto_model = build_model(configs.ner.ner_ontonotes)

    @staticmethod
    def load_conll_bert_model():
        #  Deeppavlov.conll_bert_model = build_model(configs.ner.ner_conll2003_bert, download=True) first run -  should download the models
        Deeppavlov.conll_bert_model = build_model(configs.ner.ner_conll2003_bert)

    @staticmethod
    def load_conll_model():
        Deeppavlov.conll_model = build_model(configs.ner.ner_conll2003)


    @staticmethod
    def get_entity_by_punctuation(text, index, model):
        output_entities = []
        output_tags = []
        if (index != 4):
            sentences = text.split(NERUtils.punctuation_marks[index])

            for sentence in sentences:
                if (len(sentence) < NERUtils.bert_max_length):
                    try:
                        ner_tagged = model([sentence])
                        concepts = ner_tagged[0][0]
                        tags = ner_tagged[1][0]
                        output_entities.extend(concepts)
                        output_tags.extend(tags)
                    except:
                        pass
                else:
                    output, tags = Deeppavlov.get_entity_by_punctuation(sentence, index + 1, model)
                    output_entities.extend(output)
                    output_tags.extend(tags)

        return output_entities, output_tags

    @staticmethod
    def get_continuous_chunks(tagged_sent):
        continuous_chunk = []
        current_chunk = []

        for token, tag in tagged_sent:
            if tag != "O":
                current_chunk.append((token, tag))
            else:
                if current_chunk:  # if the current chunk is not empty
                    continuous_chunk.append(current_chunk)
                    current_chunk = []
        # Flush the final current_chunk into the continuous_chunk, if any.
        if current_chunk:
            continuous_chunk.append(current_chunk)
        return continuous_chunk

    @staticmethod
    def get_deeppavlov_ontobert_entities(text):
        dt_begin = datetime.datetime.now()
        deeppavolov_model = {}

        concepts, tags = Deeppavlov.get_entity_by_punctuation(text, 0, Deeppavlov.onto_bert_model)
        sentence_chunks = [(concepts[i], tags[i].split("-")[1]) if len(tags[i]) > 1 else (concepts[i], tags[i]) for i in
                           range(len(concepts))]

        named_entities = Deeppavlov.get_continuous_chunks(sentence_chunks)

        entity_labels = NER.get_entity_label_lists(text, named_entities, NERUtils.deeppavlov_onto_bert_categories)
        deeppavolov_model["_output"] = entity_labels

        dt_end = datetime.datetime.now()
        deeppavolov_model["_stats"] = NER.get_statistics(dt_begin, dt_end, entity_labels.copy())

        return deeppavolov_model

    @staticmethod
    def get_deeppavlov_onto_entities(text):
        dt_begin = datetime.datetime.now()
        deeppavolov_model = {}

        ner_tagged = Deeppavlov.onto_model([text])
        concepts = ner_tagged[0][0]
        tags = ner_tagged[1][0]
        sentence_chunks = [(concepts[i], tags[i].split("-")[1]) if len(tags[i]) > 1 else (concepts[i], tags[i]) for i in
                           range(len(concepts))]

        named_entities = Deeppavlov.get_continuous_chunks(sentence_chunks)

        entity_labels = NER.get_entity_label_lists(text, named_entities, NERUtils.deeppavlov_onto_categories)
        deeppavolov_model["_output"] = entity_labels

        dt_end = datetime.datetime.now()
        deeppavolov_model["_stats"] = NER.get_statistics(dt_begin, dt_end, entity_labels.copy())

        return deeppavolov_model

    @staticmethod
    def get_deeppavlov_conll2003_bert_entities(text):
        dt_begin = datetime.datetime.now()
        deeppavolov_model = {}
        concepts, tags = Deeppavlov.get_entity_by_punctuation(text, 0, Deeppavlov.conll_bert_model)
        sentence_chunks = [(concepts[i], tags[i].split("-")[1]) if len(tags[i]) > 1 else (concepts[i], tags[i]) for i in
                           range(len(concepts))]

        named_entities = Deeppavlov.get_continuous_chunks(sentence_chunks)

        entity_labels = NER.get_entity_label_lists(text, named_entities, NERUtils.deeppavlov_conll2003_bert_categories)
        deeppavolov_model["_output"] = entity_labels

        dt_end = datetime.datetime.now()
        deeppavolov_model["_stats"] = NER.get_statistics(dt_begin, dt_end, entity_labels.copy())

        return deeppavolov_model

    @staticmethod
    def get_deeppavlov_conll2003_entities(text):
        dt_begin = datetime.datetime.now()
        deeppavolov_model = {}
        ner_tagged = Deeppavlov.conll_model([text])
        concepts = ner_tagged[0][0]
        tags = ner_tagged[1][0]
        sentence_chunks = [(concepts[i], tags[i].split("-")[1]) if len(tags[i]) > 1 else (concepts[i], tags[i]) for i in
                           range(len(concepts))]

        named_entities = Deeppavlov.get_continuous_chunks(sentence_chunks)

        entity_labels = NER.get_entity_label_lists(text, named_entities, NERUtils.deeppavlov_conll2003_categories)
        deeppavolov_model["_output"] = entity_labels

        dt_end = datetime.datetime.now()
        deeppavolov_model["_stats"] = NER.get_statistics(dt_begin, dt_end, entity_labels.copy())

        return deeppavolov_model


# ==================================================================================================
class FlairNer:
    tagger = None
    ontonotes_tagger = None
    fast_tagger = None
    fast_ontonotes_tagger = None
    pooled_tagger = None

    @staticmethod
    def load_flair_model():
        FlairNer.tagger = SequenceTagger.load('ner')

    @staticmethod
    def load_flair_ontonotes_model():
        FlairNer.ontonotes_tagger = SequenceTagger.load('ner-ontonotes')

    @staticmethod
    def load_flair_ontonotes_fast_model():
        FlairNer.fast_ontonotes_tagger = SequenceTagger.load('ner-ontonotes-fast')

    @staticmethod
    def load_flair_fast_model():
        FlairNer.fast_tagger = SequenceTagger.load('ner-fast')

    @staticmethod
    def load_flair_pooled_model():
        FlairNer.pooled_tagger = SequenceTagger.load('ner-pooled')

    @staticmethod
    def get_flair_fast_entities(text):
        dt_begin = datetime.datetime.now()
        sentences = [Sentence(sent, use_tokenizer=True) for sent in split_single(text)]
        FlairNer.fast_tagger.predict(sentences)

        flair_fast_model = {}
        categories = NERUtils.flair_categories
        flair_entities = []

        for sent in sentences:
            for entity in sent.get_spans('ner'):
                flair_entities.append(entity)

        entity_labels = NER.get_entity_label_lists(text, flair_entities, categories)
        flair_fast_model["_output"] = entity_labels
        dt_end = datetime.datetime.now()
        flair_fast_model["_stats"] = NER.get_statistics(dt_begin, dt_end, entity_labels.copy())
        return flair_fast_model

    @staticmethod
    def get_flair_ontonotes_fast_entities(text):
        dt_begin = datetime.datetime.now()
        sentences = [Sentence(sent, use_tokenizer=True) for sent in split_single(text)]
        FlairNer.fast_ontonotes_tagger.predict(sentences)

        flair_ontonotes_fast_model = {}
        categories = NERUtils.flair_ontonotes_categories
        flair_entities = []

        for sent in sentences:
            for entity in sent.get_spans('ner'):
                flair_entities.append(entity)

        entity_labels = NER.get_entity_label_lists(text, flair_entities, categories)
        flair_ontonotes_fast_model["_output"] = entity_labels
        dt_end = datetime.datetime.now()
        flair_ontonotes_fast_model["_stats"] = NER.get_statistics(dt_begin, dt_end, entity_labels.copy())
        return flair_ontonotes_fast_model

    @staticmethod
    def get_flair_entities(text):
        dt_begin = datetime.datetime.now()
        sentences = [Sentence(sent, use_tokenizer=True) for sent in split_single(text)]
        FlairNer.tagger.predict(sentences)

        flair_model = {}
        categories = NERUtils.flair_categories
        flair_entities = []

        for sent in sentences:
            for entity in sent.get_spans('ner'):
                flair_entities.append(entity)

        entity_labels = NER.get_entity_label_lists(text, flair_entities, categories)
        flair_model["_output"] = entity_labels
        dt_end = datetime.datetime.now()
        flair_model["_stats"] = NER.get_statistics(dt_begin, dt_end, entity_labels.copy())
        return flair_model

    @staticmethod
    def get_flair_ontonotes_entities(text):
        dt_begin = datetime.datetime.now()
        sentences = [Sentence(sent, use_tokenizer=True) for sent in split_single(text)]
        FlairNer.ontonotes_tagger.predict(sentences)

        flair_ontonotes_model = {}
        categories = NERUtils.flair_ontonotes_categories
        flair_entities = []

        for sent in sentences:
            for entity in sent.get_spans('ner'):
                flair_entities.append(entity)

        entity_labels = NER.get_entity_label_lists(text, flair_entities, categories)
        flair_ontonotes_model["_output"] = entity_labels
        dt_end = datetime.datetime.now()
        flair_ontonotes_model["_stats"] = NER.get_statistics(dt_begin, dt_end, entity_labels.copy())
        return flair_ontonotes_model

    @staticmethod
    def get_flair_pooled_entities(text):
        dt_begin = datetime.datetime.now()
        sentences = [Sentence(sent, use_tokenizer=True) for sent in split_single(text)]
        FlairNer.pooled_tagger.predict(sentences)

        flair_pooled_model = {}
        categories = NERUtils.flair_pooled_categories
        flair_entities = []

        for sent in sentences:
            for entity in sent.get_spans('ner'):
                flair_entities.append(entity)

        entity_labels = NER.get_entity_label_lists(text, flair_entities, categories)
        flair_pooled_model["_output"] = entity_labels
        dt_end = datetime.datetime.now()
        flair_pooled_model["_stats"] = NER.get_statistics(dt_begin, dt_end, entity_labels.copy())
        return flair_pooled_model


# ==================================================================================================
class SpacyNer:
    nlp_sm = None
    nlp_md = None
    nlp_lg = None

    @staticmethod
    def load_spacy_sm_model():
        SpacyNer.nlp_sm = spacy.load(NERUtils.nlp_sm)
        SpacyNer.nlp_sm.max_length = NERUtils.nlp_sm_len

    @staticmethod
    def load_spacy_md_model():
        SpacyNer.nlp_md = spacy.load(NERUtils.nlp_md)
        SpacyNer.nlp_md.max_length = NERUtils.nlp_md_len

    @staticmethod
    def load_spacy_lg_model():
        SpacyNer.nlp_lg = spacy.load(NERUtils.nlp_lg)
        SpacyNer.nlp_lg.max_length = NERUtils.nlp_lg_len

    @staticmethod
    def get_spacy_sm_entities(text):
        dt_begin = datetime.datetime.now()

        spacy_sm_model = {}
        doc_sm = SpacyNer.nlp_sm(text)
        categories = NERUtils.nlp_sm_categories
        entity_labels = NER.get_entity_label_lists(text, doc_sm.ents, categories)

        spacy_sm_model["_output"] = entity_labels
        dt_end = datetime.datetime.now()
        spacy_sm_model["_stats"] = NER.get_statistics(dt_begin, dt_end, entity_labels.copy())

        return spacy_sm_model

    @staticmethod
    def get_spacy_md_entities(text):
        dt_begin = datetime.datetime.now()

        spacy_md_model = {}
        doc_md = SpacyNer.nlp_md(text)
        categories = NERUtils.nlp_md_categories
        entity_labels = NER.get_entity_label_lists(text, doc_md.ents, categories)

        spacy_md_model["_output"] = entity_labels
        dt_end = datetime.datetime.now()
        spacy_md_model["_stats"] = NER.get_statistics(dt_begin, dt_end, entity_labels.copy())

        return spacy_md_model

    @staticmethod
    def get_spacy_lg_entities(text):
        dt_begin = datetime.datetime.now()

        spacy_lg_model = {}
        doc_lg = SpacyNer.nlp_lg(text)
        categories = NERUtils.nlp_lg_categories
        entity_labels = NER.get_entity_label_lists(text, doc_lg.ents, categories)

        spacy_lg_model["_output"] = entity_labels
        dt_end = datetime.datetime.now()
        spacy_lg_model["_stats"] = NER.get_statistics(dt_begin, dt_end, entity_labels.copy())

        return spacy_lg_model


# ==================================================================================================
class StanzaNer:
    snlp = None
    nlp = None


    @staticmethod
    def load_stanza_model():
        StanzaNer.snlp = stanza.Pipeline(lang="en")
        StanzaNer.nlp = StanzaLanguage(StanzaNer.snlp)
        StanzaNer.nlp.max_length = NERUtils.stanza_max_length

    @staticmethod
    def get_stanza_entities(text):
        dt_begin = datetime.datetime.now()
        stanza_model = {}
        doc = StanzaNer.snlp(text)
        categories = NERUtils.stanza_categories
        entity_labels = NER.get_entity_label_lists(text, doc.ents, categories)

        stanza_model["_output"] = entity_labels
        dt_end = datetime.datetime.now()
        stanza_model["_stats"] = NER.get_statistics(dt_begin, dt_end, entity_labels.copy())

        return stanza_model


# ==================================================================================================
class BERTNer:
    bert_model_path = None

    @staticmethod
    def load_bert_model():
        BERTNer.bert_model_path = Ner(NERUtils.bert_path)

    @staticmethod
    def get_continuous_chunks_bert(tagged_sent):
        continuous_chunk = []
        current_chunk = []

        for sent in tagged_sent:
            if sent['tag'] != "O":
                current_chunk.append((sent['word'], sent['tag'][2:]))
            else:
                if current_chunk:  # if the current chunk is not empty
                    continuous_chunk.append(current_chunk)
                    current_chunk = []
        # Flush the final current_chunk into the continuous_chunk, if any.
        if current_chunk:
            continuous_chunk.append(current_chunk)
        return continuous_chunk

    @staticmethod
    def get_bert_entities(text, index):
        dt_begin = datetime.datetime.now()
        bert_model = {}
        final_output = BERTNer.get_entity_by_punctuation(text, index)
        final_output = BERTNer.get_continuous_chunks_bert(final_output)
        categories = NERUtils.bert_categories
        entity_labels = NER.get_entity_label_lists(text, final_output, categories)
        bert_model["_output"] = entity_labels
        dt_end = datetime.datetime.now()
        bert_model["_stats"] = NER.get_statistics(dt_begin, dt_end, entity_labels.copy())

        return bert_model

    @staticmethod
    def get_entity_by_punctuation(text, index):
        final_output = []
        if (index != 4):
            sentences = text.split(NERUtils.punctuation_marks[index])

            for sentence in sentences:
                if (len(sentence) < NERUtils.bert_max_length):
                    final_output.extend(BERTNer.bert_model_path.predict(sentence))
                else:
                    output = BERTNer.get_entity_by_punctuation(sentence, index + 1)
                    final_output.extend(output)
        return final_output


# ==================================================================================================
class NLTKNer:

    @staticmethod
    def get_nltk_entities(text):
        dt_begin = datetime.datetime.now()
        nltk_model = {}

        entities_nltk = {}
        for category in NERUtils.nltk_categories:
            offset = 0
            for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(text))):
                if hasattr(chunk, 'label'):
                    if chunk.label() == category:

                        entity_text = ' '.join(c[0] for c in chunk)
                        offset = text.find(entity_text, offset)
                        item = {}
                        item["entity"] = entity_text
                        item["start_char"] = offset
                        item["end_char"] = offset + len(entity_text)
                        if (NERUtils.sentence_include == 1):
                            item["sentence"] = NER.get_context_sentence(offset, text)
                        offset += len(entity_text)

                        try:
                            entities_nltk[category].append(item)
                        except:
                            # entities_nltk[category] = [' '.join(c[0] for c in chunk)]
                            entities_nltk[category] = [item]

        nltk_model["_output"] = entities_nltk
        dt_end = datetime.datetime.now()
        nltk_model["_stats"] = NER.get_statistics(dt_begin, dt_end, entities_nltk.copy())

        return nltk_model


# ==================================================================================================
class StanfordNer:
    st_3class = None
    st_4class = None
    st_7class = None

    @staticmethod
    def load_stanford_class3_model():
        StanfordNer.st_3class = StanfordNERTagger(NERUtils.stanford_class3, NERUtils.stanford_ner_path,encoding='utf8')
    @staticmethod
    def load_stanford_class4_model():
        StanfordNer.st_4class = StanfordNERTagger(NERUtils.stanford_class4 , NERUtils.stanford_ner_path,
                                      encoding='utf8')

    @staticmethod
    def load_stanford_class7_model():
        StanfordNer.st_7class = StanfordNERTagger(NERUtils.stanford_class7, NERUtils.stanford_ner_path,
                                      encoding='utf8')



    @staticmethod
    def get_continuous_chunks(tagged_sent):
        continuous_chunk = []
        current_chunk = []

        for token, tag in tagged_sent:
            if tag != "O":
                current_chunk.append((token, tag))
            else:
                if current_chunk:  # if the current chunk is not empty
                    continuous_chunk.append(current_chunk)
                    current_chunk = []
        # Flush the final current_chunk into the continuous_chunk, if any.
        if current_chunk:
            continuous_chunk.append(current_chunk)
        return continuous_chunk

    @staticmethod
    def get_class3_entities(text):
        dt_begin = datetime.datetime.now()
        stanford_class3_model = {}

        tagged_sent_class3 = StanfordNer.st_3class.tag(text.split())

        named_entities_class3 = StanfordNer.get_continuous_chunks(tagged_sent_class3)

        entity_labels = NER.get_entity_label_lists(text, named_entities_class3, NERUtils.stanford_class3_categories)
        stanford_class3_model["_output"] = entity_labels

        dt_end = datetime.datetime.now()
        stanford_class3_model["_stats"] = NER.get_statistics(dt_begin, dt_end, entity_labels.copy())

        return stanford_class3_model

    @staticmethod
    def get_class4_entities(text):
        dt_begin = datetime.datetime.now()
        stanford_class4_model = {}

        tagged_sent_class4 = StanfordNer.st_4class.tag(text.split())
        named_entities_class4 = StanfordNer.get_continuous_chunks(tagged_sent_class4)

        entity_labels = NER.get_entity_label_lists(text, named_entities_class4, NERUtils.stanford_class4_categories)
        stanford_class4_model["_output"] = entity_labels

        dt_end = datetime.datetime.now()
        stanford_class4_model["_stats"] = NER.get_statistics(dt_begin, dt_end, entity_labels.copy())

        return stanford_class4_model

    @staticmethod
    def get_class7_entities(text):
        dt_begin = datetime.datetime.now()
        stanford_class7_model = {}

        tagged_sent_class7 = StanfordNer.st_7class.tag(text.split())
        named_entities_class7 = StanfordNer.get_continuous_chunks(tagged_sent_class7)

        entity_labels = NER.get_entity_label_lists(text, named_entities_class7, NERUtils.stanford_class7_categories)

        stanford_class7_model["_output"] = entity_labels
        dt_end = datetime.datetime.now()
        stanford_class7_model["_stats"] = NER.get_statistics(dt_begin, dt_end, entity_labels.copy())

        return stanford_class7_model


# ==================================================================================================
class NER:

    @staticmethod
    def csv_preprocess(file):
        text = file["Specific-Metadata"]["text-analysis"]["clean-text"]
        text = re.sub(r"[-()<=>~`|{}@#?!&$]+\ *", " ", text)
        text = text.replace("\n", ",")
        RE_BAD_CHARS = regex.compile(r"\p{Cc}|\p{Cs}")
        text = RE_BAD_CHARS.sub("", text)
        all_text = text.split(",")
        return all_text

    @staticmethod
    def preprocess_text(text):
        text = text.replace("\n", " ").replace("\\r\\n", " ").replace("\r", " ")
        text = re.sub(r"[-()<=>~`|{}@#?!&$]+\ *", " ", text)
        text = text.replace("[", "")
        text = text.replace("]", "")
        RE_BAD_CHARS = regex.compile(r"\p{Cc}|\p{Cs}")
        text = RE_BAD_CHARS.sub("", text)
        text = ' '.join(text.split())
        return text

    @staticmethod
    def get_statistics(dt_begin, dt_end, entity_list):
        _stats = {}
        _stats["start-timestamp"] = dt_begin.strftime(NERUtils.datetime2string_format)
        _stats["end-timestamp"] = dt_end.strftime(NERUtils.datetime2string_format)
        _stats["duration"] = (dt_end - dt_begin).total_seconds()
        for item in entity_list:
            entity_list[item] = len(entity_list[item])
        _stats["number-of-entities"] = entity_list
        return _stats

    @staticmethod
    def get_context_sentence(start_char, text):
        total_length = 0
        sentences = text.split(".")
        for sentence in sentences:
            total_length = len(sentence) + total_length + 1  # 1 to add the length of a period in a sentence
            if start_char < total_length:
                return sentence

    @staticmethod
    def get_entity_label_lists(text, doc, categories):
        entity_labels = {}
        for category in categories:
            offset = 0
            for entity in doc:
                if hasattr(entity, 'label_'):
                    if category == entity.label_:
                        item = {}
                        item["entity"] = entity.text
                        item["start_index"] = entity.start_char
                        item["end_index"] = entity.end_char
                        if (NERUtils.sentence_include == 1):
                            item["sentence"] = NER.get_context_sentence(entity.start_char, text)
                        try:
                            entity_labels[category].append(item)
                        except:
                            entity_labels[category] = [item]
                elif hasattr(entity, 'tag'):
                    if category == entity.tag:
                        item = {}
                        item["entity"] = entity.text
                        item["start_index"] = entity.start_pos
                        item["end_index"] = entity.end_pos
                        if (NERUtils.sentence_include == 1):
                            item["sentence"] = NER.get_context_sentence(entity.start_pos, text)
                        try:
                            entity_labels[category].append(item)
                        except:
                            entity_labels[category] = [item]

                elif hasattr(entity, 'type'):
                    if category == entity.type:
                        item = {}
                        item["entity"] = entity.text
                        item["start_index"] = entity.start_char
                        item["end_index"] = entity.end_char
                        if (NERUtils.sentence_include == 1):
                            item["sentence"] = NER.get_context_sentence(entity.start_char, text)
                        try:
                            entity_labels[category].append(item)
                        except:
                            entity_labels[category] = [item]
                else:
                    if category == entity[0][1]:
                        entity_text = " ".join([token for token, tag in entity])
                        offset = text.find(entity_text, offset)
                        item = {}
                        item["entity"] = entity_text
                        item["start_index"] = offset
                        item["end_index"] = offset + len(entity_text)
                        if (NERUtils.sentence_include == 1):
                            item["sentence"] = NER.get_context_sentence(offset, text)
                        offset += len(entity_text)
                        try:
                            entity_labels[category].append(item)
                        except:
                            entity_labels[category] = [item]
        return entity_labels

    @staticmethod
    def get_text_values(file):
        text = file["Specific-Metadata"]["text-analysis"]["clean-text"]
        text = NER.preprocess_text(text)
        return text

    @staticmethod
    def get_attachment_texts(file):
        attachment_texts = []
        if 'attachments' in file["Specific-Metadata"]:
            for attachment in file["Specific-Metadata"]["attachments"]:
                attachment_obj = {}
                attachment_obj["filename"] = file["Specific-Metadata"]["attachments"][attachment]["filename"]
                if (('Specific-Metadata'  in file["Specific-Metadata"]["attachments"][attachment]["metadata"]) and\
                    ('text-analysis'      in file["Specific-Metadata"]["attachments"][attachment]["metadata"]["Specific-Metadata"])):
                    attachment_text = \
                        file["Specific-Metadata"]["attachments"][attachment]["metadata"]\
                            ["Specific-Metadata"]["text-analysis"]["clean-text"]
                    attachment_text = NER.preprocess_text(attachment_text)
                    attachment_obj["text"] = attachment_text
                    attachment_texts.append(attachment_obj)
        return attachment_texts

    @staticmethod
    def time_details_for_csv(doc1, ner_object):
        start_time_in_doc1 = doc1["_stats"]["start-timestamp"]
        end_time_in_doc1 = doc1["_stats"]["end-timestamp"]
        start_time_in_ner = ner_object["_stats"]["start-timestamp"]
        end_time_in_ner = ner_object["_stats"]["end-timestamp"]

        start_doc1 = datetime.datetime.strptime(start_time_in_doc1, NERUtils.datetime2string_format)
        end_doc1 = datetime.datetime.strptime(end_time_in_doc1, NERUtils.datetime2string_format)
        start_ner = datetime.datetime.strptime(start_time_in_ner, NERUtils.datetime2string_format)
        end_ner = datetime.datetime.strptime(end_time_in_ner, NERUtils.datetime2string_format)

        times = [start_doc1, end_doc1, start_ner, end_ner]
        start_time = min(times).strftime(NERUtils.datetime2string_format)
        end_time = max(times).strftime(NERUtils.datetime2string_format)
        duration = (max(times) - min(times)).total_seconds()
        return start_time, end_time, duration

    @staticmethod
    def get_csv_ner_from_models(all_text, doc, models):
        # print(f"* models={models}")
        # print(f"* all_text={all_text}")

        doc1 = doc.copy()
        for model in models:
            doc1[model] = {}
            doc1[model]["_output"] = {}
            doc1[model]["_stats"] = {}

        for text in all_text:
            ner_object = NER.get_ner_from_models(text, doc, models)

            for model in models:
                categories = NERUtils._config[model]["categories"]

                for category in categories:
                    if category in ner_object[model]["_output"]:
                        if category in doc1[model]["_output"]:
                            for i in ner_object[model]["_output"][category]:
                                doc1[model]["_output"][category].append(i)

                                if "start-timestamp" in doc1[model]["_stats"]:
                                    doc1[model]["_stats"]["start-timestamp"], doc1[model]["_stats"]["end-timestamp"], \
                                    doc1[model]["_stats"]["duration"] = NER.time_details_for_csv(doc1[model],
                                                                                                 ner_object[model])
                                else:
                                    doc1[model]["_stats"]["start-timestamp"] = ner_object[model]["_stats"][
                                        "start-timestamp"]
                                    doc1[model]["_stats"]["end-timestamp"] = ner_object[model]["_stats"]["end-timestamp"]
                                    doc1[model]["_stats"]["duration"] = ner_object[model]["_stats"]["duration"]

                        else:
                            for i in ner_object[model]["_output"][category]:
                                try:
                                    doc1[model]["_output"][category].append(i)
                                except:
                                    doc1[model]["_output"][category] = [ner_object[model]["_output"][category][0]]

                                if "start-timestamp" in doc1[model]["_stats"]:
                                    doc1[model]["_stats"]["start-timestamp"], doc1[model]["_stats"]["end-timestamp"], \
                                    doc1[model]["_stats"]["duration"] = NER.time_details_for_csv(doc1[model],
                                                                                                 ner_object[model])
                                else:
                                    doc1[model]["_stats"]["start-timestamp"] = ner_object[model]["_stats"][
                                        "start-timestamp"]
                                    doc1[model]["_stats"]["end-timestamp"] = ner_object[model]["_stats"]["end-timestamp"]
                                    doc1[model]["_stats"]["duration"] = ner_object[model]["_stats"]["duration"]

        for model in models:
            entity_list = doc1[model]["_output"].copy()
            for item in entity_list:
                entity_list[item] = len(entity_list[item])

            doc1[model]["_stats"]["number-of-entities"] = entity_list

        return doc1


    @staticmethod
    def get_ner_from_models(text, doc, models):
        if len(text) == 0 :
            return doc
        if NERUtils.stanford_class7_name in models:
            doc[NERUtils.stanford_class7_name] = StanfordNer.get_class7_entities(text)
        if NERUtils.stanford_class4_name in models:
            doc[NERUtils.stanford_class4_name] = StanfordNer.get_class4_entities(text)
        if NERUtils.stanford_class3_name in models:
            doc[NERUtils.stanford_class3_name] = StanfordNer.get_class3_entities(text)
        if NERUtils.stanza_name in models:
            doc[NERUtils.stanza_name] = StanzaNer.get_stanza_entities(text)
        if NERUtils.spacy_sm_name in models:
            doc[NERUtils.spacy_sm_name] = SpacyNer.get_spacy_sm_entities(text)
        if NERUtils.spacy_md_name in models:
            doc[NERUtils.spacy_md_name] = SpacyNer.get_spacy_md_entities(text)
        if NERUtils.spacy_lg_name in models:
            doc[NERUtils.spacy_lg_name] = SpacyNer.get_spacy_lg_entities(text)
        if NERUtils.nltk_name in models:
            doc[NERUtils.nltk_name] = NLTKNer.get_nltk_entities(text)
        if NERUtils.bert_name in models:
            doc[NERUtils.bert_name] = BERTNer.get_bert_entities(text, 0)
        if NERUtils.flair_name in models:
            doc[NERUtils.flair_name] = FlairNer.get_flair_entities(text)
        if NERUtils.flair_ontonotes_name in models:
            doc[NERUtils.flair_ontonotes_name] = FlairNer.get_flair_ontonotes_entities(text)
        if NERUtils.flair_fast_name in models:
            doc[NERUtils.flair_fast_name] = FlairNer.get_flair_fast_entities(text)
        if NERUtils.flair_fast_ontonotes_name in models:
            doc[NERUtils.flair_fast_ontonotes_name] = FlairNer.get_flair_ontonotes_fast_entities(text)
        if NERUtils.flair_pooled_name in models:
            doc[NERUtils.flair_pooled_name] = FlairNer.get_flair_pooled_entities(text)
        if NERUtils.deeppavlov_onto_name in models:
            doc[NERUtils.deeppavlov_onto_name] = Deeppavlov.get_deeppavlov_onto_entities(text)
        if NERUtils.deeppavlov_onto_bert_name in models:
            doc[NERUtils.deeppavlov_onto_bert_name] = Deeppavlov.get_deeppavlov_ontobert_entities(text)
        if NERUtils.deeppavlov_conll2003_name in models:
            doc[NERUtils.deeppavlov_conll2003_name] = Deeppavlov.get_deeppavlov_conll2003_entities(text)
        if NERUtils.deeppavlov_conll2003_bert_name in models:
            doc[NERUtils.deeppavlov_conll2003_bert_name] = Deeppavlov.get_deeppavlov_conll2003_bert_entities(text)
        if NERUtils.allennlp_ner_name in models:
            doc[NERUtils.allennlp_ner_name] = AllennlpNer.get_allennlp_ner(text)
        if NERUtils.allennlp_finegrained_ner_name in models:
            doc[NERUtils.allennlp_finegrained_ner_name] = AllennlpNer.get_allennlp_fine_grained_ner(text)
        if NERUtils.polyglot_name in models:
            doc[NERUtils.polyglot_name] = Polyglot.get_polyglot_entities(text)
        return doc


    @staticmethod
    def load_models(models):
        if NERUtils.stanford_class7_name in models:
            StanfordNer.load_stanford_class7_model()
        if NERUtils.stanford_class4_name in models:
            StanfordNer.load_stanford_class4_model()
        if NERUtils.stanford_class3_name in models:
           StanfordNer.load_stanford_class3_model()
        if NERUtils.stanza_name in models:
            StanzaNer.load_stanza_model()
        if NERUtils.spacy_sm_name in models:
            SpacyNer.load_spacy_sm_model()
        if NERUtils.spacy_md_name in models:
            SpacyNer.load_spacy_md_model()
        if NERUtils.spacy_lg_name in models:
            SpacyNer.load_spacy_lg_model()
        if NERUtils.nltk_name in models:
            pass
        if NERUtils.bert_name in models:
            BERTNer.load_bert_model()
        if NERUtils.flair_name in models:
            FlairNer.load_flair_model()
        if NERUtils.flair_ontonotes_name in models:
            FlairNer.load_flair_ontonotes_model()
        if NERUtils.flair_fast_name in models:
            FlairNer.load_flair_fast_model()
        if NERUtils.flair_fast_ontonotes_name in models:
            FlairNer.load_flair_ontonotes_fast_model()
        if NERUtils.flair_pooled_name in models:
            FlairNer.load_flair_pooled_model()
        if NERUtils.deeppavlov_onto_name in models:
            Deeppavlov.load_onto_model()
        if NERUtils.deeppavlov_onto_bert_name in models:
            Deeppavlov.load_onto_bert_model()
        if NERUtils.deeppavlov_conll2003_name in models:
            Deeppavlov.load_conll_model()
        if NERUtils.deeppavlov_conll2003_bert_name in models:
            Deeppavlov.load_conll_bert_model()
        if NERUtils.allennlp_ner_name in models:
            AllennlpNer.load_ner_model()
        if NERUtils.allennlp_finegrained_ner_name in models:
            AllennlpNer.load_finegrained_ner_model()
        if NERUtils.polyglot_name in models:
            pass


    @staticmethod
    def ner_for_all_files(r, models):
        outputs = []
        n = 0
        for file in r["docs"]:
            NLP_NER = {}
            n += 1
            if ('text-analysis' in file["Specific-Metadata"]):
                doc_0 = {}
                doc_0["filename"] = file["General-Metadata"]["FILENAME"]
                if (file["General-Metadata"]["EXTENSION"] == "csv"): # only CSV | doesn't apply to XLSX
                    text = NER.csv_preprocess(file)
                    NLP_NER["doc-0"] = NER.get_csv_ner_from_models(text, doc_0, models)
                else:
                    text = NER.get_text_values(file)
                    NLP_NER["doc-0"] = NER.get_ner_from_models(text, doc_0, models)

                if (file["General-Metadata"]["EXTENSION"] == "msg"):

                    attachment_texts = NER.get_attachment_texts(file)
                    for i in range(len(attachment_texts)):
                        attachment = {}
                        attachment["filename"] = attachment_texts[i]["filename"]
                        attachment_text = attachment_texts[i]["text"]
                        NLP_NER[f"doc-{i + 1}"] = NER.get_ner_from_models(attachment_text, attachment,
                                                                          models)

                elif (file["General-Metadata"]["EXTENSION"] == "zip"):
                    print()
                    attachment_texts = NER.get_attachement_texts(file)
                    for i in range(len(attachment_texts)):
                        attachment = {}
                        NLP_NER[f"doc-{i + 1}"] = NER.get_ner_from_models(attachment_texts[i], attachment, models)

            outputs.append(NLP_NER)
            NERUtils.garbage_collector()

        return outputs

    @staticmethod
    def spacy_model_ensemble(text):
        nlp_sm = spacy.load(NERUtils.nlp_sm)
        nlp_sm.max_length = NERUtils.nlp_sm_len
        doc_sm = nlp_sm(text)
        categories_sm = NERUtils.nlp_sm_categories
        entity_labels_sm = NER.get_entity_label_lists(doc_sm.ents, categories_sm)

        nlp_md = spacy.load(NERUtils.nlp_md)
        nlp_md.max_length = NERUtils.nlp_md_len
        doc_md = nlp_md(text)
        categories_md = NERUtils.nlp_md_categories
        entity_labels_md = NER.get_entity_label_lists(doc_md.ents, categories_md)

        results = {}
        for category in entity_labels_sm:
            print(category)
            if category in entity_labels_md.keys():
                for item in entity_labels_sm[category]:
                    if item in entity_labels_md[category]:
                        try:
                            results[category].append(item)
                        except:
                            results[category] = [item]

        print(entity_labels_sm)
        print(entity_labels_md)
        print(results)

    @staticmethod
    def spacy_stanza_model_ensemble(text):

        nlp_md = spacy.load(NERUtils.nlp_md)
        nlp_md.max_length = NERUtils.nlp_md_len

        doc_md = nlp_md(text)
        categories_md = NERUtils.nlp_md_categories
        entity_labels_md = NER.get_entity_label_lists(doc_md.ents, categories_md)

        snlp = stanza.Pipeline(lang="en")
        nlp = StanzaLanguage(snlp)
        nlp.max_length = NERUtils.stanza_max_length

        doc = StanzaNer.snlp(text)
        categories = NERUtils.stanza_categories
        entity_labels_stanza = NER.get_entity_label_lists(doc.ents, categories)

        results = {}
        for category in entity_labels_stanza:
            if category in entity_labels_md.keys():
                for item in entity_labels_stanza[category]:
                    if item in entity_labels_md[category]:
                        try:
                            results[category].append(item)
                        except:
                            results[category] = [item]
