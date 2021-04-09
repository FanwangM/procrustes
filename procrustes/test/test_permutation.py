# -*- coding: utf-8 -*-
# The Procrustes library provides a set of functions for transforming
# a matrix to make it as similar as possible to a target matrix.
#
# Copyright (C) 2017-2021 The QC-Devs Community
#
# This file is part of Procrustes.
#
# Procrustes is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# Procrustes is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
# --
"""Testings for permutation module."""
# pylint: disable=too-many-lines

import itertools

import numpy as np
from numpy.testing import assert_almost_equal, assert_equal, assert_raises
from procrustes.permutation import (_guess_permutation_2sided_1trans_normal1,
                                    _guess_initial_2sided_1trans_normal2,
                                    _guess_permutation_2sided_1trans_umeyama,
                                    permutation, permutation_2sided)
import pytest


def generate_random_permutation_matrix(n):
    r"""Generate a random permutation matrix."""
    arr = np.arange(0, n)
    np.random.shuffle(arr)
    perm = np.zeros((n, n))
    perm[np.arange(0, n), arr] = 1.0
    return perm


@pytest.mark.parametrize("n", np.random.randint(50, 100, (25)))
def test_permutation_one_sided_square_matrices_rows_permuted(n):
    r"""Test one-sided permutation Procrustes with square matrices and permuted rows."""
    array_a = np.random.uniform(-10.0, 10.0, (n, n))
    perm = generate_random_permutation_matrix(n)
    # permuted array_b
    array_b = np.dot(array_a, perm)
    # procrustes with no translate and scale
    res = permutation(array_a, array_b)
    assert_almost_equal(res.t, perm, decimal=6)
    assert_almost_equal(res.error, 0., decimal=6)


@pytest.mark.parametrize("m, n, ncols, nrows", np.random.randint(50, 100, (25, 4)))
def test_permutation_one_sided_columns_pad(m, n, ncols, nrows):
    r"""Test one-sided permutation by permuted columns along with padded zeros."""
    array_a = np.random.uniform(-10.0, 10.0, (m, n))
    perm = generate_random_permutation_matrix(n)
    # permuted array_b
    array_b = np.dot(array_a, perm)
    # padded array b with zero row and columns
    array_b = np.concatenate((array_b, np.zeros((m, ncols))), axis=1)
    array_b = np.concatenate((array_b, np.zeros((nrows, n + ncols))), axis=0)
    if m < n:
        array_a = np.concatenate((array_a, np.zeros((n - m, n))), axis=0)
    # procrustes with no translate and scale
    res = permutation(array_a, array_b, unpad_col=True, unpad_row=True)
    # Test that the unpadded b is the same as the original b.
    assert_almost_equal(res.new_b, np.dot(array_a, perm), decimal=6)
    # Test that the permutation and the error are the same/zero.
    assert_almost_equal(res.t, perm, decimal=6)
    assert_almost_equal(res.error, 0., decimal=6)


@pytest.mark.parametrize("m, n", np.random.randint(50, 100, (25, 2)))
def test_permutation_one_sided_with_translate_scale(m, n):
    r"""Test permutation one_sided by translated and scaled arrays."""
    array_a = np.random.uniform(-10.0, 10.0, (m, n))
    # array_b is scaled, translated, and permuted array_a
    perm = generate_random_permutation_matrix(n)
    # obtain random translation/shift array and permute the array.
    shift = np.random.uniform(-10.0, 10.0, (n,))
    array_b = 3.78 * array_a + shift
    array_b = np.dot(array_b, perm)
    # permutation procrustes
    res = permutation(array_a, array_b, translate=True, scale=True)
    assert_almost_equal(res.t, perm, decimal=6)
    assert_almost_equal(res.error, 0., decimal=6)


def test_2sided_1trans_initial_guess_normal1_positive():
    r"""Test 2sided-perm initial normal1 guess by positive arrays."""
    # Define a random array
    array_a = np.array(
        [[1, 5, 8, 4], [0, 12, 7, 2], [3, 6, 9, 4], [2, 7, 8, 5]])
    # Build the new matrix array_b
    array_b = np.array(
        [[1, 12, 9, 5], [8, 7, 6, 8], [5, 2, 4, 7], [4, 0, 3, 2]])
    weight_p = np.power(2, -0.5)
    weight = np.empty(array_a.shape)
    for row in range(4):
        weight[row, :] = np.power(weight_p, row)
    array_b = np.multiply(array_b, weight)
    # Check
    array_new = _guess_permutation_2sided_1trans_normal1(array_a)
    assert_almost_equal(array_b, array_new, decimal=6)


