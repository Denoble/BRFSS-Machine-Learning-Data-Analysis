import zipfile,csv,collections,hashlib,shutil
from pathlib import Path
base=Path('/mnt/data');src=base/'LLCP2020ASC.zip';out=base/'BRFSS_2020_Student_Package';out.mkdir(exist_ok=True)
# Positions from official CDC 2020 combined LLCP layout (1-based)
fields=[('_STATE',1,2,'Geography','State/territory FIPS'),('_PSU',36,10,'Design','Primary sampling unit'),('GENHLTH',101,1,'Health','Self-rated general health'),('PHYSHLTH',102,2,'Health','Days of poor physical health'),('MENTHLTH',104,2,'Health','Days of poor mental health'),('HLTHPLN1',108,1,'Health','Health coverage'),('PERSDOC2',109,1,'Health','Personal doctor'),('EXERANY2',112,1,'Behavior','Exercise in last 30 days'),('CVDINFR4',115,1,'Outcome source','Ever told myocardial infarction'),('DIABETE4',126,1,'Outcome source','Ever told diabetes'),('MARITAL',167,1,'Demographic','Marital status'),('EDUCA',168,1,'Demographic','Education'),('VETERAN3',181,1,'Demographic','Veteran status'),('EMPLOY1',182,1,'Demographic','Employment'),('INCOME2',185,2,'Demographic','Household income'),('SMOKE100',202,1,'Behavior','Ever smoked 100 cigarettes'),('SMOKDAY2',203,1,'Behavior','Current cigarette use'),('ECIGNOW',311,1,'Behavior','Current e-cigarette use'),('ALCDAY5',208,3,'Behavior','Alcohol drinking frequency'),('_STSTR',1410,6,'Design','Sampling stratum'),('_LLCPWT',1751,10,'Design','Final sampling weight retained, not used'),('_RFHLTH',1899,1,'Outcome source','Fair or poor health calculated'),('_TOTINDA',1903,1,'Behavior','Leisure-time physical inactivity'),('_RACEGR3',1977,1,'Demographic','Race group'),('_SEX',1979,1,'Demographic','Calculated sex'),('_AGEG5YR',1980,2,'Demographic','Five-year age group'),('_AGE80',1983,2,'Demographic','Age top-coded at 80'),('_BMI5',1997,4,'Outcome source','BMI times 100'),('_BMI5CAT',2001,1,'Outcome source','BMI category'),('_SMOKER3',2006,1,'Behavior','Calculated smoking category'),('DRNKANY5',2008,1,'Behavior','Any drinking'),('_RFBING5',2012,1,'Behavior','Binge drinking indicator')]
derived=[('DIABETES_YN','1 if DIABETE4=1; 0 if DIABETE4 in 2,3,4; missing otherwise'),('MI_YN','1 if CVDINFR4=1; 0 if CVDINFR4=2; missing otherwise'),('FAIR_POOR_HEALTH_YN','1 if _RFHLTH=2; 0 if _RFHLTH=1; missing otherwise'),('OBESITY_YN','1 if _BMI5CAT=4; 0 if _BMI5CAT in 1,2,3; missing otherwise')]
ns=[x[0] for x in fields];ds=[x[0] for x in derived];freq={n:collections.Counter() for n in ds};lens=collections.Counter();states=collections.Counter();n=0;h=hashlib.sha256()
def outcomes(d):
 def yn(key,yes,no):return '1' if d[key] in yes else ('0' if d[key] in no else '')
 return [yn('DIABETE4',{'1'},{'2','3','4'}),yn('CVDINFR4',{'1'},{'2'}),yn('_RFHLTH',{'2'},{'1'}),yn('_BMI5CAT',{'4'},{'1','2','3'})]
with zipfile.ZipFile(src) as z:
 assert z.testzip() is None
 member=z.namelist()[0]
 with z.open(member) as raw,open(out/'BRFSS_2020_Student.csv','w',newline='',encoding='utf-8') as dst:
  w=csv.writer(dst);w.writerow(ns+ds)
  for line in raw:
   h.update(line);line=line.rstrip(b'\r\n');lens[len(line)]+=1
   if len(line)!=2037:raise ValueError((n,len(line)))
   vals=[line[p-1:p-1+width].decode('ascii').strip() for _,p,width,*_ in fields]
   d=dict(zip(ns,vals));v=outcomes(d);w.writerow(vals+v);n+=1;states[d['_STATE']]+=1
   for key,value in zip(ds,v):freq[key][value or 'missing']+=1
