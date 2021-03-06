"""Tests for calculate_scores"""

from __future__ import print_function

"""
Copyright (c) 2018, EPFL/Blue Brain Project

 This file is part of BluePyMM <https://github.com/BlueBrain/BluePyMM>

 This library is free software; you can redistribute it and/or modify it under
 the terms of the GNU Lesser General Public License version 3.0 as published
 by the Free Software Foundation.

 This library is distributed in the hope that it will be useful, but WITHOUT
 ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
 details.

 You should have received a copy of the GNU Lesser General Public License
 along with this library; if not, write to the Free Software Foundation, Inc.,
 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""


import os
import pandas
import sqlite3
import json

from nose.plugins.attrib import attr
import nose.tools as nt

import bluepymm.run_combos as run_combos
from bluepymm import tools


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEST_DIR = os.path.join(BASE_DIR, 'examples/simple1')
TMP_DIR = os.path.join(BASE_DIR, 'tmp/')


@attr('unit')
def test_run_emodel_morph_isolated():
    """run_combos.calculate_scores: test run_emodel_morph_isolated."""
    uid = 0
    emodel = 'emodel1'
    emodel_dir = os.path.join(TEST_DIR, 'data/emodels_dir/subdir/')
    emodel_params = {'cm': 1.0}
    morph_name = 'morph1'
    morph_dir = os.path.join(TEST_DIR, 'data/morphs')
    morph_path = os.path.join(morph_dir, '%s.asc' % morph_name)

    input_args = (
        uid,
        emodel,
        emodel_dir,
        emodel_params,
        morph_path)
    ret = run_combos.calculate_scores.run_emodel_morph_isolated(input_args)

    expected_ret = {'exception': None,
                    'extra_values': {'holding_current': None,
                                     'threshold_current': None},
                    'scores': {'Step1.SpikeCount': 20.0},
                    'uid': 0}
    nt.assert_dict_equal(ret, expected_ret)


@attr('unit')
def test_run_emodel_morph_isolated_exception():
    """run_combos.calculate_scores: test run_emodel_morph_isolated exception.
    """
    # input parameters
    uid = 0
    emodel = 'emodel_doesnt_exist'
    emodel_dir = os.path.join(TEST_DIR, 'data/emodels_dir/subdir/')
    emodel_params = {'cm': 1.0}
    morph_name = 'morph1'
    morph_dir = os.path.join(TEST_DIR, 'data/morphs')
    morph_path = os.path.join(morph_dir, '%s.asc' % morph_name)

    # function call
    input_args = (
        uid,
        emodel,
        emodel_dir,
        emodel_params,
        morph_path)
    ret = run_combos.calculate_scores.run_emodel_morph_isolated(input_args)

    # verify output: exception thrown because of non-existing e-model
    expected_ret = {'exception': 'this_is_a_placeholder',
                    'extra_values': None,
                    'scores': None,
                    'uid': 0}
    nt.assert_list_equal(sorted(ret.keys()), sorted(expected_ret.keys()))
    for k in ['extra_values', 'scores', 'uid']:
        nt.assert_equal(ret[k], expected_ret[k])
    nt.assert_true(emodel in ret['exception'])


@attr('unit')
def test_run_emodel_morph():
    """run_combos.calculate_scores: test run_emodel_morph."""
    emodel = 'emodel1'
    emodel_dir = os.path.join(TEST_DIR, 'data/emodels_dir/subdir/')
    emodel_params = {'cm': 1.0}

    morph_name = 'morph1'
    morph_dir = os.path.join(TEST_DIR, 'data/morphs')
    morph_path = os.path.join(morph_dir, '%s.asc' % morph_name)

    ret = run_combos.calculate_scores.run_emodel_morph(
        emodel,
        emodel_dir,
        emodel_params,
        morph_path)

    expected_scores = {'Step1.SpikeCount': 20.0}
    expected_extra_values = {'holding_current': None,
                             'threshold_current': None}
    nt.assert_dict_equal(ret[0], expected_scores)
    nt.assert_dict_equal(ret[1], expected_extra_values)


@attr('unit')
def test_run_emodel_morph_exception():
    """run_combos.calculate_scores: test run_emodel_morph exception."""
    emodel = 'emodel_doesnt_exist'
    emodel_dir = os.path.join(TEST_DIR, 'data/emodels_dir/subdir/')
    emodel_params = {'cm': 1.0}

    morph_name = 'morph1'
    morph_dir = os.path.join(TEST_DIR, 'data/morphs')
    morph_path = os.path.join(morph_dir, '%s.asc' % morph_name)

    nt.assert_raises(
        Exception,
        run_combos.calculate_scores.run_emodel_morph,
        emodel,
        emodel_dir,
        emodel_params,
        morph_path)


def _write_test_scores_database(row, testsqlite_filename):
    """Helper function to create test scores database."""
    df = pandas.DataFrame(row, index=[0])
    with sqlite3.connect(testsqlite_filename) as conn:
        df.to_sql('scores', conn, if_exists='replace')


@attr('unit')
def test_create_arg_list():
    """run_combos.calculate_scores: test create_arg_list."""
    # write database
    testsqlite_filename = os.path.join(TMP_DIR, 'test1.sqlite')
    index = 0
    morph_name = 'morph'
    morph_dir = 'morph_dir'
    mtype = 'mtype'
    etype = 'etype'
    layer = 'layer'
    emodel = 'emodel'
    row = {'index': index,
           'morph_name': morph_name,
           'morph_ext': None,
           'morph_dir': morph_dir,
           'mtype': mtype,
           'etype': etype,
           'layer': layer,
           'emodel': emodel,
           'original_emodel': emodel,
           'to_run': 1}
    _write_test_scores_database(row, testsqlite_filename)

    # extra input parameters
    emodel_dirs = {emodel: 'emodel_dirs'}
    params = 'test'
    final_dict = {emodel: {'params': params}}

    ret = run_combos.calculate_scores.create_arg_list(
        testsqlite_filename,
        emodel_dirs,
        final_dict)

    # verify output
    morph_path = os.path.join(morph_dir, '{}.asc'.format(morph_name))
    expected_ret = [(index,
                     emodel,
                     os.path.abspath(emodel_dirs[emodel]),
                     params,
                     os.path.abspath(morph_path))]
    nt.assert_list_equal(ret, expected_ret)


@attr('unit')
def test_create_arg_list_exception():
    """run_combos.calculate_scores: test create_arg_list for ValueError."""
    # write database
    testsqlite_filename = os.path.join(TMP_DIR, 'test2.sqlite')
    index = 0
    morph_name = 'morph'
    morph_dir = 'morph_dir'
    mtype = 'mtype'
    etype = 'etype'
    layer = 'layer'
    emodel = None
    row = {'index': index,
           'morph_name': morph_name,
           'morph_ext': None,
           'morph_dir': morph_dir,
           'mtype': mtype,
           'etype': etype,
           'layer': layer,
           'emodel': emodel,
           'original_emodel': emodel,
           'to_run': 1}
    _write_test_scores_database(row, testsqlite_filename)

    # extra input parameters
    emodel_dirs = {emodel: 'emodel_dirs'}
    params = 'test'
    final_dict = {emodel: {'params': params}}

    # emodel is None -> raises ValueError
    nt.assert_raises(
        ValueError,
        run_combos.calculate_scores.create_arg_list,
        testsqlite_filename,
        emodel_dirs,
        final_dict)


def _dict_factory(cursor, row):
    """Helper function to create dictionaries from database rows."""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@attr('unit')
def test_save_scores():
    """run_combos.calculate_scores: test save_scores"""
    # create test database with single entry 'row'
    testsqlite_filename = os.path.join(TMP_DIR, 'test3.sqlite')
    row = {'scores': None,
           'extra_values': None,
           'exception': None,
           'to_run': True}
    _write_test_scores_database(row, testsqlite_filename)

    # process database
    uid = 0
    scores = {'score': 1}
    extra_values = {'extra': 2}
    exception = 'exception'
    run_combos.calculate_scores.save_scores(
        testsqlite_filename,
        uid,
        scores,
        extra_values,
        exception)

    # verify database
    expected_db_row = {'index': uid,
                       'scores': json.dumps(scores),
                       'extra_values': json.dumps(extra_values),
                       'exception': exception,
                       'to_run': 0}  # False
    with sqlite3.connect(testsqlite_filename) as scores_db:
        scores_db.row_factory = _dict_factory
        scores_cursor = scores_db.execute('SELECT * FROM scores')
        db_row = scores_cursor.fetchall()[0]
        nt.assert_dict_equal(db_row, expected_db_row)

    # value already updated -> error
    nt.assert_raises(
        ValueError,
        run_combos.calculate_scores.save_scores,
        testsqlite_filename,
        uid,
        scores,
        extra_values,
        exception)


@attr('unit')
def test_expand_scores_to_score_values_table():
    """run_combos.calculate_scores: test expand_scores_to_score_values_table"""
    # create database
    db_path = os.path.join(TMP_DIR, 'test_expand_scores.sqlite')
    score_key = 'Step1.SpikeCount'
    score_value = 20.0
    scores = '{"%s": %s}' % (score_key, score_value)
    row = {'scores': scores, 'to_run': False}
    _write_test_scores_database(row, db_path)

    # process database
    run_combos.calculate_scores.expand_scores_to_score_values_table(db_path)

    # verify database
    expected_df = pandas.DataFrame(data=json.loads(scores), index=[0])
    with sqlite3.connect(db_path) as conn:
        score_values = pandas.read_sql('SELECT * FROM score_values', conn)
    pandas.util.testing.assert_frame_equal(score_values, expected_df)


@attr('unit')
def test_expand_scores_to_score_values_table_error():
    """run_combos.calculate_scores: test expand_scores_to_score_values_table 2
    """
    # create database
    db_path = os.path.join(TMP_DIR, 'test_expand_scores_error.sqlite')
    score_key = 'Step1.SpikeCount'
    score_value = 20.0
    scores = '{"%s": %s}' % (score_key, score_value)
    row = {'scores': scores, 'to_run': True}
    _write_test_scores_database(row, db_path)

    # process database
    nt.assert_raises(
        Exception,
        run_combos.calculate_scores.expand_scores_to_score_values_table,
        db_path)


@attr('unit')
def test_calculate_scores():
    """run_combos.calculate_scores: test calculate_scores"""
    # write database
    test_db_filename = os.path.join(TMP_DIR, 'test4.sqlite')
    morph_name = 'morph1'
    morph_dir = './data/morphs'
    mtype = 'mtype1'
    etype = 'etype1'
    layer = 1
    emodel = 'emodel1'
    exception = None
    row = {'morph_name': morph_name,
           'morph_ext': None,
           'morph_dir': morph_dir,
           'mtype': mtype,
           'etype': etype,
           'layer': layer,
           'emodel': emodel,
           'original_emodel': emodel,
           'to_run': 1,
           'scores': None,
           'extra_values': None,
           'exception': exception}
    _write_test_scores_database(row, test_db_filename)

    # calculate scores
    emodel_dir = os.path.join(TEST_DIR, 'data/emodels_dir/subdir/')
    emodel_dirs = {emodel: emodel_dir}
    final_dict_path = os.path.join(emodel_dir, 'final.json')
    final_dict = tools.load_json(final_dict_path)
    with tools.cd(TEST_DIR):
        run_combos.calculate_scores.calculate_scores(final_dict, emodel_dirs,
                                                     test_db_filename)

    # verify database
    scores = {'Step1.SpikeCount': 20.0}
    extra_values = {'holding_current': None, 'threshold_current': None}
    expected_db_row = {'index': 0,
                       'morph_name': morph_name,
                       'morph_ext': None,
                       'morph_dir': morph_dir,
                       'mtype': mtype,
                       'etype': etype,
                       'layer': layer,
                       'emodel': emodel,
                       'original_emodel': emodel,
                       'to_run': 0,
                       'scores': json.dumps(scores),
                       'extra_values': json.dumps(extra_values),
                       'exception': exception}
    with sqlite3.connect(test_db_filename) as scores_db:
        scores_db.row_factory = _dict_factory
        scores_cursor = scores_db.execute('SELECT * FROM scores')
        db_row = scores_cursor.fetchall()[0]
        nt.assert_dict_equal(db_row, expected_db_row)
