import random

class TopicModel:
	def __init__(self, corpus, num_topics):
		self._corpus = corpus
		self.num_topics = num_topics

		# A[i][j] is the topic assigned to the jth word of the ith document
		self._topic_distributions = []
		for doc in corpus:
			self._topic_distributions.append([0 for i in range(len(doc))])

		# A[i][j] is the number of tokens with topic j in the ith document
		self._topic_counts_by_doc = []

		# A[tpe][i] is the number of tokens with given type and ith topic
		self._topic_counts_by_type = {}

		# A[i] is the number of tokens with ith topic
		self._topic_counts = [0 for i in range(num_topics)]

		for doc in corpus:
			self._topic_counts_by_doc.append([0 for i in range(num_topics)])
			self._topic_counts_by_doc[len(self._topic_counts_by_doc) - 1][0] = len(doc)
			self._topic_counts[0] += len(doc)

			for tok in doc.tokens_iter():
				if tok not in self._topic_counts_by_type:
					self._topic_counts_by_type[tok] = [0 for i in range(num_topics)]
					self._topic_counts_by_type[tok][0] = 1
				else:
					self._topic_counts_by_type[tok][0] += 1

	# ============== Model-building methods ==============

	def random_topics(self):
		for i in range(len(self._topic_distributions)):
			doc_topics = self._topic_distributions[i]
			for j in range(len(doc_topics)):
				# Update the topic assignment
				new_topic = random.randrange(self.num_topics)
				old_topic = doc_topics[j]
				doc_topics[j] = new_topic

				# Update the count by document
				self._topic_counts_by_doc[i][new_topic] += 1
				self._topic_counts_by_doc[i][old_topic] -= 1

				# Update the global count
				self._topic_counts[new_topic] += 1
				self._topic_counts[old_topic] -= 1

				# Update the count by type
				tpe = self._corpus.document(i).get_type_by_tidx(j)
				self._topic_counts_by_type[tpe][new_topic] += 1
				self._topic_counts_by_type[tpe][old_topic] -= 1

	def get_topic(self, doc_idx, word_idx):
		return self._topic_distributions[doc_idx][word_idx]

	def count_topic_document(self, top_idx, doc_idx):
		return self._topic_counts_by_doc[doc_idx][top_idx]

	def count_topic_types(self, top_idx, tpe):
		return self._topic_counts_by_type[tpe][top_idx]

	def count_topic(self, top_idx):
		return self._topic_counts[top_idx]

	def set_topic(self, doc_idx, word_idx, topic, update_counts=True):
		old_topic = self._topic_distributions[doc_idx][word_idx]
		self._topic_distributions[doc_idx][word_idx] = topic

		if update_counts is True:
			self._topic_counts_by_doc[doc_idx][topic] += 1
			self._topic_counts_by_doc[doc_idx][old_topic] -= 1

			self._topic_counts[topic] += 1
			self._topic_counts[old_topic] -= 1

			tpe = self._corpus.document(doc_idx).get_type_by_token_idx(word_idx)
			self._topic_counts_by_type[tpe][topic] += 1
			self._topic_counts_by_type[tpe][old_topic] -= 1


	def add_to_count_topic_document(self, amt, top_idx, doc_idx):
		self._topic_counts_by_doc[doc_idx][top_idx] += amt

	def add_to_topic_count(self, amt, top_idx):
		self._topic_counts[top_idx] += amt

	def add_to_count_topic_types(self, amt, top_idx, tpe):
		self._topic_counts_by_type[tpe][top_idx] += amt

	# ============== Model-querying methods ==============
	def describe_topic(self, top_idx):
		# Return a list of words which contribute to the given topic 
		# (in no particular order)
		types = []
		for tpe, topics in self._topic_counts_by_type.iteritems():
			if topics[top_idx] > 0:
				types.append(tpe)

		return types

	def describe_document(self, doc_idx):
		# Return a list of how all topics contribute to a document (in percent)
		return [i / self.num_topics in self._topic_counts_by_doc[doc_idx]]
		
