import re

import nltk
from config import Config
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tag import PerceptronTagger
from nltk.tree import Tree
from util.constants import STOP_WORDS

if Config.args.download:
    nltk.download("averaged_perceptron_tagger")


class Grammar:
    NOUN_PHRASE = r"""
    NBAR:
        {<NN.*|JJ.*>*<NN.*>}  # Nouns and Adjectives, terminated with Nouns
    NP:
        {<NBAR><CC|IN><NBAR>}  # Above, connected with in/of/etc...
        {<JJ.*>*<CC|IN><NBAR>}
        {<NBAR>}
    """

    PROPER_NOUN_PHRASE = r"""
    NP:
        {<NNP>+<CC|IN><NNP>+}
        {(U\.S\.A\.)<CC|IN><NNP>+}
        {<NNP>+<CC|IN>(U\.S\.A\.)}
        {<NNP>+}
        {(U\.S\.A\.)}
    """


class PhraseExtractor:
    tagger = PerceptronTagger()

    @staticmethod
    def get_terms(tree: Tree) -> list[list[str]]:
        """
        Gets all the terms of the tree after normalization and filtering.
        The outer list contains the block of texts, and the inner lists
        contain all of the filtered and normalized terms.
        """
        phrase_blocks: list[list[str]] = []

        for leaves in PhraseExtractor.filtered_leaves(tree):
            terms = [word for (word, grammar_type) in leaves if PhraseExtractor.acceptable_word(word)]
            phrase_blocks.append(terms)

        return phrase_blocks

    @staticmethod
    def filtered_leaves(
        tree: Tree,
        target_subtree_labels: set[str] = {'NP', 'JJ', 'RB', 'IN', 'CC'},
    ) -> list[list[tuple[str, str]]]:
        """
        Returns lists of leaf nodes lists of a chunk tree that are part
        of the given subtree labels. Each list at the top level
        represents a block of text. The inner lists contain tuples of
        the terms and grammar types of each word in the block of text.
        """
        leaves: list[list[tuple[str, str]]] = []

        for subtree in tree.subtrees(filter=lambda tree: tree.label() in target_subtree_labels):
            if isinstance(subtree, Tree):
                leaves.append(subtree.leaves())

        return leaves

    @staticmethod
    def flatten_phrase_lists(phrase_tokens: list[list[str]]) -> list[str]:
        """
        Flattens a list of phrase lists into a list of phrase strings.
        """
        flattened_phrases: list[str] = []
        for phrase in phrase_tokens:
            token = ' '.join(phrase)
            flattened_phrases.append(token.rstrip())

        return flattened_phrases

    @staticmethod
    def normalize(word: str, lemmatizer=WordNetLemmatizer(), stemmer=PorterStemmer()) -> str:
        """Normalises words to lowercase and stems and lemmatizes it."""
        word = word.lower()
        word = stemmer.stem(word)
        word = lemmatizer.lemmatize(word)
        return word

    @staticmethod
    def acceptable_word(word: str, stop_words: set[str] = STOP_WORDS) -> bool:
        """
        Checks conditions for acceptable word.
        """
        word_has_valid_length = 1 <= len(word) <= 40
        # is_stop_word = word.lower() in stop_words

        # accepted = word_has_valid_length and not is_stop_word
        accepted = word_has_valid_length
        return accepted

    @staticmethod
    def extract_phrases(text: str, grammar: str) -> list[str]:
        if not text:
            return []

        chunked_words = PhraseExtractor.get_chunked_words(text, grammar)

        if not chunked_words:
            return []

        terms = PhraseExtractor.get_terms(chunked_words)
        flattened_phrase_lists = PhraseExtractor.flatten_phrase_lists(terms)

        return flattened_phrase_lists

    @staticmethod
    def get_chunked_words(text: str, grammar: str) -> Tree:
        tag = PhraseExtractor.tagger.tag
        chunker = nltk.RegexpParser(grammar)

        words = re.findall(r'\w+', text)
        if not words:
            return None

        tagged_words = tag(words)
        chunked_words: Tree = chunker.parse(tagged_words)

        return chunked_words