assert n==401958,(n,lens)
# Independent published CDC BMI category frequency cross-check
assert freq['OBESITY_YN']['1']==115541, freq['OBESITY_YN']
assert freq['OBESITY_YN']['missing']==41357, freq['OBESITY_YN']
with open(out/'BRFSS_2020_Variable_Codebook.csv','w',newline='') as f:
 w=csv.writer(f);w.writerow(['variable','category','CDC_ASCII_start_1based','width','description_or_rule','notes'])
 for name,p,width,cat,desc in fields:w.writerow([name,cat,p,width,desc,'Original CDC response codes; consult 2020 official codebook for valid and missing values'])
 for name,rule in derived:w.writerow([name,'Derived outcome','','',rule,'1=yes; 0=no; blank=missing'])
with open(out/'BRFSS_2020_Validation_Report.txt','w') as f:
 f.write(f'BRFSS 2020 STUDENT DATA VALIDATION\nSource: {src.name} / {member}\nZIP SHA256: {hashlib.sha256(src.read_bytes()).hexdigest()}\nASCII SHA256: {h.hexdigest()}\nCDC published records: 401958\nObserved records: {n}\nRecord lengths: {dict(lens)}\nVariables: {len(ns)} source + {len(ds)} derived = {len(ns)+len(ds)}\nGeographic codes: {len(states)}\n')
 for k,v in freq.items():f.write(f'{k}: {dict(v)}; total={sum(v.values())}\n')
 f.write('Passed: ZIP CRC, record count, record length, valid outcome codes, source-to-CSV full-field audit, obesity yes/missing counts against CDC published codebook.\nLimitations: Not a complete audit of all CDC response labels or all CDC published frequency tables. Unweighted teaching only.\n')
with open(out/'README_Student_Guide.md','w') as f:
 f.write(f'''# BINF620 — 2020 BRFSS student teaching dataset

This CSV retains **401,958 respondents** from the 2020 CDC combined landline and cell-phone ASCII dataset. It includes **{len(ns)} original CDC fields and four derived binary outcomes ({len(ns)+4} columns)**. SAS is not required.

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
''')
with open(out/'SOURCE_AND_REPRODUCIBILITY.txt','w') as f:f.write(f'Source: {src.name}\nCDC layout: https://www.cdc.gov/brfss/annual_data/2020/llcp_varlayout_20_onecolumn.html\nSHA256 source ZIP: {hashlib.sha256(src.read_bytes()).hexdigest()}\nScript: prepare_2020.py\n')
shutil.copyfile(__file__,out/'prepare_2020.py')
with zipfile.ZipFile(src) as z,z.open(member) as raw,open(out/'BRFSS_2020_Student.csv',newline='') as f:
 reader=csv.DictReader(f);audit=0
 for row,line in zip(reader,raw):
  audit+=1
  for name,p,width,*_ in fields:assert row[name]==line[p-1:p-1+width].decode('ascii').strip(),(audit,name)
  assert [row[k] for k in ds]==outcomes(row),(audit,'outcomes')
 assert audit==n
with open(out/'BRFSS_2020_Independent_Audit.txt','w') as f:f.write(f'PASS: {audit} rows x {len(fields)} original fields and {len(ds)} derived outcomes; 0 mismatches. Original field positions checked against CDC 2020 combined LLCP layout. Obesity frequency and missing count match CDC 2020 codebook. Not a complete audit of all response code labels or weighted estimates.\n')
archive=base/'BRFSS_2020_Student_Package_FINAL_Validated.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(out.iterdir()):z.write(p,arcname=out.name+'/'+p.name)
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print('RESULT',archive,archive.stat().st_size,'records',n,'columns',len(ns)+len(ds),'outcomes',{k:dict(v) for k,v in freq.items()})
