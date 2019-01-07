import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict


class BlankDetector(object):
    """
    This is a very simple detector which we look at in
    Section 00 (Introduction) of this tutorial. This serves as a
    good skeleton on how to override the methods of our base
    ChangeDetector class.
    """

    def __init__(self):
        super(BlankDetector, self).__init__()
        # Initialize all variables needed here
        self.total_val = 0

        # Initialize residuals here.
        #   All attributes ending with underscore '_' are treated
        #   as residuals.
        self.mean_ = np.nan

    def update_residuals(self, new_signal_value):
        """This method is called for every new signal value.
        Use this space to update variables and residuals"""
        self._update_base_residuals(new_signal_value)

        # Update your attributes here
        self.total_val += new_signal_value

        # Update your residuals here
        #  Here's an example residual that calculates mean
        self.mean_ = self.total_val / self.signal_size

    def check_stopping_rules(self, new_signal_value):
        """This method is called for every new signal value,
        AFTER the attributes and residuals have been updated.
        Use this space to check if a stopping rule has been
        triggered. Set self.rules_triggered to True or False
        accordingly."""
        self.rules_triggered = False


class ChangeDetector(object):
    """
    A change detection algorithm.
    The algorithm calculates residuals and updates them for each new value
    passed. Residuals are checked against stopping rules at each change,
    yielding either True or False, accordingly.
    """

    def __init__(self):
        self.rules_triggered = False
        self.has_started = False
        # Interim and calculated values
        self.signal_size = 0

        # Residuals
        #   All attributes ending in underscore (_) are treated as
        #   residual values (for plotting, printing, etc)
        #   e.g. self.mean_ = np.nan
        pass

    def update_residuals(self, new_signal_value):
        """
        Updates residuals.
        Override this method when writing your own change detector based on
        this class.
        """
        self._update_base_residuals(new_signal_value)
        # Update your residuals here
        pass

    def check_stopping_rules(self, new_signal_value):
        """
        Check Stopping Rules.
        Override this method when writing your own change detector based on
        this class
        """
        # Implemente your stopping rules here
        # Set self.rules_triggered to True when triggered
        pass

    """
    Internal methods
    -------------------
    leave the following methods alone. You should only need to override or edit
    above this line in order to implement your own change detector.
    """

    @property
    def residuals_(self):
        return self._get_residual_dict()

    def _update_base_residuals(self, x):
        """
        Input
         x: scalar, float.
            is the new signal value obtained for this step.
        Base residuals
         k: int
            the total signal size seen so far.
            TEMP: Currently called signal_size for clarity
        """
        # We'll always use these
        self.signal_size += 1

    def _get_residual_dict(self):
        """create a dictionary of residuals to return.
        Inclues all class and instance variables ending in '_'
        """
        residuals_dict = {}
        for k, v in self.__dict__.items():
            if k.endswith('_'):
                residuals_dict[k] = v

        return residuals_dict

    def _step(self, new_signal_value):
        """Internal method to "step", digest one new signal point."""
        self.has_started = True

        # Update residuals
        self.update_residuals(new_signal_value)

        # Compare residuals to stopping_rules
        self.check_stopping_rules(new_signal_value)

        yield self._get_residual_dict()

    def step(self, new_signal_value):
        return self._step(new_signal_value)

    def __repr__(self):
        return "Change Detector(triggered={}, residuals={})".format(
            self.rules_triggered, self.residuals_)


class OnlineSimulator(object):
    def __init__(self, change_detector, signal):
        """
        Simulates an online streaming scenario for change
        detection experiments.
        Given a signal and a change detector, this simulator passes one signal
        data point at a time to the change detector and processes the results.
        inputs
        ------------------------
        signal: np.array
        change_detector: class change_detector
        """
        self.signal = signal
        self.change_detector = change_detector
        self.signal_size = len(signal)

    def run(self, plot=True, **kwargs):
        signal = self.signal
        detector = self.change_detector

        # Check
        if detector.has_started is True:
            raise Exception("Detector must be re-initialized.")

        # Run simulation
        residuals_history = defaultdict(list)
        for value in signal:
            # Step to get residuals and check stopping rules
            res = next(detector.step(value))

            # Store residual_history (for plotting only)
            for k, v in res.items():
                residuals_history[k].append(v)

            if detector.rules_triggered is True:
                break

        def dict_to_arrays(ddict):
            """Convenience func to bundle residuals into a dict"""
            new_dict = {}
            for k, v in ddict.items():
                new_dict[k] = np.array(v)
            return new_dict

        residuals_history = dict_to_arrays(residuals_history)
        self.residuals_history = residuals_history

        # Display results
        if plot is True:
            self.display_results(**kwargs)

        return detector.rules_triggered

    def display_results(self, signal_name='Signal', **kwargs):
        signal = self.signal
        detector = self.change_detector
        residuals_history = self.residuals_history
        """Print out the results of our experiment. """

        print("Residuals: {}".format([res for res in residuals_history.keys()]))

        # Print results
        if detector.rules_triggered is True:
            # Length of any residual array tells us when the rule was triggered
            # some_res = residuals_history.values().next()
            sample_history = list(residuals_history.values())[0]
            stop_point = len(sample_history) - 1
            # Quick sanity check
            assert (stop_point > 0) & (stop_point <= len(signal))
            print("Change detected. Stopping Rule triggered at {}.\n".format(stop_point))
        else:
            stop_point = None
            print("Stopping rule not triggered.")

        # Generate axes to plot signal and residuals"""
        plotcount = 1 + len(residuals_history)
        fig, axes = plt.subplots(
            nrows=plotcount, ncols=1, sharex=True, figsize=(12, plotcount * 3))

        # Plot the signal
        if plotcount > 1:
            ax = axes[0]
        elif plotcount == 1:
            ax = axes

        ax.plot(signal, 'b.')
        ax.plot(signal, 'b-', alpha=0.15)
        ax.set_title(signal_name)

        # Scale signal
        ax.set_ylim(np.nanmin(signal) * .5, np.nanmax(signal) * 1.5)
        ax.set_xlim(0, len(signal))

        # Plot a horizontal line where the stop_point is indicated
        if detector.rules_triggered is True:
            ax.vlines(
                x=stop_point,
                ymin=0,
                ymax=ax.get_ylim()[1],
                colors='r',
                linestyles='dotted')

        # Plot each residual
        for ii, (res_name,
                 res_values) in enumerate(residuals_history.items()):
            ax = axes[ii + 1]
            ax.plot(res_values, 'g.', alpha=0.7)
            ax.set_title("Residual #{}: {}".format(ii + 1, res_name))
            ax.set_ylim(
                np.nanmin(res_values) * 0.5,
                np.nanmax(res_values) * 1.5)
            if stop_point is not None:
                ax.vlines(
                    x=stop_point,
                    ymin=0,
                    ymax=ax.get_ylim()[1],
                    colors='r',
                    linestyles='dotted')