def test_2sided_1trans_initial_guess_normal1_negative():
    r"""Test 2sided-perm initial normal1 guess by negative arrays."""
    # Define a random array
    array_a = np.array([[1, 5, -8, 4], [0, 12, 7, 2],
                        [3, -6, 9, 4], [2, -7, 8, -5]])
    # Build the new matrix array_b
    array_b = np.array([[1, 12, 9, -5], [-8, 7, -6, 8],
                        [5, 2, 4, -7], [4, 0, 3, 2]])
    weight_p = np.power(2, -0.5)
    weight = np.empty(array_a.shape)
    for row in range(4):
        weight[row, :] = np.power(weight_p, row)
    array_b = np.multiply(array_b, weight)
    # Check
    array_new = _guess_permutation_2sided_1trans_normal1(array_a)
    assert_almost_equal(array_b, array_new, decimal=6)


def test_2sided_1trans_initial_guess_normal2_positive():
    r"""Test 2sided-perm initial normal2 guess by positive arrays."""
    # Define a random array
    array_a = np.array([[32, 14, 3, 63, 50],
                        [24, 22, 1, 56, 4],
                        [94, 16, 28, 75, 81],
                        [19, 72, 42, 90, 54],
                        [71, 85, 10, 96, 58]])
    array_b = np.array([[32, 22, 28, 90, 58],
                        [90, 90, 32, 22, 90],
                        [63, 56, 94, 72, 96],
                        [58, 32, 58, 58, 22],
                        [50, 24, 81, 54, 85],
                        [22, 58, 90, 28, 32],
                        [14, 4, 75, 42, 71],
                        [28, 28, 22, 32, 28],
                        [3, 1, 16, 19, 10]])
    # Build the new matrix array_b
    weight_p = np.power(2, -0.5)
    weight = np.zeros([9, 5])
    weight[0, :] = 1
    for col in range(1, array_a.shape[1]):
        weight[2 * col - 1, :] = np.power(weight_p, col)
        weight[2 * col, :] = np.power(weight_p, col)
    array_b = np.multiply(array_b, weight)
    # Check
    array_new = _guess_initial_2sided_1trans_normal2(array_a)
    assert_almost_equal(array_b, array_new, decimal=6)


def test_2sided_1trans_initial_guess_normal2_negative():
    r"""Test 2sided-perm initial normal2 guess by negative arrays."""
    # Define a random matrix array_a
    array_a = np.array([[3, -1, 4, -1],
                        [-1, 5, 7, 6],
                        [4, 7, -9, 3],
                        [-1, 6, 3, 2]])
    array_b = np.array([[3, 5, -9, 2],
                        [-9, -9, 5, 5],
                        [4, 7, 7, 6],
                        [5, 2, 3, -9],
                        [-1, 6, 4, 3],
                        [2, 3, 2, 3],
                        [-1, -1, 3, -1]])
    # Build the new matrix array_b
    weight_p = np.power(2, -0.5)
    weight = np.zeros([7, 4])
    weight[0, :] = 1
    for col in range(1, array_a.shape[1]):
        weight[2 * col - 1, :] = np.power(weight_p, col)
        weight[2 * col, :] = np.power(weight_p, col)
    array_b = np.multiply(array_b, weight)
    # Check
    array_new = _guess_initial_2sided_1trans_normal2(array_a)
    assert_almost_equal(array_b, array_new, decimal=6)


def test_2sided_1trans_initial_guess_umeyama():
    r"""Test 2sided-perm initial umeyama guess by positive arrays."""
    array_a = np.array([[0, 5, 8, 6], [5, 0, 5, 1],
                        [8, 5, 0, 2], [6, 1, 2, 0]])
    array_b = np.array([[0, 1, 8, 4], [1, 0, 5, 2],
                        [8, 5, 0, 5], [4, 2, 5, 0]])

    u_umeyama = np.array([[0.909, 0.818, 0.973, 0.893],
                          [0.585, 0.653, 0.612, 0.950],
                          [0.991, 0.524, 0.892, 0.601],
                          [0.520, 0.931, 0.846, 0.618]])
    # U = _2sided_1trans_initial_guess_umeyama(array_a, array_b)
    array_u = _guess_permutation_2sided_1trans_umeyama(array_a=array_b, array_b=array_a)
    # Check
    assert_almost_equal(u_umeyama, array_u, decimal=3)


@pytest.mark.parametrize("n", np.random.randint(50, 100, (10,)))
def test_permutation_2sided_single_transform_umeyama_guess(n):
    r"""Test 2sided-permutation with single transform with umeyama guess."""
    # define a random matrix
    array_a = np.random.uniform(-10.0, 10.0, (n, n))
    array_a = (array_a + array_a.T) / 2.0
    # define array_b by permuting array_a
    perm = generate_random_permutation_matrix(n)
    array_b = np.dot(perm.T, np.dot(array_a, perm))
    # Check
    res = permutation_2sided(array_a, array_b, single=True, guess="umeyama")
    assert_almost_equal(res.t, perm, decimal=6)
    assert_almost_equal(res.error, 0, decimal=6)
    assert_equal(res.s, None)


