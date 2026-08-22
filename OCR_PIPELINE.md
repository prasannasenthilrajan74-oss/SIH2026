# OCR & Document Verification Pipeline

The Document Intelligence Center implements a structured pipeline to audit sanction orders and completion certificates against registry database records.

---

## 1. The Processing Pipeline

The text extraction pipeline executes sequentially with strict fallbacks:

```text
              [ Upload Sanction PDF ]
                         |
                         v
              [ Try digital parsing ] -----( Success? )-----> [ Extract text ]
                         |                                           |
                      ( Fails )                                      |
                         v                                           v
            [ Run pytesseract OCR ] ---> [ OCR text ] ---------> [ Combined Text ]
                                                                     |
                                                                     v
                                                          [ Entity Regex Parser ]
                                                                     |
                                                                     +--> Work ID
                                                                     +--> Sanctioned Amount
                                                                     +--> Sanction Date
                                                                     +--> Implementing Agency
                                                                     +--> Project Title
                                                                     |
                                                                     v
                                                        [ Database Cross-Validation ]
                                                                     |
                                                                     v
                                                        [ Consistency Score (0-100) ]
```

---

## 2. Parsing Extracted Entities
Regular expressions are deployed to locate critical markers:
- **Work ID**: `MPLADS-\d{4}-\d{4,5}`
- **Sanctioned Amount**: `(?:Rs\.?|Rupees|₹)\s*([\d,]+(?:\.\d{2})?)`
- **Sanction Date**: `(?:Date|Dated):\s*(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})`
- **Implementing Agency**: Scans text for substrings of active agencies fetched from the database.

---

## 3. Database Cross-Validation
After parsing the metadata, the validation engine queries the corresponding project record in the database and performs a field-by-field audit:
1. **Work ID**: Exact string comparison.
2. **Sanctioned Amount**: Evaluates numeric delta. If deviation is $<1\%$, it is a match; otherwise, a mismatch alert is flagged.
3. **Sanction Date**: Formats and compares document dates vs database values.
4. **Implementing Agency**: Evaluates containment match (e.g. "PWD" matching "Public Works Department").

The ratio of matches determines the **Consistency Score**. If the score falls below $90\%$, the system automatically spawns a `RULE_DOC_MISMATCH` active alert, prompting manual auditor review.
