# Methodological Review: Uzbekistan Liquidity Index (UZLI)
**A Critical Assessment of Metric Design, Weighting, and Normalization**
*Prepared as a methodology note for the UZLI research paper | 4 July 2026*

---

## Abstract

The Uzbekistan Liquidity Index (UZLI) is a composite daily liquidity measure constructed from five metrics applied to equity trade data from the Tashkent Stock Exchange (UZSE) for the period 1 November 2016 to 23 June 2026. This note evaluates each metric against the academic literature on market liquidity measurement, assesses the suitability of the weighting and normalization methodology for a frontier equity market, and identifies the principal methodological limitations that must be disclosed in any publication derived from this index. The review concludes that the UZLI is a credible first-generation composite measure adequate for identifying broad liquidity trends, but that two of the five components — the Amihud illiquidity score and the turnover score — contribute materially less information than their combined 45% weight implies. The spread estimator, while conceptually grounded in Corwin and Schultz (2012), departs from the published formula in ways that must be acknowledged. Recommendations for second-generation improvements are provided throughout.

---

## 1. Conceptual Framework

### 1.1 Dimensions of Market Liquidity

Market liquidity is not a single quantity but a family of related properties. The academic literature, beginning with Black (1971) and systematized by Kyle (1985) and subsequent work, identifies at least four distinct dimensions:

1. **Tightness** — the cost of executing a round-trip transaction at current prices, measured by the bid-ask spread or effective spread. Higher tightness implies lower transaction cost.
2. **Depth** — the volume of orders available at or near the current price; a deep market can absorb large orders with minimal price impact.
3. **Breadth** — the proportion of the listed universe that actively participates in trading on a given day; breadth distinguishes market-wide liquidity from idiosyncratic security-level activity.
4. **Resilience** — the speed with which prices recover to pre-shock levels following a large order; resilient markets do not retain price dislocations.

A fifth dimension, **immediacy** (Demsetz 1968) — the speed at which a buyer and seller can be matched at any time — is generally unmeasurable from daily data.

A composite liquidity index is theoretically superior to any single metric because the dimensions are partially orthogonal: a market can exhibit narrow spreads (tight) but low turnover (narrow depth), or high turnover in a subset of securities (concentrated breadth). The UZLI attempts to capture tightness (spread score), depth/flow activity (volume score, turnover score), breadth (breadth score), and price impact (Amihud score). This multi-dimensional design is conceptually appropriate.

The canonical references establishing the multi-dimensional framework are:
- Kyle, A.S. (1985). "Continuous Auctions and Insider Trading." *Econometrica*, 53(6), 1315–1335.
- Amihud, Y. & Mendelson, H. (1986). "Asset Pricing and the Bid-Ask Spread." *Journal of Financial Economics*, 17(2), 223–249.
- Grossman, S.J. & Miller, M.H. (1988). "Liquidity and Market Structure." *Journal of Finance*, 43(3), 617–633.

### 1.2 Measurement Challenges in Frontier Markets

Several structural features of frontier equity markets complicate the application of standard liquidity metrics developed for mature markets (Lesmond 2005; Bekaert, Harvey & Lundblad 2007):

- **Discrete, non-continuous trading:** Many frontier markets operate periodic call auctions rather than continuous limit-order books. The Corwin-Schultz estimator, derived assuming continuous trading, requires modification in such settings.
- **Thin trading and zero-return days:** A high proportion of listed securities generate no transactions on any given day. Standard spread and price-impact estimators require at least two observations and return undefined values for non-trading securities.
- **UZS-denomination:** Volume in domestic currency is an order of magnitude larger in nominal terms than dollar-equivalent volumes, creating scaling problems for the Amihud ratio.
- **Limited float:** Concentrated ownership and state-linked shareholders mean that the freely tradeable float is a small fraction of total shares outstanding, making share-count-based turnover ratios uninformative.

The UZSE presents all four of these complications. The metric designs must be assessed with this context in mind.

---

## 2. Metric 1: Volume Score

### 2.1 Definition and Formula

The Volume Score measures the ratio of daily aggregate market trading volume to a trailing 90-trading-day moving average of that volume, clipped to the interval [0, 3]:

$$\text{VolumeScore}_t = \min\!\left(3,\; \frac{\sum_i V^{UZS}_{it}}{\frac{1}{90}\sum_{\tau=t-89}^{t} \sum_i V^{UZS}_{i\tau}}\right)$$

where $V^{UZS}_{it}$ is the UZS-denominated trading volume of security $i$ on day $t$, and the sum is over all securities that traded on the relevant day. The ratio is then Min-Max normalized to [0, 100] across the full sample.

**Implementation (exact):**
```
daily_total = Σ volume_uzs by date
rolling_avg = 90-day rolling mean of daily_total
score = clip(daily_total / rolling_avg, 0.0, 3.0)
```

### 2.2 Intuition

A score of 1.0 indicates that today's volume precisely equals its 90-day historical mean — a "normal" trading day in relative terms. Scores above 1.0 signal unusually high activity; the hard cap at 3.0 prevents single outlier days (e.g., a large block trade in one security) from dominating the index. The use of a trailing average rather than a fixed denominator makes the measure self-normalizing: it captures whether the market is more or less active than its own recent history, rather than comparing to an external benchmark.

### 2.3 Academic Foundation

Volume-based liquidity measures have a long history in the empirical asset pricing literature. Datar, Naik & Radcliffe (1998) use share turnover as a direct liquidity proxy, finding it subsumes the book-to-market effect. Chordia, Roll & Subrahmanyam (2001) document that daily aggregate market volume — measured as the sum of individual security volumes — contains systematic information about aggregate liquidity conditions. The use of a moving-average benchmark as a normalizer follows the practice in market microstructure studies of scaling volume relative to expected volume to filter out long-term trend and seasonality effects.

The 90-day rolling window is a standard choice: long enough to smooth seasonal patterns (quarterly reporting cycles) but short enough to adapt to structural regime changes. Chordia, Roll & Subrahmanyam (2001) use 21-day windows for intraday studies; for daily composite indices measuring medium-term liquidity conditions, 60–90 day windows are conventional.

### 2.4 Strengths

