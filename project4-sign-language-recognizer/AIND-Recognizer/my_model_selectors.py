import math
import statistics
import warnings

import numpy as np
from hmmlearn.hmm import GaussianHMM
from sklearn.model_selection import KFold
from asl_utils import combine_sequences


class ModelSelector(object):
    '''
    base class for model selection (strategy design pattern)
    '''

    def __init__(self, all_word_sequences: dict, all_word_Xlengths: dict, this_word: str,
                 n_constant=3,
                 min_n_components=2, max_n_components=10,
                 random_state=14, verbose=False):
        self.words = all_word_sequences
        self.hwords = all_word_Xlengths
        self.sequences = all_word_sequences[this_word]
        self.X, self.lengths = all_word_Xlengths[this_word]
        self.this_word = this_word
        self.n_constant = n_constant
        self.min_n_components = min_n_components
        self.max_n_components = max_n_components
        self.random_state = random_state
        self.verbose = verbose

    def select(self):
        raise NotImplementedError

    def base_model(self, num_states):
        # with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        # warnings.filterwarnings("ignore", category=RuntimeWarning)
        try:
            hmm_model = GaussianHMM(n_components=num_states, covariance_type="diag", n_iter=1000,
                                    random_state=self.random_state, verbose=False).fit(self.X, self.lengths)
            if self.verbose:
                print("model created for {} with {} states".format(self.this_word, num_states))
            return hmm_model
        except:
            if self.verbose:
                print("failure on {} with {} states".format(self.this_word, num_states))
            return None


class SelectorConstant(ModelSelector):
    """ select the model with value self.n_constant

    """

    def select(self):
        """ select based on n_constant value

        :return: GaussianHMM object
        """
        best_num_components = self.n_constant
        return self.base_model(best_num_components)


class SelectorBIC(ModelSelector):
    """ select the model with the lowest Bayesian Information Criterion(BIC) score

    http://www2.imm.dtu.dk/courses/02433/doc/ch6_slides.pdf
    Bayesian information criteria: BIC = -2 * logL + p * logN
    """

    def select(self):
        """ select the best model for self.this_word based on
        BIC score for n between self.min_n_components and self.max_n_components

        :return: GaussianHMM object
        """
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        # DONE implement model selection based on BIC scores

        n_components = range(self.min_n_components, self.max_n_components + 1)

        scores_all = []

        for n_component in n_components:
            try:
                current_model = self.base_model(n_component)
                logL = current_model.score(self.X, self.lengths)
                p = n_component*(n_component-1) + 2*n_component*current_model.n_features
                logN = np.log(n_component)
                score = -2*logL + p*logN
                scores_all.append(score)

            except:
                pass

        if scores_all:
            best_n_component = max(zip(n_components, scores_all), key=lambda x: x[1])[0]
            return self.base_model(best_n_component)
        else:
            return self.base_model(self.n_constant)

class SelectorDIC(ModelSelector):
    ''' select best model based on Discriminative Information Criterion

    Biem, Alain. "A model selection criterion for classification: Application to hmm topology optimization."
    Document Analysis and Recognition, 2003. Proceedings. Seventh International Conference on. IEEE, 2003.
    http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.58.6208&rep=rep1&type=pdf
    https://pdfs.semanticscholar.org/ed3d/7c4a5f607201f3848d4c02dd9ba17c791fc2.pdf
    DIC = log(P(X(i)) - 1/(M-1)SUM(log(P(X(all but i))
    '''

    def select(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        # DONE implement model selection based on DIC scores

        n_components = range(self.min_n_components, self.max_n_components + 1)
        scores_all = []

        for n_component in n_components:
            try:
                current_model = self.base_model(n_component)
                X, lengths = self.hwords[self.this_word]
                logL_all = current_model.score(X, lengths)

            except:
                continue

            antiLogL = 0
            M = 0
            for word in self.hwords:
                if word != self.this_word:
                    try:
                        X, lengths = self.hwords[word]
                        antiLogL += current_model.score(X, lengths)
                        M += 1

                    except:
                        continue

            scores_all.append(logL_all - 1/(M-1) * antiLogL)

        if scores_all:
            best_n_component = max(zip(n_components, scores_all), key=lambda x: x[1])[0]
            return self.base_model(best_n_component)
        else:
            return self.base_model(self.n_constant)

class SelectorCV(ModelSelector):
    ''' select best model based on average log Likelihood of cross-validation folds

    '''

    def select(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        # DONE implement model selection using CV

        split_method = KFold()

        scores_mean_all = []

        n_components = range(self.min_n_components, self.max_n_components + 1)

        for n_component in n_components:
            try:

                scores_model = []
                score_mean_model = None

                for cv_train_idx, cv_test_idx in split_method.split(self.sequences):
                    X_test, X_lengths = combine_sequences(cv_test_idx, self.sequences)

                    scores_model.append(self.base_model(n_component).score(X_test, X_lengths))

                    score_mean_model = np.mean(scores_model)

                if score_mean_model:
                    scores_mean_all.append(score_mean_model)

            except:
                pass

        if scores_mean_all:
            best_n_component = max(zip(n_components, scores_mean_all), key=lambda x: x[1])[0]
            return self.base_model(best_n_component)
        else:
            return self.base_model(self.n_constant)