@pytest.mark.parametrize("n", np.random.randint(3, 6, (5,)))
def test_permutation_2sided_single_transform_small_matrices_umeyama_all_permutations(n):
    r"""Test 2sided-perm single transform with Umeyama guess for all permutations."""
    # define a random matrix
    array_a = np.random.uniform(-10.0, 10.0, (n, n))
    # check with all possible permutation matrices
    for comb in itertools.permutations(np.arange(n)):
        perm = np.zeros((n, n))
        perm[np.arange(n), comb] = 1
        # get array_b by permutation
        array_b = np.dot(perm.T, np.dot(array_a, perm))
        res = permutation_2sided(array_a, array_b, single=True, guess="umeyama")
        assert_almost_equal(res["t"], perm, decimal=6)
        assert_almost_equal(res["error"], 0, decimal=6)
        assert_equal(res.s, None)


@pytest.mark.parametrize("n", np.random.randint(50, 500, (10,)))
def test_permutation_2sided_single_transform_symmetric_umeyama_translate_scale(n):
    r"""Test 2sided-perm with Umeyama guess with symmetric arrays with translation and scale."""
    # define a random, symmetric matrix
    array_a = np.random.uniform(-10, 10.0, (n, n))
    array_a = np.dot(array_a, array_a.T)
    # define array_b by scale-translate array_a and permuting
    shift = np.random.uniform(-10.0, 10.0, n)
    perm = generate_random_permutation_matrix(n)
    array_b = np.dot(perm.T, np.dot((14.7 * array_a + shift), perm))
    # Check
    res = permutation_2sided(array_a, array_b, single=True, guess="umeyama", translate=True,
                             scale=True)
    assert_almost_equal(res.t, perm, decimal=6)
    assert_almost_equal(res.error, 0, decimal=6)
    assert_equal(res.s, None)


@pytest.mark.parametrize("n", [3, 4, 5])
def test_permutation_2sided_single_transform_umeyama_translate_scale_all_permutations(n):
    r"""Test 2-sided single transform permutation Umeyama guess for all permutations."""
    # define a random matrix
    array_a = np.random.uniform(-10.0, 10.0, (n, n))
    # check with all possible permutation matrices
    for comb in itertools.permutations(np.arange(n)):
        # Compute the permutation matrix
        perm = np.zeros((n, n))
        perm[np.arange(n), comb] = 1
        # Compute the translated, scaled matrix
        shift = np.random.uniform(-10.0, 10.0, n)
        array_b = np.dot(perm.T, np.dot(60 * array_a + shift, perm))

        res = permutation_2sided(array_a, array_b, single=True, guess="umeyama", translate=True,
                                 scale=True)
        assert_almost_equal(res.t, perm, decimal=6)
        assert_almost_equal(res.error, 0, decimal=6)
        assert_equal(res.s, None)


@pytest.mark.parametrize("n, ncol, nrow", np.random.randint(50, 100, (10, 3)))
def test_permutation_2sided_single_transform_umeyama_translate_scale_zero_padding(n, ncol, nrow):
    r"""Test permutation two-sided umeyama guess with translation, scale and padding."""
    # define a random matrix
    array_a = np.random.uniform(-10.0, 10.0, (n, n))
    # check with all possible permutation matrices
    perm = generate_random_permutation_matrix(n)
    # Compute the translated, scaled matrix padded with zeros
    array_b = np.dot(perm.T, np.dot(20 * array_a + 8, perm))
    # pad both of the matrices with zeros
    array_a = np.concatenate((array_a, np.zeros((n, ncol))), axis=1)
    array_a = np.concatenate((array_a, np.zeros((nrow, n + ncol))), axis=0)
    array_b = np.concatenate((array_b, np.zeros((n, ncol))), axis=1)
    array_b = np.concatenate((array_b, np.zeros((nrow, n + ncol))), axis=0)

    res = permutation_2sided(array_a, array_b, single=True, guess="umeyama", unpad_col=True,
                             unpad_row=True, translate=True, scale=True)
    assert_almost_equal(res.t, perm, decimal=6)
    assert_almost_equal(res.error, 0, decimal=6)
    assert_equal(res.s, None)


@pytest.mark.parametrize("n", np.random.randint(50, 100, (10,)))
def test_permutation_2sided_single_transform_umeyama_approx(n):
    r"""Test 2sided-perm, single transform with "umeyama_approx" mode."""
    # define a random, symmetric matrix
    array_a = np.random.uniform(-10.0, 10.0, (n, n))
    array_a = (array_a + array_a.T) / 2.0
    # define array_b by permuting array_a
    perm = generate_random_permutation_matrix(n)
    array_b = np.dot(perm.T, np.dot(array_a, perm))
    res = permutation_2sided(array_a, array_b, single=True, guess="umeyama_approx")
    assert_almost_equal(res.t, perm, decimal=6)
    assert_almost_equal(res.error, 0, decimal=6)
    assert_equal(res.s, None)