- **Conceptually direct:** Volume is the most unambiguous indicator of trading activity. Any investor active in a market generates volume; zero volume means zero market participation.
- **Computationally robust:** The formula requires only the UZS volume column and tolerates missing data via the `min_count=1` parameter.
- **Self-referential scaling:** Normalizing to own-history avoids currency, size, or inflation effects that would make cross-time comparison impossible in a rapidly growing economy like Uzbekistan (nominal GDP grew ~7–8% annually in UZS terms during the sample period).
- **Hard cap at 3.0:** Prevents a single extraordinary trading day from compressing all other scores toward zero after Min-Max normalization.

### 2.5 Weaknesses

- **Aggregation hides concentration:** A high aggregate volume score can be produced by heavy trading in a single security (e.g., a state enterprise with a large block trade), while the remaining 289 tickers remain dormant. The measure does not distinguish market-wide activity from concentrated activity. In the UZSE context, where a handful of large-cap SOEs dominate turnover, this is a structural limitation.
- **No size adjustment:** The volume metric does not scale by market capitalization. As market cap has grown substantially over the 2016–2026 period (from approximately USD 2B to USD 23B), the same absolute volume represents a declining proportion of market cap over time, introducing a spurious positive trend in the ratio's denominator.
- **UZS inflation effect:** Because the metric uses nominal UZS volume without inflation adjustment, real volume growth is conflated with price-level growth. Uzbekistan's average annual inflation over the sample period was approximately 9–14% (CBU data), meaning nominal volume metrics trend upward even in the absence of any real change in trading activity.
- **Rolling window introduces look-ahead:** The initial 90 observations use `min_periods=1`, meaning the first 89 days use fewer than 90 observations in the denominator, producing upwardly biased scores for the earliest part of the sample.

### 2.6 Suitability for the UZSE

The Volume Score is the most appropriate single metric for the UZSE. Given the absence of continuous quote data, intraday microstructure data, or centralized limit-order book feeds, exchange-reported daily volume in domestic currency is the most reliable and complete data available. The 90-day rolling normalization is particularly well-suited to a market undergoing structural change, as it avoids conflating cyclical activity with trend. The 3.0 ceiling is well-calibrated: the empirical maximum in the sample is exactly 3.0 (the clip boundary), confirming that at least some days were truncated.

**Statistical summary (raw score):** Mean 0.47, Std 0.85, Min 0.00, Max 3.00.

The mean of 0.47 — substantially below 1.0 — indicates that on an average trading day, UZSE volume is less than half of its own 90-day average. This reflects the highly sporadic nature of trading on the exchange, where high-volume days skew the rolling average upward and most days fall well below it. This feature is itself an important finding: the UZSE lacks the consistent daily participation that characterizes even moderately developed frontier markets.

---

## 3. Metric 2: Breadth Score

### 3.1 Definition and Formula

The Breadth Score measures the share of the total listed universe that generated at least one trade on a given day:

$$\text{BreadthScore}_t = \frac{N^{\text{active}}_t}{N^{\text{total}}}$$

where $N^{\text{active}}_t$ is the number of distinct tickers with at least one transaction on day $t$, and $N^{\text{total}} = 290$ is the total number of unique tickers ever observed in the sample.

**Implementation (exact):**
```
total_tickers = df["ticker"].nunique()  # = 290, computed once
active_per_day = count distinct tickers per date
score = active_per_day / total_tickers
```

### 3.2 Intuition

A market where 10 of 290 securities trade on a given day is structurally less liquid than one where 250 trade, even if the total volume is similar. Breadth captures this "participation" dimension of liquidity — whether risk capital is distributed across the market or concentrated in a few instruments. In the context of index investing and portfolio construction, an investor cannot build a diversified exposure to a market where fewer than 10% of securities trade on any given day.

The breadth score is conceptually related to the zero-return-day measures introduced by Lesmond, Ogden & Trzcinka (1999) and Liu (2006): both identify non-trading as a signal of illiquidity. The UZLI's breadth score uses non-trading at the market level (daily active tickers as a fraction of total) rather than at the security level, making it a market-wide rather than security-level estimator.

### 3.3 Academic Foundation

The academic foundation for breadth as a dimension of market liquidity includes:

- **Liu (2006):** Introduces the LM measure — a standardized number of zero-trading-volume days over a 12-month window, adjusted for turnover. Shows empirically that the zero-volume dimension of liquidity is priced in U.S. equities above and beyond the Amihud measure.
- **Bekaert, Harvey & Lundblad (2007):** Use the proportion of zero-return days as the primary liquidity measure for emerging market studies, arguing it is superior to spread estimators because it captures market inactivity directly and is available from any OHLCV dataset. Their paper is arguably the closest academic precedent for the UZLI's breadth score.
- **Lesmond (2005):** Finds that the proportion of zero-return days explains 60–80% of cross-country variation in liquidity costs in 31 developing countries, dominating competing measures.
- **Bekaert, Harvey & Lundblad (2007):** "Liquidity and Expected Returns: Lessons from Emerging Markets." *Review of Financial Studies*, 20(6), 1783–1831.

The UZLI uses zero-trading days (inactive tickers) rather than zero-return days (traded securities with no price change) as the breadth signal, which is a reasonable adaptation for a market where many securities simply generate no transactions at all.

### 3.4 Strengths

- **Captures the most visible feature of UZSE illiquidity:** The finding that fewer than 10% of listed securities trade on a median day is the single most salient characteristic of the UZSE's market structure. The breadth score directly measures this.
- **No unit conversion or scaling issues:** The score is a dimensionless ratio bounded in [0, 1] regardless of currency denomination or market size.
- **Robust to outliers:** Unlike the volume and turnover scores, there is no mechanism by which a single extreme observation can distort the breadth score.
- **Interpretable in absolute terms:** A breadth score of 0.107 is meaningful without reference to any historical distribution: it means ~10.7% of the listed universe traded that day.

### 3.5 Weaknesses

**Critical — Look-ahead bias in denominator (L3):**
The denominator of 290 is the all-time unique ticker count as of June 2026, applied retroactively to the entire 2016–2026 sample. This is a form of survivorship / look-ahead bias: in November 2016, when the UZSE had fewer listed securities (the exact count is unknown but materially lower), dividing by 290 understates the breadth score relative to the true proportion of the then-current market that was actively trading. The direction of the bias is downward for early observations, creating an artifactual appearance of improving breadth over time that may partially reflect the growing denominator rather than genuine improvement in market participation.

