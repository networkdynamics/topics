"""
A simple topic modelling tool. Its workflow is as follows:
	* Create documents (e.g. :py:module:TextDocument)
	* Collect the documents into a :py:module:Corpus
	* Perform topic learning on the corpus using an approriate algorithm (thus
	obtaining a :py:module:TopicModel).
"""

from text_document import TextDocument
from corpus import Corpus
from topic_model import TopicModel
from gibbs_lda import gibbs_lda_learn