def test_permutation_2sided_4by4_umeyama_approx_loop():
    r"""Test 2sided-perm with "umeyama_approx" mode by 4by4 arrays for all permutations."""
    # define a random matrix
    array_a = np.array([[4, 5, 3, 3], [5, 7, 3, 5],
                        [3, 3, 2, 2], [3, 5, 2, 5]])
    array_a = (array_a + array_a.T) / 2.0
    # check with all possible permutation matrices
    for comb in itertools.permutations(np.arange(4)):
        perm = np.zeros((4, 4))
        perm[np.arange(4), comb] = 1
        # get array_b by permutation
        array_b = np.dot(perm.T, np.dot(array_a, perm))
        # Check
        res = permutation_2sided(array_a, array_b, single=True, guess="umeyama_approx")
        assert_almost_equal(res.t, perm, decimal=6)
        assert_almost_equal(res.error, 0, decimal=6)


@pytest.mark.parametrize("n", np.random.randint(50, 100, (10,)))
def test_permutation_2sided_one_transform_symmetric_umeyama_approx_translate_scale(n):
    r"""Test 2sided-perm with "umeyama_approx" by symmetric with translation and scaling."""
    # define a random, symmetric matrix
    array_a = np.random.uniform(-10.0, 10.0, (n, n))
    array_a = (array_a + array_a.T) / 2.0
    # define array_b by scale-translate array_a and permuting
    shift = np.random.uniform(-10.0, 10.0, n)
    perm = generate_random_permutation_matrix(n)
    array_b = np.dot(perm.T, np.dot((14.7 * array_a + shift), perm))
    # Check
    res = permutation_2sided(array_a, array_b, single=True, guess="umeyama_approx", translate=True,
                             scale=True)
    assert_almost_equal(res.t, perm, decimal=6)
    assert_almost_equal(res.error, 0, decimal=6)
    assert_equal(res.s, None)


@pytest.mark.parametrize("n, ncol, nrow", np.random.randint(50, 100, (10, 3)))
def test_permutation_2sided_single_transform_umeyama_approx_trans_scale_zero_padding(n, ncol, nrow):
    r"""Test 2sided-perm single transf with "umeyama_approx" by arrays with translate, scaling."""
    # define a random, symmetric matrix
    array_a = np.random.uniform(-10.0, 10.0, (n, n))
    array_a = (array_a + array_a.T) / 2.0
    # check with all possible permutation matrices
    perm = generate_random_permutation_matrix(n)
    # Compute the translated, scaled matrix padded with zeros
    array_b = np.dot(perm.T, np.dot(20 * array_a + 9, perm))
    # pad the matrices with zeros
    array_b = np.concatenate((array_b, np.zeros((n, ncol))), axis=1)
    array_b = np.concatenate((array_b, np.zeros((nrow, n + ncol))), axis=0)
    # Check
    res = permutation_2sided(array_a, array_b, single=True, guess="umeyama_approx", unpad_col=True,
                             unpad_row=True, translate=True, scale=True)
    assert_almost_equal(res.t, perm, decimal=6)
    assert_almost_equal(res.error, 0, decimal=6)
    assert_equal(res.s, None)


@pytest.mark.parametrize("n", np.random.randint(50, 100, (10,)))
def test_permutation_2sided_single_transform_normal1(n):
    r"""Test 2sided-perm with "normal1"."""
    # define a random, symmetric matrix
    array_a = np.random.uniform(-10.0, 10.0, (n, n))
    array_a = (array_a + array_a.T) / 2.0
    # define array_b by permuting array_a
    perm = generate_random_permutation_matrix(n)
    array_b = np.dot(perm.T, np.dot(array_a, perm))
    # Check
    res = permutation_2sided(array_a, array_b, single=True, guess="normal1")
    assert_almost_equal(res.t, perm, decimal=6)
    assert_almost_equal(res.error, 0, decimal=6)
    assert_equal(res.s, None)


@pytest.mark.parametrize("n", [3, 4, 5])
def test_permutation_2sided_single_transform_small_normal1_loop(n):
    r"""Test 2sided-perm with "normal1" by small arrays with all permutations."""
    # define a random matrix
    array_a = np.random.uniform(-10.0, 10.0, (n, n))
    array_a = (array_a + array_a.T) / 2.0
    # check with all possible permutation matrices
    for comb in itertools.permutations(np.arange(n)):
        perm = np.zeros((n, n))
        perm[np.arange(n), comb] = 1
        # get array_b by permutation
        array_b = np.dot(perm.T, np.dot(array_a, perm))
        res = permutation_2sided(array_a, array_b, single=True, guess="normal1", iteration=700)
        assert_almost_equal(res.t, perm, decimal=6)
        assert_almost_equal(res.error, 0, decimal=6)
        assert_equal(res.s, None)