The magnitude of this bias depends on how many tickers were listed in 2016 versus 2026. If only 150 tickers were listed in 2016, then a day with 26 active tickers should score 0.173 (26/150), but is instead scored as 0.090 (26/290) — a 48% understatement. This bias is unresolvable without a time-series of the UZSE's listed-company count (see Information Gap G2 in the project audit).

**Moderate — Equal weighting of securities:**
The metric treats a trade in a micro-cap illiquid security the same as a trade in Uzmetkombinat (one of the largest companies by market capitalization). A market-capitalization-weighted breadth score — counting active capital rather than active security count — would be more economically meaningful.

**Minor — Double-counting within sessions:**
A security that executes multiple trades in a single day contributes exactly 1 to $N^{\text{active}}_t$ regardless of trade count, which is appropriate for a breadth measure but means the indicator cannot distinguish a market with 26 lightly traded securities from one with 26 heavily traded securities.

### 3.6 Suitability for the UZSE

The breadth score is arguably the most informative single metric for the UZSE, precisely because market inactivity is the defining structural characteristic of this exchange. Bekaert, Harvey & Lundblad (2007) and Lesmond (2005) establish that zero-activity measures dominate spread and price-impact measures in illiquid emerging markets — a finding consistent with the UZSE's empirical data, where the spread score is near-constant (Std = 0.054) but the breadth score shows meaningful variation.

**Statistical summary (raw score):** Mean 0.107, Std 0.072, Min 0.003, Max 0.286.

The maximum breadth score ever recorded (0.286, corresponding to 83 of 290 tickers active) implies that even on the single most liquid day in nine years of data, 71.4% of listed securities did not trade. This finding alone is sufficient to characterize the UZSE as a market with severe structural breadth limitations.

---

## 4. Metric 3: Turnover Score

### 4.1 Definition and Formula

The Turnover Score is intended to measure how efficiently each security's float turns over relative to its size, averaged across the active universe on a given day:

$$\text{TurnoverScore}_t = \frac{1}{N^{\text{active}}_t} \sum_{i \in \text{active}_t} \frac{V^{\text{shares}}_{it}}{\text{Close}_{it} \times \overline{V}^{\text{shares},30}_{it}}$$

where $V^{\text{shares}}_{it}$ is the share volume of security $i$ on day $t$, $\text{Close}_{it}$ is the closing price, and $\overline{V}^{\text{shares},30}_{it}$ is the 30-trading-day rolling mean of daily share volume for security $i$.

The denominator $\text{Close}_{it} \times \overline{V}^{\text{shares},30}_{it}$ serves as a proxy for market capitalization, substituting $\overline{V}^{\text{shares},30}$ for shares outstanding — a substitution that is fundamentally incorrect (see Weakness section below). The denominator is clipped at a minimum of 1.0 to prevent division-by-zero.

**Implementation (exact):**
```
avg_volume_30d = 30-day rolling mean of volume_shares per ticker
market_cap_proxy = close × avg_volume_30d  (clipped at 1.0)
ticker_turnover = volume_shares / market_cap_proxy
score = cross-sectional mean of ticker_turnover per day
```

### 4.2 Intuition

Turnover ratio — shares traded as a fraction of shares outstanding — is one of the oldest and most widely used liquidity proxies. Introduced empirically by Datar, Naik & Radcliffe (1998) and used in liquidity-adjusted asset pricing models by Pástor & Stambaugh (2003), it captures the "churn" rate of equity ownership. A high turnover ratio means that the existing float of shares changes hands frequently, indicating ease of entry and exit for investors. A low ratio indicates that shares are held inertially, with few willing sellers or buyers.

### 4.3 Academic Foundation

The use of turnover ratio as a liquidity measure is supported by:

- **Datar, Naik & Radcliffe (1998):** "Liquidity and Stock Returns: An Alternative Test." *Journal of Financial Markets*, 1(2), 203–219. Demonstrates empirically that turnover is inversely related to subsequent returns (a liquidity premium), consistent with the view that illiquid stocks require compensation for holding costs.
- **Lo & Wang (2000):** "Trading Volume: Definitions, Data Analysis, and Implications of Portfolio Theory." *Review of Financial Studies*, 13(2), 257–300. Establishes the theoretical link between portfolio rebalancing and turnover; shows that turnover captures both information-driven and liquidity-driven components of trading.
- **Aitken & Comerton-Forde (2003):** "How Should Liquidity Be Measured?" *Pacific-Basin Finance Journal*, 11(1), 45–59. Finds that turnover ratio is the best-performing single liquidity proxy for less developed markets with thin trading, precisely because it does not require continuous quote data.
- **Liu (2006):** "A Liquidity-Augmented Capital Asset Pricing Model." *Journal of Financial Economics*, 82(3), 631–671. Uses a turnover-adjusted zero-trading-day count as a composite measure; demonstrates that the turnover dimension captures a distinct factor from spread-based measures.

### 4.4 Strengths

- **Captures proportional activity:** A correctly specified turnover ratio (shares traded / shares outstanding) is the natural normalized measure of trading activity, controlling for differences in listing size.
- **Widely used and cited:** The turnover-based liquidity literature is extensive, providing a strong theoretical justification for including this dimension in a composite index.
- **Available from basic OHLCV data:** No bid-ask or intraday data required.

### 4.5 Weaknesses

**Critical — Market capitalization proxy is incorrect (L1):**
The standard turnover ratio denominator is **shares outstanding** (the total number of shares in existence for a given security). The UZLI instead uses `close_price × 30-day rolling average of daily share volume` as a proxy for market capitalization. This is not market capitalization. It is an arbitrary product of price and recent trading volume — two endogenous variables that both respond to the same liquidity conditions the index is trying to measure. The consequences are:

1. *Circularity:* The numerator and denominator both include volume, making the ratio dimensionally inconsistent and creating mechanical correlations.
2. *Unboundedness:* For securities with very low recent volume (small $\overline{V}^{\text{shares},30}$), a single active trading day produces a massive ratio that has no economic interpretation.
3. *Price-level bias:* Cheap, high-share-count securities (common in post-privatization markets where shares were issued at par at low nominal prices) systematically produce larger denominators and therefore smaller ratios, biasing the cross-sectional mean.

These defects produce the severe right skew visible in the empirical data: the raw score ranges from 0.000 to 45.85 (mean 0.587, std 2.07), which is far outside any reasonable interpretation of a turnover ratio. A properly specified share-based turnover ratio is bounded in (0, ~5) for even the most actively traded emerging market securities. The 45.85 maximum indicates at least one day where the formula produced a nonsensical result.

