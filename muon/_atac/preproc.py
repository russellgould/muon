from typing import Union
import logging
import numpy as np
from scipy.sparse import csr_matrix

from anndata import AnnData
from .._core.ammdata import AmmData

def tfidf(data: Union[AnnData, AmmData], log_tf=True, log_idf=True, scale_factor=1e4):
	"""
	Transform peak counts with TF-IDF (Term Frequency - Inverse Document Frequency).

	TF: peak counts are normalised by total number of counts per cell
	DF: total number of counts for each peak
	IDF: number of cells divided by DF

	By default, log(TF) * log(IDF) is returned.

	Parameters
	----------
	data
		AnnData object with peak counts or multimodal AmmData object with 'atac' modality.
	log_idf
		Log-transform IDF term (True by default)
	log_tf
		Log-transform TF term (True by default)
	scale_factor
	    Scale factor to multiply the TF-IDF matrix by (1e4 by default)
	"""
	if isinstance(data, AnnData):
		adata = data
	elif isinstance(data, AmmData):
		adata = data.mod['atac']
		# TODO: check that ATAC-seq slot is present with this name
	else:
		raise TypeError("Expected AnnData or AmmData object with 'atac' modality")

	n_peaks = adata.X.sum(axis=1)
	tf = np.asarray(adata.X / n_peaks)
	if scale_factor is not None and scale_factor != 0 and scale_factor != 1:
		tf = tf * scale_factor
	if log_tf:
		tf = np.log1p(tf)

	idf = np.asarray(adata.shape[0] / adata.X.sum(axis=0)).reshape(-1)
	if log_idf:
		idf = np.log1p(idf)

	tf_idf = np.dot(csr_matrix(tf), csr_matrix(np.diag(idf)))

	adata.X = np.nan_to_num(tf_idf, 0)

	return None