# BINF620 — 2020 BRFSS student teaching dataset

This CSV retains **401,958 respondents** from the 2020 CDC combined landline and cell-phone ASCII dataset. It includes **32 original CDC fields and four derived binary outcomes (36 columns)**. SAS is not required.

## Outcomes
- `DIABETES_YN`: 1 diagnosed diabetes (`DIABETE4=1`); 0 for `DIABETE4=2,3,4` (includes gestational-only and prediabetes); other responses missing.
- `MI_YN`: 1 heart attack (`CVDINFR4=1`); 0 no (`=2`); others missing.
- `FAIR_POOR_HEALTH_YN`: 1 if `_RFHLTH=2`; 0 if `_RFHLTH=1`; others missing.
- `OBESITY_YN`: 1 if `_BMI5CAT=4`; 0 if `_BMI5CAT` is 1, 2, or 3; blank if missing. The CDC BMI source `_BMI5` has two implied decimals.

## Modeling guidance
- Recode refusal, don't-know and not-asked codes to missing **for each predictor** before modeling; the original predictor fields retain CDC codes.
- Do not use outcome-source fields (`DIABETE4`, `CVDINFR4`, `_RFHLTH`, `_BMI5`, `_BMI5CAT`) to predict their corresponding derived outcome (target leakage).
- `_LLCPWT`, `_STSTR` and `_PSU` are retained only for context. Student exercises use unweighted analyses and must not describe results as population-representative. Standard errors and tests from ordinary models do not account for the survey design.
- Annual coding differs. Do not pool years without harmonizing coding and survey design.

## Example R
```r
d <- read.csv('BRFSS_2020_Student.csv', check.names=FALSE, na.strings='')
table(d[['DIABETES_YN']], useNA='ifany')
x <- subset(d, `_SEX` %in% c(1,2) & `_AGEG5YR` %in% 1:13 & !is.na(DIABETES_YN))
x$sex <- factor(x[['_SEX']]); x$age_group <- factor(x[['_AGEG5YR']])
fit <- glm(DIABETES_YN ~ sex + age_group, data=x, family=binomial())
summary(fit)
```

## Official CDC documentation
- https://www.cdc.gov/brfss/annual_data/annual_2020.html
- https://www.cdc.gov/brfss/annual_data/2020/llcp_varlayout_20_onecolumn.html
- https://www.cdc.gov/brfss/annual_data/2020/pdf/codebook20_llcp-v2-508.pdf

The original source ZIP is not duplicated. Place `LLCP2020ASC.zip` alongside `prepare_2020.py` in `/mnt/data` or adjust the source path to reproduce.