**Critical — Min-Max normalization is contaminated by the outlier (L6):**
Because the maximum raw score of 45.85 becomes the normalization anchor, the effective range of the turnover_norm column is compressed: a day with a raw score of 1.0 (what should be a well-functioning turnover day) maps to approximately 1/45.85 = 2.2 on the 0–100 scale, when it should arguably map near the midpoint. This compression means the turnover component effectively contributes less signal to the final UZLI than its 25% weight implies, except on the single outlier day.

**Moderate — Cross-sectional averaging without weighting:**
Taking a simple mean of per-ticker ratios across active securities gives equal weight to micro-cap and large-cap securities. A value-weighted mean would be more economically meaningful.

### 4.6 Suitability for the UZSE

The conceptual design (turnover ratio as a liquidity proxy) is highly appropriate for the UZSE. The implementation, however, contains a fundamental error in the denominator specification. The metric as implemented does not measure turnover ratio in the standard sense and should be clearly described as a *turnover-activity proxy* rather than as a true turnover ratio, with explicit acknowledgment that shares outstanding data were unavailable.

**Statistical summary (raw score):** Mean 0.587, Std 2.07, Min 0.000, Max 45.85.

**Recommendation:** If shares outstanding data can be obtained from UZSE annual reports or mandatory registrar filings, the denominator should be replaced with the correct market capitalization ($\text{shares outstanding} \times \text{close price}$). Failing that, the proxy should be disclosed with its limitations explicitly stated in the methodology section.

---

## 5. Metric 4: Amihud Illiquidity Score

### 5.1 Definition and Formula

The Amihud Illiquidity Score applies the Amihud (2002) illiquidity ratio at the security level and transforms it into a [0, 1]-bounded liquidity score:

$$\text{ILLIQ}_{it} = \frac{|r_{it}|}{V^{UZS}_{it}}$$

where $r_{it} = (\text{Close}_{it} - \text{Open}_{it}) / \text{Open}_{it}$ is the daily open-to-close return of security $i$ on day $t$, and $V^{UZS}_{it}$ is the UZS-denominated trading volume.

The cross-sectional mean is then taken across all active securities on day $t$, and the score is transformed via:

$$\text{AmihudScore}_t = \frac{1}{1 + \overline{\text{ILLIQ}}_t}$$

where $\overline{\text{ILLIQ}}_t = N^{-1}_t \sum_{i} \text{ILLIQ}_{it}$. Higher scores indicate lower illiquidity (more liquid).

**Implementation (exact):**
```
daily_return = (close - open) / open
amihud = |daily_return| / volume_uzs  (per ticker)
daily_avg_amihud = cross-sectional mean per date
score = 1.0 / (1.0 + daily_avg_amihud)
```

### 5.2 Intuition

The Amihud (2002) illiquidity ratio measures the price impact per unit of trading volume: how much does price move per unit of money traded? In a liquid market, large volumes can be transacted with minimal price movement (low ratio). In an illiquid market, even moderate trading volumes move prices substantially (high ratio). The ratio is the closest available proxy for Kyle's (1985) price-impact coefficient λ when intraday data is unavailable.

The transformation $1/(1 + \text{ILLIQ})$ maps the unbounded positive ratio to the interval (0, 1], with a score near 1.0 indicating near-zero price impact (high liquidity) and scores approaching zero indicating very high price impact.

### 5.3 Academic Foundation

- **Amihud, Y. (2002):** "Illiquidity and Stock Returns: Cross-Section and Time-Series Effects." *Journal of Financial Markets*, 5(1), 31–56. The foundational paper. Demonstrates that (i) the expected illiquidity of a market positively predicts the market's excess return, and (ii) an increase in illiquidity is associated with a contemporaneous decline in stock prices — consistent with illiquidity being a systematic, priced risk factor.
- **Amihud, Y., Mendelson, H. & Pedersen, L.H. (2005):** "Liquidity and Asset Prices." *Foundations and Trends in Finance*, 1(4), 269–364. Survey of the literature, confirming the illiquidity ratio as one of the two or three most widely applied liquidity measures in empirical research.
- **Lesmond (2005):** Tests the Amihud ratio in a cross-section of emerging markets; finds it performs adequately as a spread proxy but is sensitive to volume measurement conventions, particularly in markets where volume is reported in local currency at non-standardized scales.
- **Goyenko, Holden & Trzcinka (2009):** "Do Liquidity Measures Measure Liquidity?" *Journal of Financial Economics*, 92(2), 153–181. The most rigorous validation study: uses TAQ data to assess which low-frequency (daily) measures best approximate high-frequency (intraday) effective spread. The Amihud ratio is found to be the best-performing price-impact proxy but performs less well for markets with very large nominal volumes relative to price changes.

### 5.4 Strengths

- **Best available price-impact proxy from daily data:** In the absence of intraday quote and transaction data, the Amihud ratio is the standard choice for estimating price impact. Its widespread use ensures comparability with the broader empirical literature.
- **Well-grounded in theory:** The ratio maps directly onto the Kyle (1985) price-impact coefficient and has been validated across multiple developed and emerging market datasets.
- **Handles thin trading:** The formula is defined for any day with both a non-zero return and non-zero volume, making it computable on most active trading days in the UZSE sample.

### 5.5 Weaknesses

**Critical — Near-zero information content in the UZSE context (L2):**
The Amihud ratio is defined as $|\text{return}| / \text{volume}_{UZS}$. In the UZSE, daily UZS volumes are on the order of hundreds of millions to billions of Uzbek Soum (1 USD ≈ 12,600 UZS as of 2025), while daily returns are on the order of 0.1–10%. The result is that ILLIQ values are of the order $10^{-9}$ to $10^{-11}$, and therefore $1/(1 + \text{ILLIQ}) \approx 1.000000$ for virtually every observation.

The empirical confirmation: across 2,373 trading days, the amihud_score has mean 1.000, standard deviation 0.0003, minimum 0.990, and maximum 1.000. This near-constant series carries essentially no discriminating signal about variation in liquidity conditions across days. A component weighted at 20% in the composite but contributing variance of order $10^{-4}$ to the final score is not contributing 20% of the information content of the index.

