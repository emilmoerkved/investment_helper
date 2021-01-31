import pandas as pd

# Class to calculate technical analysis tools and parameters.
# For example resistance and support levels and trends.


class TechnicalAnalysis:

    def __init__(self, ticker):
        self.ticker = ticker
        self.resistance = 0  # dataframe
        self.resistance_update_date = 0
        self.support = 0  # dataframe
        self.trend = 0

    def get_resistance_levels(self):
        return self.resistance

    def get_closest_resistance_levels(self):
        resistance_df = pd.DataFrame(self.resistance[(self.resistance.Importance > 0)])
        return resistance_df.nsmallest(3, 'High')

    def get_support_levels(self):
        return self.support

    def find_resistance_levels(self, yf_df, resistance_threshold=0.01):
        # Create a resistance data frame where the resistance points are defined as where the local maxima is found
        # where the price is higher than last closing value.
        # In addition, a column for the importance of the resistance point is also calculated where the importance is
        # started at 0 and can increase in two ways. One way is that the volume on the day where
        # the resistance point was found is higher than the average volume. The second way is that
        # the resistance point gets repeated more or less (depending on the resistance_threshold.
        # If the volume is also here higher than the mean value of volume during the period,
        # the importance point gets increased by 1.

        self._get_possible_resistance_points(yf_df)
        self._update_resistance_with_importance_column()
        self._update_importance_of_resistance_df(yf_df, resistance_threshold)

    def find_support_levels(self, close_price):
        self.support = close_price[(close_price.shift(2) > close_price.shift(1))
                                    & (close_price.shift(1) > close_price)
                                    & (close_price.shift(-1) > close_price)
                                    & (close_price.shift(-2) > close_price.shift(-1))]

    def _get_possible_resistance_points(self, yf_df):
        last_close = yf_df.Close[-1]
        self.resistance = pd.DataFrame(yf_df.High[(yf_df.High.shift(1) < yf_df.High)
                                                & (yf_df.High.shift(-1) < yf_df.High)
                                                & (yf_df.High > last_close)])

    def _update_resistance_with_importance_column(self):
        self.resistance['Importance'] = 0

    def _reset_index_of_resistance(self):
        self.resistance.reset_index(inplace=True)

    def _set_date_as_index_of_resistance(self):
        self.resistance.set_index('Date', inplace=True)

    def _is_row_already_paired_index_based(self, i):
        return self.resistance.loc[i, 'Importance'] == -1

    def _get_thresholds(self, level, threshold):
        return level + level*threshold, level - level*threshold

    def _update_importance_of_resistance_df(self, yf_df, resistance_threshold):
        self._reset_index_of_resistance() # Used as its easier to iterate with indexes as numbers
        volume_mean = yf_df['Volume'].mean()

        for i in range(0, len(self.resistance)):
            if self._is_row_already_paired_index_based(i):
                continue

            resistance_level = self.resistance.loc[i, 'High']

            # If volume is higher than mean the importance increases by 1:
            date = self.resistance.loc[i, 'Date']
            if yf_df['Volume'][date] > volume_mean:
                self.resistance.loc[i, 'Importance'] += 1

            # Find threshold for comparing resistance level:
            up_threshold, down_threshold = self._get_thresholds(resistance_level, resistance_threshold)

            # See if the resistance level gets repeated:
            for j in range(i+1, len(self.resistance)):
                if self._is_row_already_paired_index_based(j):
                    continue

                comparing_resistance_level = self.resistance.loc[j, 'High']
                if down_threshold < comparing_resistance_level < up_threshold:
                    self.resistance.loc[i, 'Importance'] += 1

                    # Importance of the paired gets added into the original resistance level
                    self.resistance.loc[i, 'Importance'] += self.resistance.loc[j, 'Importance']
                    self.resistance.loc[j, 'Importance'] = -1  # to indicate that this is already paired.

        self._set_date_as_index_of_resistance()  # to put back to dates as index






