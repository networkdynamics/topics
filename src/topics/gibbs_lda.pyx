from topic_model cimport TopicModel
from corpus import Corpus

import numpy as np
cimport numpy as np

cdef update_document(corpus, TopicModel model, int d_idx, np.ndarray[np.float_t] p):
	cdef:
		# Loop iterators
		int token_idx, topic_idx, i
		
		# Topic variables
		int topic, new_topic, tpe

		# The sample drawn from the multinomial distribution
		np.ndarray[np.int_t] sample
		float p_sum

	document = corpus.document(d_idx)
	for token_idx in range(len(document)):

		tpe = corpus.get_type_idx_in_doc(d_idx, token_idx)
		topic = model.get_topic(d_idx, token_idx)
		model.add_to_counts(-1, topic, d_idx, tpe)



		for topic_idx in range(model.num_topics):
			p[topic_idx] = (model._topic_counts_by_type[tpe, topic_idx] * 
					model._topic_counts_by_doc[d_idx, topic_idx] /
					model._topic_counts[topic_idx])

		p_sum = 0.0
		for topic_idx in range(model.num_topics):
			p_sum += p[topic_idx]

		for topic_idx in range(model.num_topics):
			p[topic_idx] /= p_sum
		

		sample = np.random.multinomial(1, p)

		new_topic = 0
		for i in range(len(sample)):
			if(sample[i] == 1): 
				break
			new_topic += 1

		model.set_topic(d_idx, token_idx, new_topic, False)
		model.add_to_counts(1, new_topic, d_idx, tpe)

def gibbs_lda_learn(corpus, int num_topics, **kwargs):
	"""
	Use Collapsed Gibbs Sampling to learn topics from a corpus, using the
	Latent Dirichlet Allocation (LDA) model.

	**Args**

		* ``corpus``: the corpus for which to learn topics.
		* ``num_topics``: the number of topics to be learned.

	**Keyword Args**
		* ``num_iterations [=1000]`` (int): the number of iterations of learning.
		* ``alpha [=50/num_topics]`` (float): topics prior
		* ``beta [=0.1]`` (float): words prior

	**Returns**
		A :py:module:TopicModel containing the topic assignments to the corpus.
	"""

	cdef:
		int num_iterations = kwargs.pop("num_iterations", 1000)
		float alpha = kwargs.pop("alpha", 50.0 / num_topics)
		float beta = kwargs.pop("beta", 0.1)

		# loop iterators
		int iter_cnt, d_idx

		# Probability distribution (allocated here to avoid doing it for every token)
		np.ndarray[np.float_t] p = np.empty(num_topics, np.float_)

		TopicModel model = TopicModel(corpus, num_topics, alpha, beta)

	model.random_topics() 

	for iter_cnt in range(num_iterations):
		print iter_cnt
		for d_idx in range(len(corpus)):
			update_document(corpus, model, d_idx, p)

	return model

def gibbs_lda_infer(document, TopicModel model, **kwargs):
	"""
	Use Gibbs sampling to infer the topic distribution of a document, based on
	an existing LDA topic model.

	**Args**

		* ``document``: the document on which to infer the topics
		* ``model``: the model used as a basis for the inference process

	**Keyword Args**

		* ``num_iterations [=25]`` (int): the number of iterations of inference.
		* The same filtering parameters as those that can be passed to a corpus.

	**Returns**
		A :py:module:TopicModel containing the topic assignments for the new
		document, which has index 0 in the model. Topic indices are the same as
		with ``model``.
	"""

	num_iterations = kwargs.pop("num_iterations", 25)
	fh = kwargs.pop("filter_high", None)
	fl = kwargs.pop("filter_low", None)
	fs = kwargs.pop("filter_set", None)
	corpus = Corpus([document], filter_high=fh, filter_low=fl, filter_set=fs)
	new_model = TopicModel(corpus, model.num_topics, model.alpha, model.beta)
	new_model.random_topics()

	cdef:
		# Loop iterators
		int token_idx, topic_idx, i, iter_cnt
		
		# Topic variables
		int topic, new_topic, tpe

		# The sample drawn from the multinomial distribution
		np.ndarray[np.int_t] sample
		np.ndarray[np.float_t] p = np.empty(model.num_topics, dtype=np.float_)
		float p_sum

		float old_by_type, old_all, new_by_type, new_by_doc, new_all
		float by_type, by_doc, by_corpus

	for iter_cnt in range(num_iterations):
		for token_idx in range(len(document)):
			tpe = corpus.get_type_idx_in_doc(0, token_idx)
			topic = new_model.get_topic(0, token_idx)
			new_model.add_to_counts(-1, topic, 0, tpe)

			for topic_idx in range(new_model.num_topics):
				# Check types in both corpora
				by_type = (model._topic_counts_by_type[tpe, topic_idx] +
							new_model._topic_counts_by_type[tpe, topic_idx])

				# The new document is not part of the old corpus
				by_doc = new_model._topic_counts_by_doc[0, topic_idx]

				# new_model's corpus is just the one document
				by_corpus = model._topic_counts[topic_idx] + by_doc

				p[topic_idx] = (by_type * by_doc / by_corpus)

			p_sum = 0.0
			for topic_idx in range(new_model.num_topics):
				p_sum += p[topic_idx]

			for topic_idx in range(new_model.num_topics):
				p[topic_idx] /= p_sum
	
			sample = np.random.multinomial(1, p)

			new_topic = 0
			for i in range(len(sample)):
				if(sample[i] == 1): 
					break
				new_topic += 1

			new_model.set_topic(0, token_idx, new_topic, False)
			new_model.add_to_counts(1, new_topic, 0, tpe)

	return new_model