The root cause is not a methodological error per se but a unit-scaling problem. Amihud (2002) explicitly normalized the ratio by multiplying by $10^6$ to put it in interpretable units when working with U.S. daily data (millions of USD). The UZLI applies the formula to raw UZS volumes without any scaling adjustment, producing ratios far too small to distinguish across days.

**Moderate — Open-to-close return, not close-to-close:**
The implementation computes daily return as `(close - open) / open`. The Amihud (2002) paper uses close-to-close returns. In a continuous-trading market, close-to-close returns incorporate overnight information and are more comprehensive. In the UZSE's call-auction environment, the distinction matters less, but the departure from the canonical specification should be noted.

**Moderate — Cross-sectional simple mean:**
The market-wide Amihud illiquidity is computed as the simple (unweighted) average of per-security ratios. Amihud (2002) uses an equal-weighted average of per-security annual averages to compute a market-level illiquidity measure. The UZLI takes the daily cross-sectional mean, which is correct in principle but may be dominated by extreme ratios for very lightly traded micro-cap securities.

### 5.6 Suitability for the UZSE

The Amihud illiquidity ratio is conceptually appropriate — price impact is a genuine dimension of liquidity relevant to the UZSE — but its application without unit scaling renders it empirically uninformative for this specific market. As currently implemented, the amihud_norm component contributes approximately the same value to every day's UZLI score (the normalized series is compressed into a narrow band near the maximum), making its effective weight in the composite close to zero in terms of cross-day information content, despite its nominal 20% weight in the specification.

**Statistical summary (raw score):** Mean 1.000, Std 0.0003, Min 0.990, Max 1.000.

**Recommendation:** The Amihud ratio should be rescaled to match the units of the original paper. Following Amihud (2002), multiply the raw ratio by $10^6$ before averaging; alternatively, compute the ratio using USD-equivalent volumes rather than nominal UZS volumes. Either adjustment will restore meaningful cross-day variation to the series.

---

## 6. Metric 5: Corwin-Schultz Spread Proxy

### 6.1 Definition and Formula

The Spread Score is constructed as follows. For each trading day $t$, the cross-sectional averages of security high prices ($\overline{H}_t$) and low prices ($\overline{L}_t$) are computed across all active securities. The spread estimator is then:

$$\beta_t = \left[\ln\!\left(\frac{\overline{H}_t}{\overline{L}_t}\right)\right]^2$$

$$\text{Spread}_t = \frac{2\left(e^{\sqrt{\beta_t}} - 1\right)}{1 + e^{\sqrt{\beta_t}}} = 2\tanh\!\left(\frac{\sqrt{\beta_t}}{2}\right)$$

$$\text{SpreadScore}_t = 1 - \text{Spread}_t$$

**Implementation (exact):**
```
avg_high = cross-sectional mean of daily highs across active securities
avg_low  = cross-sectional mean of daily lows  across active securities
ratio = avg_high / avg_low
beta  = ln(ratio)²
spread = 2 × (exp(√β) − 1) / (1 + exp(√β))
score  = 1 − spread
```

### 6.2 Intuition

The bid-ask spread is the most direct measure of transaction cost and market-maker compensation for adverse selection and inventory risk. A wide spread means investors incur a higher round-trip cost on every transaction, depressing trading frequency and liquidity. In the absence of quote data — as is the case for the UZSE, which does not publish real-time bid-ask quotes in historical form — daily high-low ranges can be used as a proxy, since the high and low are influenced by the spread: the high tends toward the ask and the low tends toward the bid.

A score of 1.0 indicates an estimated spread of zero (no tightness cost); a score below 1.0 indicates estimated positive spread; scores below 0 indicate an anomalous condition (see Weakness section).

### 6.3 Academic Foundation

The foundational reference for high-low-based spread estimation is:

- **Corwin, S.A. & Schultz, P. (2012):** "A Simple Way to Estimate Bid-Ask Spreads from Daily High and Low Prices." *The Journal of Finance*, 67(2), 719–760.

Corwin & Schultz derive the estimator from two theoretical observations: (i) the daily high price is typically an ask price and the daily low is typically a bid price, so `ln(H/L)` reflects the spread plus fundamental volatility; (ii) over two consecutive days, the volatility component scales with the square root of time, while the spread component does not. By solving the two-equation system for a single day and two days, the spread and volatility can be separated.

The published Corwin-Schultz estimator (their Equation 11) is:

$$\alpha = \frac{\sqrt{2\beta} - \sqrt{\beta}}{3 - 2\sqrt{2}} - \sqrt{\frac{\gamma}{3 - 2\sqrt{2}}}$$

$$S = \frac{2\left(e^{\alpha} - 1\right)}{1 + e^{\alpha}}$$

where:
$$\beta = \sum_{j=0}^{1}\left[\ln\!\left(\frac{H^j_t}{L^j_t}\right)\right]^2, \qquad \gamma = \left[\ln\!\left(\frac{\max(H_t, H_{t+1})}{\min(L_t, L_{t+1})}\right)\right]^2$$

Other relevant references:
- **Roll, R. (1984):** "A Simple Implicit Measure of the Effective Bid-Ask Spread in an Efficient Market." *Journal of Finance*, 39(4), 1127–1139. Earlier high-low estimator; requires return autocorrelation and is less reliable for thin markets.
- **Goyenko, Holden & Trzcinka (2009):** Validate the Corwin-Schultz estimator against TAQ-derived effective spreads; find it is the most accurate daily spread proxy for U.S. data.
- **Fong, Holden & Trzcinka (2017):** "What Are the Best Liquidity Proxies for Global Research?" *Review of Finance*, 21(4), 1355–1401. Validates the Corwin-Schultz estimator in international settings, finding it performs well but with reduced accuracy in thin markets where the high-low range is frequently dominated by non-spread factors.

### 6.4 Strengths

- **Well-grounded in theory:** The Corwin-Schultz framework is derived from a structural model of how bid-ask spreads affect intraday price ranges, not a purely empirical correlation. This theoretical grounding provides interpretability.
- **Validated in empirical literature:** Among daily spread estimators, Corwin-Schultz is one of the two or three best-performing measures in both U.S. and international contexts (Goyenko et al. 2009; Fong et al. 2017).
- **Available from OHLCV data:** Computable from the exact data fields the UZSE provides.

### 6.5 Weaknesses

**Critical — The implemented formula is not the published Corwin-Schultz estimator:**

