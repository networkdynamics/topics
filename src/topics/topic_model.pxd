cimport numpy as np

cdef class TopicModel:
	cdef object _corpus
	cdef readonly int num_topics
	cdef float _alpha
	cdef float _beta

	cdef list _topic_distributions
	cdef np.ndarray _topic_counts_by_doc
	cdef np.ndarray _topic_counts_by_type
	cdef np.ndarray _topic_counts

	cpdef random_topics(self)
