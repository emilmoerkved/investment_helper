import pandas as pd

# Class to calculate technical analysis tools and parameters.
# For example resistance and support levels and trends.


class TechnicalAnalysis:

    def __init__(self, ticker):
        self.ticker = ticker
        self.df = 0  # dataframe to to analysis on
        self.resistance = 0  # dataframe
        self.support = 0  # dataframe
        self.resistance_update_date = 0  # datetime
        self.support_update_date = 0  # datetime

    def set_df(self, df):
        self.df = df

    def get_resistance_levels(self):
        return self.resistance

    def get_support_levels(self):
        return self.support

    def get_closest_resistance_levels(self):
        resistance_df = pd.DataFrame(self.resistance[(self.resistance.Importance > 0)])
        return resistance_df.nsmallest(3, 'High')

    def get_closest_support_levels(self):
        support_df = pd.DataFrame(self.support[(self.support.Importance > 0)])
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
        last_close = self.df.Close[-1]
        self.resistance_update_date = self.df.index[-1].date()
        self.resistance = pd.DataFrame(self.df.High[(self.df.High.shift(1) < self.df.High)
                                                & (self.df.High.shift(-1) < self.df.High)
                                                & (self.df.High > last_close)])

    def _get_possible_support_points(self):
        last_close = self.df.Close[-1]
        self.support_update_date = self.df.index[-1].date()
        self.support = pd.DataFrame(self.df.Low[(self.df.Low.shift(1) > self.df.Low)
                                                 & (self.df.Low.shift(-1) > self.df.Low)
                                                 & (self.df.Low < last_close)])

    def _update_resistance_with_importance_column(self):
        self.resistance['Importance'] = 0

    def _update_support_with_importance_column(self):
        self.support['Importance'] = 0

    def _reset_index_of_resistance(self):
        self.resistance.reset_index(inplace=True)

    def _reset_index_of_support(self):
        self.support.reset_index(inplace=True)

    def _set_date_as_index_of_resistance(self):
        self.resistance.set_index('Date', inplace=True)

    def _set_date_as_index_of_support(self):
        self.support.set_index('Date', inplace=True)

    def _is_resistance_row_already_paired_index_based(self, i):
        return self.resistance.loc[i, 'Importance'] == -1

    def _is_support_row_already_paired_index_based(self, i):
        return self.support.loc[i, 'Importance'] == -1

    def _get_thresholds(self, level, threshold):
        return level + level*threshold, level - level*threshold

    def _update_importance_of_resistance_df(self, resistance_threshold):
        self._reset_index_of_resistance() # Used as its easier to iterate with indexes as numbers
        volume_mean = self.df['Volume'].mean()

        for i in range(0, len(self.resistance)):
            if self._is_resistance_row_already_paired_index_based(i):
                continue

            resistance_level = self.resistance.loc[i, 'High']

            # If volume is higher than mean the importance increases by 1:
            date = self.resistance.loc[i, 'Date']
            if self.df['Volume'][date] > volume_mean:
                self.resistance.loc[i, 'Importance'] += 1

            # Find threshold for comparing resistance level:
            up_threshold, down_threshold = self._get_thresholds(resistance_level, resistance_threshold)

            # See if the resistance level gets repeated:
            for j in range(i+1, len(self.resistance)):
                if self._is_resistance_row_already_paired_index_based(j):
                    continue

                comparing_resistance_level = self.resistance.loc[j, 'High']
                if down_threshold < comparing_resistance_level < up_threshold:
                    self.resistance.loc[i, 'Importance'] += 1

                    # Importance of the paired gets added into the original resistance level
                    self.resistance.loc[i, 'Importance'] += self.resistance.loc[j, 'Importance']
                    self.resistance.loc[j, 'Importance'] = -1  # to indicate that this is already paired.

        self._set_date_as_index_of_resistance()  # to put back to dates as index

    def _filter_out_paired(self, type):
        if type == 'Resistance':
            is_not_paired = self.resistance['Importance'] >= 0
            self.resistance = self.resistance[is_not_paired]
        elif type == 'Support':
            is_not_paired = self.support['Importance'] >= 0
            self.support = self.support[is_not_paired]

    def _update_importance_of_support_df(self, support_threshold):
        self._reset_index_of_support() # Used as its easier to iterate with indexes as numbers
        volume_mean = self.df['Volume'].mean()

        for i in range(0, len(self.support)):
            if self._is_support_row_already_paired_index_based(i):
                continue

            support_level = self.support.loc[i, 'Low']

            # If volume is higher than mean the importance increases by 1:
            date = self.support.loc[i, 'Date']
            if self.df['Volume'][date] > volume_mean:
                self.support.loc[i, 'Importance'] += 1

            # Find threshold for comparing support level:
            up_threshold, down_threshold = self._get_thresholds(support_level, support_threshold)

            # See if the support level gets repeated:
            for j in range(i+1, len(self.support)):
                if self._is_support_row_already_paired_index_based(j):
                    continue

                comparing_support_level = self.support.loc[j, 'Low']
                if down_threshold < comparing_support_level < up_threshold:
                    self.support.loc[i, 'Importance'] += 1

                    # Importance of the paired gets added into the original support level
                    self.support.loc[i, 'Importance'] += self.support.loc[j, 'Importance']
                    self.support.loc[j, 'Importance'] = -1  # to indicate that this is already paired.

        self._set_date_as_index_of_support()  # to put back to dates as index