@pytest.mark.parametrize("n", np.random.randint(50, 100, (10,)))
def test_permutation_2sided_single_transform_normal1_translate_scale(n):
    r"""Test 2sided-perm with "normal1" with translation and scaling."""
    # define a random, symmetric matrix
    array_a = np.random.uniform(-10.0, 10.0, (n, n))
    array_a = np.dot(array_a, array_a.T)
    # define array_b by scale-translate array_a and permuting
    perm = generate_random_permutation_matrix(n)
    array_b = np.dot(perm.T, np.dot((14.7 * array_a + 3.14), perm))
    res = permutation_2sided(array_a, array_b, single=True, guess="normal1", translate=True,
                             scale=True)
    assert_almost_equal(res.t, perm, decimal=6)
    assert_almost_equal(res.error, 0, decimal=6)
    assert_equal(res.s, None)


@pytest.mark.parametrize("n, ncol, nrow, ncol2, nrow2", np.random.randint(50, 100, (10, 5)))
def test_permutation_2sided_single_normal1_translate_scale_zero_pad(n, ncol, nrow, ncol2, nrow2):
    r"""Test "normal1" by arrays by translation and scaling and zero padding."""
    # define a random matrix
    array_a = np.random.uniform(-10.0, 10.0, (n, n))
    array_a = (array_a + array_a.T) / 2.0
    # check with all possible permutation matrices
    perm = generate_random_permutation_matrix(n)
    # Compute the translated, scaled matrix padded with zeros
    array_b = np.dot(perm.T, np.dot(array_a, perm))
    # pad the matrices with zeros
    array_a = np.concatenate((array_a, np.zeros((n, ncol))), axis=1)
    array_a = np.concatenate((array_a, np.zeros((nrow, n + ncol))), axis=0)
    array_b = np.concatenate((array_b, np.zeros((n, ncol2))), axis=1)
    array_b = np.concatenate((array_b, np.zeros((nrow2, n + ncol2))), axis=0)
    # Check
    res = permutation_2sided(array_a, array_b, single=True, guess="normal1", unpad_col=True,
                             unpad_row=True, translate=True, scale=True)
    assert_almost_equal(res.t, perm, decimal=6)
    assert_almost_equal(res.error, 0, decimal=6)
    assert_equal(res.s, None)


@pytest.mark.parametrize("n", np.random.randint(50, 100, (10,)))
def test_permutation_2sided_single_transform_normal2(n):
    r"""Test 2sided-perm with "normal2"."""
    # define a random, symmetric matrix
    array_a = np.random.uniform(-10.0, 10.0, (n, n))
    array_a = (array_a + array_a.T) / 2.0
    # define array_b by permuting array_a
    perm = generate_random_permutation_matrix(n)
    array_b = np.dot(perm.T, np.dot(array_a, perm))
    res = permutation_2sided(array_a, array_b, single=True, guess="normal2")
    assert_almost_equal(res.t, perm, decimal=6)
    assert_almost_equal(res.error, 0, decimal=6)
    assert_equal(res.s, None)


@pytest.mark.parametrize("n", [3, 4, 5])
def test_permutation_2sided_single_transform_small_normal2_loop(n):
    r"""Test 2sided-perm with "normal2" by small arrays over all permutations."""
    # define a random, symmetric matrix
    array_a = np.random.uniform(-10.0, 10.0, (n, n))
    array_a = (array_a + array_a.T) / 2.0
    # check with all possible permutation matrices
    for comb in itertools.permutations(np.arange(n)):
        # Compute the permutation matrix
        perm = np.zeros((n, n))
        perm[np.arange(n), comb] = 1
        # Compute the translated, scaled matrix padded with zeros
        array_b = np.dot(perm.T, np.dot(array_a, perm))
        # Check
        res = permutation_2sided(array_a, array_b, single=True, guess="normal2", translate=True,
                                 scale=True)
        assert_almost_equal(res.t, perm, decimal=6)
        assert_almost_equal(res.error, 0, decimal=6)
        assert_equal(res.s, None)


@pytest.mark.parametrize("n", np.random.randint(50, 100, (10,)))
def test_permutation_2sided_single_transform_normal2_translate_scale(n):
    r"""Test 2sided-perm single transform with "normal2" with translation and scaling."""
    # generate random symmetric matrix.
    array_a = np.random.uniform(-10.0, 10.0, (n, n))
    array_a = np.dot(array_a, array_a.T)
    # define array_b by scale-translate array_a and permuting
    perm = generate_random_permutation_matrix(n)
    shift = np.random.uniform(-10.0, 10.0, n)
    array_b = np.dot(perm.T, np.dot((14.7 * array_a + shift), perm))
    res = permutation_2sided(array_a, array_b, single=True, guess="normal2", translate=True,
                             scale=True)
    assert_almost_equal(res.t, perm, decimal=6)
    assert_almost_equal(res.error, 0, decimal=6)
    assert_equal(res.s, None)


