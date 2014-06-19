from topic_model import TopicModel
from corpus import Corpus

import numpy as np
cimport numpy as np

def gibbs_lda(corpus, int num_topics, **kwargs):
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
		int iter_cnt, d_idx, token_idx, t, i

		int topic, new_topic, tpe

		np.ndarray[np.int_t] sample
		np.ndarray[np.float_t] p = np.empty(num_topics, np.float_)


	model = TopicModel(corpus, num_topics, alpha, beta)
	model.random_topics() 

	for iter_cnt in range(num_iterations):
		for d_idx in range(len(corpus)):
			document = corpus.document(d_idx)
			for token_idx in range(len(document)):

				tpe = corpus.get_type_idx_in_doc(d_idx, token_idx)
				topic = model.get_topic(d_idx, token_idx)
				model.add_to_count_topic_document(-1, topic, d_idx)
				model.add_to_count_topic_types(-1, topic, tpe)
				model.add_to_topic_count(-1, topic)

				for t in range(num_topics):
					p[t] = (model.count_all_topics_type(tpe)[t] * 
							model.count_all_topics_document(d_idx)[t] /
							float(model.count_all_topics()[t]))

				p /= p.sum()
				
				sample = np.random.multinomial(1, p)
				new_topic = 0
				for i in range(len(sample)):
					if(sample[i] == 1): 
						break
					new_topic += 1

				model.set_topic(d_idx, token_idx, new_topic, False)
				model.add_to_count_topic_document(1, new_topic, d_idx)
				model.add_to_count_topic_types(1, new_topic, tpe)
				model.add_to_topic_count(1, new_topic)

	return model
					
