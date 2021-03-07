# External modules:
import pandas as pd


class TechnicalAnalysis:
    # Class to calculate technical analysis tools and parameters.
    # For example resistance and support levels and trends.

    def __init__(self, ticker):
        self._ticker = ticker
        self._df = None  # dataframe to to analysis on
        self._resistance = None  # dataframe
        self._support = None  # dataframe
        self._resistance_update_date = None  # datetime
        self._support_update_date = None  # datetime

    def set_df(self, df):
        self._df = df

    def get_resistance_levels(self):
        return self._resistance

    def get_support_levels(self):
        return self._support

    def get_closest_resistance_levels(self):
        resistance_df = pd.DataFrame(self._resistance[(self._resistance.Importance > 0)])
        return resistance_df.nsmallest(3, 'High')

    def get_closest_support_levels(self):
        support_df = pd.DataFrame(self._support[(self._support.Importance > 0)])
        return support_df.nlargest(3, 'Low')

    def find_resistance_levels(self, resistance_threshold=0.01):
        # Create a resistance data frame where the resistance points are defined as where the local maxima is found
        # where the price is higher than last closing value.
        # In addition, a column for the importance of the resistance point is also calculated where the importance is
        # started at 0 and can increase in two ways. One way is that the volume on the day where
        # the resistance point was found is higher than the average volume. The second way is that
        # the resistance point gets repeated more or less (depending on the resistance_threshold.
        # If the volume is also here higher than the mean value of volume during the period,
        # the importance point gets increased by 1.

        self._get_possible_resistance_points()
        self._update_resistance_with_importance_column()
        self._update_importance_of_resistance_df(resistance_threshold)
        self._filter_out_paired('Resistance')

    def find_support_levels(self, support_threshold=0.01):
        # Create a support data frame where the support points are defined as where the local minima is found
        # where the price is lower than last closing value.
        # In addition, a column for the importance of the support point is also calculated where the importance is
        # started at 0 and can increase in two ways. One way is that the volume on the day where
        # the support point was found is higher than the average volume. The second way is that
        # the support point gets repeated more or less (depending on the support_threshold.
        # If the volume is also here higher than the mean value of volume during the period,
        # the importance point gets increased by 1.

        self._get_possible_support_points()
        self._update_support_with_importance_column()
        self._update_importance_of_support_df(support_threshold)
        self._filter_out_paired('Support')

    def _get_possible_resistance_points(self):
        last_close = self._df.Close[-1]
        self._resistance_update_date = self._df.index[-1].date()
        self._resistance = pd.DataFrame(self._df.High[(self._df.High.shift(1) < self._df.High)
                                                & (self._df.High.shift(-1) < self._df.High)
                                                & (self._df.High > last_close)])

    def _get_possible_support_points(self):
        last_close = self._df.Close[-1]
        self._support_update_date = self._df.index[-1].date()
        self._support = pd.DataFrame(self._df.Low[(self._df.Low.shift(1) > self._df.Low)
                                                 & (self._df.Low.shift(-1) > self._df.Low)
                                                 & (self._df.Low < last_close)])

    def _update_resistance_with_importance_column(self):
        self._resistance['Importance'] = 0

    def _update_support_with_importance_column(self):
        self._support['Importance'] = 0

    def _reset_index_of_resistance(self):
        self._resistance.reset_index(inplace=True)

    def _reset_index_of_support(self):
        self._support.reset_index(inplace=True)

    def _set_date_as_index_of_resistance(self):
        self._resistance.set_index('Date', inplace=True)

    def _set_date_as_index_of_support(self):
        self._support.set_index('Date', inplace=True)

    def _is_resistance_row_already_paired_index_based(self, i):
        return self._resistance.loc[i, 'Importance'] == -1

    def _is_support_row_already_paired_index_based(self, i):
        return self._support.loc[i, 'Importance'] == -1

    def _get_thresholds(self, level, threshold):
        return level + level*threshold, level - level*threshold

    def _update_importance_of_resistance_df(self, resistance_threshold):
        self._reset_index_of_resistance() # Used as its easier to iterate with indexes as numbers
        volume_mean = self._df['Volume'].mean()

        for i in range(0, len(self._resistance)):
            if self._is_resistance_row_already_paired_index_based(i):
                continue

            resistance_level = self._resistance.loc[i, 'High']

            # If volume is higher than mean the importance increases by 1:
            date = self._resistance.loc[i, 'Date']
            if self._df['Volume'][date] > volume_mean:
                self._resistance.loc[i, 'Importance'] += 1

            # Find threshold for comparing resistance level:
            up_threshold, down_threshold = self._get_thresholds(resistance_level, resistance_threshold)

            # See if the resistance level gets repeated:
            for j in range(i+1, len(self._resistance)):
                if self._is_resistance_row_already_paired_index_based(j):
                    continue

                comparing_resistance_level = self._resistance.loc[j, 'High']
                if down_threshold < comparing_resistance_level < up_threshold:
                    self._resistance.loc[i, 'Importance'] += 1

                    # Importance of the paired gets added into the original resistance level
                    self._resistance.loc[i, 'Importance'] += self._resistance.loc[j, 'Importance']
                    self._resistance.loc[j, 'Importance'] = -1  # to indicate that this is already paired.

        self._set_date_as_index_of_resistance()  # to put back to dates as index

    def _filter_out_paired(self, type):
        if type == 'Resistance':
            is_not_paired = self._resistance['Importance'] >= 0
            self._resistance = self._resistance[is_not_paired]
        elif type == 'Support':
            is_not_paired = self._support['Importance'] >= 0
            self._support = self._support[is_not_paired]

    def _update_importance_of_support_df(self, support_threshold):
        self._reset_index_of_support()  # Used as its easier to iterate with indexes as numbers
        volume_mean = self._df['Volume'].mean()

        for i in range(0, len(self._support)):
            if self._is_support_row_already_paired_index_based(i):
                continue

            support_level = self._support.loc[i, 'Low']

            # If volume is higher than mean the importance increases by 1:
            date = self._support.loc[i, 'Date']
            if self._df['Volume'][date] > volume_mean:
                self._support.loc[i, 'Importance'] += 1

            # Find threshold for comparing support level:
            up_threshold, down_threshold = self._get_thresholds(support_level, support_threshold)

            # See if the support level gets repeated:
            for j in range(i+1, len(self._support)):
                if self._is_support_row_already_paired_index_based(j):
                    continue

                comparing_support_level = self._support.loc[j, 'Low']
                if down_threshold < comparing_support_level < up_threshold:
                    self._support.loc[i, 'Importance'] += 1

                    # Importance of the paired gets added into the original support level
                    self._support.loc[i, 'Importance'] += self._support.loc[j, 'Importance']
                    self._support.loc[j, 'Importance'] = -1  # to indicate that this is already paired.

        self._set_date_as_index_of_support()  # to put back to dates as index