@pytest.mark.parametrize("n, ncol, nrow, ncol2, nrow2", np.random.randint(50, 100, (10, 5)))
def test_permutation_2sided_single_normal2_translate_scale_zero_pad(n, ncol, nrow, ncol2, nrow2):
    r"""Test 2sided-perm single with "normal2" by with translation, scaling and zero paddings."""
    # define a random, symmetric matrix
    array_a = np.random.uniform(-10.0, 10.0, (n, n))
    array_a = (array_a + array_a.T) / 2.0
    # check with all possible permutation matrices
    perm = generate_random_permutation_matrix(n)
    # Compute the translated, scaled matrix padded with zeros
    array_b = np.dot(perm.T, np.dot(array_a, perm))
    # pad the matrices with zeros
    array_a = np.concatenate((array_a, np.zeros((n, ncol))), axis=1)
    array_a = np.concatenate((array_a, np.zeros((nrow, n + ncol))), axis=0)
    array_b = np.concatenate((array_b, np.zeros((n, ncol2))), axis=1)
    array_b = np.concatenate((array_b, np.zeros((nrow2, n + ncol2))), axis=0)
    # Check
    res = permutation_2sided(array_a, array_b, single=True, guess="normal2", unpad_col=True,
                             unpad_row=True, translate=True, scale=True)
    assert_almost_equal(res.t, perm, decimal=6)
    assert_almost_equal(res.error, 0, decimal=6)
    assert_equal(res.s, None)


def test_permutation_2sided_invalid_mode_argument():
    r"""Test 2sided-perm with invalid mode argument."""
    # define a random matrix
    array_a = np.array([[4, 5, 3, 3], [5, 7, 3, 5], [3, 3, 2, 2], [3, 5, 2, 5]])
    # define array_b by permuting array_a
    perm = np.array([[0., 0., 1., 0.], [1., 0., 0., 0.], [0., 0., 0., 1.], [0., 1., 0., 0.]])
    array_b = np.dot(perm.T, np.dot(array_a, perm))
    assert_raises(ValueError, permutation_2sided, array_a, array_b, single=True, guess="nature")


def test_permutation_2sided_regular():
    r"""Test regular 2sided-perm by practical example."""
    # Example taken from page 64 in parallel solution of
    # svd-related problems, with applications
    # vummath.ma.man.ac.uk/~higham/links/theses/papad93.pdf
    array_m = np.array([[32, 14, 3, 63, 50],
                        [24, 22, 1, 56, 4],
                        [94, 16, 28, 75, 81],
                        [19, 72, 42, 90, 54],
                        [71, 85, 10, 96, 58]])
    array_n = np.array([[58, 96, 85, 10, 71],
                        [81, 75, 16, 28, 94],
                        [4, 56, 22, 1, 24],
                        [54, 90, 72, 42, 19],
                        [50, 63, 14, 3, 32]])
    array_p = np.array([[0, 0, 0, 0, 1],
                        [0, 0, 1, 0, 0],
                        [0, 1, 0, 0, 0],
                        [0, 0, 0, 1, 0],
                        [1, 0, 0, 0, 0]])
    array_q = np.array([[0, 0, 0, 0, 1],
                        [0, 0, 0, 1, 0],
                        [0, 1, 0, 0, 0],
                        [0, 0, 1, 0, 0],
                        [1, 0, 0, 0, 0]])
    result = permutation_2sided(array_n, array_m, single=False)
    assert_almost_equal(result.s, array_p, decimal=6)
    assert_almost_equal(result.t, array_q, decimal=6)
    assert_almost_equal(result.error, 0, decimal=6)


def test_permutation_2sided_regular2():
    r"""Test regular 2sided-perm by 4by4 random arrays."""
    # define a random matrix
    array_n = np.array([[0.74163916, 0.82661152, 0.26856538, 0.23777467],
                        [0.06530971, 0.28429819, 0.44244327, 0.79478503],
                        [0.83645105, 0.49704302, 0.34292989, 0.01406331],
                        [0.04351473, 0.85459821, 0.00663386, 0.62464223]])
    array_p = np.array([[0, 0, 1, 0],
                        [1, 0, 0, 0],
                        [0, 1, 0, 0],
                        [0, 0, 0, 1]])
    array_q = array_p.T
    array_m = np.dot(np.dot(array_p, array_n), array_q)
    result = permutation_2sided(array_m, array_n, single=False)
    assert_almost_equal(result.s, array_q, decimal=6)
    assert_almost_equal(result.t, array_p, decimal=6)
    assert_almost_equal(result.error, 0, decimal=6)


@pytest.mark.parametrize("n", np.random.randint(3, 6, (3,)))
def test_permutation_2sided_regular_with_kopt(n):
    r"""Test regular 2sided permutation with kopt."""
    array_a = np.random.uniform(-10.0, 10.0, (n, n))
    perm_p = generate_random_permutation_matrix(n)
    perm_q = generate_random_permutation_matrix(n)
    array_b = perm_q.dot(array_a.dot(perm_p))
    result = permutation_2sided(array_b, array_a, single=False, kopt=n)
    assert_almost_equal(result.s, perm_q, decimal=6)
    assert_almost_equal(result.t, perm_p.T, decimal=6)
    assert_almost_equal(result.error, 0, decimal=6)


