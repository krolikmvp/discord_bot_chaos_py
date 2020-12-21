import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys


# Class responsible for creating messages stats plots
class StatPlot:

    def __init__(self, graph_dict, plot_file_name="demo.png"):

        self.graph_dict = graph_dict
        self.suffix = None
        self.x_label = None
        self.y_label = 'Messages'
        self.plot_default_name = plot_file_name

    def plot_day_stats(self):
        self.suffix =':00'
        self.x_label = 'Hour'
        return self._create_plot()

    def plot_month_stats(self):
        self.suffix = ''
        self.x_label = 'Day'
        return self._create_plot()

    def _create_plot(self):
        """
        Creates a plot and returns path to the plot file
        """
        xs = [x + self.suffix for x in self.graph_dict.keys()]
        ys = [int(y) for y in self.graph_dict.values()]

        fig, ax = plt.subplots()
        ax.bar(xs,ys)
        ax.set_ylabel(self.y_label)
        ax.set_xlabel(self.x_label)

        ax.set_ylabel(self.y_label)
        plt.setp(ax.get_xticklabels(), rotation=90, horizontalalignment='right', fontsize='x-small')
        plt.savefig(self.plot_default_name, bbox_inches='tight')

        return self.plot_default_name