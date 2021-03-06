from corpus import Corpus
from topics_exceptions import ParseException

import numpy as np
cimport numpy as np

import re
import random

cdef class TopicModel:
	"""
	A topic model for a particular corpus. This class should not be instantiated
	directly, but rather obtained through a topic modelling algorithm. Various
	methods are available to query the model on the topics assigned. When a
	method takes a document index, it is the same as the index of this document
	in the corpus associated to this model.

	TODO: revise for readability

	TODO: Highlight serialization ability
	"""

	def __init__(self, corpus, num_topics, a, b, **kwargs):

		self._corpus = corpus
		self.num_topics = num_topics
		self.alpha = a
		self.beta = b

		# A[i][j] is the topic assigned to the jth word of the ith document
		self._topic_distributions = []
		for doc in corpus:
			self._topic_distributions.append([0 for i in range(len(doc))])

		# A[i,j] is the number of tokens with topic j in the ith document
		self._topic_counts_by_doc = np.zeros((len(corpus), num_topics), dtype=np.int_)

		# A[i,j] is the number of tokens with topic j and type i across the corpus
		self._topic_counts_by_type = np.zeros((corpus.count_types(), num_topics), dtype=np.int_)

		# A[i] is the number of tokens with ith topic
		self._topic_counts = np.zeros(num_topics, dtype=np.int_)

		if kwargs.pop("bypass_init", False):
			return

		# TODO: Check for extra kw args

		for didx, doc in enumerate(corpus):
			self._topic_counts_by_doc[didx, 0] += len(doc)
			self._topic_counts[0] += len(doc)

			for tok_idx, tok in enumerate(doc):
				tpe = corpus.get_type_idx_in_doc(didx, tok_idx)
				self._topic_counts_by_type[tpe, 0] += 1

	# ============== Model-building methods ==============

	@staticmethod
	def load(fobj):
		"""
		TODO: Document
		"""
		corpus = Corpus.load(fobj)
		
		# TODO remove duplication around here
		ln = fobj.readline().rstrip()
		mobj = re.match(r"num_topics: (\d+)", ln)
		if mobj is None:
			raise ParseException, "Load model: missing number of topics"
		num_topics = int(mobj.group(1))

		ln = fobj.readline().rstrip()
		mobj = re.match(r"alpha: (\d+)", ln)
		if mobj is None:
			raise ParseException, "Load model: missing alpha parameter"
		alpha = float(mobj.group(1))

		ln = fobj.readline().rstrip()
		mobj = re.match(r"beta: (\d+)", ln)
		if mobj is None:
			raise ParseException, "Load model: missing beta parameter"
		beta = float(mobj.group(1))

		model = TopicModel(corpus, num_topics, alpha, beta, bypass_init=True)

		ln = fobj.readline().rstrip()
		if ln != "topic_distribution:":
			raise ParseException, "Load model: missing topic distribution"

		for i in range(len(corpus)):
			topics = fobj.readline().rstrip().split(" ")
			for tok_idx, topic in enumerate(topics):
				if len(topic) == 0:
					continue
				top_idx = int(topic)
				type_idx = corpus.get_type_idx_in_doc(i, tok_idx)

				model._topic_distributions[i][tok_idx] = top_idx
				model.add_to_counts(1, top_idx, i, type_idx)

		return model

	cpdef save(TopicModel self, fobj):
		"""
		TODO: Document this
		"""
		self._corpus.save(fobj)
		fobj.write("num_topics: %d\n" % self.num_topics)
		fobj.write("alpha: %d\n" % self.alpha)
		fobj.write("beta: %d\n" % self.beta)
		fobj.write("topic_distribution:\n")
		for doc_line in self._topic_distributions:
			for topic in doc_line:
				fobj.write("%d " % topic)
			fobj.write("\n")

	cpdef random_topics(TopicModel self, bool use_labels):
		for i in range(len(self._topic_distributions)):
			doc_topics = self._topic_distributions[i]
			for j in range(len(doc_topics)):
				# Update the topic assignment

				if use_labels:
					doc = self._corpus.document(i)
					x = random.randrange(doc.count_labels())
					for i, lbl in enumerate(doc.iterlabels()):
						if i == x:
							new_topic = self._corpus.get_label_idx(lbl)
							break
				else:
					new_topic = random.randrange(self.num_topics)
				old_topic = doc_topics[j]
				doc_topics[j] = new_topic

				# Update the count by document
				self._topic_counts_by_doc[i, new_topic] += 1
				self._topic_counts_by_doc[i, old_topic] -= 1

				# Update the global count
				self._topic_counts[new_topic] += 1
				self._topic_counts[old_topic] -= 1

				# Update the count by type
				tpe = self._corpus.get_type_idx_in_doc(i, j)
				self._topic_counts_by_type[tpe, new_topic] += 1
				self._topic_counts_by_type[tpe, old_topic] -= 1

	cpdef set_topic(TopicModel self, int doc_idx, int word_idx, int topic, update_counts=True):
		old_topic = self._topic_distributions[doc_idx][word_idx]
		self._topic_distributions[doc_idx][word_idx] = topic

		if update_counts is True:
			self._topic_counts_by_doc[doc_idx, topic] += 1
			self._topic_counts_by_doc[doc_idx, old_topic] -= 1

			self._topic_counts[topic] += 1
			self._topic_counts[old_topic] -= 1

			tpe = self._corpus.get_type_idx_in_doc(doc_idx, word_idx)
			self._topic_counts_by_type[tpe, topic] += 1
			self._topic_counts_by_type[tpe, old_topic] -= 1


	cpdef add_to_counts(TopicModel self, int amt, int top_idx, int doc_idx, int type_idx):
		self._topic_counts_by_doc[doc_idx, top_idx] += amt		
		self._topic_counts_by_type[type_idx, top_idx] += amt
		self._topic_counts[top_idx] += amt

	# ============== Model-querying methods ==============

	cpdef int get_topic(TopicModel self, int doc_idx, int word_idx):
		"""
		Obtain the topic currently associated to the word with index ``word_idx``
		in the document with index ``doc_idx``.
		"""
		return self._topic_distributions[doc_idx][word_idx]

	cpdef int count_topic_document(TopicModel self, int top_idx, int doc_idx):
		"""
		Count the number of words with topic index ``top_idx`` in the document 
		with index ``doc_idx``.
		"""
		return self._topic_counts_by_doc[doc_idx, top_idx]

	cpdef int count_topic_types(TopicModel self, int top_idx, int type_idx):
		"""
		Count the number of words with topic index ``top_idx`` and type index 
		``type_idx``.
		"""
		return self._topic_counts_by_type[type_idx, top_idx]

	cpdef int count_topic(TopicModel self, int top_idx):
		"""
		Count the number of words with topic index ``top_idx`` across the corpus.
		"""
		return self._topic_counts[top_idx]

	cpdef count_all_topics_type(TopicModel self, int type_idx):
		"""
		Return a list of all the topic counts for the type with index 
		``type_idx``. The list is indexed by topic index.
		"""
		return self._topic_counts_by_type[type_idx]

	cpdef count_all_topics_document(TopicModel self, int doc_idx):
		"""
		Return a list of all the topic counts in the document with index 
		``doc_idx``. The list is indexed by topic index.
		"""
		return self._topic_counts_by_doc[doc_idx]

	cpdef count_all_topics(TopicModel self):
		"""
		Return a list of all the topic counts, indexed by topic index.
		"""
		return self._topic_counts

	def describe_document(self, doc_idx):
		"""
		Returns a list of the percentages that each topic contributes to the 
		document with document ``doc_idx``. The list is indexed by topic index.
		"""
		sum_topics = 0.0
		description = self._topic_counts_by_doc[doc_idx,:]
		for i in range(len(description)):
			sum_topics += description[i]

		return [i / sum_topics for i in description]

	def describe_topic(self, top_idx):
		"""
		Returns a list of tuples, where the first field of a tuple is a word, 
		and the second field is how many times it receives the given topic 
		(sorted in descending order of this second field).

		# TODO: Revise so the default behavior gives frequencies for each word.
		#   the kwargument normalized=False returns counts.
		"""
		type_counts = {}
		for type_idx in range(self._topic_counts_by_type.shape[0]):
			counts = self._topic_counts_by_type[type_idx]
			amt = counts[top_idx]
			if amt > 0:
				tpe = self._corpus.get_type(type_idx)
				if tpe not in type_counts:
					type_counts[tpe] = amt
				else:
					type_counts[tpe] += amt

		return sorted(type_counts.iteritems(), key=lambda i: i[1], reverse=True)
