# FEC Data Dictionary and Reference Guide

## Independent Expenditure Transaction Codes

When analyzing the PAS2 files (itpas2.txt), independent expenditures are identified by specific transaction type codes:

### Transaction Type Codes for Independent Expenditures

| Code | Description | Use in Analysis |
|------|-------------|-----------------|
| **24E** | Independent expenditure advocating **election** of candidate | ✓ Include - Supporting candidate |
| **24A** | Independent expenditure advocating **defeat** of candidate | ✓ Include - Opposing candidate |
| **24N** | Independent expenditure (non-exempt) | ✓ Include - Generic IE |
| 24K | In-kind contribution | ✗ Exclude - Not an IE |
| 24F | Independent expenditure void | ✗ Exclude - Void transaction |

## Committee Type Codes

The Committee Master (cm.txt) file contains a `CMTE_TP` field that categorizes committees:

### Critical for Citizens United Analysis

| Code | Committee Type | Significance |
|------|----------------|--------------|
| **O** | **Super PAC** (Independent Expenditure-Only Committee) | 🎯 **KEY**: Did not exist before Citizens United! |
| N | PAC - Nonqualified | Traditional PAC |
| Q | PAC - Qualified | Traditional PAC |
| V | PAC with Non-Contribution Account | Hybrid PAC |
| U | Single Candidate Independent Expenditure | Individual IE committee |

### Other Committee Types

| Code | Committee Type | Notes |
|------|----------------|-------|
| H | House candidate committee | Not usually making IEs |
| S | Senate candidate committee | Not usually making IEs |
| P | Presidential candidate committee | Not usually making IEs |
| X | Party - Nonqualified | Party committee |
| Y | Party - Qualified | Party committee |
| Z | National Party Nonfederal | Party committee |

## Committee Designation Codes

The `CMTE_DSGN` field indicates the committee's designation:

| Code | Designation |
|------|-------------|
| A | Authorized by a candidate |
| J | Joint fundraising committee |
| P | Principal campaign committee |
| U | Unauthorized |
| B | Lobbyist/Registrant PAC |
| D | Leadership PAC |

## Party Affiliation Codes

Found in both Candidate Master (cn.txt) and Committee Master (cm.txt):

| Code | Party | Use in Analysis |
|------|-------|-----------------|
| **DEM** | Democratic Party | ✓ Primary focus |
| **REP** | Republican Party | ✓ Primary focus |
| IND | Independent | Optional |
| LIB | Libertarian Party | Optional |
| GRE | Green Party | Optional |
| (blank) | Unknown | Exclude |

## Office Codes

Found in Candidate Master (cn.txt) `CAND_OFFICE` field:

| Code | Office | Use in Analysis |
|------|--------|-----------------|
| **P** | President | ✓ Include |
| **S** | Senate | ✓ Include |
| H | House | ✗ Exclude (per research scope) |

## Key Data Files

### 1. PAS2 File (itpas2.txt)
**Purpose**: Contains committee contributions to candidates AND independent expenditures

**Key Fields**:
- `CMTE_ID`: Committee making the expenditure (link to cm.txt)
- `TRANSACTION_TP`: Type of transaction (24E, 24A, 24N for IEs)
- `CAND_ID`: Candidate benefiting from expenditure (link to cn.txt)
- `TRANSACTION_AMT`: Dollar amount
- `TRANSACTION_DT`: Date of transaction
- `ENTITY_TP`: Entity type (IND=Individual, COM=Committee, etc.)

### 2. Candidate Master (cn.txt)
**Purpose**: Information about candidates

**Key Fields**:
- `CAND_ID`: Unique candidate identifier
- `CAND_NAME`: Candidate name
- `CAND_PTY_AFFILIATION`: Party (DEM, REP, etc.)
- `CAND_OFFICE`: Office sought (P, S, H)
- `CAND_OFFICE_ST`: State (for Senate races)
- `CAND_ELECTION_YR`: Election year

### 3. Committee Master (cm.txt)
**Purpose**: Information about committees

**Key Fields**:
- `CMTE_ID`: Unique committee identifier
- `CMTE_NM`: Committee name
- `CMTE_TP`: Committee type (O, N, Q, etc.)
- `CMTE_DSGN`: Committee designation
- `ORG_TP`: Organization type (C=Corporation, L=Labor, etc.)
- `CONNECTED_ORG_NM`: Connected organization name
- `CMTE_PTY_AFFILIATION`: Party affiliation

## Analysis Periods

### Pre-Citizens United (2002-2010)
**Cycles**:
- 2001-2002 (Election year: 2002)
- 2003-2004 (Election year: 2004)
- 2005-2006 (Election year: 2006)
- 2007-2008 (Election year: 2008)
- 2009-2010 (Election year: 2010)

**Expected Characteristics**:
- Limited or no Super PAC (type O) activity
- More traditional PAC activity
- Lower overall IE volumes
- Stricter contribution limits enforced

### Post-Citizens United (2011-2020)
**Cycles**:
- 2011-2012 (Election year: 2012)
- 2013-2014 (Election year: 2014)
- 2015-2016 (Election year: 2016)
- 2017-2018 (Election year: 2018)
- 2019-2020 (Election year: 2020)