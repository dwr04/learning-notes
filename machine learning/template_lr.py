import numpy as np
import pandas as pd


class LinearRegressionGD:
    def __init__(
        self,
        feature_cols,
        target_col,
        categorical_cols=None,
        scale_cols=None,
        alpha=0.1,
        n_iters=1000,
        drop_first=True
    ):
        self.feature_cols = feature_cols
        self.target_col = target_col
        self.categorical_cols = categorical_cols or []
        self.scale_cols = scale_cols
        self.alpha = alpha
        self.n_iters = n_iters
        self.drop_first = drop_first

        self.w = None
        self.w_original = None
        self.feature_names = None
        self.means = None
        self.stds = None
        self.cost_history = []

    def fit(self, csv_path):
        df = pd.read_csv(csv_path)

        used_cols = self.feature_cols + [self.target_col]
        df = df[used_cols].copy()

        if self.scale_cols is None:
            self.scale_cols = [
                col for col in self.feature_cols
                if col not in self.categorical_cols
            ]

        self.means = df[self.scale_cols].mean(axis=0)
        self.stds = df[self.scale_cols].std(axis=0, ddof=0)

        df[self.scale_cols] = (df[self.scale_cols] - self.means) / self.stds

        df = pd.get_dummies(
            df,
            columns=self.categorical_cols,
            dtype=int,
            drop_first=self.drop_first
        )

        y = df[self.target_col].values
        X_raw = df.drop(self.target_col, axis=1).values

        self.feature_names = df.drop(self.target_col, axis=1).columns.tolist()

        m = X_raw.shape[0]
        X = np.hstack([
            np.ones((m, 1)),
            X_raw
        ])

        n = X.shape[1]
        self.w = np.zeros(n)
        self.cost_history = []

        for i in range(self.n_iters):
            pred = X @ self.w
            err = pred - y

            grad = (X.T @ err) / m
            self.w = self.w - self.alpha * grad

            cost = np.mean(err ** 2) / 2
            self.cost_history.append(cost)

        self._restore_original_weights()

        return self

    def _restore_original_weights(self):
        intercept_scaled = self.w[0]
        coef_scaled = self.w[1:].copy()
        coef_original = coef_scaled.copy()

        cols_to_scale_idx = [
            self.feature_names.index(col)
            for col in self.scale_cols
        ]

        means_arr = self.means[self.scale_cols].to_numpy()
        stds_arr = self.stds[self.scale_cols].to_numpy()

        coef_original[cols_to_scale_idx] = (
            coef_scaled[cols_to_scale_idx] / stds_arr
        )

        intercept_original = intercept_scaled - np.sum(
            coef_scaled[cols_to_scale_idx] * means_arr / stds_arr
        )

        self.w_original = np.hstack([
            intercept_original,
            coef_original
        ])

    def coef_table(self):
        """
        显示特征名和参数的对应关系
        """

        if self.w is None:
            raise ValueError("模型还没有训练，请先调用 fit()")

        names = ['intercept'] + self.feature_names

        table = pd.DataFrame({
            'feature': names,
            'w_scaled': self.w,
            'w_original': self.w_original
        })

        return table

    def predict(self, data):
        if isinstance(data, dict):
            data = pd.DataFrame([data])

        df = data[self.feature_cols].copy()

        df[self.scale_cols] = (df[self.scale_cols] - self.means) / self.stds

        df = pd.get_dummies(
            df,
            columns=self.categorical_cols,
            dtype=int,
            drop_first=self.drop_first
        )

        df = df.reindex(columns=self.feature_names, fill_value=0)

        X_raw = df.values
        m = X_raw.shape[0]

        X = np.hstack([
            np.ones((m, 1)),
            X_raw
        ])

        return X @ self.w