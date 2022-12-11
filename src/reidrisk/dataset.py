"""
author: Weiyi Xia
created on 12/8/2022
last modified: 12/8/2022
"""
import pandas as pd
from google.cloud import bigquery
import os

class Dataset:
    def __init__(
            self,
            source,
            dset: pd.DataFrame=None,
            dfile: str=None,
            colnames = None,
            header=0,
            index_col=False,
            sep=",",
            bigquery_service_account_key_file=None,
            bigquery_dataset=None,
            bigquery_table=None
    ):
        self.dset = dset
        self.source = source
        self.dfile = dfile
        self.colnames = colnames
        self.header = header
        self.index_col = index_col
        self.sep = sep
        self.bigquery_service_account_key_file = bigquery_service_account_key_file
        self.bigquery_dataset = bigquery_dataset
        self.bigquery_table = bigquery_table

    def load(self):
        if self.source == "dataframe":
            pass
        elif self.source == 'file':
            if self.dfile is None:
                raise ValueError("dataset file is not specified")
            else:
                self.dset = pd.read_csv(self.dfile, sep=self.sep, header=self.header, index_col=self.index_col)

        elif self.source == "bigquery":
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.bigquery_service_account_key_file
            client = bigquery.Client()
            query = "SELECT * FROM {}.{}".format(self.bigquery_dataset, self.bigquery_table)
            self.dset = client.query(query).to_dataframe()
        else:
            raise ValueError("dataset source is not specified")