def test_permutation_2sided_regular_unsquared():
    r"""Test regular 2sided-perm by unsquared 4by2 random arrays."""
    array_n = np.array([[6, 8], [10, 8], [5, 8], [5, 7]])
    perm_p = np.array([[0, 1, 0, 0], [0, 0, 1, 0],
                       [1, 0, 0, 0], [0, 0, 0, 1]])
    perm_q = np.array([[0, 1], [1, 0]])
    array_m = np.linalg.multi_dot([perm_p, array_n, perm_q])
    result = permutation_2sided(array_n, array_m, single=False, iteration=500)
    assert_almost_equal(result.s, perm_p, decimal=6)
    assert_almost_equal(result.t, perm_q, decimal=6)
    assert_almost_equal(result.error, 0, decimal=6)


def test_permutation_2sided_regular_unsquared_negative():
    r"""Test regular 2sided-perm by unsquared negative 6by4 random arrays."""
    # build random matrix by seed 999
    np.random.seed(999)
    array_n = np.random.randint(-5, 6, size=(6, 4))
    array_n = np.float_(array_n)
    perm_p = np.random.permutation(np.eye(6, 6))
    perm_q = np.random.permutation(np.eye(4, 4))
    array_m = np.linalg.multi_dot([perm_p, array_n, perm_q])
    result = permutation_2sided(array_m, array_n, single=False, iteration=500)
    assert_almost_equal(result.s, perm_p, decimal=6)
    assert_almost_equal(result.t, perm_q, decimal=6)
    assert_almost_equal(result.error, 0, decimal=6)


@pytest.mark.parametrize("n", np.random.randint(10, 100, (10,)))
def test_permutation_2sided_single_directed(n):
    r"""Test 2sided-perm with single transform and directed."""
    # A random array
    array_a = np.random.uniform(-10.0, 10.0, (n, n))
    # permutation
    perm = generate_random_permutation_matrix(n)
    # permuted array_b
    array_b = np.dot(perm.T, np.dot(array_a, perm))
    # Procrustes with no translate and scale
    result = permutation_2sided(array_a, array_b, single=True)
    assert_almost_equal(result.t, perm, decimal=6)
    assert_almost_equal(result.error, 0., decimal=6)


@pytest.mark.parametrize("n", [3, 4, 5])
def test_permutation_2sided_single_transform_directed_all_permutations(n):
    r"""Test 2sided-perm with "directed" over all permutations."""
    # define a random matrix
    array_a = np.random.uniform(-10.0, 10.0, (n, n))
    # check with all possible permutation matrices
    for comb in itertools.permutations(np.arange(n)):
        perm = np.zeros((n, n))
        perm[np.arange(n), comb] = 1
        # get array_b by permutation
        array_b = np.dot(perm.T, np.dot(array_a, perm))
        result = permutation_2sided(array_a, array_b, single=True)
        assert_almost_equal(result.t, perm, decimal=6)
        assert_almost_equal(result.error, 0, decimal=6)


@pytest.mark.parametrize("n", np.random.randint(50, 100, (10,)))
def test_permutation_2sided_single_directed_translate_scale(n):
    r"""Test 2sided-perm single transform with "directed" and translation, and scaling."""
    # A random array
    array_a = np.random.uniform(-10.0, 10.0, (n, n))
    # permutation
    perm = generate_random_permutation_matrix(n)
    # permuted array_b
    array_b = np.dot(perm.T, np.dot(15.3 * array_a + 5.45, perm))
    # Procrustes with no translate and scale
    result = permutation_2sided(array_a, array_b, single=True, translate=True, scale=True)
    assert_almost_equal(result.t, perm, decimal=6)
    assert_almost_equal(result.error, 0., decimal=6)
    assert_equal(result.s, None)


@pytest.mark.parametrize("n", np.random.randint(50, 100, (10,)))
def test_permutation_2sided_single_directed_translate_scale_padding(n):
    r"""Test 2sided-perm single transform directed with translation, scaling and zero paddings."""
    # A random array
    array_a = np.random.uniform(-10.0, 10.0, (n, n))
    # permutation
    perm = generate_random_permutation_matrix(n)
    # permuted array_b
    array_b = np.dot(perm.T, np.dot(15.3 * array_a + 5.45, perm))
    # pad the matrices with zeros
    array_a = np.concatenate((array_a, np.zeros((n, 3))), axis=1)
    array_a = np.concatenate((array_a, np.zeros((10, n + 3))), axis=0)
    array_b = np.concatenate((array_b, np.zeros((n, 2))), axis=1)
    array_b = np.concatenate((array_b, np.zeros((6, n + 2))), axis=0)
    # Procrustes with no translate and scale
    result = permutation_2sided(array_a, array_b,
                                single=True,
                                translate=True,
                                scale=True,
                                unpad_col=True,
                                unpad_row=True
                                )
    assert_almost_equal(result.t, perm, decimal=6)
    assert_almost_equal(result.error, 0., decimal=6)