The UZLI implementation departs from the published Corwin & Schultz (2012) formula in three material ways:

**Departure 1 — Single day, not two consecutive days.**
The published estimator requires two consecutive trading days' high-low ranges to decompose volatility from spread. The UZLI applies the formula using a single day's high-low ratio, computing $\beta = [\ln(H/L)]^2$ for one day only. This eliminates the two-day identification strategy that is the estimator's core mechanism. Without the two-day design, the volatility and spread components cannot be separated; the resulting $\sqrt{\beta}$ conflates the two.

**Departure 2 — Cross-sectional average, not per-security estimation.**
The published estimator applies to individual security time series. The UZLI first averages the high prices and low prices across all active securities, then applies the formula to the resulting market averages. This order of operations is incorrect: the market average of $\ln(H/L)$ is not the same as the average of per-security spreads. Jensen's inequality implies that taking logarithms after averaging will systematically underestimate the average spread.

**Departure 3 — Missing the α computation.**
The published formula computes an intermediate parameter α (which adjusts for the relative contributions of β and γ) before applying the logistic-type transformation $2(e^\alpha - 1)/(1 + e^\alpha)$. The UZLI skips this step and passes $\sqrt{\beta}$ directly into the transformation. The result is a formula structurally similar in appearance to Corwin-Schultz but numerically different and lacking the theoretical justification of the original paper.

**Moderate — Negative scores on two days:**
The implementation produces spread_score values below zero on two trading days (minimum = −0.231), which is economically nonsensical. Negative implied spreads can arise when the high-low range is very small (H ≈ L, often in a thin market with a single trade setting both H and L to the same price), causing the ratio to approach 1, β to approach 0, the spread to approach 0, and — due to floating-point precision — occasionally to produce a slightly negative value. These two observations should either be floored at 0 (setting spread = 0) or excluded from the sample.

**Moderate — UZSE market microstructure mismatch:**
The Corwin-Schultz estimator was derived for continuous limit-order-book markets where prices evolve throughout the trading day. The UZSE operates periodic call auctions, potentially with a single clearing price for each security per session. In this setting, the theoretical mechanism linking bid-ask spreads to intraday high-low ranges does not apply cleanly: a single-auction clearing price generates high = low = close, producing a β = 0 and a spread estimate of zero. The empirical prevalence of exactly equal high and low prices in the UZSE data is unknown but likely non-trivial.

### 6.6 Suitability for the UZSE

The spread score is the most methodologically complex component of the UZLI and, as implemented, the one that departs most significantly from the academic literature it cites. The formula structure is inspired by Corwin & Schultz (2012) but is not that estimator. The score should be described in the paper as a **high-low range-based spread proxy** rather than a "Corwin-Schultz estimator," and the simplifications relative to the published formula must be explicitly disclosed.

Despite these limitations, the spread score's empirical behaviour is reassuring: mean 0.965, std 0.054, and only 2 negative observations out of 2,373 days. The score shows meaningful time-series variation (the minimum of −0.231 on the worst day and the maximum of 1.000 on the best), suggesting it captures real variation in market-wide price range dynamics even if its interpretation as a precise spread estimate is compromised.

**Statistical summary (raw score):** Mean 0.965, Std 0.054, Min −0.231, Max 1.000.

---

## 7. Weighting Methodology

### 7.1 Specification

The UZLI composite score is computed as a fixed-weight linear combination of the five Min-Max-normalized component scores:

$$\text{UZLI}_t = \sum_{k=1}^{5} w_k \cdot \text{norm}_{k,t}$$

with weights:

| Component | Weight |
|---|---|
| volume_norm | 0.25 |
| breadth_norm | 0.20 |
| turnover_norm | 0.25 |
| amihud_norm | 0.20 |
| spread_norm | 0.10 |
| **Total** | **1.00** |

The weights are fixed across the entire 2016–2026 sample and are not estimated from data.

### 7.2 Rationale and Academic Context

Expert-determined fixed weights are the conventional approach in composite index construction when sample sizes or data availability preclude statistical estimation of weights. Precedents include:

- **The IMF Financial Development Index (Svirydzenka 2016):** Uses principal component analysis (PCA) weights for sub-indices, but equal weights within sub-categories.
- **The World Bank Doing Business composite index:** Uses fixed, expert-determined weights.
- **FTSE liquidity factor screens:** Use fixed market-capitalization and volume thresholds rather than statistically estimated weights.
- **The MSCI Market Accessibility Criteria:** Use a scoreboard approach with pre-specified weights for each criterion.

The UZLI weight specification is plausible:
- Volume and turnover (each 25%) appropriately dominate the composite, reflecting the primacy of trading activity as an observable, actionable signal of liquidity.
- Amihud and breadth (each 20%) provide meaningful additional information on market structure and price impact.
- Spread (10%) receives the lowest weight, appropriate given both its conceptual importance and the lower reliability of the daily high-low estimator relative to, say, a centralized limit-order-book spread.

### 7.3 Critique

**Effective weights differ from nominal weights due to unequal variance:**

A fixed-weight composite implicitly assigns each component's influence in proportion to both its weight *and* its variance. When components have highly unequal variances, the actual information contribution of each component to variation in the composite differs from the nominal weights. For the UZLI, this is a material issue:

| Component | Nominal Weight | Raw Score Std | Normalized Std (approx.) |
|---|---|---|---|
| volume_norm | 25% | 0.85 | High |
| breadth_norm | 20% | 0.072 | Moderate |
| turnover_norm | 25% | 2.07 | Very high (outlier-distorted) |
| amihud_norm | 20% | 0.0003 | Near-zero |
| spread_norm | 10% | 0.054 | Low |

The amihud_norm component, with a standard deviation of approximately 0.0003 before normalization (and compressed further after Min-Max normalization), contributes near-zero variance to the composite, effectively functioning as a constant offset. The turnover_norm component, by contrast, is anchored to an extreme outlier (raw max = 45.85), compressing most variation into a narrow low range. After normalization, the effective variance contribution of the turnover and Amihud components to the final composite is likely far below their nominal 25% and 20% shares.

A rigorous approach would estimate weights via **principal component analysis (PCA)**, allowing the data to determine which linear combinations of the five metrics capture the greatest variance in market-wide liquidity conditions. The first principal component of the correlation matrix would assign higher weights to metrics with more variation and lower co-linearity. Alternatively, **variance-equalizing weights** (setting $w_k \propto 1/\text{Std}(m_k)$, then renormalizing) would ensure equal effective contribution from each component, consistent with the goal of a balanced composite.

