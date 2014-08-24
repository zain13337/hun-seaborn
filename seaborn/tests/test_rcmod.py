import numpy as np
import matplotlib as mpl
from distutils.version import LooseVersion

import nose
import nose.tools as nt
import numpy.testing as npt

from .. import rcmod


class RCParamTester(object):

    def flatten_list(self, orig_list):

        iter_list = map(np.atleast_1d, orig_list)
        flat_list = [item for sublist in iter_list for item in sublist]
        return flat_list

    def assert_rc_params(self, params):

        for k, v in params.items():
            if k == "svg.embed_char_paths":
                # This param causes test issues and is deprecated anyway
                continue
            elif isinstance(v, np.ndarray):
                npt.assert_array_equal(mpl.rcParams[k], v)
            else:
                nt.assert_equal((k, mpl.rcParams[k]), (k, v))


class TestAxesStyle(RCParamTester):

    styles = ["white", "dark", "whitegrid", "darkgrid", "ticks"]

    def test_default_return(self):

        current = rcmod.axes_style()
        self.assert_rc_params(current)

    def test_key_usage(self):

        _style_keys = set(rcmod._style_keys)
        for style in self.styles:
            nt.assert_true(not set(rcmod.axes_style(style)) ^ _style_keys)

    def test_bad_style(self):

        with nt.assert_raises(ValueError):
            rcmod.axes_style("i_am_not_a_style")

    def test_rc_override(self):

        rc = {"axes.facecolor": "blue", "foo.notaparam": "bar"}
        out = rcmod.axes_style("darkgrid", rc)
        nt.assert_equal(out["axes.facecolor"], "blue")
        nt.assert_not_in("foo.notaparam", out)

    def test_set_style(self):

        for style in self.styles:

            style_dict = rcmod.axes_style(style)
            rcmod.set_style(style)
            self.assert_rc_params(style_dict)

    def test_style_context_manager(self):

        rcmod.set_style("darkgrid")
        orig_params = rcmod.axes_style()
        with rcmod.axes_style("whitegrid"):
            context_params = rcmod.axes_style("whitegrid")
            self.assert_rc_params(context_params)
        self.assert_rc_params(orig_params)

    def test_style_context_independence(self):

        nt.assert_true(set(rcmod._style_keys) ^ set(rcmod._context_keys))

    def test_set_rc(self):

        rcmod.set(rc={"lines.linewidth": 4})
        nt.assert_equal(mpl.rcParams["lines.linewidth"], 4)
        rcmod.set()

    def test_reset_defaults(self):

        # Changes to the rc parameters make this test hard to manage
        # on older versions of matplotlib, so we'll skip it
        if LooseVersion(mpl.__version__) < LooseVersion("1.3"):
            raise nose.SkipTest

        rcmod.reset_defaults()
        self.assert_rc_params(mpl.rcParamsDefault)
        rcmod.set()

    def test_reset_orig(self):

        # Changes to the rc parameters make this test hard to manage
        # on older versions of matplotlib, so we'll skip it
        if LooseVersion(mpl.__version__) < LooseVersion("1.3"):
            raise nose.SkipTest

        rcmod.reset_orig()
        self.assert_rc_params(mpl.rcParamsOrig)
        rcmod.set()


class TestPlottingContext(RCParamTester):

    contexts = ["paper", "notebook", "talk", "poster"]

    def test_default_return(self):

        current = rcmod.plotting_context()
        self.assert_rc_params(current)

    def test_key_usage(self):

        _context_keys = set(rcmod._context_keys)
        for context in self.contexts:
            missing = set(rcmod.plotting_context(context)) ^ _context_keys
            nt.assert_true(not missing)

    def test_bad_context(self):

        with nt.assert_raises(ValueError):
            rcmod.plotting_context("i_am_not_a_context")

    def test_font_scale(self):

        notebook_ref = rcmod.plotting_context("notebook")
        notebook_big = rcmod.plotting_context("notebook", 2)

        font_keys = ["axes.labelsize", "axes.titlesize", "legend.fontsize",
                     "xtick.labelsize", "ytick.labelsize"]

        for k in font_keys:
            nt.assert_equal(notebook_ref[k] * 2, notebook_big[k])

    def test_rc_override(self):

        key, val = "grid.linewidth", 5
        rc = {key: val, "foo": "bar"}
        out = rcmod.plotting_context("talk", rc=rc)
        nt.assert_equal(out[key], val)
        nt.assert_not_in("foo", out)

    def test_set_context(self):

        for context in self.contexts:

            context_dict = rcmod.plotting_context(context)
            rcmod.set_context(context)
            self.assert_rc_params(context_dict)

    def test_context_context_manager(self):

        rcmod.set_context("notebook")
        orig_params = rcmod.plotting_context()
        with rcmod.plotting_context("paper"):
            context_params = rcmod.plotting_context("paper")
            self.assert_rc_params(context_params)
        self.assert_rc_params(orig_params)