@pytest.mark.parametrize("n", [3, 4, 5])
def test_permutation_2sided_single_transform_with_kopt_all_permutations(n):
    r"""Test 2sided-perm single transform with kopt over all permutations."""
    # define a random matrix
    array_a = np.random.uniform(-10.0, 10.0, (n, n))
    # check with all possible permutation matrices
    for comb in itertools.permutations(np.arange(n)):
        perm = np.zeros((n, n))
        perm[np.arange(n), comb] = 1
        # get array_b by permutation
        array_b = np.dot(perm.T, np.dot(array_a, perm))
        result = permutation_2sided(array_a, array_b, single=True, kopt=n)
        assert_almost_equal(result.t, perm, decimal=6)
        assert_almost_equal(result.error, 0, decimal=6)
        assert_equal(result.s, None)


@pytest.mark.parametrize("n", np.random.randint(3, 8, (3,)))
def test_permutation_2sided_explicit_translate_scale(n):
    r"""Test 2-sided permutation with explicit method by 4by4 method."""
    # define a random matrix
    array_a = np.random.uniform(-10.0, 10.0, (n, n))
    # define array_b by scale-translate array_a and permuting
    shift = 2.14
    perm = generate_random_permutation_matrix(n)
    array_b = np.dot(perm.T, np.dot((14.7 * array_a + shift), perm))
    # check
    result = permutation_2sided(array_a, array_b, translate=True, scale=True,
                                single=True, kopt=n)
    assert_almost_equal(result.t, perm, decimal=6)
    assert_almost_equal(result.error, 0, decimal=6)
    assert_equal(result.s, None)


@pytest.mark.parametrize("n, ncol, nrow", np.random.randint(5, 10, (5, 3)))
def test_permutation_2sided_single_kopt_translate_scale_zero_padding(n, ncol, nrow):
    r"""Test 2sided perm, single transform with kopt with translation, scaling and zero padding."""
    # define a random matrix
    array_a = np.random.uniform(-10.0, 10.0, (n, n))
    # check with all possible permutation matrices
    perm = generate_random_permutation_matrix(n)
    # Compute the translated, scaled matrix padded with zeros
    array_b = np.dot(perm.T, np.dot(20 * array_a + 9, perm))
    # pad the matrices with zeros
    array_b = np.concatenate((array_b, np.zeros((n, ncol))), axis=1)
    array_b = np.concatenate((array_b, np.zeros((nrow, n + ncol))), axis=0)
    result = permutation_2sided(array_a, array_b, unpad_row=True, unpad_col=True,
                                translate=True, scale=True, kopt=n, single=True)
    assert_almost_equal(result.t, perm, decimal=6)
    assert_almost_equal(result.error, 0, decimal=6)
    assert_equal(result.s, None)


def test_permutation_2sided_invalid_input_kopt_single_transform():
    r"""Test 2-sided permutation with invalid inputs to kopt and single transform."""
    # define a random matrix and symmetric matrix
    array_a = np.array([[4, 5, 3, 3], [5, 7, 3, 5], [3, 3, 2, 2], [3, 5, 2, 5]])
    # define array_b by permuting array_a
    perm = np.array([[0., 0., 1., 0.], [1., 0., 0., 0.],
                     [0., 0., 0., 1.], [0., 1., 0., 0.]])
    array_b = np.dot(perm.T, np.dot(array_a, perm))
    # check
    assert_raises(TypeError, permutation_2sided, array_a, array_b, single="invalid")
    assert_raises(TypeError, permutation_2sided, array_a, array_b, single=True, kopt=20.1)
    assert_raises(ValueError, permutation_2sided, array_a, np.eye(20), single=True, pad=False)


def test_permutation_2sided_dominators_zero():
    """Test two-sided permutations which has zeros in the dominator in updating step."""
    array_a = np.array([[6, 3, 0, 0],
                        [3, 6, 1, 0],
                        [0, 1, 6, 2],
                        [0, 0, 2, 6]])
    array_b = np.array([[6, 3, 0, 0, 0, 0, 0],
                        [3, 6, 1, 0, 0, 0, 0],
                        [0, 1, 6, 1, 0, 1, 1],
                        [0, 0, 1, 6, 2, 0, 0],
                        [0, 0, 0, 2, 6, 0, 0],
                        [0, 0, 1, 0, 0, 6, 0],
                        [0, 0, 1, 0, 0, 0, 6]])
    res = permutation_2sided(array_a, array_b,
                             single=True,
                             unpad_col=False,
                             unpad_row=False,
                             scale=False,
                             pad=True)
    perm = np.array([[1, 0, 0, 0, 0, 0, 0],
                     [0, 1, 0, 0, 0, 0, 0],
                     [0, 0, 0, 1, 0, 0, 0],
                     [0, 0, 0, 0, 1, 0, 0],
                     [0, 0, 1, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 1, 0],
                     [0, 0, 0, 0, 0, 0, 1]])
    assert_almost_equal(res["t"], perm)