**No sensitivity analysis presented:**

A robustness standard for composite indices is to report how sensitive the composite score and its rankings are to alternative weight specifications. For the UZLI, this would mean computing alternative index series using, for example, equal weights (20% each), PCA weights, and a breadth-only specification, and verifying that the main findings (trend improvement since 2022, low average score, extreme seasonal variation) are not weight-dependent.

### 7.4 Formal Statement for the Methodology Section

The UZLI adopts a **fixed-weight, additive linear aggregation** of five normalized liquidity dimensions, following the approach of Chordia, Roll & Subrahmanyam (2001) for market-wide liquidity composites. Weights were determined by expert judgment prior to data analysis, following a principle of dimensional balance: each of the four measurable dimensions of liquidity (trading activity, market breadth, price impact, and transaction cost) is represented, with the two primary dimensions of trading activity (volume and turnover) together receiving equal weight as the breadth and price-impact dimensions combined. The spread dimension receives reduced weight reflecting the lower reliability of the daily high-low estimator relative to direct transaction-cost measurement.

---

## 8. Normalization Methodology

### 8.1 Specification

Each raw metric score is transformed to a [0, 100] scale using Min-Max normalization over the **full historical sample**:

$$\text{norm}_{k,t} = 100 \times \frac{x_{k,t} - \min_s(x_{k,s})}{\max_s(x_{k,s}) - \min_s(x_{k,s})}$$

where the minimum and maximum are computed over all $T = 2{,}373$ trading days.

### 8.2 Critique

