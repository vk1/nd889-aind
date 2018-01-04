import warnings
from asl_data import SinglesData


def recognize(models: dict, test_set: SinglesData):
    """ Recognize test word sequences from word models set

   :param models: dict of trained models
       {'SOMEWORD': GaussianHMM model object, 'SOMEOTHERWORD': GaussianHMM model object, ...}
   :param test_set: SinglesData object
   :return: (list, list)  as probabilities, guesses
       both lists are ordered by the test set word_id
       probabilities is a list of dictionaries where each key a word and value is Log Likelihood
           [{SOMEWORD': LogLvalue, 'SOMEOTHERWORD' LogLvalue, ... },
            {SOMEWORD': LogLvalue, 'SOMEOTHERWORD' LogLvalue, ... },
            ]
       guesses is a list of the best guess words ordered by the test set word_id
           ['WORDGUESS0', 'WORDGUESS1', 'WORDGUESS2',...]
   """
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    probabilities = []
    guesses = []
    # DONE implement the recognizer

    for item_idx in range(test_set.num_items):
        LogLvalues = {}
        best_score = float('-inf')
        best_word = None

        X, lengths = test_set.get_item_Xlengths(item_idx)

        for word, model in models.items():
            try:
                LogLvalues[word] = model.score(X, lengths)

                if LogLvalues[word] > best_score:
                    best_score = LogLvalues[word]
                    best_word = word

            except:
                LogLvalues[word] = float('-inf')

        probabilities.append(LogLvalues)
        guesses.append(best_word)

    return probabilities, guesses