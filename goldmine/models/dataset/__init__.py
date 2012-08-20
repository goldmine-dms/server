#!/usr/bin/env python
#-*- coding:utf-8 -*-

from goldmine.models.dataset.dataset import Dataset
from goldmine.models.dataset.type import Type


# FIXME: auto enumerate dataset types
from goldmine.models.dataset import sequence
from goldmine.models.dataset import file


DATASET_TYPES = (
    ("sequence", sequence),
    ("file",     file),
)