**Full-sample normalization introduces look-ahead bias for real-time applications:**
The normalization uses future data (the full sample's extremes) to scale historical observations. This means that the UZLI score for, say, January 2018 incorporates information about what happened in 2023–2026. A practitioner constructing the index in real-time in January 2018 would have used different normalization bounds and arrived at a different score. This look-ahead does not invalidate the index for retrospective academic analysis (where the goal is to characterize historical liquidity conditions with the benefit of full-sample perspective), but it must be disclosed and would need to be addressed in any implementation of the index as a live monitoring tool.

**Sensitivity to outliers (L6):**
The turnover_score maximum of 45.85 — an apparent outlier — anchors the normalization for that component. Every other observation in the sample is normalized relative to this extreme day, compressing all other turnover_norm values into the bottom 0–3% of the [0, 100] range (since 1/45.85 ≈ 2.2). Robustness requires either (i) winsorizing the turnover score at the 99th or 95th percentile before normalization, or (ii) logging the turnover score before normalization (given its severe right-skew), or (iii) using percentile-rank normalization which is inherently outlier-resistant.

**Alternative approaches:**
- **Z-score standardization** (`(x - μ) / σ`): Preserves the distributional shape and does not require assuming bounds; standard in the financial economics literature (e.g., Chordia et al. 2000).
- **Percentile rank**: Maps each observation to its fractional rank in the sample, producing a uniform distribution on [0, 1]. Used by the IMF in some composite liquidity assessments; outlier-resistant by construction.
- **Rolling percentile rank**: Rank each observation within a rolling backward-looking window (e.g., 250 trading days), eliminating look-ahead bias while maintaining interpretability.

---

## 9. Overall Methodological Assessment

### 9.1 Summary Rating by Component

| Component | Conceptual Design | Implementation Fidelity | Information Content | Overall |
|---|---|---|---|---|
| Volume Score | ✓ Appropriate | ✓ Correctly implemented | ✓ High | **Strong** |
| Breadth Score | ✓ Appropriate | ⚠ Look-ahead bias in denominator | ✓ High | **Good, with disclosure** |
| Turnover Score | ✓ Appropriate | ✗ Incorrect denominator specification | ⚠ Degraded by outlier | **Weak as implemented** |
| Amihud Score | ✓ Appropriate | ⚠ Unit-scaling omitted | ✗ Near-zero in UZSE context | **Uninformative as scaled** |
| Spread Score | ✓ Appropriate | ✗ Significant deviations from CS (2012) | ⚠ Plausible range but unvalidated | **Partial** |

### 9.2 What the UZLI Reliably Measures

Despite the above limitations, the UZLI is a credible indicator of **broad-trend liquidity conditions** on the UZSE for the following reasons:

1. The two most reliable components — volume score and breadth score — together account for 45% of the composite and provide genuine, independently validated signals of market-wide activity.
2. The structural break at 2022–2023, visible in the annual means, is robust to the component-level weaknesses: it appears in both the volume and breadth components individually, not merely in the composite.
3. The finding that fewer than 10% of securities trade on a median day is directly observable from the raw data and does not depend on any index construction choices.
4. The absolute level of the composite (mean 41.20) is plausible in relative terms — it is consistent with other frontier market liquidity studies that find participation rates and turnover ratios far below developed market norms.

### 9.3 What the UZLI Should Not Be Used to Assert

1. **Precise numerical comparisons** between days or weeks, particularly where the difference is within the margin of the amihud and spread component noise.
2. **Cross-market comparability:** The Min-Max bounds and the unit-scaling choices make direct comparison to, for example, a similarly constructed Vietnamese or Kazakhstan liquidity index impossible without recalibration.
3. **The precise contribution of each dimension** to total liquidity, since the Amihud component contributes effectively no information and the turnover component is distorted by the denominator misspecification.

---

## 10. Recommendations for Second-Generation Implementation

| Priority | Component | Recommended Change | Expected Impact |
|---|---|---|---|
| 1 (Critical) | Turnover Score | Replace denominator with shares outstanding × close price | Corrects fundamental mismatch; removes outlier |
| 2 (Critical) | Amihud Score | Scale raw ILLIQ by 10⁶, or use USD-equivalent volumes | Restores cross-day information content; std rises from 0.0003 to informative range |
| 3 (High) | Spread Score | Implement correct two-day Corwin-Schultz α at security level, then average | Aligns with published formula; improves theoretical credibility |
| 4 (High) | Normalization | Replace Min-Max with percentile rank, or winsorize at 99th percentile | Eliminates outlier distortion of turnover_norm scale |
| 5 (High) | Breadth Score | Use time-varying listed-company count as denominator | Eliminates look-ahead bias for 2016–2018 observations |
| 6 (Moderate) | Weighting | Report sensitivity analysis with equal weights and PCA weights | Demonstrates robustness of main findings to weight specification |
| 7 (Moderate) | Amihud Score | Use close-to-close returns, consistent with Amihud (2002) | Aligns with canonical specification |
| 8 (Low) | Spread Score | Floor spread at 0 on days with negative estimates | Removes 2 economically nonsensical observations |

---

## 11. Recommended Citations for the Methodology Section

### Foundational Liquidity Theory
- Black, F. (1971). "Toward a Fully Automated Stock Exchange." *Financial Analysts Journal*, 27(4), 28–35.
- Kyle, A.S. (1985). "Continuous Auctions and Insider Trading." *Econometrica*, 53(6), 1315–1335.
- Amihud, Y. & Mendelson, H. (1986). "Asset Pricing and the Bid-Ask Spread." *Journal of Financial Economics*, 17(2), 223–249.

### Volume and Turnover Measures
- Datar, V.T., Naik, N.Y. & Radcliffe, R. (1998). "Liquidity and Stock Returns: An Alternative Test." *Journal of Financial Markets*, 1(2), 203–219.
- Lo, A.W. & Wang, J. (2000). "Trading Volume: Definitions, Data Analysis, and Implications of Portfolio Theory." *Review of Financial Studies*, 13(2), 257–300.
- Chordia, T., Roll, R. & Subrahmanyam, A. (2001). "Market Liquidity and Trading Activity." *Journal of Finance*, 56(2), 501–530.

### Breadth / Zero-Return / Zero-Volume Measures
- Lesmond, D.A., Ogden, J.P. & Trzcinka, C.A. (1999). "A New Estimate of Transaction Costs." *Review of Financial Studies*, 12(5), 1113–1141.
- Liu, W. (2006). "A Liquidity-Augmented Capital Asset Pricing Model." *Journal of Financial Economics*, 82(3), 631–671.
- Bekaert, G., Harvey, C.R. & Lundblad, C. (2007). "Liquidity and Expected Returns: Lessons from Emerging Markets." *Review of Financial Studies*, 20(6), 1783–1831.

### Amihud Price-Impact Measure
- Amihud, Y. (2002). "Illiquidity and Stock Returns: Cross-Section and Time-Series Effects." *Journal of Financial Markets*, 5(1), 31–56.
- Amihud, Y., Mendelson, H. & Pedersen, L.H. (2005). "Liquidity and Asset Prices." *Foundations and Trends in Finance*, 1(4), 269–364.

### Spread Estimation from Daily Data
- Roll, R. (1984). "A Simple Implicit Measure of the Effective Bid-Ask Spread in an Efficient Market." *Journal of Finance*, 39(4), 1127–1139.
- Corwin, S.A. & Schultz, P. (2012). "A Simple Way to Estimate Bid-Ask Spreads from Daily High and Low Prices." *Journal of Finance*, 67(2), 719–760.
- Fong, K.Y.L., Holden, C.W. & Trzcinka, C.A. (2017). "What Are the Best Liquidity Proxies for Global Research?" *Review of Finance*, 21(4), 1355–1401.

### Metric Validation and Comparison
- Goyenko, R.Y., Holden, C.W. & Trzcinka, C.A. (2009). "Do Liquidity Measures Measure Liquidity?" *Journal of Financial Economics*, 92(2), 153–181.
- Aitken, M. & Comerton-Forde, C. (2003). "How Should Liquidity Be Measured?" *Pacific-Basin Finance Journal*, 11(1), 45–59.
- Lesmond, D.A. (2005). "Liquidity of Emerging Markets." *Journal of Financial Economics*, 77(2), 411–452.

### Composite Index Construction
- Chordia, T., Roll, R. & Subrahmanyam, A. (2000). "Commonality in Liquidity." *Journal of Financial Economics*, 56(1), 3–28.
- Korajczyk, R.A. & Sadka, R. (2008). "Pricing the Commonality across Alternative Measures of Liquidity." *Journal of Financial Economics*, 87(1), 45–72.
- Svirydzenka, K. (2016). "Introducing a New Broad-Based Index of Financial Development." IMF Working Paper WP/16/5. Washington, D.C.: International Monetary Fund.

### Emerging Market Context
- Pástor, Ľ. & Stambaugh, R.F. (2003). "Liquidity Risk and Expected Stock Returns." *Journal of Political Economy*, 111(3), 642–685.
- Acharya, V.V. & Pedersen, L.H. (2005). "Asset Pricing with Liquidity Risk." *Journal of Financial Economics*, 77(2), 375–410.

---

## 12. Suggested Disclosure Paragraph for the Methodology Section

The following paragraph is offered for direct use or adaptation in the UZLI research paper:

> "Five liquidity dimensions are measured: aggregate market volume relative to its 90-day rolling average (volume score, weight 25%); the fraction of listed securities that actively traded on a given day (breadth score, weight 20%); a turnover-activity proxy using per-security share volume scaled by a market-cap surrogate (turnover score, weight 25%); the Amihud (2002) price-impact measure transformed to a liquidity score (Amihud score, weight 20%); and a high-low-based spread proxy inspired by Corwin & Schultz (2012) (spread score, weight 10%). Each raw metric is Min-Max normalized over the full 2016–2026 sample to a [0, 100] scale, and the weighted composite defines the UZLI score for each trading day. Three limitations of the current implementation merit disclosure: (i) the turnover score denominator substitutes a trailing-volume-based proxy for shares outstanding, which is unavailable for UZSE-listed securities, producing an unbounded raw series with a maximum of 45.85 that anchors the normalization; (ii) the Amihud illiquidity ratio, applied without the scaling factor recommended in the original paper for UZS-denominated volumes, produces near-constant values (std = 0.0003) that contribute negligible discriminating information to the composite; and (iii) the spread estimator applies a single-day adaptation of the Corwin-Schultz framework using cross-sectional average high-low ranges, departing from the published two-day, per-security implementation. These limitations are documented in full in the project audit and methodology review files; second-generation revisions are proposed therein."

---

*This review was prepared using exact formula verification against the project's source code (`scripts/compute_metrics.py`, `scripts/build_liquidity_index.py`, `scripts/build_index.py`) and the project audit data (`daily_metrics.csv`, `uzli_final.csv`). All statistical summaries cited are computed from the live dataset as at repository commit `4064565`.*
