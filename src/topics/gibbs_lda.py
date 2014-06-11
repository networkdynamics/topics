from topic_model import TopicModel

import numpy as np

def compute_multinomial_step(model, tidx, didx, tpe, a, b):
	numerator = ((model.count_topic_document(tidx, didx) + a) *
				(model.count_topic_types(tidx, tpe) + b))
	denominator = (model.count_topic(tidx) + model.num_topics * b)
	return numerator / denominator

def gibbs_lda(corpus, num_topics, **kwargs):
	num_iterations = kwargs.pop("num_iterations", 1000)
	alpha = kwargs.pop("alpha", 50.0 / num_topics)
	beta = kwargs.pop("beta", 0.1)

	model = TopicModel(corpus, num_topics, alpha, beta)
	model.random_topics()

	p = np.empty(num_topics)

	for iter_cnt in range(num_iterations):
		print iter_cnt
		for d_idx in range(len(corpus)):
			document = corpus.document(d_idx)
			for token_idx in range(len(document)):

				tpe = document.get_type_by_token_idx(token_idx)
				topic = model.get_topic(d_idx, token_idx)
				model.add_to_count_topic_document(-1, topic, d_idx)
				model.add_to_count_topic_types(-1, topic, tpe)
				model.add_to_topic_count(-1, topic)

				p = [i * j / float(k) for i, j, k in 
							zip(model.count_all_topics_type(tpe),
							model.count_all_topics_document(d_idx),
							model.count_all_topics())]

				s = sum(p)
				for i in range(len(p)):
					p[i] /= s	
				
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
					
